import pandas as pd
import numpy as np
from dataclasses import dataclass
from datetime import datetime
from typing import Tuple, Dict, Any, Generator
from river import compose, preprocessing, tree, metrics, drift

from backend.models.prediction import HistoricalPrediction
from backend.utils.sensor_stream_simulator import full_packet_stream_simulator, load_historical_data
from backend.dao.prediction_dao import PredictionDao #this is used for tests
from backend.dao.weather_dao import WeatherDAO #this is used for tests



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



#def preprocess_realtime(raw_reading: Dict[str, Any]) -> Tuple[dict, float, datetime, str]:
#    """
#    Performs preprocessing as data arrives
#    """
#    timestamp = pd.to_datetime(raw_reading['DATE_TIME'])
#    plant_id = raw_reading['SOURCE_KEY']
#    target = float(raw_reading['AC_POWER'])
#
#    features = {
#        'AMBIENT_TEMPERATURE': raw_reading['AMBIENT_TEMPERATURE'],
#        'MODULE_TEMPERATURE': raw_reading['MODULE_TEMPERATURE'],
#        'IRRADIATION': raw_reading['IRRADIATION']
#    }
#
#    hour = timestamp.hour
#    features['hour_sin'] = np.sin(2 * np.pi * hour / 24)
#    features['hour_cos'] = np.cos(2 * np.pi * hour / 24)
#
#    return features, target, timestamp, plant_id



def preprocess_realtime_2(features: Dict[str, Any], timestamp: datetime) -> Dict[str, Any]:
    hour = timestamp.hour
    features['hour_sin'] = np.sin(2 * np.pi * hour / 24)
    features['hour_cos'] = np.cos(2 * np.pi * hour / 24)

    return features
    


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



def run_realtime_controller(
        interval_s: int = 1, data_directory: str = "cleaned_data", 
        plant_id: str= "solar_1", panel_id: str = None, 
        start_time: datetime = None, end_time: datetime = None):
    """
    Contains the full training of the model
    """
    model = create_model()
    metric = create_metric()
    adwin = create_adwin()
    
    predictions = []
    
    print("System Initialized. Listening for sensor events...")

    # sensor_stream_simulator: simulation of sensor data stream
    for i, full_packet in enumerate(full_packet_stream_simulator(interval_s=interval_s, data_directory=data_directory, plant_id=plant_id, start_time=start_time, end_time=end_time)): 
        x, y, ts, panel_id = full_packet
        x = preprocess_realtime_2(x, ts)

        y_pred, is_drift = process_one_reading(model, metric, adwin, x, y)

        result = HistoricalPrediction(
            timestamp = ts,
            plant_id= plant_id,
            panel_id=panel_id,
            predicted_ac_power=y_pred,
            real_ac_power=y,
            drift=is_drift
        )

        predictions.append(result)
        
        #print(f"\r\n\nRaw packet {i}: {full_packet}")
        #print(f"Result {i}: {result}")

        # logging
        """if i % 500 == 0:
            print(f"[{ts}] Event #{i} | Actual: {y:.2f} | Pred: {y_pred:.2f} | MAE: {metric.get()[0]:.4f} | R^2: {metric.get()[1]:.4f}")
            if is_drift:
                print(f"!!! DRIFT DETECTED at {ts} !!!")"""

    print(f"\nStream ended. Final MAE: {metric.get()[0]:.4f}, Final R^2: {metric.get()[1]:.4f}")
    return predictions, model



def train_model_on_historical_data(data_directory: str = "cleaned_data", plant_id: str = "solar_1", end_time: datetime = None):

    model = create_model()
    metric = create_metric()
    adwin = create_adwin()

    prediction_dao = PredictionDao("historical_predictions")

    if end_time is None:
        s = "2020-06-14 23:45:00"
        end_time = datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
    
    for historical_data in load_historical_data(data_directory=data_directory, plant_id=plant_id, end_time=end_time):
        x, y, ts, panel_id = historical_data
        x = preprocess_realtime_2(x, ts)
        y_pred, is_drift = process_one_reading(model, metric, adwin, x, y)

        prediction = HistoricalPrediction(
            timestamp = ts,
            plant_id= plant_id,
            panel_id=panel_id,
            predicted_ac_power=y_pred,
            real_ac_power=y,
            drift=is_drift
        )
        prediction_dao.save_prediction(prediction)

    return model, metric, adwin

        


    
    


##testing
#interval_s = 0
#data_directory = "cleaned_data"
#plant_id = "solar_1"
#s = "2020-06-13 19:00:00"
#end_time = datetime.strptime(s, "%Y-%m-%d %H:%M:%S")
#start_time = 30
#predictions, model = run_realtime_controller(interval_s=interval_s,data_directory = data_directory, plant_id=plant_id, end_time=end_time, start_time=start_time)
#
#prediction_directory = "historical_predictions"
#prediction_dao = PredictionDao(prediction_directory)
#for prediction in predictions:
#    prediction_dao.save_prediction(prediction)
#
#weather_dao = WeatheDAO("cleaned_data")
#model = train_model_on_historical_data()
#for i, measure in enumerate(weather_dao.get_all_weather_measurements_by_plant_id("solar_1")):
#
#    x =  {
#        'AMBIENT_TEMPERATURE': measure.ambient_temperature ,
#        'MODULE_TEMPERATURE': measure.module_temperature,
#        'IRRADIATION': measure.irradiation
#    }
#
#    x = preprocess_realtime_2(x, measure.timestamp)
#
#    prediction = model.predict_one(x)
#    print(f"Prediction {i} at time {measure.timestamp}: {prediction}")