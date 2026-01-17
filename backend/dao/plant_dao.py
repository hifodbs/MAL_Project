from typing import List
from backend.models.plant import Plant
from pathlib import Path



class PlantsDAO:
    # specify the directory where csv files are sotred to use this class
    def __init__(self, data_directory: str):
        self.data_directory = Path(data_directory)



    def _name_refactor(self, string: str):
        name = ""
        parts = string.split("_")
        for word in parts:
            name += word[0].upper() + word[1:] + " "
        return name



    def get_all(self) -> List[Plant]:
        plants: List[Plant] = []

        for csv_file in self.data_directory.glob("*.csv"):
            plant_name = self._name_refactor(csv_file.stem)
            plant = Plant(
                name=plant_name,
                id=str(csv_file.stem)
            )
            plants.append(plant)

        return plants
    


# testing

dao = PlantsDAO(data_directory="cleaned_data")
plant = dao.get_all()

print("Plants:")
for p in plant[:5]: 
    print(p)