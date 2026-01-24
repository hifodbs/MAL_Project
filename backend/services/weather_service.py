from backend.dao.weather_dao import WeatheDAO
from backend.dao.measurements_dao import MeasurementsDAO
from datetime import datetime, timedelta


class WeatherService:
    def __init__(self, data_directory="cleaned_data"):
        self.weather_dao = WeatheDAO(data_directory=data_directory)


    def get_all(self):
        return self.weather_dao.get_all_weather_measurements()


    def get_all_by_plant_id(self, plant_id: str):
        return self.weather_dao.get_all_weather_measurements_by_plant_id(plant_id=plant_id)