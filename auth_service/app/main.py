# auth_service/app/main.py
from flask import Flask
import os
from .routes import bp  # Import the blueprint

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "supersecretkey")  # load from .env in production

# Register blueprint
app.register_blueprint(bp)

if __name__ == "__main__":
    app.run(debug=True)
