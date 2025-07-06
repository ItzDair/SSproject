from flask import Flask, request, jsonify
import pyotp
import os
import logging
import requests  # Added for notification service calls
from datetime import datetime
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')

# Rate limiting
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=[os.getenv('RATE_LIMIT', '200 per day')]
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('MFA_Server')

# Initialize users from environment variables
users = {
    "dair": {
        "secret": os.getenv('Dair_SECRET'),
        "telegram_id": os.getenv('DAIR_TELEGRAM_ID'),  # New field
        "email": os.getenv('Dair_email')  # New field
    },
    "bob": {
        "secret": os.getenv('BOB_SECRET'),
        "telegram_id": os.getenv('BOB_TELEGRAM_ID'),  # New field
        "email": os.getenv('BOB_EMAIL')  # New field
    }
}

@app.route('/request-otp', methods=['POST'])
@limiter.limit("3 per minute")
def request_otp():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400
            
        username = data.get('username', '').lower()
        
        if not username:
            return jsonify({"error": "Username required"}), 400

        if username not in users:
            logger.warning(f"User not found: {username}")
            return jsonify({"error": "User not found"}), 404

        # Generate OTP
        totp = pyotp.TOTP(users[username]["secret"])
        otp_code = totp.now()

        # Get both contact methods
        telegram_id = users[username].get("telegram_id")
        email = users[username].get("email")
        
        if not telegram_id and not email:
            return jsonify({"error": "No contact method found for user"}), 400

        success_channels = []
        errors = []

        # Send to Telegram if configured
        if telegram_id:
            try:
                response = requests.post(
                    "http://notification-service:6000/send",
                    json={
                        "channel": "telegram",
                        "recipient": telegram_id,
                        "message": f"Your OTP code is: {otp_code}"
                    },
                    timeout=3
                )
                response.raise_for_status()
                success_channels.append("telegram")
                logger.info(f"OTP sent to {username} via Telegram")
            except requests.exceptions.RequestException as e:
                errors.append(f"Telegram failed: {str(e)}")
                logger.error(f"Telegram delivery failed for {username}: {str(e)}")

        # Send to Email if configured
        if email:
            try:
                response = requests.post(
                    "http://notification-service:6000/send",
                    json={
                        "channel": "email",
                        "recipient": email,
                        "message": f"Your OTP code is: {otp_code}"
                    },
                    timeout=5
                )
                response.raise_for_status()
                success_channels.append("email")
                logger.info(f"OTP sent to {username} via Email")
            except requests.exceptions.RequestException as e:
                errors.append(f"Email failed: {str(e)}")
                logger.error(f"Email delivery failed for {username}: {str(e)}")

        # Return results
        if success_channels:
            return jsonify({
                "status": "OTP sent",
                "successful_channels": success_channels,
                "failed_channels": errors if errors else None
            })
        else:
            return jsonify({
                "error": "All delivery methods failed",
                "details": errors
            }), 500

    except Exception as e:
        logger.error(f"Error in request_otp: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

@app.route('/verify', methods=['POST'])
@limiter.limit("5 per minute")
def verify():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Invalid JSON"}), 400
            
        username = data.get('username', '').lower()
        token = data.get('token', '')
        
        if not username or not token:
            return jsonify({"error": "Username and token required"}), 400

        if username not in users:
            logger.warning(f"User not found: {username}")
            return jsonify({"error": "User not found"}), 404

        totp = pyotp.TOTP(users[username]["secret"])
        is_valid = totp.verify(token, valid_window=4)
        
        logger.info(f"{datetime.now()} | User: {username} | Valid: {is_valid}")
        
        return jsonify({
            "valid": is_valid,
            "message": "Authentication successful" if is_valid else "Invalid token"
        })

    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        return jsonify({"error": "Internal server error"}), 500

@app.route('/healthcheck')
def healthcheck():
    try:
        if not os.getenv('ALICE_SECRET'):
            raise ValueError("Missing ALICE_SECRET in environment")
        
        # Test notification service connection
        try:
            requests.get("http://notification-service:6000/healthcheck", timeout=2)
        except requests.exceptions.RequestException:
            raise ConnectionError("Cannot connect to notification service")
        
        return jsonify({
            "status": "healthy",
            "service": "mfa-auth",
            "users_configured": len(users)
        })
    except Exception as e:
        logger.error(f"Healthcheck failed: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    logger.info(f"Starting server with users: {list(users.keys())}")
    app.run(host='0.0.0.0', port=6000)