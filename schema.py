#pip install psycopg2-binary


import psycopg2
import os 
from dotenv import load_dotenv 


load_dotenv()

db_url = os.getenv('DATABASE_URL') 

def create_tables():
    conn = psycopg2.connect(db_url)
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        username TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS services (
        service_id SERIAL PRIMARY KEY,
        name TEXT,
        admin_id TEXT
    )
    """)


    cursor.execute("""
    CREATE TABLE IF NOT EXISTS slots (
        slot_id SERIAL PRIMARY KEY,
        service_id INTEGER,
        date TEXT,
        time TEXT,
        status TEXT DEFAULT 'available'
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS appointments (
        appointment_id SERIAL PRIMARY KEY,
        user_id TEXT,
        slot_id INTEGER
    )
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_tables()
    print("Tables created successfully!")
