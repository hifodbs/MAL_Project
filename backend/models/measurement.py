from dataclasses import dataclass
from datetime import datetime

@dataclass
class PanelMeasurement:
    timestamp: datetime
    plant_id: str
    panel_id: str
    ac_power: float


@dataclass
class GlobalMeasurment:
    timestamp: datetime
    plant_id: str
    ac_power: float