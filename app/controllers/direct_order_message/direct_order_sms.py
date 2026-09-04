from flask import Blueprint, Flask, request, jsonify
from twilio.rest import Client # pyright: ignore[reportMissingImports]
from app.controllers import user
from app.models.direct_order_message.direct_order import DirectMessage,db
from flask_cors import CORS
from app.models.user.user_model import User
import os
from app.controllers.order.place_order_controller import update_monthly_order_count
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user.user_model import User
from flask_mail import Message
from app.extensions import  mail
import re


direct_order_bp = Blueprint('direct_order', __name__, url_prefix='/api/direct_order')
@direct_order_bp.route('/send-contact-sms', methods=['POST', 'OPTIONS'])
def send_contact_sms():
    if request.method == 'OPTIONS':
        return '', 200  # Respond OK to preflight request

    data = request.get_json()
    name = data.get('name')
    phone = data.get('phone')
    subject = data.get('subject')
    message_content = data.get('message')

    if not all([name, phone, subject, message_content]):
        return jsonify({'error': 'All fields are required.'}), 400

    # Validate phone number: must be exactly 10 digits
    if not re.fullmatch(r"\d{10}", phone):
        return jsonify({'error': 'Phone number must be exactly 10 digits'}), 400

    try:
        # Find or create customer
        existing_user = User.query.filter_by(phone=phone).first()
        if not existing_user:
            existing_user = User(
                name=name,
                phone=phone,
                is_admin=False,
                source="Direct Order"
            )
            db.session.add(existing_user)
            db.session.commit()

        # Save message linked to customer
        new_msg = DirectMessage(
            name=name,
            phone=phone,
            subject=subject,
            message=message_content,
            customer_id=existing_user.id
        )
        db.session.add(new_msg)
        db.session.commit()

        # For now, skip sending notifications

        return jsonify({'message': 'Message saved successfully'}), 200

    except Exception as e:
        print("Error in send_contact_sms:", e)
        return jsonify({'error': 'Failed to save message'}), 500

# @direct_order_bp.route('/send-contact-sms', methods=['POST', 'OPTIONS'])
# def send_contact_sms():
#     if request.method == 'OPTIONS':
#         return '', 200  # Respond OK to preflight request

#     data = request.get_json()
#     name = data.get('name')
#     phone = data.get('phone')
#     subject = data.get('subject')
#     message_content = data.get('message')

#     if not all([name, phone, subject, message_content]):
#         return jsonify({'error': 'All fields are required.'}), 400

#     try:
#         # Find or create customer
#         existing_user = User.query.filter_by(phone=phone).first()
#         if not existing_user:
#             existing_user = User(
#                 name=name,
#                 phone=phone,
#                 is_admin=False,
#                 source="Direct Order"
#             )
#             db.session.add(existing_user)
#             db.session.commit()

#         # Save message linked to customer
#         new_msg = DirectMessage(
#             name=name,
#             phone=phone,
#             subject=subject,
#             message=message_content,
#             customer_id=existing_user.id
#         )
#         db.session.add(new_msg)
#         db.session.commit()

#         # For now, just skip sending SMS/email notifications
#         # You can add email notification later after fixing CORS

#         return jsonify({'message': 'Message saved successfully'}), 200

#     except Exception as e:
#         print("Error in send_contact_sms:", e)
#         return jsonify({'error': 'Failed to save message'}), 500




# Direct order Mesage
@direct_order_bp.route('/all-messages', methods=['GET'])
@jwt_required()
def get_all_messages():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user or not user.is_admin:
        return jsonify({"error": "Access denied. Admins only."}), 403

    messages = DirectMessage.query.order_by(DirectMessage.id.desc()).all()

    result = [
        {
            'id': msg.id,
            'name': msg.name,
            'phone': msg.phone,
            'subject': msg.subject,
            'message': msg.message,
            'created_at': msg.created_at.strftime('%Y-%m-%d %H:%M:%S') if msg.created_at else "N/A",
            'is_delivered': msg.is_delivered,
            "is_rejected": msg.is_rejected
        }
        for msg in messages
    ]

    return jsonify(result), 200



# Unread message count
@direct_order_bp.route('/unread_messages_count', methods=['GET'])
def count_unread_messages():
    try:
        count = DirectMessage.query.filter_by(is_delivered=False, is_rejected=False).count()
        return jsonify({"count": count}), 200
    except Exception as e:
        return jsonify({"error": "Failed to count unread messages", "details": str(e)}), 500




# # Update monthly performance for messages

@direct_order_bp.route('/mark-delivered/<int:id>', methods=['PATCH'])
@jwt_required()
def mark_delivered(id):
    message = DirectMessage.query.get(id)
    if not message:
        return jsonify({'error': 'Order not found'}), 404

    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user or not user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403

    data = request.get_json()
    is_delivered = data.get('is_delivered', False)

    if not message.is_delivered and is_delivered:
        try:
            update_monthly_order_count(message.created_at, delivered=True)
        except Exception as e:
            print("Error updating monthly performance for message order:", e)

    message.is_delivered = is_delivered
    db.session.commit()
    return jsonify({'message': 'Status updated successfully'}), 200





# # Delete Message
@direct_order_bp.route('/delete-message/<int:id>', methods=['DELETE'])
def delete_message(id):
    message = DirectMessage.query.get(id)
    if not message:
        return jsonify({'error': 'Order not found'}), 404

    db.session.delete(message)
    db.session.commit()
    return jsonify({'message': 'Message deleted successfully'}), 200


# routes/direct_order.py or wherever your blueprint is defined

@direct_order_bp.route('/reject-order/<int:order_id>', methods=['PATCH'])
def reject_order(order_id):
    order = DirectMessage.query.get(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404

    data = request.get_json()
    order.is_rejected = data.get("is_rejected", False)

    db.session.commit()
    return jsonify({"message": "Order rejection updated", "order_id": order_id})





# View delivered orders
@direct_order_bp.route('/view_delivered_direct_orders', methods=['GET'])
@jwt_required()
def view_delivered_direct_orders():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user or not user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403

    try:
        delivered_orders = DirectMessage.query.filter_by(is_delivered=True).order_by(DirectMessage.created_at.desc()).all()

        results = []
        for msg in delivered_orders:
            results.append({
                'id': msg.id,
                'customer_name': msg.name,
                'phone': msg.phone,
                'subject': msg.subject,
                'message': msg.message,
                'status': 'Delivered',
                'is_rejected': msg.is_rejected,
                'created_at': msg.created_at.strftime('%Y-%m-%d %H:%M')
            })

        return jsonify(results), 200

    except Exception as e:
        return jsonify({'error': 'Failed to fetch delivered direct orders', 'details': str(e)}), 500
