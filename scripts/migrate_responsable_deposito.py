import sqlite3
import psycopg2
import os

def migrate_sqlite():
    db_path = "test.db"
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    try:
        cur.execute("ALTER TABLE CONTRATOS_MANDATOS DROP COLUMN responsable_deposito_id;")
        print("Dropped responsable_deposito_id from CONTRATOS_MANDATOS in sqlite")
    except Exception as e:
        print(f"Skipped dropping in sqlite: {e}")
        
    try:
        cur.execute("ALTER TABLE CONTRATOS_ARRENDAMIENTOS ADD COLUMN responsable_deposito_id INTEGER;")
        print("Added responsable_deposito_id to CONTRATOS_ARRENDAMIENTOS in sqlite")
    except Exception as e:
        print(f"Skipped adding in sqlite: {e}")
        
    conn.commit()
    conn.close()

def migrate_postgres():
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        return
    if "postgres" not in db_url:
        return
        
    conn = psycopg2.connect(db_url)
    cur = conn.cursor()
    
    try:
        cur.execute("ALTER TABLE CONTRATOS_MANDATOS DROP COLUMN responsable_deposito_id;")
        print("Dropped responsable_deposito_id from CONTRATOS_MANDATOS in postgres")
    except Exception as e:
        print(f"Skipped dropping in postgres: {e}")
        conn.rollback()
        
    try:
        cur.execute("ALTER TABLE CONTRATOS_ARRENDAMIENTOS ADD COLUMN responsable_deposito_id INTEGER;")
        print("Added responsable_deposito_id to CONTRATOS_ARRENDAMIENTOS in postgres")
    except Exception as e:
        print(f"Skipped adding in postgres: {e}")
        conn.rollback()
        
    conn.commit()
    conn.close()

if __name__ == "__main__":
    migrate_sqlite()
    try:
        migrate_postgres()
    except:
        pass
