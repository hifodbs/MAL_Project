from flask import Blueprint, jsonify, request
from backend.services.panels_service import PanelsService
from datetime import datetime
import random 

panels_bp = Blueprint( "panels", __name__ )

data_directory = "cleaned_data"
panels_service = PanelsService(data_directory)

# GET /plants/<plant_id>/panels

@panels_bp.route("/plants/<plant_id>/panels", methods=["GET"])
def get_plant_panels(plant_id):

    try:
        panels = panels_service.get_all_by_plant_id(plant_id=plant_id)
        return jsonify([
            {"id": p.id, "plant_id": p.plant_id}
            for p in panels
        ]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# GET /plants/<plant_id>/panels/<panel_id>/measurements

@panels_bp.route(
    "/plants/<plant_id>/panels/<panel_id>/measurements",
    methods=["GET"],
)
def get_measurements(plant_id, panel_id):

    #Returns a list of measurements for a specific panel.
    #Each measurement: {"timestamp": ISO8601 string, "plant_id": string, "panel_id": string, "ac_power": float}

    hours = request.args.get("hours", default=24, type=int) 
    starting_time = request.args.get("time", default="2020-05-31T00:00:00")

    try:
        starting_time = datetime.fromisoformat(starting_time)
    except ValueError:
        return jsonify({"error": "Invalid time format. Use ISO 8601."}), 400

    try:
        measurements = panels_service.get_all_panel_measurements_by_id_and_time_reange(
            plant_id=plant_id,
            panel_id=panel_id,
            start_time=starting_time,
            hours=hours,
        )
        return jsonify([
            {
                "timestamp": m.timestamp.isoformat(),
                "plant_id": m.plant_id,
                "panel_id": m.panel_id,
                "ac_power": m.ac_power,
            }
            for m in measurements
        ]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# GET /plants/<plant_id>/panels/<panel_id>/predictions

@panels_bp.route(
    "/plants/<plant_id>/panels/<panel_id>/predictions",
    methods=["GET"],
)
def get_predictions(plant_id, panel_id):

    #Returns a list of predictions for a specific panel.
    #Each prediction: {"timestamp": ISO8601 string, "plant_id": string, "panel_id": string, "ac_power": float}

    hours = request.args.get("hours", default=48, type=int) 
    starting_time = request.args.get("time", default="2020-06-01T00:00:00")

    try:
        starting_time = datetime.fromisoformat(starting_time)
    except ValueError:
        return jsonify({"error": "Invalid time format. Use ISO 8601."}), 400

    try:
        predictions = panels_service.get_all_panel_measurements_by_id_and_time_reange( #this is fake
            plant_id=plant_id,
            panel_id=panel_id,
            start_time=starting_time,
            hours=hours,
        )
        return jsonify([
            {
                "timestamp": p.timestamp.isoformat(),
                "plant_id": p.plant_id,
                "panel_id": p.panel_id,
                "ac_power": p.ac_power * random.uniform(0.5, 1.5),
            }
            for p in predictions
        ]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    


##testing
#
#panels = panels_service.get_all_by_plant_id(
#    "solar_1",
#)
#
#for p in panels[:5]:
#    print(m)
#count = 0 
#for p in panels:
#    count += 1
#print(count)