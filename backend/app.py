from flask import Flask, request
from flask_cors import CORS

from ais import classify_news,valid_detectors

app = Flask(__name__)

CORS(app)


@app.route("/")
def home():
    return "TruthShield AI Backend Running"

@app.route("/detect",methods=["POST"])
def detect():
    data=request.json
    news=data["news"]
    result,confidence=classify_news(news,valid_detectors)
    return {
        "result":result,
        "confidence":confidence
    }



if __name__ == "__main__":
    app.run(debug=True)