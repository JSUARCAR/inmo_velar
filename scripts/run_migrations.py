import sqlite3
import os

# Try both possible database locations
possible_paths = [
    os.path.join(os.path.dirname(__file__), '..', 'migraciones', 'DB_Inmo_Velar.db'),
    os.path.join(os.path.dirname(__file__), '..', 'DB_Inmo_Velar.db'),
    os.path.join(os.path.dirname(__file__), '..', 'velar.db'),
    os.path.join(os.path.dirname(__file__), '..', 'src', 'migraciones', 'DB_Inmo_Velar.db'),
]

db_path = None
for p in possible_paths:
    p = os.path.abspath(p)
    if os.path.exists(p):
        db_path = p
        break

if db_path is None:
    # Use the default from settings
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'migraciones', 'DB_Inmo_Velar.db'))

print(f"DB path: {db_path}")
print(f"Exists: {os.path.exists(db_path)}")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# List existing tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [r[0] for r in cursor.fetchall()]
print(f"\nExisting tables ({len(tables)}):")
for t in tables:
    print(f"  - {t}")

# Check which new tables are missing
new_tables = ['PLAN_PAGO_INCIDENTE', 'CUOTA_INCIDENTE', 'INCIDENTE_LIQUIDACION', 'BLOQUEOS_EDICION']
missing = [t for t in new_tables if t not in tables]
print(f"\nMissing tables: {missing}")

# Check which migrations to run
migrations_dir = os.path.join(os.path.dirname(__file__), 'migration_001.sql')
for i in range(1, 7):
    sql_file = os.path.join(os.path.dirname(__file__), f'migration_{i:03d}.sql')
    if os.path.exists(sql_file):
        with open(sql_file, 'r') as f:
            content = f.read()
        # Check if this migration has tables we need
        for table in missing:
            if table in content.upper() or f'CREATE TABLE IF NOT EXISTS {table}' in content.upper():
                print(f"\nRunning migration {i:03d} for {table}...")
                try:
                    cursor.executescript(content)
                    print(f"  OK")
                except Exception as e:
                    print(f"  Error: {e}")
                break

# Run all migrations that are safe (CREATE IF NOT EXISTS)
print("\nRunning all migrations (safe with IF NOT EXISTS)...")
for i in range(1, 7):
    sql_file = os.path.join(os.path.dirname(__file__), f'migration_{i:03d}.sql')
    if os.path.exists(sql_file):
        with open(sql_file, 'r') as f:
            content = f.read()
        try:
            cursor.executescript(content)
            print(f"  migration_{i:03d}.sql: OK")
        except Exception as e:
            print(f"  migration_{i:03d}.sql: {e}")

conn.commit()

# Verify
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables_after = [r[0] for r in cursor.fetchall()]
print(f"\nTables after migration ({len(tables_after)}):")
for t in tables_after:
    print(f"  - {t}")

conn.close()
