import psycopg2
import os

# Config from .env
DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "db_inmo_velar"
DB_USER = "postgres"
DB_PASSWORD = "7323"

try:
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )
    cursor = conn.cursor()
    
    print("--- Checking for Audit Triggers in PostgreSQL ---")
    
    # Check for triggers starting with 'trg_audit_'
    cursor.execute("""
        SELECT trigger_name, event_object_table, action_statement
        FROM information_schema.triggers 
        WHERE trigger_schema = 'public' 
        AND trigger_name LIKE 'trg_audit_%'
    """)
    
    triggers = cursor.fetchall()
    
    if triggers:
        print(f"Found {len(triggers)} audit triggers:")
        for t in triggers:
            print(f"- {t[0]} on {t[1]}")
    else:
        print("[WARN] No audit triggers found starting with 'trg_audit_'")

    conn.close()

except Exception as e:
    print(f"[CRITICAL ERROR] {e}")
