from flask import Blueprint, jsonify, request
from backend.services.plants_service import get_measurements, get_predictions, get_plants

plants_bp = Blueprint("plants", __name__)

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
        plants = get_plants()
        if not plants:
            return jsonify({"error": f"No plants found"}), 404
        return jsonify(plants), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

# GET /plants/<plant_id>/predictions

@plants_bp.route("/plants/<plant_id>/predictions", methods=["GET"])
def plant_predictions(plant_id):
    """
    Returns a list of predictions for a specific plant.
    Each prediction: {"timestamp": ISO8601 string, "power": float}
    """
    try:
        predictions = get_predictions(plant_id)
        if not predictions:
            return jsonify({"error": f"No predictions found for plant {plant_id}"}), 404
        return jsonify(predictions), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# GET /plants/<plant_id>/measurements

@plants_bp.route("/plants/<plant_id>/measurements", methods=["GET"])
def plant_measurements(plant_id):
    """
    Returns historical measurements for a plant.
    """
    #hours = request.args.get("hours", default=24, type=int) this can be used to add query parameters 
    try:
        measurements = get_measurements(plant_id)
        if not measurements:
            return jsonify({"error": f"No measurements found for plant {plant_id}"}), 404
        return jsonify(measurements), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
