# app/models/user_otp_model.py
from app.extensions import db
from datetime import datetime

class UserOTP(db.Model):
    __tablename__ = 'user_otps'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False, index=True)
    otp_code = db.Column(db.Integer, nullable=False)
    expiry = db.Column(db.DateTime, nullable=False)
    attempts = db.Column(db.Integer, default=0)
