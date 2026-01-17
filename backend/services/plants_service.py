# services/prediction_service.py
from backend.dao.plant_dao import PlantsDAO
from backend.dao.measurements_dao import MeasurementsDAO
from datetime import datetime, timedelta


class PlantsService:
    def __init__(self, data_directory="cleaned_data"):
        self.plants_dao = PlantsDAO(data_directory=data_directory)
        self.measurements_dao = MeasurementsDAO(data_directory=data_directory)

    def get_plants(self):
        return self.plants_dao.get_all()

    def get_global_measurements_by_plant_id(self, plant_id: str):
        return self.measurements_dao.get_all_global_measurements_by_plant_id(plant_id=plant_id)
    
    def get_global_measurements_by_plant_id_and_time_range(self, plant_id: str, start_time: datetime, hours: int):
        return self.measurements_dao.get_global_measurements_by_plant_id_and_time_range(plant_id=plant_id, start_time=start_time, hours=hours)