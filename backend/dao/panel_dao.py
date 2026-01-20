from pathlib import Path
from typing import List
import csv
from backend.models.panel import Panel  

class PanelsDAO:
    def __init__(self, data_directory: str):
        self.data_directory = Path(data_directory)



    def _parse_row(self, plant_id: str, row: dict) -> Panel | None:
        try:
            return Panel(
                id=row["SOURCE_KEY"],
                plant_id=plant_id
            )
        except KeyError:
            return None



    def get_all_by_plant_id(self, plant_id: str) -> List[Panel]:
        panels: List[Panel] = []

        csv_file = self.data_directory / f"{plant_id}.csv"
        if not csv_file.exists():
            return []

        seen_panel_ids = set()

        with open(csv_file, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                panel = self._parse_row(plant_id, row)
                if panel is not None and panel.id not in seen_panel_ids:
                    panels.append(panel)
                    seen_panel_ids.add(panel.id)

        return panels



## testing 
#dao = PanelsDAO(data_directory="cleaned_data")
#panels = dao.get_all_by_plant_id("solar_2")
#print(panels)
#print("idiota")
#
#print("Plants:")
#for p in plant[:50]: 
#    print(p)