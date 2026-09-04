from app.extensions import db
from datetime import datetime


class PageView(db.Model):

    __tablename__ = 'pageViewers'


    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
