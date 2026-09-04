from flask import Blueprint, request, jsonify
from app.models.freq_asked_qns.questions_model import FAQ, db
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user.user_model import User


# Updated URL prefix without v1
questions_bp = Blueprint('faq', __name__, url_prefix='/api/questions')

# Get the single FAQ record (assume id=1

questions_bp = Blueprint('faq', __name__, url_prefix='/api/questions')

@questions_bp.route('/get_faqs', methods=['GET'])
def get_faqs():
    faq_record = FAQ.query.get(1)
    if not faq_record:
        return jsonify({"message": "No FAQs found"}), 404

    return jsonify({
        "id": faq_record.id,
        "title": faq_record.title,
        "faqs": faq_record.faqs
    }), 200




# Update quns
@questions_bp.route('/update_faqs', methods=['PUT', 'OPTIONS'])
@jwt_required(optional=True)  # allow OPTIONS without JWT
def update_faqs():
    if request.method == 'OPTIONS':
        # Respond to preflight request with HTTP 200 OK and CORS headers
        return jsonify({}), 200

    current_user_id = get_jwt_identity()
    user = User.query.get(current_user_id)

    if not user or not user.is_admin:
        return jsonify({"message": "Admin access required"}), 403

    data = request.json
    faq_record = FAQ.query.get(1)

    if not faq_record:
        faq_record = FAQ(id=1)

    faq_record.title = data.get('title', faq_record.title)
    faqs_list = data.get('faqs')

    if not isinstance(faqs_list, list):
        return jsonify({"message": "faqs must be a list of [question, answer] pairs"}), 400

    faq_record.faqs = faqs_list

    db.session.add(faq_record)
    db.session.commit()

    return jsonify({"message": "FAQs updated successfully"}), 200
