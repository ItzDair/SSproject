from .database import get_db

def get_user_by_username(username: str):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

def get_user_by_id(user_id):
    conn = get_db()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user

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
