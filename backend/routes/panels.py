from flask import Blueprint, jsonify, request
from backend.services.panels_service import get_panels, get_panel_measurements, get_panel_predictions


panels_bp = Blueprint( 
    "panels", 
    __name__, 
    url_prefix="/plants/<plant_id>/panels"
)



# GET /plants/<plant_id>/panels

@panels_bp.route("", methods=["GET"])
def get_plant_panels(plant_id):
    panels = get_panels(plant_id=plant_id)
    return jsonify(panels), 200


# GET /plants/<plant_id>/panels/<panel_id>/measurements

@panels_bp.route(
    "/<panel_id>/measurements",
    methods=["GET"],
)
def get_measurements(plant_id, panel_id):
    measurements = get_panel_measurements(
        plant_id=plant_id,
        panel_id=panel_id,
    )
    return jsonify(measurements), 200



# GET /plants/<plant_id>/panels/<panel_id>/predictions

@panels_bp.route(
    "/<panel_id>/predictions",
    methods=["GET"],
)
def get_predictions(plant_id, panel_id):
    predictions = get_panel_predictions(
        plant_id=plant_id,
        panel_id=panel_id,
    )
    return jsonify(predictions), 200
