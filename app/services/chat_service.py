# app/services/chat_service.py

import os
import re
import requests

def get_reply(message):
    q = (message or "").lower().strip()
    
    # Try Gemini API if key is present
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        try:
            system_instruction = (
                "You are Rubi, the official AI chatbot of Rubriq Africa. "
                "Rubriq Africa is a leading sustainable building materials company in Uganda. "
                "We manufacture and supply high-quality, eco-friendly pavers, bricks, and hollow blocks, "
                "including pavers made from recycled tires (colored pavers, interlocking pavers, eco-rubber bricks). "
                "Prices start at 1,200 UGX for clay bricks. Standard grey interlocking pavers are 2,500 UGX. "
                "Recycled colored pavers are 4,800 UGX. We deliver all over Uganda and East Africa. "
                "Our business contact is hello@rubriq.africa or +256 704 363 512. "
                "Always be warm, professional, concise, and focused on helping customers with pricing, ordering, "
                "and custom paving blends. Keep your answers brief (1-3 sentences)."
            )
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            headers = {"Content-Type": "application/json"}
            payload = {
                "contents": [
                    {"role": "user", "parts": [{"text": f"{system_instruction}\n\nCustomer: {message}"}]}
                ]
            }
            res = requests.post(url, json=payload, headers=headers, timeout=5)
            if res.status_code == 200:
                data = res.json()
                reply = data["candidates"][0]["content"]["parts"][0]["text"]
                return reply.strip()
        except Exception as e:
            print("Gemini API call failed, falling back to rule engine:", e)

    # Fallback Rule Engine
    if re.search(r"price|cost|ugx|how much", q):
        return "Our products start from 1,200 UGX (clay brick). Visit Products for the full price list."

    if re.search(r"deliver|shipping|location", q):
        return "We deliver across Uganda and East Africa. Contact us with your location for a specific quote."

    if re.search(r"about|company|who are you", q):
        return "Rubriq Africa is a Ugandan firm making sustainable bricks and pavers from local clay and recycled rubber."

    if re.search(r"contact|phone|email|whatsapp|address", q):
        return "You can reach us at hello@rubriq.africa or +256 704 363 512. Or tap the WhatsApp icon next to a product!"

    if re.search(r"paver|brick|block|stock|product", q):
        return "We stock clay bricks (1,200 UGX), grey pavers (2,500 UGX), colored pavers (4,800 UGX), and hollow blocks. Check our Products page!"

    if re.search(r"hello|hi|hey|greetings", q):
        return "Hello! 👋 I'm Rubi, the Rubriq assistant. Ask me about products, prices or delivery."

    return "Thanks for reaching out! A team member will follow up shortly. Feel free to browse our Products or Contact page."