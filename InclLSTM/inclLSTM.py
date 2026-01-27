import numpy as np
import tensorflow as tf
from tensorflow.keras import layers, models, backend as K, optimizers, losses
import os
import json

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
tf.get_logger().setLevel('ERROR')

class FLShareLayer(layers.Layer):
    """Fuses the hidden states of old and new models"""
    def __init__(self, units, **kwargs):
        super(FLShareLayer, self).__init__(**kwargs)
        self.units = units

    def build(self, input_shape):
        self.U = self.add_weight(name='U', shape=(self.units, self.units), initializer='glorot_uniform', trainable=True)
        self.W = self.add_weight(name='W', shape=(self.units, self.units), initializer='glorot_uniform', trainable=True)
        super(FLShareLayer, self).build(input_shape)

    def call(self, inputs):
        h_old, h_new = inputs
        gate_old = K.dot(h_old, self.U)
        gate_new = K.dot(h_new, self.W)
        return tf.nn.relu(gate_old + gate_new)

    def get_config(self):
        config = super(FLShareLayer, self).get_config()
        config.update({"units": self.units})
        return config

class IncLSTMDual:
    def __init__(self, steps_past, features_past, steps_future, features_future, buffer_size=5):
        self.steps_past = steps_past
        self.features_past = features_past
        self.steps_future = steps_future
        self.features_future = features_future
        self.buffer_size = buffer_size
        self.weak_learners = []
        self.learner_weights = []
        self.learner_count = 0

    def _build_graph(self, trainable=True):
        """Builds the dual input graph"""
        input_past = layers.Input(shape=(self.steps_past, self.features_past), name="input_past")
        x = layers.Bidirectional(layers.LSTM(64, return_sequences=True, dropout=0.1))(input_past)
        x = layers.Bidirectional(layers.LSTM(32, return_sequences=False, dropout=0.1))(x)

        input_future = layers.Input(shape=(self.steps_future, self.features_future), name="input_future")
        future_flat = layers.Flatten()(input_future)

        concat = layers.Concatenate()([x, future_flat])
        hidden = layers.Dense(128, activation='relu')(concat)

        hook_name = f"shared_hook_{self.learner_count}"
        h_state = layers.Lambda(lambda x: x, name=hook_name)(hidden)

        outputs = layers.Dense(self.steps_future, name="output_power")(h_state)

        model = models.Model(inputs=[input_past, input_future], outputs=outputs)
        model.trainable = trainable
        return model

    def _build_base_model(self):
        model = self._build_graph(trainable=True)
        model.compile(optimizer=optimizers.Adam(learning_rate=0.001), loss=losses.Huber())
        self.learner_count += 1
        return model

    def _build_transfer_model(self, old_model):
        """Implements FL-Share Transfer """
        target_name = f"shared_hook_{self.learner_count - 1}"

        try:
            old_out = old_model.get_layer(target_name).output
        except ValueError:
            old_out = old_model.layers[-2].output

        old_branch = models.Model(inputs=old_model.input, outputs=old_out)

        input_past = layers.Input(shape=(self.steps_past, self.features_past), name="input_past")
        input_future = layers.Input(shape=(self.steps_future, self.features_future), name="input_future")

        x = layers.Bidirectional(layers.LSTM(64, return_sequences=True, dropout=0.1))(input_past)
        x = layers.Bidirectional(layers.LSTM(32, return_sequences=False, dropout=0.1))(x)
        future_flat = layers.Flatten()(input_future)
        concat = layers.Concatenate()([x, future_flat])
        hidden = layers.Dense(128, activation='relu')(concat)

        hook_name = f"shared_hook_{self.learner_count}"
        h_new = layers.Lambda(lambda x: x, name=hook_name)(hidden)

        h_old = old_branch([input_past, input_future])

        fusion = FLShareLayer(units=128)([h_old, h_new])
        outputs = layers.Dense(self.steps_future)(fusion)

        model = models.Model(inputs=[input_past, input_future], outputs=outputs)
        model.compile(optimizer=optimizers.Adam(learning_rate=0.0005), loss=losses.Huber())
        self.learner_count += 1
        return model

    def update_weights_and_buffer(self, X_p_new, X_f_new, y_new):
        """
        Implements weighting and buffer, evaluates existing learners on the new data to determine validity
        """
        if not self.weak_learners:
            return

        errors = []
        for model in self.weak_learners:
            pred = model.predict([X_p_new, X_f_new], verbose=0)
            abs_err = np.abs(pred - y_new.reshape(pred.shape))
            mean_err = np.mean(abs_err)
            errors.append(mean_err)

        if len(self.weak_learners) >= self.buffer_size:
            worst_idx = np.argmax(errors)

            self.weak_learners.pop(worst_idx)
            self.learner_weights.pop(worst_idx)
            errors.pop(worst_idx)

        errors_arr = np.array(errors)
        scale = 10.0
        weights = np.exp(-errors_arr * scale)

        sum_weights = np.sum(weights)
        if sum_weights == 0:
            weights = np.ones(len(errors))
        else:
            weights /= sum_weights

        self.learner_weights = list(weights)

    def fit_incremental(self, X_p, X_f, y, epochs=10):
        """Trains a new weak learner and adds it to the ensemble"""
        K.clear_session()

        if not self.weak_learners:
            model = self._build_base_model()
            model.fit([X_p, X_f], y, epochs=epochs*2, batch_size=32, verbose=0)
        else:
            prev = self.weak_learners[-1]
            model = self._build_transfer_model(prev)
            model.fit([X_p, X_f], y, epochs=epochs, batch_size=32, verbose=0)

        self.weak_learners.append(model)

        if self.learner_weights:
            avg_weight = sum(self.learner_weights) / len(self.learner_weights)
            self.learner_weights.append(avg_weight)
        else:
            self.learner_weights.append(1.0)

        total = sum(self.learner_weights)
        self.learner_weights = [w/total for w in self.learner_weights]

    def predict(self, X_past, X_future):
        if not self.weak_learners:
            return np.zeros((len(X_past), self.steps_future))

        preds_stack = np.zeros((len(X_past), self.steps_future))
        total_w = sum(self.learner_weights)

        for model, w in zip(self.weak_learners, self.learner_weights):
            p = model.predict([X_past, X_future], verbose=0)
            preds_stack += p * w

        return preds_stack / total_w

    def save_system(self, directory):
        """Saves the entire ensemble, metadata, and config"""
        if not os.path.exists(directory):
            os.makedirs(directory)

        metadata = {
            'steps_past': self.steps_past,
            'features_past': self.features_past,
            'steps_future': self.steps_future,
            'features_future': self.features_future,
            'buffer_size': self.buffer_size,
            'learner_weights': self.learner_weights,
            'learner_count': self.learner_count
        }
        with open(os.path.join(directory, 'metadata.json'), 'w') as f:
            json.dump(metadata, f)

        for i, model in enumerate(self.weak_learners):
            model_path = os.path.join(directory, f'learner_{i}.keras')
            model.save(model_path)

        print(f"System saved to: {directory}")

    @staticmethod
    def load_system(directory):
        """Load the model from disk."""
        if not os.path.exists(directory):
            raise FileNotFoundError(f"Directory {directory} not found.")

        with open(os.path.join(directory, 'metadata.json'), 'r') as f:
            meta = json.load(f)

        instance = IncLSTMDual(
            steps_past=meta['steps_past'],
            features_past=meta['features_past'],
            steps_future=meta['steps_future'],
            features_future=meta['features_future'],
            buffer_size=meta['buffer_size']
        )
        instance.learner_weights = meta['learner_weights']
        instance.learner_count = meta['learner_count']

        custom_objects = {'FLShareLayer': FLShareLayer}

        i = 0
        while True:
            model_path = os.path.join(directory, f'learner_{i}.keras')
            if not os.path.exists(model_path):
                break

            model = tf.keras.models.load_model(model_path, custom_objects=custom_objects)
            instance.weak_learners.append(model)
            i += 1

        print(f"System loaded from: {directory} ({len(instance.weak_learners)} models)")
        return instance