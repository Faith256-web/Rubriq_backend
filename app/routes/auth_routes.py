# app/routes/auth_routes.py

from flask import Blueprint, request, jsonify
from app.models.user.user_model import User
from app.models.user_otp.user_otp_model import UserOTP
from app.models.token_blocklist import TokenBlocklist
from app.models.auth_logs import AuthLog
from app.extensions import db
from flask_jwt_extended import create_access_token, jwt_required, get_jwt, get_jwt_identity
from datetime import datetime, timedelta
import random

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")

def send_otp(identifier, code, method="email"):
    if method == "email":
        try:
            from flask_mail import Message
            from app.extensions import mail
            subject = "Rubriq Africa Verification Code"
            body = f"Your verification code is {code}. It will expire in 10 minutes."
            msg = Message(subject=subject, recipients=[identifier], body=body)
            mail.send(msg)
            print(f"✅ OTP email sent to {identifier}: {code}")
            return True
        except Exception as e:
            print(f"❌ Failed to send OTP email to {identifier}: {e}")
            return False
    else: # method == "sms"
        try:
            from twilio.rest import Client
            import os
            sid = os.getenv("TWILIO_ACCOUNT_SID")
            token = os.getenv("TWILIO_AUTH_TOKEN")
            sender = os.getenv("TWILIO_PHONE_NUMBER", "+13612663978")
            if sid and token:
                client = Client(sid, token)
                client.messages.create(
                    body=f"🔐 Your Rubriq Africa verification code is: {code}. It expires in 10 minutes.",
                    from_=sender,
                    to=identifier
                )
                print(f"✅ OTP SMS sent to {identifier}: {code}")
                return True
            else:
                print(f"⚠️ Twilio credentials missing. Print OTP to console: {code}")
                return False
        except Exception as e:
            print(f"❌ Failed to send OTP SMS to {identifier}: {e}")
            return False

def is_account_locked(identifier):
    # Find all attempts for this identifier, ordered by time desc in the last 15 minutes
    fifteen_mins_ago = datetime.utcnow() - timedelta(minutes=15)
    logs = AuthLog.query.filter(
        AuthLog.attempt_identifier == identifier,
        AuthLog.time >= fifteen_mins_ago
    ).order_by(AuthLog.time.desc()).limit(5).all()
    
    if len(logs) < 5:
        return False
    # Check if all of the last 5 logs are failures
    return all(not log.is_success for log in logs)

def log_auth(user_id, identifier, is_success):
    log = AuthLog(
        user_id=user_id,
        attempt_identifier=identifier,
        is_success=is_success,
        ip=request.remote_addr,
        device=request.headers.get("User-Agent", "Unknown")
    )
    db.session.add(log)
    db.session.commit()

# REGISTER REQUEST
@auth_bp.route("/register-request", methods=["POST"])
def register_request():
    data = request.get_json() or {}
    name = data.get("name")
    email = data.get("email")
    phone = data.get("phone")
    password = data.get("password")
    method = data.get("method", "email") # "email" or "sms"

    if not name or not email or not phone or not password:
        return jsonify({"message": "Missing fields"}), 400

    # Check if verified email/phone already exists
    existing_user = User.query.filter((User.email == email) | (User.phone == phone)).first()
    if existing_user:
        if existing_user.is_verified:
            return jsonify({"message": "An account with that email or phone number already exists"}), 400
        else:
            # User exists but is not verified yet. We update their info and password.
            user = existing_user
            user.name = name
            user.email = email
            user.phone = phone
            user.set_password(password)
    else:
        # Create new unverified user
        user = User(name=name, email=email, phone=phone, is_verified=False)
        user.set_password(password)
        # First user is superadmin
        if User.query.count() == 0:
            user.role = "superadmin"
            user.is_admin = True
            user.is_verified = True # Superadmin auto-verified to avoid lockout
            db.session.add(user)
            db.session.commit()
            # Auto login superadmin
            token = create_access_token(identity=str(user.id))
            return jsonify({
                "message": "Superadmin account created successfully",
                "access_token": token,
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "phone": user.phone,
                    "role": user.role,
                    "is_admin": True
                }
            }), 201
        else:
            user.role = "user"
            user.is_admin = False
            db.session.add(user)
            db.session.commit()

    # Generate OTP
    otp_code = random.randint(100000, 999999)
    expiry = datetime.utcnow() + timedelta(minutes=10) # 10 minutes expiry

    # Save OTP record
    existing_otp = UserOTP.query.filter_by(email=email).first()
    if existing_otp:
        existing_otp.otp_code = otp_code
        existing_otp.expiry = expiry
        existing_otp.attempts = 0
    else:
        new_otp = UserOTP(email=email, otp_code=otp_code, expiry=expiry, attempts=0)
        db.session.add(new_otp)
    db.session.commit()

    # Send OTP
    target = email if method == "email" else phone
    send_otp(target, otp_code, method)

    # Return OTP for testing convenience
    return jsonify({
        "message": f"Verification code sent via {method}.",
        "otp_code": otp_code,
        "email": email,
        "phone": phone
    }), 200

# REGISTER VERIFY
@auth_bp.route("/register-verify", methods=["POST"])
def register_verify():
    data = request.get_json() or {}
    email = data.get("email")
    otp_code = data.get("otp_code")

    if not email or not otp_code:
        return jsonify({"message": "Email and OTP code are required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"message": "User not found"}), 404

    otp_record = UserOTP.query.filter_by(email=email).first()
    if not otp_record:
        return jsonify({"message": "Verification code not found. Please request a new one."}), 404

    if otp_record.attempts >= 5:
        return jsonify({"message": "Too many failed attempts. Please request a new code."}), 400

    if datetime.utcnow() > otp_record.expiry:
        return jsonify({"message": "Verification code has expired. Please request a new one."}), 400

    if str(otp_record.otp_code) != str(otp_code):
        otp_record.attempts += 1
        db.session.commit()
        return jsonify({"message": "Invalid verification code"}), 400

    # OTP is correct! Mark user as verified
    user.is_verified = True
    db.session.delete(otp_record)
    db.session.commit()

    # Create JWT
    token = create_access_token(identity=str(user.id))

    return jsonify({
        "access_token": token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "role": user.role,
            "is_admin": user.is_admin
        }
    }), 200

# LOGIN
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    identifier = data.get("email") or data.get("phone")
    password = data.get("password")
    admin_code = data.get("admin_code") # for admin login

    if not identifier or not password:
        return jsonify({"message": "Email/Phone and password are required"}), 400

    # Check lock status
    if is_account_locked(identifier):
        return jsonify({"message": "Account locked due to 5 consecutive failed login attempts. Please try again in 15 minutes."}), 403

    # Find user by email or phone
    user = User.query.filter((User.email == identifier) | (User.phone == identifier)).first()

    is_success = False
    if user and user.check_password(password):
        # Check admin secret code if they are admin
        if user.is_admin:
            ADMIN_SECRET_CODE = "Okumu@078@078"
            if not admin_code:
                log_auth(user_id=user.id, identifier=identifier, is_success=False)
                return jsonify({"message": "Secret code is required for admin login."}), 401
            if admin_code != ADMIN_SECRET_CODE:
                log_auth(user_id=user.id, identifier=identifier, is_success=False)
                return jsonify({"message": "Invalid secret code."}), 401
        
        # Check if verified (only for non-admin users or everyone? Usually user accounts need verification)
        if not user.is_verified:
            log_auth(user_id=user.id, identifier=identifier, is_success=False)
            return jsonify({"message": "Account not verified. Please verify your account first."}), 403

        is_success = True

    if not is_success:
        log_auth(user_id=user.id if user else None, identifier=identifier, is_success=False)
        return jsonify({"message": "Invalid credentials"}), 401

    # Log success
    log_auth(user_id=user.id, identifier=identifier, is_success=True)

    # Create token
    token = create_access_token(identity=str(user.id))

    return jsonify({
        "access_token": token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "role": user.role,
            "is_admin": user.is_admin
        }
    }), 200

# LOGOUT
@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]
    blocked = TokenBlocklist(jti=jti)
    db.session.add(blocked)
    db.session.commit()
    return jsonify({"message": "Logged out successfully"}), 200

# CURRENT USER PROFILE (convenience endpoint)
@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_current_user():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"message": "User not found"}), 404
    return jsonify({
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "phone": user.phone,
        "role": user.role,
        "is_admin": user.is_admin
    }), 200