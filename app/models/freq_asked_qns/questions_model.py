# models.py
from app.extensions import db
class FAQ(db.Model):

    __tablename__ = "questions"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))  # Optional heading, e.g., "Most Asked Questions"
    faqs = db.Column(db.JSON)  # List of [question, answer]
