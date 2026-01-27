from datetime import datetime, timedelta, time
from collections import defaultdict
import pandas as pd
import numpy as np

from backend.dao.panel_dao import PanelsDAO
from backend.dao.weather_dao import WeatherDAO
from backend.dao.prediction_dao import PredictionDao
from backend.dao.measurements_dao import MeasurementsDAO
from backend.models.prediction import HistoricalPrediction, GlobalPrediction
from backend.utils.sensor_stream_simulator import load_future_weather_data
from backend.utils.model_script import preprocess_realtime_2, process_one_reading



class PredictionService:
    def __init__(self, models, data_directory="cleaned_data", historical_predictions: str = "historical_predictionss"):
        self.prediction_dao = PredictionDao(historical_predictions)
        self.weather_dao = WeatherDAO(data_directory)
        self.measure_dao = MeasurementsDAO(data_directory)
        self.panels_dao = PanelsDAO(data_directory)
        self.LSTM_prediction_dao = PredictionDao("InclLSTM") #this is to show LSTM dashboard 
        self.models = models
        self.data_directory = data_directory


    def train_next_timestamp_for_given_panel_and_timestamp(self, plant_id: str, panel_id: str, timestamp: datetime):

        w = self.weather_dao.get_weather_by_plant_id_and_timestamp(plant_id, timestamp)
        weather_features = {
            "AMBIENT_TEMPERATURE": w.ambient_temperature,
            "MODULE_TEMPERATURE": w.module_temperature,
            "IRRADIATION": w.irradiation
        }
        features = preprocess_realtime_2(weather_features, timestamp)

        m = self.measure_dao.get_panel_measurement_by_plant_id_and_panel_id_and_timestamp(plant_id, panel_id, timestamp)
        target = m.ac_power
        
        model, metric, adwin = self.models.get(plant_id)
        y_pred, drift_detected = process_one_reading(model, metric, adwin, features, target)
        prediction = HistoricalPrediction(
            timestamp = timestamp,
            plant_id= plant_id,
            panel_id=panel_id,
            predicted_ac_power=y_pred,
            real_ac_power=m.ac_power,
            drift=drift_detected
        )
        return prediction

    def train_next_timestamp(self, plant_id: str, panel_id: str, timestamp: datetime):
        _, predictions = self.train_all_panels_for_given_timestamp(plant_id, timestamp)
        return next((p for p in predictions if p.panel_id == panel_id),None)

    def train_all_panels_for_given_timestamp(self, plant_id: str, timestamp: datetime):
        
        w = self.weather_dao.get_weather_by_plant_id_and_timestamp(plant_id, timestamp)
        if not w:
            return None, []

        weather_features = {
            "AMBIENT_TEMPERATURE": w.ambient_temperature,
            "MODULE_TEMPERATURE": w.module_temperature,
            "IRRADIATION": w.irradiation
        }
        features = preprocess_realtime_2(weather_features, timestamp)

        all_measurements = self.measure_dao.get_panel_measurements_by_plant_id_and_time_range(
            plant_id, start_time=timestamp, end_time=timestamp
        )

        meas_map = {m.panel_id: m for m in all_measurements}

        predictions = []
        global_power = 0.0
        model, metric, adwin = self.models.get(plant_id)
        for panel_id, m in meas_map.items():
            y_pred, drift_detected = process_one_reading(model, metric, adwin, features, m.ac_power)

            prediction = HistoricalPrediction(
                timestamp=timestamp,
                plant_id=plant_id,
                panel_id=panel_id,
                predicted_ac_power=y_pred,
                real_ac_power=m.ac_power,
                drift=drift_detected
            )
            predictions.append(prediction)
            global_power += y_pred

        global_prediction = GlobalPrediction(timestamp=timestamp, plant_id=plant_id, ac_power=global_power)
        return global_prediction, predictions

    def predict_panel(self, plant_id: str, panel_id: str, start_time: datetime = None, end_time: datetime = None):

        model, metric, adwin = self.models.get(plant_id)

        if model is None:
            raise ValueError("No model available for this plant")
        
        packets = load_future_weather_data(
            data_directory=self.data_directory,
            plant_id=plant_id,
            start_time=end_time
        )

        packets = [p for p in packets if p[2] == panel_id]


        if start_time is None:
            start_time = datetime.min
        if end_time is None :
            end_time = datetime.max

        packets = [p for p in packets if start_time <= p[1] <= end_time]
        

        predictions_list = []
        for weather_info, timestamp, _ in packets:
            x = preprocess_realtime_2(weather_info, timestamp)
            y_pred = model.predict_one(x)
            predictions_list.append({
                "timestamp": timestamp.isoformat(),
                "plant_id": plant_id,
                "panel_id": panel_id,
                "ac_power": y_pred
            })

        return predictions_list
    

    
    def predict_plant(self, plant_id: str, start_time: datetime = None, end_time: datetime = None):

        model, metric, adwin = self.models.get(plant_id)

        if model is None:
            raise ValueError("No model available for this plant")
        
        packets = load_future_weather_data(
            data_directory=self.data_directory,
            plant_id=plant_id,
            start_time=end_time
        )

        if start_time is not None or end_time is not None:
            if start_time is None:
                start_time = datetime.min
            if end_time is None:
                end_time = datetime.max

            packets = [p for p in packets if start_time <= p[2] <= end_time]
        

        aggregated = defaultdict(float)  

        for weather_info, timestamp, panel_id in packets:
            x = preprocess_realtime_2(weather_info, timestamp)
            y_pred = model.predict_one(x)
            aggregated[timestamp] += y_pred  


        predictions_list = [
            {
                "timestamp": ts.isoformat(),
                "plant_id": plant_id,
                "ac_power": ac_power
            }
            for ts, ac_power in sorted(aggregated.items())
        ]
        

        return predictions_list
    
    def get_past_global_plant_predictions(self, plant_id: str, start_time: datetime = None, end_time: datetime = None):
        return self.prediction_dao.get_global_predictions_by_plant_id_and_time_range(plant_id, start_time, end_time)
    
    def get_past_panel_predictions(self, plant_id: str, panel_id: str ,start_time: datetime = None, end_time: datetime = None):
        return self.prediction_dao.get_panel_predictions_by_panel_id_and_time_range(plant_id, panel_id, start_time, end_time)
    
    def get_drifts_by_plant_id_panel_id_and_time_range(self, plant_id: str, panel_id: str ,start_time: datetime = None, end_time: datetime = None):
        predictions = self.prediction_dao.get_panel_predictions_by_panel_id_and_time_range(plant_id, panel_id, start_time, end_time)
        number_of_drifts = sum(1 for p in predictions if p.drift)
        return number_of_drifts
    
    def get_drifts_by_plant_id_and_time_range(self, plant_id: str, start_time: datetime = None, end_time: datetime = None):
        drifts = {}
        for panel in self.panels_dao.get_all_by_plant_id(plant_id):
            drift = self.get_drifts_by_plant_id_panel_id_and_time_range(plant_id, panel.id, start_time, end_time)
            drifts[panel.id] = drift
        return drifts
    
    def generate_report(self, plant_id: str, day: datetime):
        
        end = datetime.combine(day.date(), time.max)
        start = datetime.combine(day.date(), time.min)
 
        prediction_list = self.prediction_dao.get_panel_predictions_by_plant_id_and_time_range(plant_id, start_time=start, end_time=end)

        if not prediction_list:
            return 0.0, {}, 0, {}
        
        df = pd.DataFrame([vars(p) for p in prediction_list])

        total_drifts = int(df['drift'].sum())

        df['abs_error'] = (df['real_ac_power'] - df['predicted_ac_power']).abs()

        total_actual = df['real_ac_power'].sum()
        total_error = df['abs_error'].sum()

        total_kpi = (total_error / total_actual * 100) if total_actual != 0 else 0.0

        grouped = df.groupby('panel_id').agg({'abs_error': 'sum','real_ac_power': 'sum', 'drift': 'sum'})

        grouped['kpi'] = np.where(
            grouped['real_ac_power'] != 0,
            (grouped['abs_error'] / grouped['real_ac_power']) * 100,
            0.0
        )

        panels_kpis = grouped['kpi'].to_dict()
        panels_drifts = grouped['drift'].astype(int).to_dict()
    
        return total_kpi, panels_kpis, total_drifts, panels_drifts
    
    def get_LSTM_predictions_by_plant_id_and_panel_id(self, plant_id, panel_id):
        return self.LSTM_prediction_dao.get_all_panel_predictions_by_plant_id(plant_id, panel_id)
        