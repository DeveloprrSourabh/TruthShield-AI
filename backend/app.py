from flask import Flask, request, jsonify
from flask_cors import CORS

from ais import classify_news, valid_detectors
from decision import verify_news


app = Flask(__name__)

CORS(app)


@app.route("/")
def home():
    return "TruthShield AI Backend Running"


@app.route("/detect", methods=["POST"])
def detect():

    data = request.get_json()

    if not data or "news" not in data:
        return jsonify({
            "error": "News text is required."
        }), 400

    news = data["news"]

    result, confidence = classify_news(
        news,
        valid_detectors
    )

    return jsonify({
        "result": result,
        "confidence": confidence
    })


@app.route("/verify", methods=["POST"])
def verify():

    data = request.get_json()

    if not data or "news" not in data:
        return jsonify({
            "error": "News text is required."
        }), 400

    news = data["news"]

    result = verify_news(news)

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)