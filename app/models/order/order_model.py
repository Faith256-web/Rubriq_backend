from datetime import datetime
from app.extensions import db


class Order(db.Model):
    __tablename__ = 'orders'


    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    street_number = db.Column(db.String(50))
    payment_method = db.Column(db.String(50))
    message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)
    order_items = db.relationship('OrderItem', backref='orders', cascade="all, delete", lazy=True)
    payment_method = db.Column(db.String(50))
    order_status = db.Column(db.String(20), default='pending')  # example default status
    is_rejected = db.Column(db.Boolean, default=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    customer = db.relationship('User', backref='orders')
    






    