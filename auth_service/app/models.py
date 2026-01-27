# auth_service/app/models.py
from .database import get_db

# Simple helper to get user by username
def get_user_by_username(username: str):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

# Get enabled MFA method
def get_enabled_mfa_method(user_id: int):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM mfa_methods WHERE user_id=%s AND enabled=1 LIMIT 1",
        (user_id,)
    )
    method = cursor.fetchone()
    cursor.close()
    conn.close()
    return method
