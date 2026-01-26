from flask import Flask
from backend.routes.test_endpoint import predictions_bp
from backend.routes.plants import plants_bp
from backend.routes.panels import panels_bp
from backend.utils.startups_tasks import startup_tasks

def create_app():
    app = Flask(__name__)


    app.config["DATA_DIRECTORY"] = "cleaned_data"
    app.config["HISTORICAL_PREDICTIONS"] = "historical_predictions"

    app.register_blueprint(predictions_bp)
    app.register_blueprint(plants_bp)
    app.register_blueprint(panels_bp)

    startup_tasks(app)

    return app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)