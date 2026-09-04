from datetime import timedelta
import os
from dotenv import load_dotenv # type: ignore

load_dotenv()

# Render PostgreSQL URL handling
db_url = os.getenv("DATABASE_URL")
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

class Config:
    SQLALCHEMY_DATABASE_URI = db_url or os.getenv("SQLALCHEMY_DATABASE_URI", "sqlite:///rubriq_africa.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv("SECRET_KEY", "rubriq-super-secret-key")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "rubriq-jwt-secret-key")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)

SMTP_SERVER = os.getenv('SMTP_SERVER')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
SMTP_USERNAME = os.getenv('SMTP_USERNAME')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL')