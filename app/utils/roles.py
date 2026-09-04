# app/utils/roles.py

from flask_jwt_extended import get_jwt_identity
from functools import wraps
from flask import jsonify
from app.models.user.user_model import User

def role_required(roles):
    def wrapper(fn):
        @wraps(fn)
        def decorated(*args, **kwargs):
            user = User.query.get(get_jwt_identity())

            if not user or user.role not in roles:
                return jsonify({"error": "Access denied"}), 403

            return fn(*args, **kwargs)
        return decorated
    return wrapper