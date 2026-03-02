"""
Verify FECHA_PAGO column existence.
"""
import sys
import os
import sqlite3

# Add src to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, "../"))
sys.path.insert(0, project_root)

def verify():
    db_path = os.path.join(project_root, "src/infraestructura/persistencia/inmobiliaria.db")
    print(f"Checking DB at: {db_path}")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(CONTRATOS_MANDATOS)")
        columns = cursor.fetchall()
        
        found = False
        for col in columns:
            # col[1] is name, col[2] is type
            if col[1] == "FECHA_PAGO":
                print(f"✅ Column FECHA_PAGO found! Type: {col[2]}")
                found = True
                break
        
        if not found:
            print("❌ Column FECHA_PAGO NOT found.")
            
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    verify()
