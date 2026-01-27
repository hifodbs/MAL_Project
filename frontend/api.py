import requests
import streamlit as st

BASE_URL = "http://127.0.0.1:5000"  # Flask backend

@st.cache_data(ttl=600)
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
        return []
    
@st.cache_data(ttl=600)
def get_predictions_by_plant_id(plant_id, start_time = None, end_time = None):
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
        if start_time is not None:
            params["start_time"] = start_time
        if end_time is not None:
            params["end_time"] = end_time

        response = requests.get(f"{BASE_URL}/plants/{plant_id}/predictions", params=params)
        response.raise_for_status()

        return response.json()
    
    except requests.RequestException as e:
        print(f"Error fetching predictions for plant {plant_id}: {e}")
        return []

@st.cache_data(ttl=600)
def get_measurements_by_plant_id(plant_id, start_time = None, end_time = None):
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
        if start_time is not None:
            params["start_time"] = start_time
        if end_time is not None:
            params["end_time"] = end_time

        response = requests.get(f"{BASE_URL}/plants/{plant_id}/measurements", params=params)
        response.raise_for_status()

        return response.json()
    
    except requests.RequestException as e:
        print(f"Error fetching predictions for plant {plant_id}: {e}")
        return []

@st.cache_data(ttl=600)
def get_panels_by_plant_id(plant_id):
    try:
        response = requests.get(f"{BASE_URL}/plants/{plant_id}/panels")
        response.raise_for_status()

        return response.json()
    
    except requests.RequestException as e:
        print(f"Error fetching panels for plant {plant_id}: {e}")
        return []

@st.cache_data(ttl=600)
def get_measurements_by_panel_id(plant_id, panel_id, start_time = None, end_time = None):
    try:
        params = {}
        if start_time is not None:
            params["start_time"] = start_time
        if end_time is not None:
            params["end_time"] = end_time

        response = requests.get(f"{BASE_URL}/plants/{plant_id}/panels/{panel_id}/measurements", params=params)
        response.raise_for_status()

        return response.json()
    
    except requests.RequestException as e:
        print(f"Error fetching measurements for panel {panel_id}: {e}")
        return []
    
@st.cache_data(ttl=600)
def get_predictions_by_panel_id(plant_id, panel_id, start_time = None, end_time= None):
    try:
        params = {}
        if start_time is not None:
            params["start_time"] = start_time
        if end_time is not None:
            params["end_time"] = end_time
        
        response = requests.get(f"{BASE_URL}/plants/{plant_id}/panels/{panel_id}/predictions", params=params)
        response.raise_for_status()

        return response.json()
    
    except requests.RequestException as e:
        print(f"Error fetching predictions for panel {panel_id}: {e}")
        return []

@st.cache_data(ttl=600)
def get_new_prediction_by_panel_id(plant_id, panel_id, time=None):
    try:
        params = {}
        if time is not None:
            params["time"] = time 

        response = requests.get(f"{BASE_URL}/plants/{plant_id}/panels/{panel_id}/new_prediction",params=params)
        response.raise_for_status()

        return response.json()

    except requests.RequestException as e:
        print(f"Error gettin prediction for panel {panel_id}: {e}")
        return []
    
@st.cache_data(ttl=600)
def get_new_prediction_by_plant_id(plant_id, time=None):
    try:
        params = {}
        if time is not None:
            params["time"] = time 

        response = requests.get(f"{BASE_URL}/plants/{plant_id}/new_prediction",params=params)
        response.raise_for_status()

        return response.json()

    except requests.RequestException as e:
        print(f"Error gatting prediction for panel {plant_id}: {e}")
        return []
    

@st.cache_data(ttl=600)
def get_report(plant_id, day=None):
    
    if day is None:
        return None
    try:
        params = {"day": day}
        response = requests.get(f"{BASE_URL}/plants/{plant_id}/report", params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching report for plant {plant_id}: {e}")
        return None
    

@st.cache_data(ttl=600)
def get_drift_summary_by_plant_id(plant_id, start_time=None, end_time=None):
    try:
        params = {"start_time": start_time, "end_time": end_time}
        response = requests.get(f"{BASE_URL}/plants/{plant_id}/drift_summary", params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching drift summary: {e}")
        return {}
    

@st.cache_data(ttl=600)
def get_LSTM_measurements_by_plant_id_and_panel_id(plant_id, panel_id):
    try:
        response = requests.get(f"{BASE_URL}/plants/{plant_id}/panels/{panel_id}/lstm_measurements")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching drift summary: {e}")
        return {}


@st.cache_data(ttl=600)
def get_LSTM_predictions_by_plant_id_and_panel_id(plant_id, panel_id):
    try:
        response = requests.get(f"{BASE_URL}/plants/{plant_id}/panels/{panel_id}/lstm_predictions")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching drift summary: {e}")
        return {}