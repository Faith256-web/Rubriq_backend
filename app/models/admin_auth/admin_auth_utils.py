# # You can put this in utils.py or admin_auth.py


# import os
# from dotenv import load_dotenv

# from config import EMAIL_PASS, EMAIL_USER

# load_dotenv()



# import smtplib

# def send_email(recipient, subject, message):
#     try:
#         server = smtplib.SMTP('smtp.gmail.com', 587)
#         server.starttls()
#         server.login('your_email@gmail.com', 'your_app_password')  # Use env vars
#         email_body = f"Subject: {subject}\n\n{message}"
#         server.sendmail('your_email@gmail.com', recipient, email_body)
#         server.quit()
#         return True
#     except Exception as e:
#         print("Email error:", e)
#         return False



# def send_email(recipient, subject, message):
#     try:
#         server = smtplib.SMTP('smtp.gmail.com', 587)
#         server.starttls()
#         server.login(EMAIL_USER, EMAIL_PASS)
#         email_body = f"Subject: {subject}\n\n{message}"
#         server.sendmail(EMAIL_USER, recipient, email_body)
#         server.quit()
#         return True
#     except Exception as e:
#         print("Email error:", e)
#         return False
# app/routes/auth.py

from flask import Blueprint, request, jsonify
from app.models.user.user_model import User
from app.extensions import db
from flask_bcrypt import Bcrypt
from flask_jwt_extended import create_access_token

from app.models.auth_logs import AuthLog
import datetime

auth_bp = Blueprint("auth_bp", __name__, url_prefix="/api/auth")

bcrypt = Bcrypt()


# ======================
# REGISTER
# ======================
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    hashed_pw = bcrypt.generate_password_hash(data["password"]).decode("utf-8")

    user = User(
        name=data["name"],
        email=data["email"],
        password=hashed_pw,
        role="user"
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User created successfully"}), 201


# ======================
# LOGIN
# ======================
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    user = User.query.filter_by(email=data["email"]).first()

    if not user or not bcrypt.check_password_hash(user.password, data["password"]):
        return jsonify({"error": "Invalid credentials"}), 401

    # create token
    token = create_access_token(identity=user.id)

    # log login activity
    log = AuthLog(
        user_id=user.id,
        ip=request.remote_addr,
        device=request.headers.get("User-Agent"),
        time=datetime.datetime.utcnow()
    )

    db.session.add(log)
    db.session.commit()

    return jsonify({
        "token": token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }
    }), 200