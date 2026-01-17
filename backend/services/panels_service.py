
from backend.dao.panel_dao import PanelsDAO
from backend.dao.measurements_dao import MeasurementsDAO
from datetime import datetime, timedelta


class PanelsService:
    def __init__(self, data_directory="cleaned_data"):
        self.panel_dao = PanelsDAO(data_directory=data_directory)
        self.measurements_dao = MeasurementsDAO(data_directory=data_directory)


    def get_all_panel_measurements_by_id(self, plant_id: str, panel_id: str):
        return self.measurements_dao.get_all_panel_measurements_by_panel_id(plant_id=plant_id, panel_id=panel_id)


    def get_all_panel_measurement_by_id_and_time_reange(self, plant_id: str, panel_id: str, start_time: datetime, hours: int):
        return self.measurements_dao.get_panel_measurements_by_panel_id_and_time_range(plant_id=plant_id, panel_id=panel_id, start_time=start_time, hours=hours)


    def get_all_by_plant_id(self, plant_id: str):
        return self.panel_dao.get_all_by_plant_id(plant_id=plant_id)