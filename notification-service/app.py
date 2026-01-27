from flask import Flask, request

app = Flask(__name__)

@app.route("/notify", methods=["POST"])
def notify():
    return {"status": "sent"}

app.run(host="0.0.0.0", port=5001)
