from flask import Flask
from routes.test_endpoint import predictions_bp
from routes.plants import plants_bp

app = Flask(__name__)

#attaches routes defined in (...) and becomes active
app.register_blueprint(predictions_bp) 
app.register_blueprint(plants_bp)

if __name__ == "__main__":
    app.run(debug=True)