from dataclasses import dataclass
from datetime import datetime

@dataclass
class Measurement:
    timestamp: datetime
    plant_id: str
    panel_id: str
    ac_power: float