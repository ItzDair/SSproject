import random
from datetime import datetime, timedelta
from flask import Blueprint, render_template, request, redirect, session
from .models import get_user_by_username, update_user_otp
from .database import get_db
from .security import hash_password, verify_password
from .mfa import send_otp_email

bp = Blueprint("routes", __name__)

# Login page
@bp.route("/", methods=["GET"])
def login_page():
    return render_template("login.html")

# Login action
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

    # If MFA enabled, generate OTP and send email
    if user.get("mfa_enabled"):
        otp = f"{random.randint(100000, 999999)}"
        expiry = datetime.utcnow() + timedelta(minutes=5)
        update_user_otp(user["id"], otp, expiry)
        send_otp_email(user["email"], otp)
        return redirect("/mfa")

    # No MFA, login directly
    session["user_id"] = user["id"]
    return redirect("/dashboard")

# MFA page
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
        # OTP already sent at login
        return render_template("mfa_verify.html")

    if request.method == "POST":
        entered_otp = request.form.get("code")
        otp_db = user.get("otp")
        otp_expiry = user.get("otp_expiry")

        if not otp_db or entered_otp != otp_db:
            return "Invalid OTP", 403
        if datetime.utcnow() > otp_expiry:
            return "OTP expired", 403

        # OTP valid
        session.pop("tmp_user_id", None)
        session["user_id"] = user_id
        update_user_otp(user_id, None, None)  # clear OTP

        return redirect("/dashboard")

# Registration
@bp.route("/register", methods=["GET", "POST"])
def register_user_page():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        phone_number = request.form.get("phone_number")
        password = request.form.get("password")

        if not all([username, email, phone_number, password]):
            return "Missing fields", 400

        hashed_password = hash_password(password)
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (username, email, phone_number, password_hash, mfa_enabled) VALUES (%s,%s,%s,%s,TRUE)",
            (username, email, phone_number, hashed_password)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return redirect("/")

    return render_template("register.html")

# Dashboard
@bp.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect("/")
    return render_template("dashboard.html")

# Logout
@bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect("/")
