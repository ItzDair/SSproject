import os
import requests

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def send_otp_telegram(chat_id: str, otp: str):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": f"Your OTP is {otp}. It expires in 5 minutes."
    }
    try:
        response = requests.post(url, json=payload, timeout=5)
        response.raise_for_status()
    except Exception as e:
        print("Error sending Telegram OTP:", e)
