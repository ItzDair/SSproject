from flask import Flask
import os
from .routes import bp
from .telegram_webhook import bp_telegram

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "supersecretkey")

# Register blueprints
app.register_blueprint(bp)
app.register_blueprint(bp_telegram)

if __name__ == "__main__":
    app.run(debug=True)
