from flask import Blueprint, request, jsonify, current_app
from app.extensions import db
from app.models.about.about_model import AboutContent
import os, time
from werkzeug.utils import secure_filename

about_bp = Blueprint('about_bp', __name__, url_prefix='/api/about')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# =========================
# GET ABOUT PAGE DATA
# =========================
@about_bp.route('/', methods=['GET'])
def get_about():
    content = AboutContent.query.first()

    if not content:
        return jsonify({
            "heroTitle": "About Us",
            "heroSubtitle": "Building Uganda sustainably, locally and with pride.",
            "background": [
                "Rubriq Africa was founded in 2025 in Mbale, Plot 6 Nsoba Lane. We are tackling Uganda's urban waste problem through recycling and sustainable engineering.",
                "In our first year we've supplied thousands of bricks and pavers across Uganda, partnering with contractors and promoting sustainable construction."
            ],
            "mission": "To reduce urban waste pollution by transforming discarded materials into durable construction products.",
            "vision": "To see a Uganda where waste becomes a valuable resource for sustainable development.",
            "values": "Quality, sustainability, and integrity in every product we make.",
            "imageUrl": None
        })

    return jsonify({
        "heroTitle": content.hero_title,
        "heroSubtitle": content.hero_subtitle,
        "background": content.background,  # store as list or JSON
        "mission": content.mission,
        "vision": content.vision,
        "values": content.values,
        "imageUrl": content.image_url
    })


# =========================
# UPDATE ABOUT PAGE
# =========================
@about_bp.route('/', methods=['PUT'])
def update_about():
    data = request.get_json()
    content = AboutContent.query.first()

    if not content:
        content = AboutContent()

    content.hero_title = data.get("heroTitle")
    content.hero_subtitle = data.get("heroSubtitle")
    content.background = data.get("background", [])
    content.mission = data.get("mission")
    content.vision = data.get("vision")
    content.values = data.get("values")
    content.image_url = data.get("imageUrl")

    db.session.add(content)
    db.session.commit()

    return jsonify({"message": "About page updated successfully"}), 200


# =========================
# IMAGE UPLOAD (optional)
# =========================
@about_bp.route('/upload-image', methods=['POST'])
def upload_image():
    image = request.files.get("image")

    if not image or not allowed_file(image.filename):
        return jsonify({"error": "Invalid image"}), 400

    filename = secure_filename(image.filename)
    unique_name = f"{int(time.time() * 1000)}_{filename}"

    upload_folder = os.path.join(current_app.root_path, "static", "uploads")
    os.makedirs(upload_folder, exist_ok=True)

    path = os.path.join(upload_folder, unique_name)
    image.save(path)

    return jsonify({
        "imageUrl": f"/static/uploads/{unique_name}"
    }), 201