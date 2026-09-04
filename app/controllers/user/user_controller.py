import time
from flask import Blueprint, current_app, request, jsonify
from flask_jwt_extended import create_access_token
from app.models.user.user_model import db, User
from app.extensions import bcrypt, mail
from flask_jwt_extended import create_access_token
import random
from datetime import datetime, timedelta
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.direct_order_message.direct_order import DirectMessage
from app.models.order.order_model import Order
from twilio.rest import Client
import os
from flask_mail import Message
import traceback
import re  # For checking the number of digits
from werkzeug.utils import secure_filename


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp', 'tiff'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS






#Define the blue print for user routes
user_bp = Blueprint('user', __name__, url_prefix='/api/user')
@user_bp.route('/signup', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    phone = data.get('phone')
    email = data.get('email')
    password = data.get('password')
    admin_code = data.get('admin_code', '')

    # Check for required fields
    if not name or not phone or not password or not email:
        return jsonify({'error': 'All fields are required'}), 400

    # ✅ Validate phone: must be exactly 10 digits
    if not re.fullmatch(r"\d{10}", phone):
        return jsonify({'error': 'Phone number must be exactly 10 digits'}), 400

    # Check if phone already exists
    existing_user = User.query.filter_by(phone=phone).first()
    if existing_user:
        return jsonify({'error': 'Phone number already registered'}), 409

    # Admin check
    is_admin = admin_code == "Okumu@078@078"

    # Hash password
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    user = User(
        name=name,
        phone=phone,
        email=email,
        password=hashed_password,
        is_admin=is_admin
    )

    db.session.add(user)
    db.session.commit()

    # Send welcome email
    try:
        msg = Message(
            subject="Welcome to Rubriq Africa!",
            sender=current_app.config['MAIL_USERNAME'],
            recipients=[email],
            body=f"🎉 Welcome to Rubriq Africa, {name}! Enjoy shopping with us."
        )
        mail.send(msg)
    except Exception as e:
        print("Failed to send welcome email:", e)

    return jsonify({'message': 'Registered successfully', 'is_admin': is_admin}), 201




# Inside user routes    For allowing admins to view te form for ading others
@user_bp.route('/me', methods=['GET'])
@jwt_required()
def get_current_user():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({
        "id": user.id,
        "name": user.name,
        "phone": user.phone,
        "is_admin": user.is_admin
    }), 200






# Login a user
@user_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    phone = data.get('phone')
    password = data.get('password')
    admin_code = data.get('admin_code')  # Optional field

    if not phone or not password:
        return jsonify({"error": "Phone and password are required."}), 400

    user = User.query.filter_by(phone=phone).first()

    if not user or not bcrypt.check_password_hash(user.password, password):
        return jsonify({"error": "Invalid credentials."}), 401

    # Check if user is NOT admin but provided admin code
    if not user.is_admin and admin_code:
        return jsonify({"error": "Secret code is only required for admins."}), 400

    # If user IS admin, validate the secret code
    if user.is_admin:
        ADMIN_SECRET_CODE = "Okumu@078@078"  # Ideally from environment variables
        if not admin_code:
            return jsonify({"error": "Secret code is required for admin login."}), 400
        if admin_code != ADMIN_SECRET_CODE:
            return jsonify({"error": "Invalid secret code."}), 401

    # Create access token after successful checks
    access_token = create_access_token(identity=str(user.id))

    return jsonify({
        "access_token": access_token,
        "user": {
            "id": user.id,
            "name": user.name,
            "is_admin": user.is_admin,
            "phone": user.phone
        }
    }), 200

        


# Get all Admins Only (only accessible by admins)
@user_bp.route('/get_all_admins', methods=['GET'])
@jwt_required()
def get_admins():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user or not user.is_admin:
        return jsonify({"error": "Access denied. Admins only."}), 403

    admins = User.query.filter_by(is_admin=True).all()
    return jsonify({
        "admins": [
            {
                "id": admin.id,
                "name": admin.name,
                "phone": admin.phone,
                'email': admin.email,
                "created_at": admin.created_at
            }
            for admin in admins
        ]
    }), 200








# Getting the admin profile

@user_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "id": user.id,
        "name": user.name,
        "phone": user.phone,
        "email": user.email,
        "profile_image": user.profile_image,
        "address": user.address,
        "bio": user.bio,
        "is_admin": user.is_admin,
        "created_at": user.created_at,
        "updated_at": user.updated_at
    }), 200




# Edit Profile
@user_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.form.to_dict() if request.form else request.get_json() or {}

    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')
    address = data.get('address')
    bio = data.get('bio')

    # Unique email check
    if email and User.query.filter(User.email == email, User.id != user.id).first():
        return jsonify({"error": "Email already in use"}), 400

    # Unique phone check
    if phone and User.query.filter(User.phone == phone, User.id != user.id).first():
        return jsonify({"error": "Phone number already in use"}), 400

    if name: user.name = name
    if email: user.email = email
    if phone: user.phone = phone
    if address: user.address = address
    if bio: user.bio = bio


        
    if 'profile_image' in request.files:
        file = request.files['profile_image']
        if file.filename:
            filename = secure_filename(file.filename)
            unique_filename = f"{int(time.time()*1000)}_{filename}"
            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
            os.makedirs(upload_folder, exist_ok=True)
            file.save(os.path.join(upload_folder, unique_filename))
            user.profile_image = f"/static/uploads/{unique_filename}"



    db.session.commit()
    return jsonify({"message": "Profile updated successfully"}), 200




#Verify admin password
@user_bp.route('/profile/password', methods=['PUT'])
@jwt_required()
def change_password():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()
    old_password = data.get('old_password')
    new_password = data.get('new_password')

    if not old_password or not new_password:
        return jsonify({"error": "Both old and new passwords are required"}), 400

    if not bcrypt.check_password_hash(user.password, old_password):
        return jsonify({"error": "Old password is incorrect"}), 400

    user.password = bcrypt.generate_password_hash(new_password).decode('utf-8')
    db.session.commit()

    return jsonify({"message": "Password updated successfully"}), 200




#Verify admin profile
@user_bp.route('/verify_admin_profile/<int:admin_id>', methods=['POST'])
@jwt_required()
def verify_admin_profile(admin_id):
    data = request.get_json()
    password = data.get('password')

    if not password:
        return jsonify({"error": "Password is required"}), 400

    admin = User.query.get(admin_id)
    if not admin or not admin.is_admin:
        return jsonify({"error": "Admin not found"}), 404

    if not bcrypt.check_password_hash(admin.password, password):
        return jsonify({"error": "Incorrect password"}), 401

    # Return admin profile
    return jsonify({
        "id": admin.id,
        "name": admin.name,
        "email": admin.email,
        "phone": admin.phone,
        "address": admin.address,
        "bio": admin.bio,
        "profile_image": admin.profile_image,
        "created_at": admin.created_at,
        "updated_at": admin.updated_at
    }), 200




#Get agdmin by id
@user_bp.route('/get_admin/<int:admin_id>', methods=['GET'])
def get_admin(admin_id):
    admin = User.query.get(admin_id)
    if not admin:
        return jsonify({"error": "Admin not found"}), 404

    return jsonify({
        "id": admin.id,
        "name": admin.name,
        "email": admin.email,
        "phone": admin.phone,
        "address": admin.address,
        "bio": admin.bio,
        "profile_image": admin.profile_image,
        "created_at": admin.created_at,
        "updated_at": admin.updated_at
    })





#Upload profile image
@user_bp.route('/profile_upload-image', methods=['POST'])
@jwt_required()
def profile_upload_image():
    file = request.files.get('profile_image')
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_filename = f"{int(time.time()*1000)}_{filename}"
        upload_folder = os.path.join(current_app.root_path, 'static', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        file.save(os.path.join(upload_folder, unique_filename))

        image_url = f"/static/uploads/{unique_filename}"

        # Save to current user
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if user:
            user.profile_image = image_url
            db.session.commit()

        return jsonify({"image_url": image_url}), 201

    return jsonify({"error": "Invalid image"}), 400









# # # # Get all Customers Only (only accessible by admins)

@user_bp.route('/view_all_customers', methods=['GET'])
@jwt_required()
def view_all_customers():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user or not user.is_admin:
            return jsonify({"error": "Access denied. Admins only."}), 403

        customers_dict = {}

        # 1. Registered users (Created Account)
        registered_users = User.query.filter_by(is_admin=False).all()
        for u in registered_users:
            customers_dict[u.phone] = {
                "id": u.id,
                "name": u.name,
                'email': u.email,
                "phone": u.phone,
                "joined_at": u.created_at.strftime('%Y-%m-%d %H:%M') if u.created_at else None,
                "source": "Created Account"
            }

        # 2. Cart-based orders (prefer over Created Account)
        cart_orders = Order.query.all()
        for o in cart_orders:
            phone = o.phone
            # Try to find actual user ID if they already exist
            existing_user = User.query.filter_by(phone=phone).first()
            customers_dict[phone] = {
                "id": existing_user.id if existing_user else None,
                "name": o.customer_name,
                "phone": phone,
                "joined_at": o.created_at.strftime('%Y-%m-%d %H:%M') if o.created_at else None,
                "source": "Cart Order"
            }

        # 3. Direct Orders (prefer over both)
        messages = DirectMessage.query.all()
        for m in messages:
            phone = m.phone
            existing_user = User.query.filter_by(phone=phone).first()
            customers_dict[phone] = {
                "id": existing_user.id if existing_user else None,
                "name": m.name,
                "phone": phone,
                "joined_at": m.created_at.strftime('%Y-%m-%d %H:%M') if m.created_at else None,
                "source": "Direct Order"
            }

        # Convert to list
        unique_customers = list(customers_dict.values())

        return jsonify({"customers": unique_customers}), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Failed to fetch customers", "details": str(e)}), 500





#Delete Admin
@user_bp.route('/delete_admin/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_admin(user_id):
    from flask_jwt_extended import get_jwt_identity

    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)

    if not current_user or not current_user.is_admin:
        return jsonify({'error': 'Unauthorized. Admins only.'}), 403

    admin_to_delete = User.query.get(user_id)
    if not admin_to_delete:
        return jsonify({'error': 'Admin not found.'}), 404

    if not admin_to_delete.is_admin:
        return jsonify({'error': 'This user is not an admin.'}), 400

    try:
        db.session.delete(admin_to_delete)
        db.session.commit()
        return jsonify({'message': 'Admin deleted successfully.'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete admin.'}), 500




# Flask route: Count all unique customers
@user_bp.route('/customers_count', methods=['GET'])
@jwt_required()
def customers_count():
    try:
        unique_customers = set()

        # Get all admin phones/emails for exclusion
        admin_users = User.query.filter_by(is_admin=True).all()
        admin_phones = {u.phone for u in admin_users if u.phone}
        admin_emails = {u.email for u in admin_users if u.email}

        # Users who are not admins
        users = User.query.filter_by(is_admin=False).all()
        for u in users:
            identifier = u.phone or u.email
            if identifier:
                unique_customers.add(identifier)

        # Orders
        orders = Order.query.all()
        for o in orders:
            identifier = getattr(o, 'phone', None) or getattr(o, 'email', None)
            if identifier and identifier not in admin_phones and identifier not in admin_emails:
                unique_customers.add(identifier)

        # Direct Messages
        messages = DirectMessage.query.all()
        for m in messages:
            identifier = getattr(m, 'phone', None) or getattr(m, 'email', None)
            if identifier and identifier not in admin_phones and identifier not in admin_emails:
                unique_customers.add(identifier)

        return jsonify({"count": len(unique_customers)})

    except Exception as e:
        import traceback
        print("Error in customers_count route:", e)
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500




# Deleting a customer and their related data
@user_bp.route('/delete_customer/<string:phone>', methods=['DELETE'])
@jwt_required()
def delete_customer(phone):
    from flask_jwt_extended import get_jwt_identity

    current_user_id = get_jwt_identity()
    current_user = User.query.get(current_user_id)

    if not current_user or not current_user.is_admin:
        return jsonify({'error': 'Unauthorized. Admins only.'}), 403

    try:
        deleted_any = False

        # Delete from registered users
        user = User.query.filter_by(phone=phone).first()
        if user:
            if user.is_admin:
                return jsonify({'error': 'Cannot delete another admin.'}), 400
            db.session.delete(user)
            deleted_any = True

        # Delete orders
        orders = Order.query.filter_by(phone=phone).all()
        for order in orders:
            db.session.delete(order)
            deleted_any = True

        # Delete messages
        messages = DirectMessage.query.filter_by(phone=phone).all()
        for msg in messages:
            db.session.delete(msg)
            deleted_any = True

        if deleted_any:
            db.session.commit()
            return jsonify({'message': f'Deleted customer and related data for phone {phone}'}), 200
        else:
            return jsonify({'message': f'No customer found with phone {phone}'}), 404

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'An error occurred while deleting.', 'details': str(e)}), 500
