# # app/routes/analytics.py
# from flask import Blueprint, jsonify
# from app.models.monthly_sales.monthly_top_sales import MonthlyTopProduct

# analytics_bp = Blueprint('analytics_bp', __name__, url_prefix='/api/orders')

# @analytics_bp.route('/most-bought-items', methods=['GET'])
# def most_bought_items():
#     records = MonthlyTopProduct.query.all()
#     return jsonify([r.to_dict() for r in records])
