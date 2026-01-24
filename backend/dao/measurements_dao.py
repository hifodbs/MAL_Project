import csv
from datetime import datetime, timedelta
from typing import List
from pathlib import Path
from collections import defaultdict
from backend.models.measurement import PanelMeasurement, GlobalMeasurement


class MeasurementsDAO:
    def __init__(self, data_directory: str):
        self.data_directory = Path(data_directory)


    def _parse_row(self, plant_id: str, row: dict, panel_id: str = None) -> PanelMeasurement:

        try:
            if panel_id is not None and row.get("SOURCE_KEY") != panel_id:
                return None  

            return PanelMeasurement(
                timestamp=datetime.strptime(row["DATE_TIME"], "%Y-%m-%d %H:%M:%S"),
                plant_id=plant_id,
                panel_id=row["SOURCE_KEY"],
                ac_power=float(row["AC_POWER"]),
            )
        except (KeyError, ValueError, TypeError):
            return None


    def get_all_panel_measurements_by_panel_id(self, plant_id: str, panel_id: str) -> List[PanelMeasurement]:
        
        measurements = []

        csv_file = self.data_directory / f"{plant_id}.csv"
        if not csv_file.exists():
            return []

        with open(csv_file, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                m = self._parse_row(plant_id, row, panel_id=panel_id)
                if m is not None:
                    measurements.append(m)
        return measurements
    

    def get_panel_measurements_by_panel_id_and_time_range(
        self, plant_id: str, panel_id: str, end_time: datetime, hours: int
    ) -> List[PanelMeasurement]:
        
        measurements = []

        csv_file = self.data_directory / f"{plant_id}.csv"
        if not csv_file.exists():
            return []

        if hours != None:
            start_time = end_time - timedelta(hours=hours)
        else:
            start_time = datetime.min

        with open(csv_file, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                m = self._parse_row(plant_id, row, panel_id)
                if m is not None and start_time <= m.timestamp <= end_time:
                    measurements.append(m)

        return measurements


    def get_all_panel_measurements_by_plant_id(self, plant_id: str) -> List[PanelMeasurement]:
        
        measurements = []

        csv_file = self.data_directory / f"{plant_id}.csv"
        if not csv_file.exists():
            return []
        
        with open(csv_file, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                m = self._parse_row(plant_id, row)
                if m is not None:
                    measurements.append(m)
        return measurements


    def get_panel_measurements_by_plant_id_and_time_range(
        self, plant_id: str, end_time: datetime, hours: int
    ) -> List[PanelMeasurement]:
        
        measurements = []

        csv_file = self.data_directory / f"{plant_id}.csv"
        if not csv_file.exists():
            return []
        
        if hours != None:
            start_time = end_time - timedelta(hours=hours)
        else:
            start_time = datetime.min

        with open(csv_file, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                m = self._parse_row(plant_id, row)
                if m is not None and start_time <= m.timestamp <= end_time:
                    measurements.append(m)

        return measurements
    

    def get_all_panel_measurements(self) -> List[PanelMeasurement]:
        
        measurements = []

        for csv in self.data_directory.iterdir():
            plant_id = csv.stem
            plant_measurements = self.get_all_panel_measurements_by_plant_id(plant_id)
            measurements.extend(plant_measurements)

        return measurements



    def get_all_global_measurements_by_plant_id(self, plant_id: str) -> List[GlobalMeasurement]:
        
        panel_measurements = self.get_all_panel_measurements_by_plant_id(plant_id)

        agg: dict[datetime, float] = defaultdict(float)
        for m in panel_measurements:
            agg[m.timestamp] += m.ac_power
    
        global_measurements = [
            GlobalMeasurement(timestamp=ts, plant_id=plant_id, ac_power=power)
            for ts, power in sorted(agg.items())
        ]
    
        return global_measurements


    def get_global_measurements_by_plant_id_and_time_range(
        self, plant_id: str, end_time: datetime, hours: int
    ) -> List[GlobalMeasurement]:
        
        all_measurements = self.get_all_global_measurements_by_plant_id(plant_id)
        
        measurements = []

        if hours != None:
            start_time = end_time - timedelta(hours=hours)
        else:
            start_time = datetime.min

        for m in all_measurements:
            if m is not None and start_time <= m.timestamp <= end_time:
                measurements.append(m)

        return measurements
    




## this works if you use it as a module with python -m backend.dao.measurments_dao
#
#plant_id = "solar_1"
#panel_id = "pkci93gMrogZuBj" #this is a panel in solar_1
#
#dao = MeasurementsDAO(data_directory="cleaned_data")
#measurements = dao.get_all_global_measurements_by_plant_id(plant_id)
#
#print("\n\rGlobel measurements:")
#for m in measurements[:5]: 
#    print(m)
#
#dt_str = "2020-05-15 15:00:00"
#dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
#print(dt)
#
#time_range_global_measurement = dao.get_global_measurements_by_plant_id_and_time_range(plant_id, dt, 1)
#time_range_panel_measurement = dao.get_panel_measurements_by_panel_id_and_time_range(plant_id, panel_id, dt, 1) 
#
#print(f"\n\r{len(time_range_global_measurement)} measurements for datetime:")
#for i in range(len(time_range_global_measurement)):
#    print(f"Iteration {i}")
#    print(time_range_global_measurement[i])
#    print(time_range_panel_measurement[i])
#
#all_measurements = dao.get_all_panel_measurements()
#for i in range(3):
#    print(all_measurements[i])
#    print(all_measurements[len(all_measurements) - i - 1])