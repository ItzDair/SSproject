import random
import os
import secrets
from datetime import datetime, timedelta
from flask import Blueprint, request, session, redirect, render_template, jsonify
from .models import get_user_by_username, update_user_otp
from .database import get_db
from .security import hash_password, verify_password
from .mfa import send_otp_email
from .telegram_mfa import send_otp_telegram

bp = Blueprint("routes", __name__)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# ----------------- Login -----------------
@bp.route("/", methods=["GET"])
def login_page():
    return render_template("login.html")

@bp.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    mfa_channel = request.form.get("mfa_channel")

    user = get_user_by_username(username)
    if not user:
        return "User not found", 404
    if not verify_password(password, user["password_hash"]):
        return "Invalid credentials", 401

    session["tmp_user_id"] = user["id"]
    session["mfa_channel"] = mfa_channel

    if user.get("mfa_enabled"):
        otp = f"{random.randint(100000, 999999)}"
        expiry = datetime.utcnow() + timedelta(minutes=5)
        update_user_otp(user["id"], otp, expiry)

        if mfa_channel == "email":
            send_otp_email(user["email"], otp)
        elif mfa_channel == "telegram":
            if not user.get("telegram_chat_id"):
                return redirect("/link_telegram")  # redirect to link page
            send_otp_telegram(user["telegram_chat_id"], otp)
        else:
            return "Invalid MFA channel", 400

        return redirect("/mfa")

    # No MFA
    session["user_id"] = user["id"]
    return redirect("/dashboard")

# ----------------- Link Telegram -----------------
@bp.route("/link_telegram", methods=["GET"])
def link_telegram_page():
    if "tmp_user_id" not in session:
        return redirect("/")

    # Generate a secure random token
    token = secrets.token_urlsafe(16)

    # Store token in the database
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET telegram_link_token=%s WHERE id=%s",
        (token, session["tmp_user_id"])
    )
    conn.commit()
    cursor.close()
    conn.close()

    return render_template("link_telegram.html", token=token)

# ----------------- Telegram Webhook -----------------
@bp.route("/telegram_webhook", methods=["POST"])
def telegram_webhook():
    data = request.get_json()

    if "message" not in data:
        return jsonify({"status": "no message"}), 200

    message = data["message"]
    chat_id = message["chat"]["id"]
    text = message.get("text", "").strip()

    if text.startswith("/start"):
        parts = text.split()
        if len(parts) == 2:
            token = parts[1]

            # Look up user by token
            conn = get_db()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM users WHERE telegram_link_token=%s",
                (token,)
            )
            user = cursor.fetchone()

            if user:
                user_id = user["id"]

                # Link Telegram account and clear token
                cursor.execute(
                    "UPDATE users SET telegram_chat_id=%s, telegram_link_token=NULL WHERE id=%s",
                    (chat_id, user_id)
                )
                conn.commit()

                # Generate OTP automatically
                otp = f"{random.randint(100000, 999999)}"
                expiry = datetime.utcnow() + timedelta(minutes=5)
                cursor.execute(
                    "UPDATE users SET otp=%s, otp_expiry=%s WHERE id=%s",
                    (otp, expiry, user_id)
                )
                conn.commit()
                cursor.close()
                conn.close()

                # Send OTP via Telegram
                send_otp_telegram(chat_id, otp)

                # Optional: reply to user
                import requests
                url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                requests.post(url, json={
                    "chat_id": chat_id,
                    "text": f"Your account is linked. OTP has been sent: {otp}. It expires in 5 minutes."
                })

                return jsonify({"status": "linked and OTP sent"}), 200

            cursor.close()
            conn.close()

    return jsonify({"status": "ok"}), 200


# ----------------- Resend Telegram OTP -----------------
@bp.route("/resend_telegram_otp", methods=["POST"])
def resend_telegram_otp():
    user_id = session.get("tmp_user_id")
    if not user_id:
        return "Session expired", 400

    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if not user or not user.get("telegram_chat_id"):
        return "Telegram not linked", 400

    otp = f"{random.randint(100000, 999999)}"
    expiry = datetime.utcnow() + timedelta(minutes=5)
    update_user_otp(user_id, otp, expiry)
    send_otp_telegram(user["telegram_chat_id"], otp)

    return redirect("/mfa")

# ----------------- MFA -----------------
@bp.route("/mfa", methods=["GET", "POST"])
def mfa():
    user_id = session.get("tmp_user_id")
    if not user_id:
        return redirect("/")

    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if not user or not user.get("mfa_enabled"):
        session["user_id"] = user_id
        return redirect("/dashboard")

    if request.method == "GET":
        return render_template("mfa_verify.html")

    entered_otp = request.form.get("code")
    if entered_otp != user.get("otp") or datetime.utcnow() > user.get("otp_expiry"):
        return "Invalid or expired OTP", 403

    session.pop("tmp_user_id", None)
    session["user_id"] = user_id
    update_user_otp(user_id, None, None)
    return redirect("/dashboard")

# ----------------- Dashboard -----------------
@bp.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/")
    return render_template("dashboard.html")

# ----------------- Logout -----------------
@bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect("/")
