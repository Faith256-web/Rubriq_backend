from app.extensions import db

class CartItem(db.Model):
    __tablename__ = "cart_items"

    id = db.Column(db.Integer, primary_key=True)

    cart_id = db.Column(db.Integer, db.ForeignKey("carts.id"))
    product_id = db.Column(db.Integer, db.ForeignKey("products.id"))

    quantity = db.Column(db.Integer, default=1)