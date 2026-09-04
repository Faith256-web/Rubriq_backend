# app/models/auth_logs.py

from app.extensions import db
from datetime import datetime

class AuthLog(db.Model):
    __tablename__ = "auth_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    ip = db.Column(db.String(100))
    device = db.Column(db.String(255))
    time = db.Column(db.DateTime, default=datetime.utcnow)
    is_success = db.Column(db.Boolean, default=True)
    attempt_identifier = db.Column(db.String(120), nullable=True) # email or phone of the attempt