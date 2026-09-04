from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.services.cart_service import CartService # pyright: ignore[reportMissingImports]

cart_bp = Blueprint("cart", __name__, url_prefix="/api/cart")


# GET CART
@cart_bp.get("/")
@jwt_required()
def get_cart():
    user_id = int(get_jwt_identity())
    items = CartService.get_cart(user_id)

    total = sum(i.product_price * i.quantity for i in items)

    return jsonify({
        "items": [
            {
                "product_id": i.product_id,
                "name": i.product_name,
                "image": i.product_image,
                "price": i.product_price,
                "qty": i.quantity,
                "subtotal": i.product_price * i.quantity
            } for i in items
        ],
        "total": total
    })


# ADD ITEM
@cart_bp.post("/add")
@jwt_required()
def add_item():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    item = CartService.add_item(user_id, data)

    return jsonify({"message": "Item added", "id": item.id})


# UPDATE QTY
@cart_bp.put("/update")
@jwt_required()
def update_qty():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    item = CartService.update_qty(
        user_id,
        data["product_id"],
        data["quantity"]
    )

    if not item:
        return jsonify({"error": "Item not found"}), 404

    return jsonify({"message": "Quantity updated"})


# REMOVE ITEM
@cart_bp.delete("/remove/<int:product_id>")
@jwt_required()
def remove_item(product_id):
    user_id = int(get_jwt_identity())

    CartService.remove_item(user_id, product_id)

    return jsonify({"message": "Item removed"})


# CLEAR CART
@cart_bp.delete("/clear")
@jwt_required()
def clear_cart():
    user_id = int(get_jwt_identity())
    CartService.clear_cart(user_id)

    return jsonify({"message": "Cart cleared"})


# MOCK CHECKOUT
@cart_bp.post("/checkout")
@jwt_required()
def checkout():
    user_id = int(get_jwt_identity())

    CartService.clear_cart(user_id)

    return jsonify({
        "message": "Order placed successfully (mock)",
        "status": "pending_confirmation"
    })