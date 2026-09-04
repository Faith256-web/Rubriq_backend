# # models/admin_otp.py
# from app.extensions import db
# from flask_sqlalchemy import SQLAlchemy
# from datetime import datetime, timedelta

# db = SQLAlchemy()

# class AdminOTP(db.Model):
#     __tablename__ = 'admin_otps'

#     id = db.Column(db.Integer, primary_key=True)
#     email = db.Column(db.String(120), nullable=False)
#     code = db.Column(db.String(6), nullable=False)
#     attempts = db.Column(db.Integer, default=0)
#     created_at = db.Column(db.DateTime, default=datetime.utcnow)
#     expires_at = db.Column(db.DateTime, nullable=False)

#     def is_expired(self):
#         return datetime.now() > self.expires_at

#     def max_attempts_reached(self, max_attempts=3):
#         return self.attempts >= max_attempts
