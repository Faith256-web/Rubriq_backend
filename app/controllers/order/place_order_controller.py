

from collections import defaultdict
from tkinter import messagebox
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask_mail import Message
from sqlalchemy import extract, func
from app.controllers import user
from app.models.order_item.order_item_model import OrderItem
from app.models.order.order_model import Order
from app.models.direct_order_message.direct_order import DirectMessage
from app.models.user.user_model import User
from app.models.monthly_sales.delivered_order_history import DeliveredOrderHistory
from app.models.product.product_model import Product
from app.extensions import db,mail
from datetime import datetime, date
import calendar
import json

# Monthly Sales Summary
from collections import defaultdict
from sqlalchemy import extract, func
from app.utils.top_products import update_monthly_top_products  #  Import here
from app.utils.top_products import update_monthly_top_products
import os
from twilio.rest import Client
from app.models.monthly_sales.monthly_sales import MonthlySalesPerformance
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart



place_order_bp = Blueprint('order_placed', __name__, url_prefix='/api/orders')

@place_order_bp.route('/place-order', methods=['POST'])
def place_order():
    data = request.get_json()
    customer = data.get('customerInfo', {})
    items = data.get('items', [])

    if not items:
        return jsonify({"error": "No items provided"}), 400

    try:
        # Step 1: Find or Create Customer
        existing_user = User.query.filter_by(phone=customer['phone']).first()
        if not existing_user:
            existing_user = User(
                name=customer['name'],
                phone=customer['phone'],
                is_admin=False,
                source="Cart Order"
            )
            db.session.add(existing_user)
            db.session.commit()

        # Step 2: Save the Order and link to customer
        order = Order(
            customer_name=customer['name'],
            phone=customer['phone'],
            address=customer['address'],
            street_number=customer['streetNumber'],
            payment_method=customer['paymentMethod'],
            message=customer.get('message', ''),
            order_status='Pending',
            customer_id=existing_user.id
        )
        db.session.add(order)
        db.session.commit()

        # Step 3: Save all order items
        for item in items:
            product_type = item.get('type', 'hardcoded')

            if product_type == 'backend':
                product_id = item.get('productId')
                product = None
                if product_id:  # Only query if ID exists
                    product = Product.query.filter_by(id=product_id).first()

                order_item = OrderItem(
                    order_id=order.id,
                    product_id=product.id if product else None,
                    product_name=product.name if product else item['name'],
                    image=product.image if product else item.get('image'),
                    quantity=item['quantity'],
                    product_type='backend'
                )
            else:
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=None,
                    product_name=item['name'],
                    image=item.get('image'),
                    quantity=item['quantity'],
                    product_type='hardcoded'
                )

            db.session.add(order_item)

        db.session.commit()

        # Step 4: Prepare email body
        product_summary = "\n".join([
            f" {item['name']} x {item['quantity']}" for item in items
        ])

        notification_body = f"""
                                📥 NEW CART ORDER PLACED:

                                👤 Name: {customer['name']}
                                📞 Phone: {customer['phone']}
                                🏠 Address: {customer['address']}, Street: {customer['streetNumber']}
                                💳 Payment: {customer['paymentMethod']}
                                📦 Products:
                                {product_summary}
                                📝 Message: {customer.get('message', '')}
                                """

        # Step 5: Send Email to admin
        admin_email = os.getenv('ADMIN_EMAIL')
        subject = "New Order Placed"

        msg = Message(subject=subject, recipients=[admin_email], body=notification_body.strip())
        mail.send(msg)

        return jsonify({'message': 'Order placed and email sent successfully'}), 200
    

    except Exception as e:
        db.session.rollback()
        print("Email send error:", e)
        return jsonify({
            'message': 'Order saved, but failed to send email notification.',
            'error': str(e)
        }), 207



 # Update order status
@place_order_bp.route('/update_order_status/<int:order_id>', methods=['PUT'])
@jwt_required()
def update_order_status(order_id):
  

    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user or not user.is_admin:
        return jsonify({"error": "Admin access required"}), 403

    order = Order.query.get(order_id)

    try:
        if order:
            if order.order_status != 'Delivered':
                order.order_status = 'Delivered'
                archive_delivered_order(order, is_cart_order=True)
                update_monthly_order_count(order.created_at, delivered=True)


                # Track top 5 for CartOrders only
                update_monthly_top_products(order.created_at)

            else:
                order.order_status = 'Pending'

            db.session.commit()
            return jsonify({"message": f"Cart Order status updated to {order.order_status}"}), 200

        else:
            message = DirectMessage.query.get(order_id)
            if not message:
                return jsonify({"error": "Order not found"}), 404

            if not message.is_delivered:
                message.is_delivered = True
                archive_delivered_order(message, is_cart_order=False)
                update_monthly_order_count(message.created_at, delivered=True)
           
            else:
                message.is_delivered = False

            db.session.commit()
            return jsonify({"message": f"Direct Order status updated to {'Delivered' if message.is_delivered else 'Pending'}"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to update order status", "details": str(e)}), 500



# Get all orders ever made
@place_order_bp.route('/view_all_orders', methods=['GET'])
@jwt_required()
def view_all_orders():
    try:
        orders = Order.query.order_by(Order.created_at.desc()).all()

        result = []
        for order in orders:
            order_data = {
                "order_id": order.id,
                "customer_name": order.customer_name,
                "phone": order.phone,
                "address": order.address,
                "street_number": order.street_number,
                "payment_method": order.payment_method,
                "message": order.message,
                "status": order.order_status,
                "created_at": order.created_at.strftime('%Y-%m-%d %H:%M'),
                "is_rejected": order.is_rejected,
                "items": []
            }

            for item in order.order_items:
                product = Product.query.get(item.product_id)
                item_data = {
                    "product_name": item.product_name,
                    "quantity": item.quantity,
                    "image": item.image or (product.image_url if product else None)
                }
                order_data["items"].append(item_data)

            result.append(order_data)

        return jsonify({"orders": result}), 200

    except Exception as e:
        return jsonify({"error": "Failed to fetch orders", "details": str(e)}), 500




# All delivered Orders

@place_order_bp.route('/view_all_delivered_orders', methods=['GET'])
@jwt_required()
def view_all_delivered_orders():
    try:
        current_user = User.query.get(get_jwt_identity())
        if not current_user or not current_user.is_admin:
            return jsonify({"error": "Unauthorized"}), 403

        #  1. Get delivered cart orders
        cart_orders = Order.query.filter_by(order_status='Delivered').all()
        cart_results = []
        for order in cart_orders:
            cart_results.append({
                "type": "CartOrder",
                "id": order.id,
                "customer_name": order.customer_name,
                "phone": order.phone,
                "address": order.address,
                "payment_method": order.payment_method,
                "message": order.message,
                "status": order.order_status,
                "created_at": order.created_at.strftime("%Y-%m-%d %H:%M"),
                "items": [
                    {
                        "product_name": item.product_name,
                        "quantity": item.quantity,
                        "image": item.image  # make sure this is the correct field name
                    }
                    for item in order.order_items
                ]
            })

        # 2. Get delivered direct orders
        direct_orders = DirectMessage.query.filter_by(is_delivered=True).all()
        direct_results = []
        for order in direct_orders:
            direct_results.append({
                "type": "DirectOrder",
                "id": order.id,
                "customer_name": order.name,
                "phone": order.phone,
                "location": order.subject,
                "product_name": order.message,  # or split message content if needed
                "quantity": "N/A",  # Assuming not available in Message model
                "status": "Delivered",
                "created_at": order.created_at.strftime("%Y-%m-%d %H:%M"),
            })

        combined_results = cart_results + direct_results

        sorted_results = sorted(combined_results, key=lambda x: x['created_at'], reverse=True)

        return jsonify(sorted_results), 200

    except Exception as e:
        return jsonify({"error": "Failed to fetch delivered orders", "details": str(e)}), 500





# Archive delivered order
@place_order_bp.route('/archive_delivered_order', methods=['GET'])
@jwt_required()
def archive_delivered_order(order, is_cart_order=True):
    if is_cart_order:
        product_snapshot = json.dumps([
            {
                "product_name": item.product_name,
                "quantity": item.quantity,
                "image": item.image
            } for item in order.order_items
        ])
        archived = DeliveredOrderHistory(
            order_type="CartOrder",
            customer_name=order.customer_name,
            phone=order.phone,
            address=order.address,
            payment_method=order.payment_method,
            message=order.message,
            product_snapshot=product_snapshot,
            status='Delivered',
            created_at=order.created_at,
            month=order.created_at.month,
            year=order.created_at.year
        )
    else:
        archived = DeliveredOrderHistory(
            order_type="DirectOrder",
            customer_name=order.name,
            phone=order.phone,
            address=order.subject,
            payment_method=None,
            message=order.message,
            product_snapshot=None,
            status='Delivered',
            created_at=order.created_at,
            month=order.created_at.month,
            year=order.created_at.year
        )

    db.session.add(archived)



# Clear delivered Orders after download
@place_order_bp.route('/clear_delivered_orders', methods=['DELETE'])
@jwt_required()
def clear_delivered_orders():
    try:
        # 1. Get all delivered cart orders
        delivered_cart_orders = Order.query.filter_by(order_status='Delivered').all()
        for order in delivered_cart_orders:
            archive_delivered_order(order, is_cart_order=True)
            db.session.delete(order)

        # 2. Get all delivered direct orders
        delivered_direct_orders = DirectMessage.query.filter_by(is_delivered=True).all()
        for message in delivered_direct_orders:
            archive_delivered_order(message, is_cart_order=False)
            db.session.delete(message)

        db.session.commit()
        return jsonify({"message": "Delivered orders cleared and archived."}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Failed to clear orders.", "details": str(e)}), 500
    


# Count  undelivered cart orders
@place_order_bp.route('/undelivered_count', methods=['GET'])
@jwt_required()
def count_undelivered_orders():
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        if not user or not user.is_admin:
            return jsonify({"error": "Access denied. Admins only."}), 403

        # ✅ Only count orders with status "Pending"
        pending_count = Order.query.filter_by(order_status='Pending').count()

        return jsonify({"count": pending_count}), 200

    except Exception as e:
        return jsonify({"error": "Failed to fetch undelivered order count", "details": str(e)}), 500




# Reject Cart Order
@place_order_bp.route('/reject_order/<int:order_id>', methods=['PUT'])
@jwt_required()
def reject_order(order_id):
    order = Order.query.get(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404

    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user or not user.is_admin:
        return jsonify({"error": "Admin access only"}), 403

    data = request.get_json()
    order.is_rejected = data.get("is_rejected", False)

    # If marked as rejected, update status and monthly performance
    if order.is_rejected:
        order.order_status = "Rejected"
       
        update_monthly_order_count(order.created_at, rejected=True)

    db.session.commit()
    return jsonify({"message": "Order rejection status updated."})


# @place_order_bp.route('/reject_order/<int:order_id>', methods=['PUT'])
# @jwt_required()
# def reject_order(order_id):
#     order = Order.query.get(order_id)
#     if not order:
#         return jsonify({"error": "Order not found"}), 404

#     data = request.get_json()
#     order.is_rejected = data.get("is_rejected", False)
#     db.session.commit()
#     return jsonify({"message": "Order rejection status updated."})






# Delete order
@place_order_bp.route('/delete_order/<int:order_id>', methods=['DELETE'])
@jwt_required()
def delete_order(order_id):
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user or not user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403

    try:
        order = Order.query.get(order_id)
        if not order:
            return jsonify({'error': 'Order not found'}), 404

        for item in order.order_items:
            db.session.delete(item)

        db.session.delete(order)
        db.session.commit()

        return jsonify({'message': f'Order {order_id} deleted successfully.'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Failed to delete order', 'details': str(e)}), 500




#Getting monthly sales summary
from collections import defaultdict
import calendar
from datetime import datetime
from sqlalchemy import extract, func

@place_order_bp.route('/monthly_sales_summary', methods=['GET'])
@jwt_required()
def monthly_sales_summary():
    try:
        current_year = datetime.now().year

        # ✅ Live delivered cart orders (in Order table)
        live_cart = db.session.query(
            extract('month', Order.created_at).label('month'),
            func.count(Order.id).label('delivered')
        ).filter(
            Order.order_status == 'Delivered',
            extract('year', Order.created_at) == current_year
        ).group_by('month').all()

        #  Delivered direct orders (in Message table)
        direct_delivered = db.session.query(
            extract('month', DirectMessage.created_at).label('month'),
            func.count(DirectMessage.id).label('delivered')
        ).filter(
            DirectMessage.is_delivered == True,
            extract('year', DirectMessage.created_at) == current_year
        ).group_by('month').all()

        #  Archived delivered orders (from history table)
        archived_delivered = db.session.query(
            DeliveredOrderHistory.month,
            func.count(DeliveredOrderHistory.id).label('delivered')
        ).filter(
            DeliveredOrderHistory.year == current_year,
            DeliveredOrderHistory.status == 'Delivered'
        ).group_by(DeliveredOrderHistory.month).all()

        #  Rejected direct orders (from Message table)
        rejected_direct = db.session.query(
            extract('month', DirectMessage.created_at).label('month'),
            func.count(DirectMessage.id).label('rejected')
        ).filter(
            DirectMessage.is_rejected == True,
            extract('year', DirectMessage.created_at) == current_year
        ).group_by('month').all()

        #  Rejected cart orders (from Order table)
        rejected_cart = db.session.query(
            extract('month', Order.created_at).label('month'),
            func.count(Order.id).label('rejected')
        ).filter(
            Order.order_status == 'Rejected',
            extract('year', Order.created_at) == current_year
        ).group_by('month').all()

        #  Combine all into dictionaries
        delivered_dict = defaultdict(int)
        for row in live_cart:
            delivered_dict[int(row.month)] += row.delivered
        for row in direct_delivered:
            delivered_dict[int(row.month)] += row.delivered
        for row in archived_delivered:
            delivered_dict[int(row.month)] += row.delivered

        rejected_dict = defaultdict(int)
        for row in rejected_cart:
            rejected_dict[int(row.month)] += row.rejected
        for row in rejected_direct:
            rejected_dict[int(row.month)] += row.rejected

        #  Build final monthly summary
        result = []
        for m in range(1, 13):
            result.append({
                'month': m,
                'month_name': calendar.month_name[m],
                'total_delivered_orders': delivered_dict[m],
                'rejected_orders': rejected_dict[m]
            })

        return jsonify(result), 200

    except Exception as e:
        return jsonify({"error": "Failed to fetch monthly sales summary", "details": str(e)}), 500




# Update monthly orders
def update_monthly_order_count(order_date, delivered=False, rejected=False):
    year = order_date.year
    month = order_date.month

    record = MonthlySalesPerformance.query.filter_by(year=year, month=month).first()
    if not record:
        record = MonthlySalesPerformance(
            year=year,
            month=month,
            total_delivered_orders=0,
            rejected_orders=0
        )
        db.session.add(record)

    # Ensure no None values before incrementing
    if record.total_delivered_orders is None:
        record.total_delivered_orders = 0
    if record.rejected_orders is None:
        record.rejected_orders = 0

    if delivered:
        record.total_delivered_orders += 1
    if rejected:
        record.rejected_orders += 1

    record.last_updated = datetime.now()
    db.session.commit()




#  route to clear history on Jan 1st (use cronjob or admin button)
@place_order_bp.route('/reset_yearly_sales_data', methods=['DELETE'])
@jwt_required()
def reset_yearly_sales():
    if datetime.now().month == 1:
        DeliveredOrderHistory.query.delete()
        db.session.commit()
        return jsonify({"message": "Yearly sales data reset."}), 200
    else:
        return jsonify({"message": "Can only reset in January."}), 403





# Route for most ordered items 
@place_order_bp.route('/most-bought-items', methods=['GET'])
@jwt_required()
def most_bought_items():
    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)
    if not user or not user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403

    try:
        from sqlalchemy import extract, func
        from collections import defaultdict

        order_items = db.session.query(
            OrderItem.product_name,
            func.sum(OrderItem.quantity).label('total_quantity'),
            extract('month', Order.created_at).label('month'),   # 👈 Corrected this line
            extract('year', Order.created_at).label('year')       # 👈 Corrected this too
        ).join(Order).filter(Order.order_status == 'Delivered') \
         .group_by(OrderItem.product_name, extract('month', Order.created_at), extract('year', Order.created_at)) \
         .order_by(extract('year', Order.created_at), extract('month', Order.created_at)).all()

        data = []
        for row in order_items:
            data.append({
                'product_name': row.product_name,
                'month': int(row.month),
                'year': int(row.year),
                'total_quantity': int(row.total_quantity)
            })

        return jsonify(data), 200

    except Exception as e:
        print("Error generating most bought items data:", str(e))
        return jsonify({"error": "Failed to generate item sales data"}), 500




