import mysql.connector
import os
from dotenv import load_dotenv

# Load .env from your project folder
load_dotenv(dotenv_path="/Users/pass1234/ss/SSproject/.env")

# Debug print to ensure variables are loaded
print("DB_HOST:", os.getenv("DB_HOST"))
print("DB_USER:", os.getenv("DB_USER"))
print("DB_PASSWORD:", os.getenv("DB_PASSWORD"))
print("DB_NAME:", os.getenv("DB_NAME"))

# Connect to MySQL
try:
    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "mfa_user"),
        password=os.getenv("DB_PASSWORD", "mfa_pass"),
        database=os.getenv("DB_NAME", "mfa")
    )

    cur = conn.cursor()
    cur.execute("SHOW TABLES")
    print("✅ Connected. Tables:")
    for t in cur.fetchall():
        print("-", t[0])

    cur.close()
    conn.close()

except mysql.connector.Error as e:
    print("❌ Connection failed:", e)
