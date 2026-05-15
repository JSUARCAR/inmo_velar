import sqlite3
import os

# Database path
DB_PATH = "migraciones/DB_Inmo_Velar.db"

def add_consignatario_column():
    """Adds the CONSIGNATARIO column to the PROPIETARIOS table if it doesn't exist."""
    
    current_db_path = DB_PATH
    
    if not os.path.exists(current_db_path):
        print(f"Error: Database file not found at {current_db_path}")
        # Try checking root if not found in migraciones
        if os.path.exists("DB_Inmo_Velar.db"):
             print("Found DB_Inmo_Velar.db in root, trying that...")
             current_db_path = "DB_Inmo_Velar.db"
        else:
             return

    try:
        conn = sqlite3.connect(current_db_path)
        cursor = conn.cursor()

        # Check if column exists
        cursor.execute("PRAGMA table_info(PROPIETARIOS)")
        columns = [info[1] for info in cursor.fetchall()]
        
        if "CONSIGNATARIO" not in columns:
            print(f"Adding CONSIGNATARIO column to PROPIETARIOS table in {current_db_path}...")
            cursor.execute("ALTER TABLE PROPIETARIOS ADD COLUMN CONSIGNATARIO TEXT")
            conn.commit()
            print("Column added successfully.")
        else:
            print(f"Column CONSIGNATARIO already exists in PROPIETARIOS table in {current_db_path}.")

        conn.close()

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    add_consignatario_column()
