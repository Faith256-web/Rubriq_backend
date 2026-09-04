from flask import Blueprint, request, jsonify
from app.models.contact_info.contact_info_model import ContactInfo
from app.extensions import db

contact_bp = Blueprint('contact_bp', __name__, url_prefix='/api/contact')

@contact_bp.route('/', methods=['GET'])
def get_contact_info():
    contact = ContactInfo.query.first()

    if not contact:
        return jsonify({
            "title": "Get in touch",
            "subtitle": "Tell us about your project needs bricks, pavers, blocks or anything in between.",
            "cards": [
                {
                    "type": "visit",
                    "label": "Visit us",
                    "value": "Plot 6 Nsoba Lane, Mbale, Uganda"
                },
                {
                    "type": "phone",
                    "label": "Call us",
                    "value": "+256 704363651"
                },
                {
                    "type": "email",
                    "label": "Email us",
                    "value": "info@rubriq.africa"
                }
            ],
            "socials": {
                "facebook": "",
                "instagram": "",
                "twitter": "",
                "linkedin": ""
            }
        })

    return jsonify({
        "title": "Get in touch",
        "subtitle": "Tell us about your project needs bricks, pavers, blocks or anything in between.",
        "cards": [
            {
                "type": "visit",
                "label": "Visit us",
                "value": contact.location
            },
            {
                "type": "phone",
                "label": "Call us",
                "value": contact.phone
            },
            {
                "type": "email",
                "label": "Email us",
                "value": contact.email
            }
        ],
        "socials": {
            "facebook": contact.facebook,
            "instagram": contact.instagram,
            "twitter": contact.twitter,
            "linkedin": contact.linkedin
        }
    }), 200


# =========================
# UPDATE CONTACT INFO
# =========================
@contact_bp.route('/', methods=['PUT'])
def update_contact_info():
    data = request.get_json()
    contact = ContactInfo.query.first()

    if not contact:
        contact = ContactInfo()

    contact.phone = data.get("phone", contact.phone)
    contact.email = data.get("email", contact.email)
    contact.location = data.get("location", contact.location)

    contact.facebook = data.get("facebook", contact.facebook)
    contact.instagram = data.get("instagram", contact.instagram)
    contact.twitter = data.get("twitter", contact.twitter)
    contact.linkedin = data.get("linkedin", contact.linkedin)

    db.session.add(contact)
    db.session.commit()

    return jsonify({"message": "Contact info updated successfully"}), 200