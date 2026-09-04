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

    # Seed Admin Users
    superadmin = User(
        name="Super Admin",
        email="superadmin@rubriq.com",
        phone="0700000001",
        password=bcrypt.generate_password_hash("SuperAdmin123!").decode("utf-8"),
        is_admin=True,
        role="superadmin",
        is_verified=True
    )
    admin = User(
        name="Admin User",
        email="admin@rubriq.com",
        phone="0700000002",
        password=bcrypt.generate_password_hash("Admin123!").decode("utf-8"),
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
    print("Database successfully seeded with 2 admin users and 5 products!")
    print("\n--- SEEDED ACCOUNTS ---")
    print("Superadmin: Phone = 0700000001, Email = superadmin@rubriq.com, Password = SuperAdmin123!, Secret Code = Okumu@078@078")
    print("Admin: Phone = 0700000002, Email = admin@rubriq.com, Password = Admin123!, Secret Code = Okumu@078@078")
    print("------------------------\n")
