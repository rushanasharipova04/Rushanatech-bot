import os
import time
import threading
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# BotFather bergan tokenni shu yerga yozing.
BOT_TOKEN = os.getenv("8818253269:AAGJjMOeW8TBZA8jQgObXVWwoq23WqJmQCg")

# /start bosilgandan keyin bot sizga chat ID ni yuboradi.
# Keyin quyidagi joyga o'sha raqamni yozasiz.
ADMIN_CHAT_ID = "1015460915"

last_update_id = 0


def telegram_api(method, data=None):
    """Telegram API ga so'rov yuboradi."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"

    try:
        response = requests.post(url, data=data, timeout=30)
        return response.json()
    except requests.RequestException as error:
        print("Internet yoki Telegram bilan bog'lanish xatosi:", error)
        return {"ok": False}


def send_message(chat_id, text):
    """Telegram chatiga xabar yuboradi."""
    return telegram_api("sendMessage", {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    })


def bot_listener():
    """Botga kelgan /start xabarlarini doimiy tekshiradi."""
    global last_update_id

    while True:
        result = telegram_api("getUpdates", {
            "offset": last_update_id + 1,
            "timeout": 20
        })

        if result.get("ok"):
            for update in result.get("result", []):
                last_update_id = update["update_id"]

                message = update.get("message")

                if not message:
                    continue

                chat_id = message["chat"]["id"]
                text = message.get("text", "")

                if text == "/start":
                    send_message(
                        chat_id,
                        f"✅ Bot ishlayapti!\n\n"
                        f"Sizning <b>Chat ID</b> raqamingiz:\n"
                        f"<code>{chat_id}</code>\n\n"
                        f"Bu raqamni koddagi ADMIN_CHAT_ID joyiga yozing."
                    )
                else:
                    send_message(
                        chat_id,
                        "Salom! Saytdan kelgan yangi mijozlar kontaktlari shu yerga yuboriladi."
                    )

        time.sleep(1)


@app.route("/", methods=["GET"])
def home():
    return "RushanaTech lead bot ishlayapti."


@app.route("/new-lead", methods=["POST"])
def new_lead():
    """Saytdan kelgan ro'yxatdan o'tish ma'lumotlarini qabul qiladi."""
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "success": False,
            "message": "Ma'lumot JSON formatida yuborilmadi."
        }), 400

    name = data.get("name", "Kiritilmagan")
    phone = data.get("phone", "Kiritilmagan")
    direction = data.get("direction", "Kiritilmagan")
    client_message = data.get("message", "Xabar qoldirilmagan")

    lead_text = f"""
<b>🚀 Yangi RushanaTech so‘rovi</b>

<b>👤 Ism:</b> {name}
<b>📞 Telefon:</b> {phone}
<b>📚 Yo‘nalish:</b> {direction}
<b>💬 Xabar:</b> {client_message}
"""

    result = send_message(ADMIN_CHAT_ID, lead_text)

    if result.get("ok"):
        return jsonify({
            "success": True,
            "message": "So‘rovingiz qabul qilindi."
        })

    return jsonify({
        "success": False,
        "message": "Telegramga xabar yuborilmadi.",
        "error": result.get("description", "Noma'lum xato")
    }), 500


if __name__ == "__main__":
    if BOT_TOKEN == "BU_YERGA_BOT_TOKENINGIZNI_YOZING":
        print("XATO: BOT_TOKEN ni kiriting!")
    else:
        threading.Thread(target=bot_listener, daemon=True).start()
        print("Bot va server ishga tushdi: http://127.0.0.1:5000")
        app.run(host="0.0.0.0", port=5000, debug=False)