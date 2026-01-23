import psycopg2
from psycopg2 import sql

DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'db_inmo_velar',
    'user': 'inmo_user',
    'password': '7323'
}

def check_blocking():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        print("Checking for blocking processes...")
        cursor.execute("""
            SELECT 
                blocked.pid AS blocked_pid,
                left(blocked.query, 50) AS blocked_query,
                blocking.pid AS blocking_pid,
                blocking.usename AS blocking_user,
                blocking.application_name AS blocking_app,
                blocking.state AS blocking_state,
                blocking.query_start AS blocking_start,
                left(blocking.query, 50) AS blocking_query
            FROM pg_stat_activity blocked
            JOIN pg_stat_activity blocking ON blocking.pid = ANY(pg_blocking_pids(blocked.pid));
        """)
        
        rows = cursor.fetchall()
        if not rows:
            print("No blocking chains found.")
        else:
            print("\nBlocking chains:")
            for row in rows:
                print(f"Blocked PID: {row[0]} ({row[1]}...)")
                print(f"  BLOCKED BY -> PID: {row[2]}")
                print(f"  User: {row[3]}, App: {row[4]}")
                print(f"  State: {row[5]}, Start: {row[6]}")
                print(f"  Query: {row[7]}...\n")
                
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_blocking()
