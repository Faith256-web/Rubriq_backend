from app.extensions import db
from app.models.cart.cart_model import Cart as CartItem
from app.models.product.product_model import Product

class CartService:

    @staticmethod
    def get_cart(user_id):
        return CartItem.query.filter_by(user_id=user_id).all()

    @staticmethod
    def add_item(user_id, data):
        product_id_str = str(data["product_id"])
        
        # Look up product in DB if available
        product = None
        try:
            p_id_int = int(data["product_id"])
            product = Product.query.get(p_id_int)
        except (ValueError, TypeError):
            product = Product.query.filter_by(id=data["product_id"]).first()

        name = product.name if product else data.get("name", data.get("product_name", "Product"))
        image = product.image if product else data.get("image", data.get("product_image", ""))
        price = product.price if product else data.get("price", data.get("product_price", 0.0))

        item = CartItem.query.filter_by(
            user_id=user_id,
            product_id=product_id_str
        ).first()

        if item:
            item.quantity += data.get("quantity", 1)
        else:
            item = CartItem(
                user_id=user_id,
                product_id=product_id_str,
                product_name=name,
                product_image=image,
                product_price=price,
                quantity=data.get("quantity", 1),
            )
            db.session.add(item)

        db.session.commit()
        return item

    @staticmethod
    def update_qty(user_id, product_id, qty):
        item = CartItem.query.filter_by(
            user_id=user_id,
            product_id=str(product_id)
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
            product_id=str(product_id)
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