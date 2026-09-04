# models.py
from datetime import datetime
from app import db

class MonthlySalesPerformance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    total_delivered_orders = db.Column(db.Integer, default=0)
    last_updated = db.Column(db.DateTime, default=datetime.now)
    rejected_orders = db.Column(db.Integer, default=0) 

    __table_args__ = (db.UniqueConstraint('year', 'month', name='unique_month_year'),)
