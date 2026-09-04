# from app.controllers.inquiry.inquiry_controller import create_inquiry, get_all_inquiries
from app.extensions import db
from app.models.inquiry.inquiry_model import Inquiry

def create_inquiry(data):
    inquiry = Inquiry(
        name=data["name"],
        email=data["email"],
        message=data["message"]
    )

    db.session.add(inquiry)
    db.session.commit()

    return inquiry


def get_all_inquiries():
    return Inquiry.query.order_by(Inquiry.created_at.desc()).all()