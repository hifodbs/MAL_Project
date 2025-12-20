from flask import Flask
from routes.test_endpoint import predictions_bp

app = Flask(__name__)
app.register_blueprint(predictions_bp)

if __name__ == "__main__":
    app.run(debug=True)
