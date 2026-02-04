from flask import Blueprint, request
from .database import get_db
import os

bp_telegram = Blueprint("telegram_webhook", __name__)
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

@bp_telegram.route("/telegram_webhook", methods=["POST"])
def telegram_webhook():
    data = request.get_json()

    if "message" not in data:
        return {"ok": True}

    chat_id = data["message"]["chat"]["id"]
    text = data["message"].get("text", "")

    # Handle /link <user_id> command
    if text.startswith("/link"):
        try:
            user_id = int(text.split()[1])
        except (IndexError, ValueError):
            return {"ok": True}

        # Update telegram_chat_id in the database
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET telegram_chat_id=%s WHERE id=%s",
            (chat_id, user_id)
        )
        conn.commit()
        cursor.close()
        conn.close()

    return {"ok": True}
