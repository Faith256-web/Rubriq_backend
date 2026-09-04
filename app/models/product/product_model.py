from app.extensions import db

class Product(db.Model):
    __tablename__ = "products"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # Bricks, Pavers, Blocks
    price = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(50))  # e.g. "per piece", "per m²"
    stock = db.Column(db.Integer, default=0)
    image = db.Column(db.String(255))  # image URL or filename

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "price": self.price,
            "unit": self.unit,
            "stock": self.stock,
            "image": self.image
        }