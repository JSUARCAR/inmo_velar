import os
import sqlite3

DB_PATH = r"C:\Users\PC\OneDrive\Desktop\inmobiliaria velar\PYTHON-FLET\database.db"

def seed_proveedor():
    print(f"Connecting to DB at: {DB_PATH}")
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if exists
        cursor.execute("SELECT COUNT(*) FROM PROVEEDORES")
        count = cursor.fetchone()[0]
        print(f"Current providers count: {count}")
        
        if count == 0:
            print("Inserting test provider...")
            cursor.execute("""
                INSERT INTO PROVEEDORES (NOMBRE_PROVEEDOR, ESPECIALIDAD, TELEFONO, EMAIL, ESTADO_REGISTRO) 
                VALUES ('Proveedor Test', 'Mantenimiento General', '3001234567', 'contacto@proveedor.com', 1)
            """)
            conn.commit()
            print("Provider inserted successfully.")
        else:
            print("Providers already exist. Skipping insertion.")
            
        cursor.execute("SELECT * FROM PROVEEDORES")
        print("Providers in DB:", cursor.fetchall())
        
        conn.close()
    except Exception as e:
        print(f"Error seeding DB: {e}")

if __name__ == "__main__":
    seed_proveedor()
