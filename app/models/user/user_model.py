from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    phone = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    profile_image = db.Column(db.String(500), nullable=True)
    address = db.Column(db.String(255), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    is_admin = db.Column(db.Boolean, default=False)
    role = db.Column(db.String(20), default="user")
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_password(self, password_str):
        from app.extensions import bcrypt
        self.password = bcrypt.generate_password_hash(password_str).decode('utf-8')

    def check_password(self, password_str):
        from app.extensions import bcrypt
        try:
            return bcrypt.check_password_hash(self.password, password_str)
        except Exception:
            return False