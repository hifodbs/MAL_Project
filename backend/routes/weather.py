from flask import Blueprint, jsonify, request
from services.weather_service import get_weather, get_weather_measurements, get_weather_predictions

weather_bp = Blueprint(
    "weather", 
    __name__,
    url_prefix="/plants/<plant_id>/weather"
)


"""
# GET /plants/<weather_id>/weather  

@weather_bp.route("", methods=["GET"])
def get_plant_weather(plant_id):
    weather = get_weather(plant_id=plant_id)
    return jsonify(weather), 200
"""


# GET /plants/<plant_id>/weather/measurements

@weather_bp.route(
    "/measurements",
    methods=["GET"],
)
def get_measurements(plant_id):
    measurements = get_weather_measurements(
        plant_id=plant_id
    )
    return jsonify(measurements), 200



# GET /plants/<plant_id>/weather/predictions

@weather_bp.route(
    "/<weather_id>/predictions",
    methods=["GET"],
)
def get_predictions(plant_id):
    predictions = get_weather_predictions(
        plant_id=plant_id
    )
    return jsonify(predictions), 200

