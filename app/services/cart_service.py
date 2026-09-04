from app.extensions import db
from app.models.cart.cart_model import Cart as CartItem
from app.models.product.product_model import Product

class CartService:

    @staticmethod
    def get_cart(user_id):
        return CartItem.query.filter_by(user_id=user_id).all()

    @staticmethod
    def add_item(user_id, data):
        # Resolve product information from DB first to be secure and support simplified request payload
        product = Product.query.get(data["product_id"])
        if not product:
            raise ValueError("Product not found")

        item = CartItem.query.filter_by(
            user_id=user_id,
            product_id=data["product_id"]
        ).first()

        if item:
            item.quantity += data.get("quantity", 1)
        else:
            item = CartItem(
                user_id=user_id,
                product_id=data["product_id"],
                product_name=product.name,
                product_image=product.image,
                product_price=product.price,
                quantity=data.get("quantity", 1),
            )
            db.session.add(item)

        db.session.commit()
        return item

    @staticmethod
    def update_qty(user_id, product_id, qty):
        item = CartItem.query.filter_by(
            user_id=user_id,
            product_id=product_id
        ).first()

        if not item:
            return None

        item.quantity = qty
        db.session.commit()
        return item

    @staticmethod
    def remove_item(user_id, product_id):
        item = CartItem.query.filter_by(
            user_id=user_id,
            product_id=product_id
        ).first()

        if item:
            db.session.delete(item)
            db.session.commit()

        return True

    @staticmethod
    def clear_cart(user_id):
        CartItem.query.filter_by(user_id=user_id).delete()
        db.session.commit()
        return True