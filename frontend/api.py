import requests

BASE_URL = "http://127.0.0.1:5000"  # Flask backend

def get_plants():
    """
    Fetch plants from the Flask API.

    Returns:
        list: [
            {"id": "plant_id", "name": "plant_name"},
            ...
        ]
    """
    try: 
        response = requests.get(f"{BASE_URL}/plants")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching plants: {e}")
        return 
    
def get_predictions_by_plant_id(plant_id, time):
    """
    Fetch predictions for a specific plant from the Flask API.

    Args:
        plant_id (str): ID of the plant

    Returns:
        list: [
            {"timestamp": ISO8601 string, "ac_power": float},
            ...
        ]
    """
    try:
        params = {}
        if time is not None:
            params["time"] = time
        response = requests.get(f"{BASE_URL}/plants/{plant_id}/predictions")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching predictions for plant {plant_id}: {e}")
        return []
    
def get_measurements_by_plant_id(plant_id, time = None):
    """
    Fetch measurements for a specific plant from the Flask API.

    Args:
        plant_id (str): ID of the plant

    Returns:
        list: [
            {"timestamp": ISO8601 string, "ac_power": float},
            ...
        ]
    """
    try:
        params = {}
        if time is not None:
            params["time"] = time
        response = requests.get(f"{BASE_URL}/plants/{plant_id}/measurements")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching predictions for plant {plant_id}: {e}")
        return []

def get_panels_by_plant_id(plant_id):
    try:
        response = requests.get(f"{BASE_URL}/plants/{plant_id}/panels")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching panels for plant {plant_id}: {e}")
        return []

def get_meaurements_by_panel_id(plant_id, panel_id, time):
    try:
        params = {}
        if time is not None:
            params["time"] = time
        response = requests.get(f"{BASE_URL}/plants/{plant_id}/panels/{panel_id}/measurements")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching measurements for panel {panel_id}: {e}")
        return []
    
def get_predictions_by_panel_id(plant_id, panel_id, time=None):
    try:
        params = {}
        if time is not None:
            params["time"] = time
        response = requests.get(f"{BASE_URL}/plants/{plant_id}/panels/{panel_id}/predictions")
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching predictions for panel {panel_id}: {e}")
        return []

def get_new_prediction_by_panel_id(plant_id, panel_id, time=None):
    try:
        params = {}
        if time is not None:
            params["time"] = time 

        response = requests.get(
            f"{BASE_URL}/plants/{plant_id}/panels/{panel_id}/new_prediction",
            params=params
        )
        response.raise_for_status()
        return response.json()

    except requests.RequestException as e:
        print(f"Error fetching predictions for panel {panel_id}: {e}")
        return []
    
def get_new_prediction_by_plant_id(plant_id, time=None):
    try:
        params = {}
        if time is not None:
            params["time"] = time 

        response = requests.get(
            f"{BASE_URL}/plants/{plant_id}/new_prediction",
            params=params
        )
        response.raise_for_status()
        return response.json()

    except requests.RequestException as e:
        print(f"Error fetching predictions for panel {plant_id}: {e}")
        return []