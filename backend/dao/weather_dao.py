import csv
from datetime import datetime, timedelta
from typing import List
from pathlib import Path
from collections import defaultdict
from backend.models.weather import Weather

class WeatheDAO:
    def __init__(self, data_directory: str):
        self.data_directory = Path(data_directory)


    def _parse_row(self, plant_id: str, row: dict) -> Weather:

        try:
            return Weather(
                timestamp=datetime.strptime(row["DATE_TIME"], "%Y-%m-%d %H:%M:%S"),
                plant_id=plant_id,
                ambient_temperature=float(row["AMBIENT_TEMPERATURE"]),
                module_temperature=float(row["MODULE_TEMPERATURE"]),
                irradiation=float(row["IRRADIATION"])
            )
        except (KeyError, ValueError, TypeError):
            return None
    

    def get_all_weather_measurements_by_plant_id(
        self, plant_id: str
    )-> List[Weather]:

        weather_measurements = []

        csv_file = self.data_directory / f"{plant_id}.csv"

        if not csv_file.exists():
            return []

        seen_timestamps = set()

        with open(csv_file, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                wm = self._parse_row(plant_id, row)
                if wm is not None and wm.timestamp not in seen_timestamps:
                    weather_measurements.append(wm)
                    seen_timestamps.add(wm.timestamp)
        return weather_measurements
    

    def get_weather_measurements_by_plant_id_and_time_range(
            self, plant_id: str, end_time: datetime, hours: int
    ) -> List[Weather]:
        
        measurements = []
        
        csv_file = self.data_directory / f"{plant_id}.csv"

        if not csv_file.exists():
            return []
        
        seen_timestamps = set()
        if hours is not None:
            start_time = end_time - timedelta(hours=hours)
        else: 
            start_time = datetime.min

        with open(csv_file, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                m = self._parse_row(plant_id, row)
                if m is not None and start_time <= m.timestamp <= end_time and m.timestamp not in seen_timestamps:
                    measurements.append(m)
                    seen_timestamps.add(m.timestamp)

        return measurements
    

    def get_weather_measurements_time_range(
            self, end_time: datetime, hours: int = 24
    ) -> List[Weather]:
        weather_measurements = []

        for csv in self.data_directory.iterdir():
            plant_id = csv.stem
            plant_weather_measurements = self.get_weather_measurements_by_plant_id_and_time_range(plant_id, end_time, hours)
            weather_measurements.extend(plant_weather_measurements)

        return weather_measurements

    def get_all_weather_measurements(self) -> List[Weather]:

        weather_measurements = []

        for csv in self.data_directory.iterdir():
            plant_id = csv.stem
            plant_weather_measurements = self.get_all_weather_measurements_by_plant_id(plant_id)
            weather_measurements.extend(plant_weather_measurements)

        return weather_measurements

#data_directory = "cleaned_data"
#plant_id = "solar_1"  
#
#
#waether_dao = WeatheDAO(data_directory)
#
#all_measurements = waether_dao.get_all_weather_measurements()
#for i in range(3):
#    print(all_measurements[i])
#    print(all_measurements[len(all_measurements) - i - 1])

