from flask import Blueprint, request, jsonify
from app.controllers.inquiry.inquiry_controller import create_inquiry, get_all_inquiries

inquiry_bp = Blueprint("inquiry_bp", __name__, url_prefix="/api/inquiries")


@inquiry_bp.route("", methods=["POST"])
def submit_inquiry():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Missing JSON data"}), 400

    required_fields = ["name", "email", "message"]

    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({"error": f"{field} is required"}), 400

    inquiry = create_inquiry(data)

    return jsonify({
        "message": "Inquiry submitted successfully",
        "inquiry": inquiry.to_dict()
    }), 201


@inquiry_bp.route("", methods=["GET"])
def list_inquiries():
    inquiries = get_all_inquiries()
    return jsonify([i.to_dict() for i in inquiries]), 200