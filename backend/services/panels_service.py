sample_panels = [
    {
        "id": "panel_1",
        "id_plant": "plant_1",
        "status": "Performing"
    },
    {
        "id": "panel_2",
        "id_plant": "plant_1",
        "status": "Performing"
    },
    {
        "id": "panel_3",
        "id_plant": "plant_1",
        "status": "Underperforming"
    },
    {
        "id": "panel_4",
        "id_plant": "plant_1",
        "status": "Broken"
    },
    {
        "id": "panel_5",
        "id_plant": "plant_1",
        "status": "Performing"
    },
    {
        "id": "panel_2",
        "id_plant": "plant_2",
        "status": "Underperforming"
    },
    {
        "id": "panel_2",
        "id_plant": "plant_2",
        "status": "Underperforming"
    },
    {
        "id": "panel_3",
        "id_plant": "plant_2",
        "status": "Broken"
    },
    {
        "id": "panel_4",
        "id_plant": "plant_2",
        "status": "Underperforming"
    },
    {
        "id": "panel_5",
        "id_plant": "plant_2",
        "status": "Performing"
    }
]

sample_measurements = {
    "panel_1": [
        {"timestamp": "2025-12-21T10:00:00Z", "power": 534},
        {"timestamp": "2025-12-21T11:00:00Z", "power": 512},
        {"timestamp": "2025-12-21T12:00:00Z", "power": 564}
    ],
    "panel_2": [
        {"timestamp": "2025-12-21T10:00:00Z", "power": 321},
        {"timestamp": "2025-12-21T11:00:00Z", "power": 342},
        {"timestamp": "2025-12-21T12:00:00Z", "power": 291}
    ]
}


sample_predictions = {
    "panel_1": [
        {"timestamp": "2025-12-21T10:00:00Z", "power": 500},
        {"timestamp": "2025-12-21T11:00:00Z", "power": 520},
        {"timestamp": "2025-12-21T12:00:00Z", "power": 510},
        {"timestamp": "2025-12-21T13:00:00Z", "power": 530},
        {"timestamp": "2025-12-21T14:00:00Z", "power": 540},
        {"timestamp": "2025-12-21T15:00:00Z", "power": 525}
    ],
    "panel_2": [
        {"timestamp": "2025-12-21T10:00:00Z", "power": 300},
        {"timestamp": "2025-12-21T11:00:00Z", "power": 320},
        {"timestamp": "2025-12-21T12:00:00Z", "power": 310},
        {"timestamp": "2025-12-21T13:00:00Z", "power": 290},
        {"timestamp": "2025-12-21T14:00:00Z", "power": 270},
        {"timestamp": "2025-12-21T15:00:00Z", "power": 265}
    ]
}

def get_panels(plant_id):
    """
    Fetch the list of panels for a given plant_id.
    Returns None if panels for the given plant_id do not exist.
    """
    return sample_panels.get(plant_id)

def get_panel_measurements(panel_id):
    """
    """
    return sample_predictions.get(panel_id)

def get_panel_predictions(panel_id):

    return sample_measurements.get(panel_id)