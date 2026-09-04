from datetime import datetime
from app.extensions import db


class OrderItem(db.Model):
    __tablename__ = 'order_items'


    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=True)
    product_name = db.Column(db.String(100))  # Captured from Product.name
    image = db.Column(db.String(255))         # Captured from Product.image              
    quantity = db.Column(db.Integer)
    product_type = db.Column(db.String(20))  # 'backend' or 'hardcoded'
   

   

    


