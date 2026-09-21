from flask import Flask, request, jsonify
from flask_cors import CORS

from decision import verify_news

app = Flask(__name__)

CORS(
    app,
    resources={
        r"/verify": {
            "origins": [
                "https://truth-shield-ai-nine.vercel.app"
            ]
        }
    }
)


@app.route("/")
def home():
    return "TruthShield AI Backend Running"


@app.route("/verify", methods=["POST"])
def verify():

    data = request.get_json()

    if not data or "news" not in data:
        return jsonify({
            "error": "News text is required."
        }), 400

    news = str(data["news"]).strip()

    if not news:
        return jsonify({
            "error": "News text cannot be empty."
        }), 400

    try:

        result = verify_news(news)

        return jsonify(result)

    except Exception as e:

        return jsonify({
            "error": "Verification failed.",
            "details": str(e)
        }), 500


if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
