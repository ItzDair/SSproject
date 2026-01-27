# auth_service/app/security.py
import bcrypt
import pyotp

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def generate_mfa_secret() -> str:
    return pyotp.random_base32()

def generate_otp(secret_key: str) -> str:
    totp = pyotp.TOTP(secret_key)
    return totp.now()
