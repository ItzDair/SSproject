# auth_service/app/database.py
import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import Error

load_dotenv()  # loads .env variables

DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT"))
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Function to get a DB connection
def get_db():
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )
        return connection
    except Error as e:
        print("Error connecting to DB:", e)
        return None

# Optional: a pre-made connection object (if you want to import it directly)
try:
    connection = get_db()
except:
    connection = None
