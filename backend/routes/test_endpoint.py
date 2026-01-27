from flask import Blueprint, jsonify
from backend.services.test_service import get_predictions

predictions_bp = Blueprint("predictions", __name__)

@predictions_bp.route("/predictions")
def predictions():
    real, predicted = get_predictions()
    return jsonify({
        "real": real,
        "predicted": predicted
    })
