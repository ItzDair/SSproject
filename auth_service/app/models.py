from .database import get_db

# Get user by username
def get_user_by_username(username: str):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

# Update OTP and expiry
def update_user_otp(user_id, otp, expiry):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE users SET otp=%s, otp_expiry=%s WHERE id=%s",
        (otp, expiry, user_id)
    )
    conn.commit()
    cursor.close()
    conn.close()

# Get enabled MFA method (optional, if you expand later)
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
