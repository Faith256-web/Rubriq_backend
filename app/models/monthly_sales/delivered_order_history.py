from datetime import datetime
from app.extensions import db

class DeliveredOrderHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_type = db.Column(db.String(20))  # 'CartOrder' or 'DirectOrder'
    customer_name = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    address = db.Column(db.String(255), nullable=True)
    payment_method = db.Column(db.String(50), nullable=True)
    message = db.Column(db.Text, nullable=True)
    product_snapshot = db.Column(db.Text, nullable=True)  # Store product info as JSON string
    status = db.Column(db.String(20))  # 'Delivered'
    created_at = db.Column(db.DateTime)
    month = db.Column(db.Integer)
    year = db.Column(db.Integer)


