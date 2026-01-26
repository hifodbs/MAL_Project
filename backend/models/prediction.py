from dataclasses import dataclass
from datetime import datetime

@dataclass
class PanelPrediction:
    timestamp: datetime
    plant_id: str
    panel_id: str
    ac_power: float


@dataclass
class GlobalPrediction:
    timestamp: datetime
    plant_id: str
    ac_power: float

@dataclass
class HistoricalPrediction:
    timestamp: datetime
    plant_id: str
    panel_id: str
    predicted_ac_power: float
    real_ac_power: float
    drift: bool