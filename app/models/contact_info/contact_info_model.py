from app.extensions import db
from sqlalchemy.dialects.postgresql import JSON # pyright: ignore[reportMissingImports]

class ContactInfo(db.Model):
    __tablename__ = "contact_info"

    id = db.Column(db.Integer, primary_key=True)

    phone = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    location = db.Column(db.String(255), nullable=True)

    # Store all socials in one place (cleaner)
    socials = db.Column(JSON, nullable=True)

    def __repr__(self):
        return f"<ContactInfo {self.email}>"