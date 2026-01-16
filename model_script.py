import pandas as pd
import numpy as np
from dataclasses import dataclass
from datetime import datetime
from typing import Tuple, Dict, Any, Generator

from river import compose, preprocessing, tree, metrics, drift

@dataclass
class Prediction:
    timestamp: datetime
    plant_id: str
    predicted_power: float
    actual_power: float
    is_drift: bool

def create_model():
    return compose.Pipeline(
        preprocessing.StandardScaler(),
        tree.HoeffdingTreeRegressor(
            grace_period=100,
            model_selector_decay=0.9
        )
    )

def create_metric():
    return metrics.MAE() + metrics.R2()

def create_adwin():
    return drift.ADWIN(delta=0.002)

def preprocess_realtime(raw_reading: Dict[str, Any]) -> Tuple[dict, float, datetime, str]:
    """
    Performs preprocessing as data arrives
    """
    timestamp = pd.to_datetime(raw_reading['DATE_TIME'])
    plant_id = raw_reading['SOURCE_KEY']
    target = float(raw_reading['AC_POWER'])

    features = {
        'AMBIENT_TEMPERATURE': raw_reading['AMBIENT_TEMPERATURE'],
        'MODULE_TEMPERATURE': raw_reading['MODULE_TEMPERATURE'],
        'IRRADIATION': raw_reading['IRRADIATION']
    }

    hour = timestamp.hour
    features['hour_sin'] = np.sin(2 * np.pi * hour / 24)
    features['hour_cos'] = np.cos(2 * np.pi * hour / 24)

    return features, target, timestamp, plant_id

def process_one_reading(model, metric, adwin, features: dict, target: float) -> Tuple[float, bool]:
    """
    Contains the training loop for one reading: predict, detect drift, update metric, learn
    """
    y_pred = model.predict_one(features)
    if y_pred is None:
        y_pred = 0.0

    error = abs(target - y_pred)
    adwin.update(error)
    drift_detected = adwin.drift_detected

    metric.update(target, y_pred)

    model.learn_one(features, target)

    return y_pred, drift_detected

def sensor_stream_simulator(csv_path: str) -> Generator[Dict[str, Any], None, None]:
    """
    Yields data as if coming from sensors
    """
    print(f"Connecting to sensor stream at {csv_path}...")
    df = pd.read_csv(csv_path)
    stream_data = df.to_dict('records')
    
    for packet in stream_data:
        yield packet


def run_realtime_controller(csv_path):
    """
    Contains the full training of the model
    """
    model = create_model()
    metric = create_metric()
    adwin = create_adwin()
    
    predictions = []
    
    print("System Initialized. Listening for sensor events...")

    # sensor_stream_simulator: simulation of sensor data stream
    for i, raw_packet in enumerate(sensor_stream_simulator(csv_path)): 
        x, y, ts, plant_id = preprocess_realtime(raw_packet)

        y_pred, is_drift = process_one_reading(model, metric, adwin, x, y)

        result = Prediction(
            timestamp=ts,
            plant_id=plant_id,
            predicted_power=y_pred,
            actual_power=y,
            is_drift=is_drift
        )
        predictions.append(result)
        
        # logging
        """if i % 500 == 0:
            print(f"[{ts}] Event #{i} | Actual: {y:.2f} | Pred: {y_pred:.2f} | MAE: {metric.get()[0]:.4f} | R^2: {metric.get()[1]:.4f}")
            if is_drift:
                print(f"!!! DRIFT DETECTED at {ts} !!!")"""

    print(f"\nStream ended. Final MAE: {metric.get()[0]:.4f}, Final R^2: {metric.get()[1]:.4f}")
    return predictions