from flask import Flask, request, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from notification_service import send_email, send_telegram
import os

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')

# Initialize rate limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=[os.getenv('RATE_LIMIT', '200 per day')]
)

@app.route('/send', methods=['POST'])
@limiter.limit("5 per minute")
def send():
    data = request.json
    
    # Input validation
    required_fields = ['channel', 'recipient', 'message']
    if not all(field in data for field in required_fields):
        return jsonify({"error": "Missing required fields"}), 400
    
    channel = data['channel']
    recipient = data['recipient']
    message = data['message']

    try:
        if channel == 'email':
            send_email(recipient, "Your OTP Code", message)
        elif channel == 'telegram':
            send_telegram(recipient, f"🔑 Your OTP: {message}")
        else:
            return jsonify({"error": "Unsupported channel"}), 400
        
        return jsonify({"status": "sent"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/healthcheck')
def healthcheck():
    return jsonify({"status": "healthy", "service": "notification"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=6000)