import os
import sqlite3

DB_PATH = (
    r"c:\Users\PC\OneDrive\Desktop\inmobiliaria velar\PYTHON-REFLEX\migraciones\DB_Inmo_Velar.db"
)


def migrate():
    if not os.path.exists(DB_PATH):
        print(f"Error: Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Check if columns exist to avoid errors
        cursor.execute("PRAGMA table_info(RECIBOS_PUBLICOS)")
        columns = [info[1] for info in cursor.fetchall()]

        if "FECHA_DESDE" not in columns:
            print("Adding FECHA_DESDE...")
            cursor.execute("ALTER TABLE RECIBOS_PUBLICOS ADD COLUMN FECHA_DESDE TEXT")

        if "FECHA_HASTA" not in columns:
            print("Adding FECHA_HASTA...")
            cursor.execute("ALTER TABLE RECIBOS_PUBLICOS ADD COLUMN FECHA_HASTA TEXT")

        if "DIAS_FACTURADOS" not in columns:
            print("Adding DIAS_FACTURADOS...")
            cursor.execute("ALTER TABLE RECIBOS_PUBLICOS ADD COLUMN DIAS_FACTURADOS INTEGER")

        conn.commit()
        print("Migration completed successfully.")

    except Exception as e:
        print(f"Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()
