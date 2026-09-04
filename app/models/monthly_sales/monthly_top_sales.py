# app/models/monthly_top_products.py

from app.extensions import db

class MonthlyTopProduct(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    product_name = db.Column(db.String(255), nullable=False)
    total_quantity = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            'year': self.year,
            'month': self.month,
            'product_name': self.product_name,
            'total_quantity': self.total_quantity
        }
