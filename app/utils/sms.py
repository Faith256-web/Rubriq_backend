from twilio.rest import Client
from app.models.user.user_model import User
import os
from dotenv import load_dotenv
load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)


def send_reset_sms(phone, code):
    try:
        client.messages.create(
            body=f"🔐 Your Rubriq password reset code is: {code}. It expires in 2 minutes.",
            from_=+13612663978,
            to=phone
        )
        print(f"✅ SMS sent to {phone}")
    except Exception as e:
        print(f"❌ Failed to send SMS to {phone}: {e}")







#Sending the SMS to admins when an order is placed

def send_sms_to_admins(message_body):
    # Fetch all admins or employees from DB
    admins = User.query.filter_by(is_admin=True).all()

    for admin in admins:
        if admin.phone:
            try:
                client.messages.create(
                    body=message_body,
                    from_=+14026476707,
                    to=admin.phone
                )
                print(f"✅ SMS sent to admin {admin.name} ({admin.phone})")
            except Exception as e:
                print(f"❌ Failed to send SMS to {admin.phone}: {e}")