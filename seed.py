import os
from app import create_app, db
from app.models.product.product_model import Product
from app.models.user.user_model import User
from app.extensions import bcrypt

app = create_app()
with app.app_context():
    # Ensure all tables are created
    db.create_all()
    
    # Clear existing users and products
    User.query.delete()
    Product.query.delete()

    superadmin_email = os.getenv("SUPERADMIN_EMAIL", "faithmercy256@gmail.com")
    superadmin_phone = os.getenv("SUPERADMIN_PHONE", "0762823503")
    superadmin_pass = os.getenv("SUPERADMIN_PASSWORD", "Tibagonzeka01")

    admin_email = os.getenv("ADMIN_EMAIL", "info@rubriqafrica.com")
    admin_phone = os.getenv("ADMIN_PHONE", "0700000002")
    admin_pass = os.getenv("ADMIN_PASSWORD", "@Rubriq2026")

    # Seed Admin Users
    superadmin = User(
        name="Super Admin",
        email=superadmin_email,
        phone=superadmin_phone,
        password=bcrypt.generate_password_hash(superadmin_pass).decode("utf-8"),
        is_admin=True,
        role="superadmin",
        is_verified=True
    )
    admin = User(
        name="Admin User",
        email=admin_email,
        phone=admin_phone,
        password=bcrypt.generate_password_hash(admin_pass).decode("utf-8"),
        is_admin=True,
        role="admin",
        is_verified=True
    )
    db.session.add(superadmin)
    db.session.add(admin)

    products = [
        Product(
            name="Eco-Rubber Brick",
            category="Bricks",
            price=1200.0,
            unit="per brick",
            image="/static/uploads/eco_rubber_bricks.png",
            description="Kiln-fired solid clay brick — load-bearing walls and facades.",
            stock=18000
        ),
        Product(
            name="Rubber Paver",
            category="Pavers",
            price=2500.0,
            unit="per paver",
            image="/static/uploads/rubberPaver.jpg",
            description="Standard grey interlocking paver for driveways and walkways.",
            stock=9400
        ),
        Product(
            name="Colored Paver",
            category="Pavers",
            price=4800.0,
            unit="per paver",
            image="/static/uploads/coloredPaver.jpg",
            description="Eco-friendly paver made from recycled tires — slip resistant.",
            stock=3200
        ),
        Product(
            name="Rubber Bricks",
            category="Bricks",
            price=1200.0,
            unit="per brick",
            image="/static/uploads/rubber_bricks.png",
            description="Lightweight hollow block for fast wall construction.",
            stock=6700
        ),
        Product(
            name="Rubber Paver Pallet",
            category="Pavers",
            price=3800.0,
            unit="per paver",
            image="/static/uploads/rubber_paver_pallet.png",
            description="Classic cobblestone profile for premium courtyards.",
            stock=5100
        )
    ]

    for p in products:
        db.session.add(p)

    db.session.commit()
    print("Database successfully seeded with admin users and products using environment configuration!")
