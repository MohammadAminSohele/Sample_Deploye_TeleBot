#pip install psycopg2-binary


import psycopg2
import os 
from dotenv import load_dotenv 


load_dotenv()

db_url = os.getenv('DATABASE_URL') 

def create_tables():
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        username TEXT
    )
    """)

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_tables()
    print("Tables created successfully!")
