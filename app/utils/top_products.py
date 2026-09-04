# app/utils/top_products.py

import json
from collections import defaultdict
from app.models.monthly_sales.monthly_top_sales import MonthlyTopProduct
from app.models.monthly_sales.delivered_order_history import DeliveredOrderHistory
from app.extensions import db

def update_monthly_top_products(order_date):
    year = order_date.year
    month = order_date.month

    # Step 1: Filter only delivered CartOrders for that month
    delivered_orders = DeliveredOrderHistory.query.filter_by(
        order_type='CartOrder',
        status='Delivered',
        month=month,
        year=year
    ).all()

    product_counts = defaultdict(int)

    # Step 2: Parse product_snapshot and count quantities
    for order in delivered_orders:
        try:
            products = json.loads(order.product_snapshot)
            for item in products:
                name = item.get("name")
                qty = int(item.get("quantity", 0))
                if name:
                    product_counts[name] += qty
        except Exception as e:
            print(f"Error parsing snapshot for order {order.id}: {e}")

    # Step 3: Pick top 5 products
    top_five = sorted(product_counts.items(), key=lambda x: x[1], reverse=True)[:5]

    # Step 4: Delete existing record for that month
    MonthlyTopProduct.query.filter_by(month=month, year=year).delete()

    # Step 5: Save new top 5
    for name, qty in top_five:
        top = MonthlyTopProduct(
            month=month,
            year=year,
            product_name=name,
            total_quantity=qty
        )
        db.session.add(top)

    db.session.commit()
