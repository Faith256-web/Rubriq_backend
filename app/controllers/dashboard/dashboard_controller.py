from flask import Blueprint, jsonify, request
from app.models.user.user_model import User
from app.models.auth_logs import AuthLog
from app.models.product.product_model import Product
from app.extensions import db
from flask_jwt_extended import jwt_required, get_jwt_identity

dashboard_bp = Blueprint('dashboard_routes', __name__, url_prefix='/api/dashboard')


@dashboard_bp.route('/', methods=['GET'])
@jwt_required()
def admin_dashboard():
    user_id = int(get_jwt_identity())
    current_user = User.query.get(user_id)

    if not current_user or current_user.role not in ["admin", "superadmin"]:
        return jsonify({'error': 'Admins only'}), 403

    total_products = Product.query.count()

    total_stock = sum(
        p.stock or 0 for p in Product.query.all()
    )

    total_users = User.query.count()
    total_logs = AuthLog.query.count()

    return jsonify({
        # USER INFO (for header)
        "user": {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email,
            "role": current_user.role
        },

        # DASHBOARD STATS
        "stats": {
            "products": total_products,
            "stock": total_stock,
            "users": total_users,
            "logs": total_logs
        }
    }), 200


@dashboard_bp.route('/users', methods=['GET'])
@jwt_required()
def list_users():
    user_id = int(get_jwt_identity())
    current_user = User.query.get(user_id)

    if not current_user or current_user.role not in ["admin", "superadmin"]:
        return jsonify({'error': 'Admins only'}), 403

    users = User.query.all()
    return jsonify([{
        "id": u.id,
        "name": u.name,
        "email": u.email,
        "phone": u.phone,
        "role": u.role,
        "is_verified": u.is_verified,
        "created_at": u.created_at.isoformat()
    } for u in users]), 200


@dashboard_bp.route('/users/<int:u_id>/toggle-role', methods=['PUT'])
@jwt_required()
def toggle_user_role(u_id):
    user_id = int(get_jwt_identity())
    current_user = User.query.get(user_id)

    if not current_user or current_user.role != "superadmin":
        return jsonify({'error': 'Superadmins only can modify roles'}), 403

    user = User.query.get(u_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    if user.id == current_user.id:
        return jsonify({'error': 'You cannot change your own role'}), 400

    # Toggle role
    user.role = "admin" if user.role == "user" else "user"
    user.is_admin = (user.role == "admin")
    db.session.commit()

    return jsonify({
        "message": f"User {user.name} role changed to {user.role}",
        "role": user.role
    }), 200


@dashboard_bp.route('/users/<int:u_id>/toggle-status', methods=['PUT'])
@jwt_required()
def toggle_user_status(u_id):
    user_id = int(get_jwt_identity())
    current_user = User.query.get(user_id)

    if not current_user or current_user.role not in ["admin", "superadmin"]:
        return jsonify({'error': 'Admins only'}), 403

    user = User.query.get(u_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    if user.id == current_user.id:
        return jsonify({'error': 'You cannot lock your own account'}), 400

    # Toggle verification / status
    user.is_verified = not user.is_verified
    db.session.commit()

    action = "unlocked" if user.is_verified else "locked / disabled"
    return jsonify({
        "message": f"User {user.name} has been {action}",
        "is_verified": user.is_verified
    }), 200


@dashboard_bp.route('/users/<int:u_id>', methods=['DELETE'])
@jwt_required()
def delete_user(u_id):
    user_id = int(get_jwt_identity())
    current_user = User.query.get(user_id)

    if not current_user or current_user.role != "superadmin":
        return jsonify({'error': 'Superadmins only'}), 403

    user = User.query.get(u_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    if user.id == current_user.id:
        return jsonify({'error': 'You cannot delete yourself'}), 400

    # Delete all associated cart items and messages to avoid integrity constraints
    from app.models.cart.cart_model import Cart
    from app.models.chat.chat_message import ChatMessage
    Cart.query.filter_by(user_id=u_id).delete()
    ChatMessage.query.filter((ChatMessage.sender_id == str(u_id)) | (ChatMessage.recipient_id == str(u_id))).delete()
    AuthLog.query.filter_by(user_id=u_id).delete()

    db.session.delete(user)
    db.session.commit()

    return jsonify({"message": f"User {user.name} has been deleted"}), 200


@dashboard_bp.route('/logs', methods=['GET'])
@jwt_required()
def list_logs():
    user_id = int(get_jwt_identity())
    current_user = User.query.get(user_id)

    if not current_user or current_user.role not in ["admin", "superadmin"]:
        return jsonify({'error': 'Admins only'}), 403

    logs = AuthLog.query.order_by(AuthLog.time.desc()).limit(100).all()
    return jsonify([{
        "id": log.id,
        "user_id": log.user_id,
        "attempt_identifier": log.attempt_identifier,
        "ip": log.ip,
        "device": log.device,
        "is_success": log.is_success,
        "time": log.time.isoformat()
    } for log in logs]), 200