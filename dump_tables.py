import sqlite3
import os

# Try to find the DB
db_files = []
for root, dirs, files in os.walk("."):
    for file in files:
        if file.endswith(".db"):
            db_files.append(os.path.join(root, file))

print(f"Found DB files: {db_files}")

for db_path in db_files:
    print(f"\nScanning {db_path}...")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name, sql FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        for name, sql in tables:
            if name in ['USUARIOS', 'PERSONAS', 'PROPIEDADES', 'CONTRATOS_ARRENDAMIENTOS']:
                print(f"Table: {name}")
                # Simple string check on CREATE statement
                if "UPDATED_BY" in (sql or ""):
                    print(f"  - Has UPDATED_BY in SQL definition")
                else:
                    print(f"  - MISSING UPDATED_BY in SQL definition")
        conn.close()
    except Exception as e:
        print(f"Error reading {db_path}: {e}")
