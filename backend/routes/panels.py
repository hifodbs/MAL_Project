from flask import Blueprint, jsonify, request, current_app
from backend.services.panels_service import PanelsService
from backend.services.prediction_service import PredictionService
from datetime import datetime

panels_bp = Blueprint( "panels", __name__ )

data_directory = "cleaned_data"
historical_predictions = "historical_predictions"
panels_service = PanelsService(data_directory)


def get_prediction_service():
    return PredictionService(
        models=current_app.models,
        data_directory=current_app.config["DATA_DIRECTORY"],
        historical_predictions=current_app.config["HISTORICAL_PREDICTIONS"],
    )


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

    start_time_str = request.args.get("start_time", default=None)
    end_time_str = request.args.get("end_time", default=None)

    if start_time_str is not None:
        try:
            start_time = datetime.fromisoformat(start_time_str)
        except ValueError:
            return jsonify({"error": "Invalid time format. Use ISO 8601."}), 400
    else:
        start_time = None

    if end_time_str is not None:
        try:
            end_time = datetime.fromisoformat(end_time_str)
        except ValueError:
            return jsonify({"error": "Invalid time format. Use ISO 8601."}), 400
    else: 
        end_time = None

    try:
        measurements = panels_service.get_all_panel_measurements_by_id_and_time_reange(
            plant_id=plant_id,
            panel_id=panel_id,
            start_time=start_time,
            end_time=end_time
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
def get_panels_predictions(plant_id, panel_id):
    
    start_time_str = request.args.get("start_time", default=None)
    end_time_str = request.args.get("end_time", default=None)

    if start_time_str is not None:
        try:
            start_time = datetime.fromisoformat(start_time_str)
        except ValueError:
            return jsonify({"error": "Invalid time format. Use ISO 8601."}), 400
    else:
        start_time = None

    if end_time_str is not None:
        try:
            end_time = datetime.fromisoformat(end_time_str)
        except ValueError:
            return jsonify({"error": "Invalid time format. Use ISO 8601."}), 400
    else:
        end_time = None
        

    predictions_service = get_prediction_service()
    try:
        predictions = predictions_service.get_past_panel_predictions(
            plant_id=plant_id,
            panel_id=panel_id,
            start_time=start_time,
            end_time=end_time
        )

        return jsonify([
            {
                "timestamp": p.timestamp.isoformat(),
                "plant_id": p.plant_id,
                "panel_id": p.panel_id,
                "ac_power": p.predicted_ac_power,
                "drift": p.drift,
            }
            for p in predictions
        ]), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 500
    

# GET /plants/<plant_id>/panels/<panel_id>/new_prediction


@panels_bp.route(
    "/plants/<plant_id>/panels/<panel_id>/new_prediction",
    methods=["GET"],
)
def get_new_prediction_by_panel_id(plant_id, panel_id):

    time_str = request.args.get("time", default=None)

    if time_str is None:
        return jsonify({"error": "Invalid time format. Use ISO 8601."}), 400

    try:
        time = datetime.fromisoformat(time_str)
        predictions_service = get_prediction_service()
        
        prediction = predictions_service.train_next_timestamp(
            plant_id=plant_id,
            panel_id=panel_id,
            timestamp=time,
        )

        if prediction is None:
            return jsonify({"error": "No data available for the requested timestamp"}), 404    
           
        return jsonify([
            {
                "timestamp": prediction.timestamp.isoformat(),
                "plant_id": prediction.plant_id,
                "panel_id": prediction.panel_id,
                "ac_power": prediction.predicted_ac_power,
                "drift": prediction.drift
            }
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