import os
from sib_api_v3_sdk import Configuration, ApiClient
from sib_api_v3_sdk.api.transactional_emails_api import TransactionalEmailsApi
from sib_api_v3_sdk.models import SendSmtpEmail

BREVO_API_KEY = os.getenv("BREVO_API_KEY")

def send_otp_email(to_email, otp):
    configuration = Configuration()
    configuration.api_key['api-key'] = BREVO_API_KEY
    api_instance = TransactionalEmailsApi(ApiClient(configuration))

    send_smtp_email = SendSmtpEmail(
        to=[{"email": to_email}],
        sender={"email": "otpnoreplyss@gmail.com", "name": "Dair Sultanov"},
        subject="Your One-Time Password",
        html_content=f"<p>Your OTP is <b>{otp}</b>. It expires in 5 minutes.</p>"
    )

    try:
        api_instance.send_transac_email(send_smtp_email)
    except Exception as e:
        print("Error sending email OTP:", e)
