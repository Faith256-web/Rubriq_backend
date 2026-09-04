from flask import Blueprint, jsonify, request
from app.models.product.product_model import Product
from app.extensions import db

product_bp = Blueprint("products", __name__)


@product_bp.route("/api/products", methods=["GET"])
@product_bp.route("/api/products/", methods=["GET"])
@product_bp.route("/products", methods=["GET"])
@product_bp.route("/products/", methods=["GET"])
def fetch_products():
    products = Product.query.all()
    return jsonify([p.to_dict() for p in products]), 200


@product_bp.route("/api/products/<int:product_id>", methods=["GET"])
@product_bp.route("/products/<int:product_id>", methods=["GET"])
def fetch_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(product.to_dict()), 200


@product_bp.route("/api/products", methods=["POST"])
@product_bp.route("/products", methods=["POST"])
def create_product():
    data = request.get_json() or {}
    name = data.get("name")
    description = data.get("description", "")
    category = data.get("category", "General")
    price = data.get("price")
    unit = data.get("unit", "per piece")
    stock = data.get("stock", 0)
    image = data.get("image", "")

    if not name or price is None:
        return jsonify({"error": "Name and price are required"}), 400

    product = Product(
        name=name,
        description=description,
        category=category,
        price=float(price),
        unit=unit,
        stock=int(stock),
        image=image
    )
    db.session.add(product)
    db.session.commit()

    return jsonify(product.to_dict()), 201


@product_bp.route("/api/products/<int:product_id>", methods=["PUT"])
@product_bp.route("/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    data = request.get_json() or {}
    if "name" in data:
        product.name = data["name"]
    if "description" in data:
        product.description = data["description"]
    if "category" in data:
        product.category = data["category"]
    if "price" in data:
        product.price = float(data["price"])
    if "unit" in data:
        product.unit = data["unit"]
    if "stock" in data:
        product.stock = int(data["stock"])
    if "image" in data:
        product.image = data["image"]

    db.session.commit()
    return jsonify(product.to_dict()), 200


@product_bp.route("/api/products/<int:product_id>", methods=["DELETE"])
@product_bp.route("/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Product deleted successfully"}), 200
