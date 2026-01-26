from datetime import datetime, timedelta
from collections import defaultdict

from backend.dao.plant_dao import PlantsDAO
from backend.dao.weather_dao import WeatherDAO
from backend.dao.prediction_dao import PredictionDao
from backend.dao.measurements_dao import MeasurementsDAO
from backend.models.prediction import HistoricalPrediction
from backend.utils.sensor_stream_simulator import load_future_weather_data
from backend.utils.model_script import preprocess_realtime_2, process_one_reading



class PredictionService:
    def __init__(self, models, data_directory="cleaned_data", historical_predictions: str = "historical_predictionss"):
        self.prediction_dao = PredictionDao(historical_predictions)
        self.weather_dao = WeatherDAO(data_directory)
        self.measure_dao = MeasurementsDAO(data_directory)
        self.models = models
        self.data_directory = data_directory


    def train_next_timestamp(self, plant_id: str, panel_id: str, timestamp: datetime):

        w = self.weather_dao.get_weather_by_plant_id_and_timestamp(panel_id, timestamp)
        features = preprocess_realtime_2((w.ambient_temperature, w.module_temperature, w.irradiation), timestamp)

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
    
