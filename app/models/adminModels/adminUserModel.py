# from datetime import datetime
# from app.extensions import db
# from flask_sqlalchemy import SQLAlchemy
# from datetime import datetime
# from werkzeug.security import generate_password_hash, check_password_hash


# class AdminUser(db.Model):
#     __tablename__ = 'admin_users'

#     id = db.Column(db.Integer, primary_key=True)
#     email = db.Column(db.String(120), unique=True, nullable=False)
#     password_hash = db.Column(db.String(128), nullable=False)
#     role = db.Column(db.String(20), nullable=False)  # "superadmin" or "subadmin"
#     created_at = db.Column(db.DateTime, default=datetime.now)

#     def set_password(self, password):
#         self.password_hash = generate_password_hash(password)

#     def check_password(self, password):
#         return check_password_hash(self.password_hash, password)