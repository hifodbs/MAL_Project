from flask import Blueprint, jsonify, request
from backend.services.panels_service import PanelsService
import random 

panels_bp = Blueprint( 
    "panels", 
    __name__, 
    url_prefix="/plants/<plant_id>/panels"
)

data_directory = "cleaned_data"
panels_service = PanelsService(data_directory)

# GET /plants/<plant_id>/panels

@panels_bp.route("", methods=["GET"])
def get_plant_panels(plant_id):
    panels = panels_service.get_all_by_plant_id(plant_id=plant_id)
    return jsonify(panels), 200


# GET /plants/<plant_id>/panels/<panel_id>/measurements

@panels_bp.route(
    "/<panel_id>/measurements",
    methods=["GET"],
)
def get_measurements(plant_id, panel_id):
    measurements = panels_service.get_all_panel_measurements_by_id(
        plant_id=plant_id,
        panel_id=panel_id,
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



# GET /plants/<plant_id>/panels/<panel_id>/predictions

@panels_bp.route(
    "/<panel_id>/predictions",
    methods=["GET"],
)
def get_predictions(plant_id, panel_id):
    predictions = panels_service.get_all_panel_measurements_by_id( #this is fake
        plant_id=plant_id,
        panel_id=panel_id,
    )
    return jsonify([
        {
            "timestamp": p.timestamp.isoformat(),
            "plant_id": p.plant_id,
            "panel_id": p.panel_id,
            "ac_power": p.ac_power * random.uniform(0.9, 1.1),
        }
        for p in predictions
    ]), 200
