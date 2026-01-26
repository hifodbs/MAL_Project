from flask import Blueprint, jsonify, request, current_app
from backend.services.plants_service import PlantsService
from backend.services.panels_service import PanelsService
from backend.services.prediction_service import PredictionService
from datetime import datetime

plants_bp = Blueprint("plants", __name__)


data_directory = "cleaned_data"
historical_predictions = "historical_predictions"
panles_service = PanelsService(data_directory)
plants_service = PlantsService(data_directory)


def get_prediction_service():
    return PredictionService(
        models=current_app.models,
        data_directory=current_app.config["DATA_DIRECTORY"],
        historical_predictions=current_app.config["HISTORICAL_PREDICTIONS"],
    )


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
    
    start_time_str = request.args.get("start_time", default=None)
    end_time_str = request.args.get("end_time", default="2020-06-14T10:45:00")

    if start_time_str:
        try:
            start_time = datetime.fromisoformat(start_time)
        except ValueError:
            return jsonify({"error": "Invalid time format. Use ISO 8601."}), 400
    else:
        start_time = None

    if end_time_str:
        try:
            end_time = datetime.fromisoformat(end_time_str)
        except ValueError:
            return jsonify({"error": "Invalid time format. Use ISO 8601."}), 400
    else:
        end_time = None 

    try:
        prediction_service = get_prediction_service()
        predictions = prediction_service.predict_plant(
            plant_id=plant_id,
            start_time=start_time,
            end_time=end_time
        )
        return jsonify(predictions), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 500


# GET /plants/<plant_id>/measurements

@plants_bp.route("/plants/<plant_id>/measurements", methods=["GET"])
def plant_measurements(plant_id):
    
    #Returns historical measurements for a plant.
    
    start_time_str = request.args.get("start_time", default=None)
    end_time_str = request.args.get("end_time", default="2020-06-14T10:45:00")

    if start_time_str:
        try:
            start_time = datetime.fromisoformat(start_time)
        except ValueError:
            return jsonify({"error": "Invalid time format. Use ISO 8601."}), 400
    else:
        start_time = None

    if end_time_str:
        try:
            end_time = datetime.fromisoformat(end_time_str)
        except ValueError:
            return jsonify({"error": "Invalid time format. Use ISO 8601."}), 400
    else:
        end_time = None 

    try:
        measurements = plants_service.get_global_measurements_by_plant_id_and_time_range(plant_id, end_time, start_time)
        if not measurements:
            return jsonify({"error": f"No measurements found for plant {plant_id}"}), 404
        return jsonify([{ "timestamp": m.timestamp.isoformat(), "plant_id": m.plant_id, "ac_power": m.ac_power} for m in measurements]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    



# GET /plants/<plant_id>/report

@plants_bp.route("/plants/<plant_id>/report", methods=["GET"])
def plant_report(plant_id, day):
    
    day = request.args.get("day",default="2020-06-14T10:45:00")

    try:
        day = request.args.get("day",default="2020-06-14T10:45:00")
    except ValueError:
        return jsonify({"error": "Invalid time format. Use ISO 8601."}), 400

    try:
        report = plants_service.generate_report(plant_id, day)
        return jsonify(report), 200
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