import csv
from datetime import datetime, timedelta
from typing import List
from pathlib import Path
from collections import defaultdict
from backend.models.prediction import PanelPrediction, GlobalPrediction, HistoricalPrediction


class PredictionDao:
    def __init__(self, data_directory: str = "historical_predictions"):
        self.data_directory = Path(data_directory)
        self._index = {}


    def _load_index(self, path: Path):
        if path in self._index:
            return

        seen = set()

        if path.exists():
            with path.open("r", newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    seen.add((
                        row["DATE_TIME"],
                        row["PLANT_ID"],
                        row["PANEL_ID"],
                    ))

        self._index[path] = seen


    def _parse_row(self, plant_id: str, row: dict, panel_id: str = None) -> PanelPrediction:

        try:
            if panel_id is not None and row.get("SOURCE_KEY") != panel_id:
                return None  

            return PanelPrediction(
                timestamp=datetime.strptime(row["DATE_TIME"], "%Y-%m-%d %H:%M:%S"),
                plant_id=plant_id,
                panel_id=row["SOURCE_KEY"],
                ac_power=float(row["PREDICTED_AC_POWER"]),
            )
        except (KeyError, ValueError, TypeError):
            return None


    def get_all_panel_predictions_by_panel_id(self, plant_id: str, panel_id: str) -> List[PanelPrediction]:
        
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
    

    def get_panel_predictions_by_panel_id_and_time_range(
        self, plant_id: str, panel_id: str, start_time: datetime = None, end_time: datetime = None
    ) -> List[PanelPrediction]:
        
        prediction = []

        csv_file = self.data_directory / f"{plant_id}.csv"
        if not csv_file.exists():
            return []

        if end_time is None and start_time is None:
            return self.get_all_panel_predictions_by_panel_id(panel_id=panel_id)

        if end_time is None:
            end_time = start_time.max
        
        if start_time is None:
            start_time = datetime.min

        with open(csv_file, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                m = self._parse_row(plant_id, row, panel_id)
                if m is not None and start_time <= m.timestamp <= end_time:
                    prediction.append(m)

        return prediction


    def get_all_panel_predictions_by_plant_id(self, plant_id: str) -> List[PanelPrediction]:
        
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


    def get_panel_predictions_by_plant_id_and_time_range(
        self, plant_id: str, start_time: datetime = None, end_time: datetime = None
    ) -> List[PanelPrediction]:
        
        prediction = []

        csv_file = self.data_directory / f"{plant_id}.csv"
        if not csv_file.exists():
            return []

        if end_time is None:
            end_time = datetime.max
        if start_time is None:
            start_time = datetime.min

        with open(csv_file, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                m = self._parse_row(plant_id, row)
                if m is not None and start_time <= m.timestamp <= end_time:
                    prediction.append(m)

        return prediction
    

    def get_all_panel_predictions(self) -> List[PanelPrediction]:
        
        prediction = []

        for csv in self.data_directory.iterdir():
            plant_id = csv.stem
            plant_prediction = self.get_all_panel_predictions_by_plant_id(plant_id)
            prediction.extend(plant_prediction)

        return prediction



    def get_all_global_predictions_by_plant_id(self, plant_id: str) -> List[GlobalPrediction]:
        
        panel_prediction = self.get_all_panel_predictions_by_plant_id(plant_id)

        agg: dict[datetime, float] = defaultdict(float)
        for m in panel_prediction:
            agg[m.timestamp] += m.ac_power
    
        global_prediction = [
            GlobalPrediction(timestamp=ts, plant_id=plant_id, ac_power=power)
            for ts, power in sorted(agg.items())
        ]
    
        return global_prediction


    def get_global_predictions_by_plant_id_and_time_range(
        self, plant_id: str, start_time: datetime = None, end_time: datetime = None
    ) -> List[GlobalPrediction]:
        
        all_prediction = self.get_all_global_predictions_by_plant_id(plant_id)

        if end_time is None and start_time is None:
            return all_prediction

        prediction = []

        if end_time is None:
            end_time = datetime.max
        if start_time is None:
            start_time = datetime.min

        for m in all_prediction:
            if m is not None and start_time <= m.timestamp <= end_time:
                prediction.append(m)

        return prediction
    

    def save_prediction(self, prediction: HistoricalPrediction):
        data_dir = Path(self.data_directory)
        data_dir.mkdir(parents=True, exist_ok=True)

        path = data_dir / f"{prediction.plant_id}.csv"

        self._load_index(path)

        timestamp = prediction.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        plant_id = str(prediction.plant_id)
        panel_id = str(prediction.panel_id)

        key = (timestamp, plant_id, panel_id)

        if key in self._index[path]:
            return

        write_header = not path.exists()

        with path.open("a", newline="") as f:
            writer = csv.writer(f)

            if write_header:
                writer.writerow([
                    "DATE_TIME",
                    "PLANT_ID",
                    "PANEL_ID",
                    "PREDICTED_AC_POWER",
                    "REAL_AC_POWER",
                    "DRIFT"
                ])

            writer.writerow([
                timestamp,
                plant_id,
                panel_id,
                prediction.predicted_ac_power,
                prediction.real_ac_power,
                prediction.drift
            ])

        self._index[path].add(key)


## this works if you use it as a module with python -m backend.dao.measurments_dao
#
#plant_id = "solar_1"
#panel_id = "pkci93gMrogZuBj" #this is a panel in solar_1
#
#dao = PredictionDao(data_directory="historical_predictions")
#prediction = dao.get_all_global_predictions_by_plant_id(plant_id)
#
#print("\n\rGlobel prediction:")
#for m in prediction[:5]: 
#    print(m)
#
#dt_str = "2020-05-15 15:00:00"
#dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
#print(dt)
#
#time_range_global_measurement = dao.get_global_predictions_by_plant_id_and_time_range(plant_id, end_time=dt)
#time_range_panel_measurement = dao.get_panel_predictions_by_plant_id_and_time_range(plant_id, end_time=dt) 
#
#print(f"\n\r{len(time_range_global_measurement)} prediction for datetime:")
#for i in range(len(time_range_global_measurement)):
#    print(f"Iteration {i}")
#    print(time_range_global_measurement[i])
#    print(time_range_panel_measurement[i])