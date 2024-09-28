import os
import psycopg2
from psycopg2 import sql

# Use environment variables for database connection
db_params = {
    'dbname': os.environ.get('PGDATABASE'),
    'user': os.environ.get('PGUSER'),
    'password': os.environ.get('PGPASSWORD'),
    'host': os.environ.get('PGHOST'),
    'port': os.environ.get('PGPORT')
}

def initialize_db():
    """
    Initialize the database and create the necessary table.
    """
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()
    
    try:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS user_stocks (
                id SERIAL PRIMARY KEY,
                symbol VARCHAR(10) NOT NULL,
                UNIQUE(symbol)
            )
        """)
        conn.commit()
    except Exception as e:
        print(f"Error initializing database: {e}")
    finally:
        cur.close()
        conn.close()

def save_stock_to_db(symbol):
    """
    Save a stock symbol to the database.
    """
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()
    
    try:
        cur.execute(
            sql.SQL("INSERT INTO user_stocks (symbol) VALUES (%s) ON CONFLICT (symbol) DO NOTHING"),
            [symbol]
        )
        conn.commit()
    except Exception as e:
        print(f"Error saving stock to database: {e}")
    finally:
        cur.close()
        conn.close()

def get_user_stocks():
    """
    Retrieve all tracked stock symbols from the database.
    """
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT symbol FROM user_stocks")
        return [row[0] for row in cur.fetchall()]
    except Exception as e:
        print(f"Error retrieving stocks from database: {e}")
        return []
    finally:
        cur.close()
        conn.close()
