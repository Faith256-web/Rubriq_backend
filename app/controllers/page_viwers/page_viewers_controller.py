from flask import Blueprint, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from app.models.page_views.page_viewers_model import PageView, db


view_bp = Blueprint('view_bp', __name__, url_prefix='/api/views')



@view_bp.route('/add_viewer', methods=['POST'])
def add_view():
    new_view = PageView()
    db.session.add(new_view)
    db.session.commit()
    return jsonify({'message': 'View recorded'}), 201




#Get all page viewers
@view_bp.route('/get_all_viewers_total', methods=['GET'])
def total_views():
    count = PageView.query.count()
    return jsonify({'total_views': count}), 200