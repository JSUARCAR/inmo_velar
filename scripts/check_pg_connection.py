import os
import sys
import psycopg2
from dotenv import load_dotenv

# Load env vars
load_dotenv()

def check_connection():
    print("=== Checking PostgreSQL Connection ===")
    
    # Try getting URL from env
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        print("[ERROR] DATABASE_URL not found in .env")
        return

    print(f"DATABASE_URL found (length: {len(db_url)})")
    
    try:
        conn = psycopg2.connect(db_url)
        print("[OK] Connection successful!")
        
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()
        print(f"[INFO] Server version: {version[0]}")
        
        conn.close()
        return True
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")
        return False

if __name__ == "__main__":
    check_connection()
