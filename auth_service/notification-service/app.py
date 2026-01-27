from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/sms", methods=["POST"])
def sms():
    data = request.json
    print(f"[SMS] {data['phone']} -> {data['code']}")
    return jsonify({"status": "sent"})

@app.route("/email", methods=["POST"])
def email():
    data = request.json
    print(f"[EMAIL] {data['email']} -> {data['code']}")
    return jsonify({"status": "sent"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
