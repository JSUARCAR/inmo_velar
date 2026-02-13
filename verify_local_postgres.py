import psycopg2
import sys

# Credentials from commented out section in .env
DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "db_inmo_velar"
DB_USER = "inmo_user"
DB_PASSWORD = "7323"  # From comments

def verify_local_connection():
    print(f"Attempting to connect to local PostgreSQL: {DB_USER}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        print("✅ Connection successful!")
        
        cursor = conn.cursor()
        cursor.execute("SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public'")
        count = cursor.fetchone()[0]
        print(f"✅ Found {count} tables in public schema.")
        
        cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' LIMIT 5")
        print("Sample tables:")
        for row in cursor.fetchall():
            print(f"- {row[0]}")
            
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    verify_local_connection()
