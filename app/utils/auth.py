# from flask_jwt_extended import create_access_token
# from app.extensions import bcrypt
# from app.models.user.user_model import User


# def hash_password(password):
#     return bcrypt.generate_password_hash(password).decode('utf-8')

# def check_password(password, hashed):
#     return bcrypt.check_password_hash(hashed, password)

# def generate_token(user):
#     return create_access_token(identity=str(user.id))

# app/models/auth_logs.py

from app.extensions import db
from datetime import datetime

class AuthLog(db.Model):
    __tablename__ = "auth_logs"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    ip = db.Column(db.String(100))
    device = db.Column(db.String(255))

    time = db.Column(db.DateTime, default=datetime.utcnow)