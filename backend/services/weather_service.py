from datetime import datetime, timedelta




sample_measurements = {
    "plant_1": [
        {"timestamp": "2025-12-21T10:00:00Z", "temperature": 22, "irradiation": 0.45},
        {"timestamp": "2025-12-21T11:00:00Z", "temperature": 23, "irradiation": 0.40},
        {"timestamp": "2025-12-21T12:00:00Z", "temperature": 24, "irradiation": 0.45}
    ],
    "plant_2": [
        {"timestamp": "2025-12-21T10:00:00Z", "temperature": 19, "irradiation": 0.30},
        {"timestamp": "2025-12-21T11:00:00Z", "temperature": 20, "irradiation": 0.30},
        {"timestamp": "2025-12-21T12:00:00Z", "temperature": 18, "irradiation": 0.25}
    ]
}


sample_predictions = {
    "plant_1": [
        {"timestamp": "2025-12-21T10:00:00Z", "temperature": 20, "irradiation": 0.25},
        {"timestamp": "2025-12-21T11:00:00Z", "temperature": 20, "irradiation": 0.35},
        {"timestamp": "2025-12-21T12:00:00Z", "temperature": 20, "irradiation": 0.25},
        {"timestamp": "2025-12-21T13:00:00Z", "temperature": 20, "irradiation": 0.25},
        {"timestamp": "2025-12-21T14:00:00Z", "temperature": 20, "irradiation": 0.35},
        {"timestamp": "2025-12-21T15:00:00Z", "temperature": 20, "irradiation": 0.25}
    ],
    "plant_2": [
        {"timestamp": "2025-12-21T10:00:00Z", "temperature": 20, "irradiation": 0.25},
        {"timestamp": "2025-12-21T11:00:00Z", "temperature": 20, "irradiation": 0.25},
        {"timestamp": "2025-12-21T12:00:00Z", "temperature": 20, "irradiation": 0.25},
        {"timestamp": "2025-12-21T13:00:00Z", "temperature": 20, "irradiation": 0.20},
        {"timestamp": "2025-12-21T14:00:00Z", "temperature": 20, "irradiation": 0.20},
        {"timestamp": "2025-12-21T15:00:00Z", "temperature": 20, "irradiation": 0.20}
    ]
}


def get_weather(plant_id):
    return


def get_weather_predictions(plant_id):
    """
    Fetch the list of predictions for a given plant_id.
    Returns None if the plant_id does not exist.
    """
    return sample_predictions.get(plant_id)


def get_weather_measurements(plant_id):
    """
    Fetch the list of measurments for a given plant_id.
    Returns None if the plant_id does not exist.
    """
    return sample_measurements.get(plant_id)