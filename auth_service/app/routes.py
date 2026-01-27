from flask import Blueprint, request, jsonify, render_template, session
from database import db
from models import User, MFAMethod
from security import verify_password
from mfa import verify_totp, send_sms, send_email
import random

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("face/login.html")

    username = request.form["username"]
    password = request.form["password"]

    user = User.query.filter_by(username=username).first()
    if not user or not verify_password(user.password_hash, password):
        return "Invalid credentials", 401

    if user.mfa_enabled:
        session["mfa_user"] = user.id
        return render_template("face/mfa_verify.html")

    session["user"] = user.id
    return render_template("face/dashboard.html")

@auth_bp.route("/mfa/verify", methods=["POST"])
def mfa_verify():
    user_id = session.get("mfa_user")
    code = request.form["code"]

    methods = MFAMethod.query.filter_by(user_id=user_id, enabled=True).all()

    for method in methods:
        if method.method_type == "TOTP":
            if verify_totp(method.secret_key, code):
                session["user"] = user_id
                return render_template("face/dashboard.html")

        elif method.method_type == "SMS":
            if session.get("sms_code") == code:
                session["user"] = user_id
                return render_template("face/dashboard.html")

        elif method.method_type == "EMAIL":
            if session.get("email_code") == code:
                session["user"] = user_id
                return render_template("face/dashboard.html")

    return "Invalid MFA code", 401

@auth_bp.route("/mfa/send", methods=["POST"])
def send_mfa():
    user_id = session.get("mfa_user")
    methods = MFAMethod.query.filter_by(user_id=user_id, enabled=True).all()

    code = str(random.randint(100000, 999999))

    for method in methods:
        if method.method_type == "SMS":
            session["sms_code"] = code
            send_sms(method.phone_number, code)

        if method.method_type == "EMAIL":
            session["email_code"] = code
            send_email(method.email, code)

    return jsonify({"status": "sent"})
