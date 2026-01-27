import mysql.connector
import os

conn = mysql.connector.connect(
    host=os.getenv("DB_HOST", "localhost"),
    user=os.getenv("DB_USER", "mfa_user"),
    password=os.getenv("DB_PASSWORD", "mfa_pass"),
    database=os.getenv("DB_NAME", "mfa")
)

cur = conn.cursor()
cur.execute("SHOW TABLES")
print("Connected. Tables:")
for t in cur.fetchall():
    print("-", t[0])

cur.close()
conn.close()
