from flask import Blueprint, jsonify, request
from backend.services.plants_service import PlantsService
from backend.services.panels_service import PanelsService
import random
from datetime import datetime

plants_bp = Blueprint("plants", __name__)


data_directory = "cleaned_data"
panles_service = PanelsService(data_directory)
plants_service = PlantsService(data_directory)

# GET /plants

@plants_bp.route("/plants", methods=["GET"])
def plants():
    """
    Returns a list of plants.
    Each plant: {
        "id": "plant_id",
        "name": "plant_name",
    }
    """
    try:
        plants = plants_service.get_plants()
        if not plants:
            return jsonify({"error": f"No plants found"}), 404
        return jsonify(plants), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    



# GET /plants/<plant_id>/predictions

@plants_bp.route("/plants/<plant_id>/predictions", methods=["GET"])
def plant_predictions(plant_id):
    
    #Returns a list of predictions for a specific plant.
    #Each prediction: {"timestamp": ISO8601 string, "plant_id": string, "ac_power": float}
    
    hours = request.args.get("hours", default=48, type=int) 
    starting_time = request.args.get("time", default="2020-06-01T00:00:00")

    try:
        starting_time = datetime.fromisoformat(starting_time)
    except ValueError:
        return jsonify({"error": "Invalid time format. Use ISO 8601."}), 400

    try:

        #this predictions are fake 
        predictions = plants_service.get_global_measurements_by_plant_id_and_time_range(plant_id, starting_time, hours)
        if not predictions:
            return jsonify({"error": f"No predictions found for plant {plant_id}"}), 404
        return jsonify([
        {
            "timestamp": p.timestamp.isoformat(),
            "plant_id": p.plant_id,
            "ac_power": p.ac_power * random.uniform(0.5, 1.5),
        }
        for p in predictions
    ]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# GET /plants/<plant_id>/measurements

@plants_bp.route("/plants/<plant_id>/measurements", methods=["GET"])
def plant_measurements(plant_id):
    
    #Returns historical measurements for a plant.
    
    hours = request.args.get("hours", default=24, type=int) 
    starting_time = request.args.get("time", default="2020-05-31T00:00:00")

    try:
        starting_time = datetime.fromisoformat(starting_time)
    except ValueError:
        return jsonify({"error": "Invalid time format. Use ISO 8601."}), 400

    try:
        measurements = plants_service.get_global_measurements_by_plant_id_and_time_range(plant_id, starting_time, hours)
        if not measurements:
            return jsonify({"error": f"No measurements found for plant {plant_id}"}), 404
        return jsonify([
        {
            "timestamp": m.timestamp.isoformat(),
            "plant_id": m.plant_id,
            "ac_power": m.ac_power,
        }
        for m in measurements
    ]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

##testing
#
#measurements = plants_service.get_global_measurements_by_plant_id_and_time_range(
#    "solar_1",
#    datetime.fromisoformat("2020-05-31T00:00:00"),
#    24,
#)
#
#for m in measurements[:5]:
#    print(m)
#count = 0 
#for m in measurements:
#    count += 1
#print(count)