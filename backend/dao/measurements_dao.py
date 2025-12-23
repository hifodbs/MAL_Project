import csv
from datetime import datetime
from typing import List
from backend.models.measurement import Measurement


class MeasurementsDAO:
    def __init__(self, plant_id: str, csv_file: str):
        self.plant_id = plant_id
        self.csv_file = csv_file

    def get_all(self) -> List[Measurement]:
        measurements = []
        with open(self.csv_file, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                m = Measurement(
                    timestamp=datetime.strptime(row["DATE_TIME"], "%Y-%m-%d %H:%M:%S"),
                    plant_id=self.plant_id,
                    panel_id=row["SOURCE_KEY"],
                    ac_power=float(row["AC_POWER"])
                )
                measurements.append(m)
        return measurements



# this works only if you properly fix paths...

#dao = MeasurementsDAO(plant_id="solar_1", csv_file="cleaned_data/solar_1.csv")
#measurements = dao.get_all()

#print("Measurements:")
#for m in measurements[:5]: 
#    print(m)

