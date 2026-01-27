# auth_service/app/routes.py
import random
from flask import Blueprint, render_template, request, redirect, session, jsonify
from telegram import Bot
from .models import get_user_by_username
from .database import get_db
from .security import hash_password, verify_password

bp = Blueprint("routes", __name__)

# Telegram bot token (replace with your bot token)
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN"

# Helper function to send OTP via Telegram
def send_telegram_otp(phone_number, otp):
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    chat_id = phone_number  # for testing, map phone_number to chat_id
    bot.send_message(chat_id=chat_id, text=f"Your OTP code is: {otp}")

# Login page (GET)
@bp.route("/", methods=["GET"])
def login_page():
    return render_template("face/login.html")

# Login action (POST)
@bp.route("/login", methods=["POST"])
def login():
    username = request.form.get("username")
    password = request.form.get("password")
    user = get_user_by_username(username)

    if not user:
        return "User not found", 404

    if not verify_password(password, user["password_hash"]):
        return "Invalid credentials", 401

    session["tmp_user_id"] = user["id"]

    # If MFA is enabled for the user, redirect to MFA page
    if user.get("mfa_enabled"):
        return redirect("/mfa")

    # Otherwise, login directly
    session["user_id"] = user["id"]
    return redirect("/dashboard")

# MFA page (GET/POST)
@bp.route("/mfa", methods=["GET", "POST"])
def mfa():
    user_id = session.get("tmp_user_id")
    if not user_id:
        return redirect("/")

    # Fetch user from DB
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if not user or not user.get("mfa_enabled"):
        # No MFA, proceed to dashboard
        session["user_id"] = user_id
        return redirect("/dashboard")

    if request.method == "GET":
        # Generate OTP and store in session
        otp = str(random.randint(100000, 999999))
        session["telegram_otp"] = otp
        send_telegram_otp(user["phone_number"], otp)
        return render_template("face/mfa_verify.html")  # page with OTP input

    if request.method == "POST":
        entered_otp = request.form.get("code")
        if entered_otp == session.get("telegram_otp"):
            session.pop("tmp_user_id")
            session["user_id"] = user_id
            session.pop("telegram_otp")
            return redirect("/dashboard")
        return "Invalid OTP", 403

# Registration page (GET/POST)
@bp.route("/register", methods=["GET", "POST"])
def register_user_page():
    if request.method == "POST":
        # Handle both JSON API or HTML form
        if request.is_json:
            data = request.get_json()
            username = data.get("username")
            email = data.get("email")
            phone_number = data.get("phone_number")
            password = data.get("password")
        else:
            username = request.form.get("username")
            email = request.form.get("email")
            phone_number = request.form.get("phone_number")
            password = request.form.get("password")

        if not all([username, email, password, phone_number]):
            return jsonify({"error": "Missing fields"}), 400

        hashed_password = hash_password(password)

        conn = get_db()
        cursor = conn.cursor()
        # Automatically enable MFA for every new user
        cursor.execute(
            "INSERT INTO users (username, email, phone_number, password_hash, mfa_enabled) VALUES (%s,%s,%s,%s,TRUE)",
            (username, email, phone_number, hashed_password)
        )
        conn.commit()
        cursor.close()
        conn.close()

        # Return JSON for API, redirect for HTML form
        if request.is_json:
            return jsonify({"message": "User registered successfully"}), 201
        else:
            return redirect("/")

    # GET request → show registration page
    return render_template("face/register.html")

# Dashboard page (protected)
@bp.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/")
    return render_template("face/dashboard.html")
