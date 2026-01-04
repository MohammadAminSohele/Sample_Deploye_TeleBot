#pip install psycopg2-binary


import psycopg2
import os 
from dotenv import load_dotenv 


load_dotenv()

db_url = os.getenv('DATABASE_URL') 

def create_tables():
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id SERIAL PRIMARY KEY ,
            question TEXT NOT NULL,
            option1 TEXT NOT NULL,
            option2 TEXT NOT NULL,
            option3 TEXT NOT NULL,
            option4 TEXT NOT NULL,
            correct_option INTEGER NOT NULL
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS results (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            score INTEGER NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_tables()
    print("Tables created successfully!")
