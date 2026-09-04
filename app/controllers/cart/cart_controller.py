from app.extensions import db
from app.models.cart.cart_model import Cart
from flask import Blueprint

cart_bp = Blueprint('cart', __name__)

@cart_bp.route('/cart')
def get_cart():
    return {"message": "Cart route works"}

@cart_bp.route('/cart/<int:cart_id>/items', methods=['POST'])
def add_to_cart(cart_id, product_id, quantity=1):
    item = Cart.query.filter_by(cart_id=cart_id, product_id=product_id).first()

    if item:
        item.quantity += quantity
    else:
        item = Cart(cart_id=cart_id, product_id=product_id, quantity=quantity)
        db.session.add(item)

    db.session.commit()
    return item