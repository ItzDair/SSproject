import smtplib, os, time
from email.message import EmailMessage
from functools import wraps
import requests

# Telegram Bot Function
def send_telegram(chat_id, message):
    token = os.getenv('TELEGRAM_TOKEN')
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    params = {"chat_id": chat_id, "text": message}
    response = requests.post(url, json=params)
    response.raise_for_status() 

def retry(max_attempts=3, delay=5):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_attempts:
                try:
                    return func(*args, **kwargs)
                except smtplib.SMTPException as e:
                    attempts += 1
                    if attempts == max_attempts:
                        raise
                    time.sleep(delay)
        return wrapper
    return decorator

@retry(max_attempts=3, delay=5)
def send_email(to_email, subject, body):
    if not all([to_email, subject, body]):
        raise ValueError("Missing required email parameters")
    
    msg = EmailMessage()
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = os.getenv('EMAIL_SENDER')
    msg['To'] = to_email

    try:
        with smtplib.SMTP_SSL(
            os.getenv('EMAIL_SMTP_SERVER'), 
            int(os.getenv('EMAIL_SMTP_PORT'))
        ) as smtp:
            smtp.login(
                os.getenv('EMAIL_SENDER'), 
                os.getenv('EMAIL_PASSWORD')
            )
            smtp.send_message(msg)
    except smtplib.SMTPException as e:
        raise RuntimeError(f"Failed to send email: {str(e)}")