from flask import request, jsonify, Blueprint
from app.extensions import db, bcrypt,mail
from app.models.user.user_model import User
from app.models.user_otp.user_otp_model import UserOTP
from app.utils.sms import send_reset_sms
from datetime import datetime, timedelta
import random
from flask_mail import Message
import random
from datetime import datetime, timedelta
from flask_bcrypt import generate_password_hash


otp_bp = Blueprint('user_otp', __name__, url_prefix='/api/user_otp')


# 1. Request OTP
@otp_bp.route('/request-password-reset', methods=['POST'])
def request_otp():
    data = request.get_json()
    email = data.get('email')
    phone = data.get('phone')
    if not (email or phone):
        return jsonify({"error": "Email or phone required"}), 400

    user = None
    if email:
        user = User.query.filter_by(email=email).first()
    elif phone:
        user = User.query.filter_by(phone=phone).first()

    if not user:
        return jsonify({"error": "User not found"}), 404

    otp_code = random.randint(100000, 999999)
    expiry = datetime.now() + timedelta(minutes=2)

    existing_otp = UserOTP.query.filter_by(email=user.email).first()
    if existing_otp:
        existing_otp.otp_code = otp_code
        existing_otp.expiry = expiry
        existing_otp.attempts = 0
    else:
        new_otp = UserOTP(email=user.email, otp_code=otp_code, expiry=expiry, attempts=0)
        db.session.add(new_otp)
    db.session.commit()

    # Send OTP email only
    subject = "Your Password Reset Code"
    body = f"Your OTP for password reset is: {otp_code}. It expires in 2 minutes."
    msg = Message(subject=subject, recipients=[user.email], body=body)
    mail.send(msg)

    return jsonify({"message": "OTP sent to email"}), 200


# 2. Verify OTP
@otp_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    data = request.get_json()
    email = data.get('email')
    phone = data.get('phone')
    otp_code = data.get('otp_code')

    if not otp_code or not (email or phone):
        return jsonify({"error": "Email/phone and OTP are required"}), 400

    user = None
    if email:
        user = User.query.filter_by(email=email).first()
    elif phone:
        user = User.query.filter_by(phone=phone).first()

    if not user:
        return jsonify({"error": "User not found"}), 404

    otp_record = UserOTP.query.filter_by(email=user.email).first()
    if not otp_record:
        return jsonify({"error": "OTP not found. Request a new one."}), 404

    if otp_record.attempts >= 3:
        return jsonify({"error": "Max OTP attempts reached. Request a new one."}), 403

    if datetime.now() > otp_record.expiry:
        return jsonify({"error": "OTP expired. Request a new one."}), 400

    if str(otp_record.otp_code) != str(otp_code):
        otp_record.attempts += 1
        db.session.commit()
        return jsonify({"error": "Invalid OTP"}), 400

    return jsonify({"message": "OTP verified"}), 200


# 3. Reset Password
@otp_bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json()
    email = data.get('email')
    phone = data.get('phone')
    new_password = data.get('new_password')
    confirm_password = data.get('confirm_password')

    if not new_password or not confirm_password or new_password != confirm_password:
        return jsonify({"error": "Passwords do not match or missing"}), 400

    user = None
    if email:
        user = User.query.filter_by(email=email).first()
    elif phone:
        user = User.query.filter_by(phone=phone).first()

    if not user:
        return jsonify({"error": "User not found"}), 404

    hashed_password = generate_password_hash(new_password).decode('utf-8')
    user.password = hashed_password

    # Delete OTP after reset
    otp_record = UserOTP.query.filter_by(email=user.email).first()
    if otp_record:
        db.session.delete(otp_record)

    db.session.commit()

    return jsonify({"message": "Password reset successful"}), 200