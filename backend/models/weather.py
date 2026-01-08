from dataclasses import dataclass
from datetime import datetime

@dataclass
class Weather:
    timestamp: datetime
    plant_id: str
    ambient_temperature: float
    module_temperature: float
    irradiation: float