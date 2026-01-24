import csv
from datetime import datetime, timedelta
from typing import List
from pathlib import Path
from collections import defaultdict
from backend.models.prediction import PanelPrediction, GlobalPrediction


class PredictionDao:
    def __init__(self, data_directory: str):
        self.data_directory = Path(data_directory)


    def _parse_row(self, plant_id: str, row: dict, panel_id: str = None) -> PanelPrediction:

        try:
            if panel_id is not None and row.get("SOURCE_KEY") != panel_id:
                return None  

            return PanelPrediction(
                timestamp=datetime.strptime(row["DATE_TIME"], "%Y-%m-%d %H:%M:%S"),
                plant_id=plant_id,
                panel_id=row["SOURCE_KEY"],
                ac_power=float(row["AC_POWER"]),
            )
        except (KeyError, ValueError, TypeError):
            return None


    def get_all_panel_prediction_by_panel_id(self, plant_id: str, panel_id: str) -> List[PanelPrediction]:
        
        prediction = []

        csv_file = self.data_directory / f"{plant_id}.csv"
        if not csv_file.exists():
            return []

        with open(csv_file, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                p = self._parse_row(plant_id, row, panel_id=panel_id)
                if p is not None:
                    prediction.append(p)
        return prediction
    

    def get_panel_prediction_by_panel_id_and_time_range(
        self, plant_id: str, panel_id: str, end_time: datetime, hours: int
    ) -> List[PanelPrediction]:
        
        prediction = []

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
                    prediction.append(m)

        return prediction


    def get_all_panel_prediction_by_plant_id(self, plant_id: str) -> List[PanelPrediction]:
        
        prediction = []

        csv_file = self.data_directory / f"{plant_id}.csv"
        if not csv_file.exists():
            return []
        
        with open(csv_file, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                m = self._parse_row(plant_id, row)
                if m is not None:
                    prediction.append(m)
        return prediction


    def get_panel_prediction_by_plant_id_and_time_range(
        self, plant_id: str, end_time: datetime, hours: int
    ) -> List[PanelPrediction]:
        
        prediction = []

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
                    prediction.append(m)

        return prediction
    

    def get_all_panel_prediction(self) -> List[PanelPrediction]:
        
        prediction = []

        for csv in self.data_directory.iterdir():
            plant_id = csv.stem
            plant_prediction = self.get_all_panel_prediction_by_plant_id(plant_id)
            prediction.extend(plant_prediction)

        return prediction



    def get_all_global_prediction_by_plant_id(self, plant_id: str) -> List[GlobalPrediction]:
        
        panel_prediction = self.get_all_panel_prediction_by_plant_id(plant_id)

        agg: dict[datetime, float] = defaultdict(float)
        for m in panel_prediction:
            agg[m.timestamp] += m.ac_power
    
        global_prediction = [
            GlobalPrediction(timestamp=ts, plant_id=plant_id, ac_power=power)
            for ts, power in sorted(agg.items())
        ]
    
        return global_prediction


    def get_global_prediction_by_plant_id_and_time_range(
        self, plant_id: str, end_time: datetime, hours: int
    ) -> List[GlobalPrediction]:
        
        all_prediction = self.get_all_global_prediction_by_plant_id(plant_id)
        
        prediction = []

        if hours != None:
            start_time = end_time - timedelta(hours=hours)
        else:
            start_time = datetime.min

        for m in all_prediction:
            if m is not None and start_time <= m.timestamp <= end_time:
                prediction.append(m)

        return prediction
    

    def save_prediction(self, prediction: PanelPrediction):

        data_dir = Path(self.data_directory)
        data_dir.mkdir(parents=True, exist_ok=True)

        path = data_dir / f"{prediction.plant_id}.csv"

        timestamp = prediction.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        plant_id = prediction.plant_id
        panel_id = prediction.panel_id

        if path.exists():
            with path.open(mode="r", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if (
                        row["TIMESTAMP"] == timestamp
                        and row["PLANT_ID"] == plant_id
                        and row["PANEL_ID"] == panel_id
                    ):
                        return

        write_header = not path.exists()

        with path.open(mode="a", newline="") as f:
            writer = csv.writer(f)

            if write_header:
                writer.writerow([
                    "TIMESTAMP",
                    "PLANT_ID",
                    "PANEL_ID",
                    "AC_POWER",
                ])

            writer.writerow([
                timestamp,
                prediction.plant_id,
                prediction.panel_id,
                prediction.ac_power,
            ])



## this works if you use it as a module with python -m backend.dao.measurments_dao
#
#plant_id = "solar_1"
#panel_id = "pkci93gMrogZuBj" #this is a panel in solar_1
#
#dao = predictionDAO(data_directory="cleaned_data")
#prediction = dao.get_all_global_prediction_by_plant_id(plant_id)
#
#print("\n\rGlobel prediction:")
#for m in prediction[:5]: 
#    print(m)
#
#dt_str = "2020-05-15 15:00:00"
#dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
#print(dt)
#
#time_range_global_measurement = dao.get_global_prediction_by_plant_id_and_time_range(plant_id, dt, 1)
#time_range_panel_measurement = dao.get_panel_prediction_by_panel_id_and_time_range(plant_id, panel_id, dt, 1) 
#
#print(f"\n\r{len(time_range_global_measurement)} prediction for datetime:")
#for i in range(len(time_range_global_measurement)):
#    print(f"Iteration {i}")
#    print(time_range_global_measurement[i])
#    print(time_range_panel_measurement[i])
#
#all_prediction = dao.get_all_panel_prediction()
#for i in range(3):
#    print(all_prediction[i])
#    print(all_prediction[len(all_prediction) - i - 1])