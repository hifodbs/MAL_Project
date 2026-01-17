# services/prediction_service.py
from backend.dao.plant_dao import PlantsDAO
from datetime import datetime, timedelta

sample_plants = [
    {
        "id": "plant_1",
        "name": "Solar Plant Alpha",
    },
    {
        "id": "plant_2",
        "name": "Solar Plant Beta",
    },
    {
        "id": "plant_3",
        "name": "Solar Plant Charlie",
    },
    {
        "id": "plant_4",
        "name": "Solar Plant Delta",
    }
]


sample_measurements = {
    "plant_1": [
        {"timestamp": "2025-12-21T10:00:00Z", "power": 534},
        {"timestamp": "2025-12-21T11:00:00Z", "power": 512},
        {"timestamp": "2025-12-21T12:00:00Z", "power": 564}
    ],
    "plant_2": [
        {"timestamp": "2025-12-21T10:00:00Z", "power": 321},
        {"timestamp": "2025-12-21T11:00:00Z", "power": 342},
        {"timestamp": "2025-12-21T12:00:00Z", "power": 291}
    ]
}


sample_predictions = {
    "plant_1": [
        {"timestamp": "2025-12-21T10:00:00Z", "power": 500},
        {"timestamp": "2025-12-21T11:00:00Z", "power": 520},
        {"timestamp": "2025-12-21T12:00:00Z", "power": 510},
        {"timestamp": "2025-12-21T13:00:00Z", "power": 530},
        {"timestamp": "2025-12-21T14:00:00Z", "power": 540},
        {"timestamp": "2025-12-21T15:00:00Z", "power": 525}
    ],
    "plant_2": [
        {"timestamp": "2025-12-21T10:00:00Z", "power": 300},
        {"timestamp": "2025-12-21T11:00:00Z", "power": 320},
        {"timestamp": "2025-12-21T12:00:00Z", "power": 310},
        {"timestamp": "2025-12-21T13:00:00Z", "power": 290},
        {"timestamp": "2025-12-21T14:00:00Z", "power": 270},
        {"timestamp": "2025-12-21T15:00:00Z", "power": 265}
    ]
}

def get_plants():
    """
    Fetch the list of plants.
    """

    dao = PlantsDAO(data_directory="cleaned_data")
    plants = dao.get_all()

    return plants

def get_predictions(plant_id):
    """
    Fetch the list of predictions for a given plant_id.
    Returns None if the plant_id does not exist.
    """
    return sample_predictions.get(plant_id)

def get_measurements(plant_id):
    """
    Fetch the list of past measures for a given plant_id.
    Returns None if the plant_id does not exist.
    """
    return sample_measurements.get(plant_id)