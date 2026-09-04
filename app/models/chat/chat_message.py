from app.extensions import db
from datetime import datetime

class ChatMessage(db.Model):
    __tablename__ = "chat_messages"

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.String(100), nullable=False) # Can be user_id (stringified) or "guest_<session_id>" or "admin"
    recipient_id = db.Column(db.String(100), nullable=False) # "admin", user_id, or "guest_<session_id>"
    sender_name = db.Column(db.String(120), nullable=False, default="Guest")
    message = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {
            "id": self.id,
            "sender_id": self.sender_id,
            "recipient_id": self.recipient_id,
            "sender_name": self.sender_name,
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "is_read": self.is_read
        }
