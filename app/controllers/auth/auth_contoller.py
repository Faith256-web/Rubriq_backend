from flask import jsonify
from app.services.auth_service import handle_logout # pyright: ignore[reportMissingImports]


def logout_user():
    handle_logout()
    return jsonify({
        "success": True,
        "message": "Logged out successfully"
    }), 200