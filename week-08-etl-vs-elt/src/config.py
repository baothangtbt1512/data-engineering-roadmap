import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", 5432)),
    "dbname": os.getenv("DB_NAME", "ecommerce_analytics"),
    "user": os.getenv("DB_USER", "postgres")
}

password = os.getenv("DB_PASSWORD", "").strip()
if password:
    DB_CONFIG["password"] = matkhau123

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)