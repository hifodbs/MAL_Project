from flask import Blueprint, jsonify, request
from backend.services.plants_service import PlantsService
from backend.services.panels_service import PanelsService
import random

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
    #Each prediction: {"timestamp": ISO8601 string, "power": float}
    
    try:

        #this predictions are fake 
        predictions = plants_service.get_global_measurements_by_plant_id(plant_id)
        if not predictions:
            return jsonify({"error": f"No predictions found for plant {plant_id}"}), 404
        return jsonify([
        {
            "timestamp": p.timestamp.isoformat(),
            "plant_id": p.plant_id,
            "ac_power": p.ac_power * random.uniform(0.9, 1.1),
        }
        for p in predictions
    ]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# GET /plants/<plant_id>/measurements

@plants_bp.route("/plants/<plant_id>/measurements", methods=["GET"])
def plant_measurements(plant_id):
    
    #Returns historical measurements for a plant.
    
    #hours = request.args.get("hours", default=24, type=int) this can be used to add query parameters 
    try:
        measurements = plants_service.get_global_measurements_by_plant_id(plant_id)
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
