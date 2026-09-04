# app/routes/chat_routes.py

from flask import Blueprint, request, jsonify
from app.models.chat.chat_message import ChatMessage
from app.services.chat_service import get_reply
from app.extensions import db
from datetime import datetime

chat_bp = Blueprint("chat", __name__, url_prefix="/api/chat")

# In-memory store for thread modes (AI bot vs human agent)
# Maps session_id (sender_id) to "bot" or "human"
thread_modes = {}

# DIRECT CHATBOT ROUTE (Called by floating widget POST /api/chat)
@chat_bp.route("", methods=["POST"])
@chat_bp.route("/", methods=["POST"])
def direct_chat():
    data = request.get_json() or {}
    message_text = data.get("message")
    if not message_text:
        return jsonify({"error": "message is required"}), 400
    
    reply_text = get_reply(message_text)
    return jsonify({"reply": reply_text})

# GET MESSAGES
@chat_bp.route("/messages", methods=["GET"])
def get_messages():
    session_id = request.args.get("session_id")
    if not session_id:
        return jsonify({"error": "session_id is required"}), 400

    # Fetch messages between session_id and admin
    messages = ChatMessage.query.filter(
        ((ChatMessage.sender_id == session_id) & (ChatMessage.recipient_id == "admin")) |
        ((ChatMessage.sender_id == "admin") & (ChatMessage.recipient_id == session_id))
    ).order_by(ChatMessage.timestamp.asc()).all()

    # Mark all user messages in this thread as read when retrieved (by admin or client)
    for m in messages:
        if not m.is_read:
            m.is_read = True
    db.session.commit()

    return jsonify([m.to_dict() for m in messages])

# SEND MESSAGE
@chat_bp.route("/send", methods=["POST"])
def send_message():
    data = request.get_json() or {}
    sender_id = data.get("sender_id")
    recipient_id = data.get("recipient_id", "admin")
    sender_name = data.get("sender_name", "Guest")
    message_text = data.get("message")
    
    if not sender_id or not message_text:
        return jsonify({"error": "sender_id and message are required"}), 400

    # Save user message
    user_msg = ChatMessage(
        sender_id=sender_id,
        recipient_id=recipient_id,
        sender_name=sender_name,
        message=message_text,
        is_read=False
    )
    db.session.add(user_msg)
    db.session.commit()

    response_payload = {
        "message": user_msg.to_dict(),
        "bot_reply": None
    }

    # Resolve thread mode
    current_mode = thread_modes.get(sender_id if sender_id != "admin" else recipient_id, "bot")

    # If message is sent to admin and current mode is bot, trigger bot response
    if recipient_id == "admin" and current_mode == "bot":
        reply_text = get_reply(message_text)
        bot_msg = ChatMessage(
            sender_id="admin",
            recipient_id=sender_id,
            sender_name="Rubi (AI)",
            message=reply_text,
            is_read=True
        )
        db.session.add(bot_msg)
        db.session.commit()
        response_payload["bot_reply"] = bot_msg.to_dict()

    return jsonify(response_payload), 201

# GET CHAT THREADS (for admin dashboard)
@chat_bp.route("/threads", methods=["GET"])
def get_threads():
    # Retrieve all messages sorted by time desc to identify last message per thread
    messages = ChatMessage.query.order_by(ChatMessage.timestamp.desc()).all()
    threads = {}
    for m in messages:
        other_party = m.sender_id if m.sender_id != "admin" else m.recipient_id
        if other_party == "admin":
            continue
        if other_party not in threads:
            threads[other_party] = {
                "session_id": other_party,
                "sender_name": m.sender_name if m.sender_id != "admin" else "Customer",
                "last_message": m.message,
                "timestamp": m.timestamp.isoformat(),
                "is_read": m.is_read if m.sender_id != "admin" else True,
                "chat_mode": thread_modes.get(other_party, "bot")
            }
    return jsonify(list(threads.values()))

# TOGGLE THREAD MODE (for admin dashboard)
@chat_bp.route("/thread/<string:session_id>/toggle-mode", methods=["POST"])
def toggle_thread_mode(session_id):
    data = request.get_json() or {}
    new_mode = data.get("mode") # "bot" or "human"
    if new_mode not in ["bot", "human"]:
        return jsonify({"error": "invalid mode. Must be 'bot' or 'human'"}), 400

    thread_modes[session_id] = new_mode
    return jsonify({
        "session_id": session_id,
        "mode": new_mode,
        "message": f"Thread mode switched to {new_mode}"
    }), 200