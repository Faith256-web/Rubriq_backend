from datetime import datetime
from app.extensions import db


class DirectMessage(db.Model):
    __tablename__ = 'messages'


    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    subject = db.Column(db.String(200))
    message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.now)
    is_delivered = db.Column(db.Boolean, default=False)
    is_rejected = db.Column(db.Boolean, default=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    customer = db.relationship('User', backref='messages')