import random
from telegram import Bot
from flask import session, request, redirect
from telegram import Bot

TELEGRAM_BOT_TOKEN = "8396245929:AAFyCnMS_g8TlBo-cW7jyvVMDTMqWnfnIg0"

def send_telegram_otp(phone_number, otp):
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    
    # Map phone_number to Telegram chat_id for testing
    phone_to_chat = {
        "+1234567890": 123456789,  # replace with your Telegram chat ID
        # Add other users here
    }
    
    chat_id = phone_to_chat.get(phone_number)
    if chat_id:
        bot.send_message(chat_id=chat_id, text=f"Your OTP code is: {otp}")
    else:
        print(f"No chat_id found for {phone_number}")
