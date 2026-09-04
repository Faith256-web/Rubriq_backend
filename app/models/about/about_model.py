from app.extensions import db

class AboutContent(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(255))
    hero_description = db.Column(db.Text)

    background = db.Column(db.Text)

    mission = db.Column(db.Text)
    vision = db.Column(db.Text)
    values = db.Column(db.Text)

    image_url = db.Column(db.String(500))