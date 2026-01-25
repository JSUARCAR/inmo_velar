import sqlite3
import sys
import os

if len(sys.argv) < 2:
    print("Usage: python execute_sql.py <sql_file_path>")
    sys.exit(1)

sql_file = sys.argv[1]

if not os.path.exists(sql_file):
    print(f"Error: File '{sql_file}' not found.")
    sys.exit(1)

print(f"SQLite Version: {sqlite3.sqlite_version}")
print(f"Executing: {sql_file}")

try:
    with open(sql_file, 'r', encoding='utf-8') as f:
        sql = f.read()
    
    # Use config/rxconfig.py db path logic if possible, otherwise hardcode for now as per other scripts
    # The other script used 'DB_Inmo_Velar.db'. Let's check if that's the correct DB.
    # Step 11 showed 'DB_Inmo_Velar.db' exists.
    
    conn = sqlite3.connect('DB_Inmo_Velar.db')
    cursor = conn.cursor()
    
    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON;")
    
    # Execute script allows multiple statements
    cursor.executescript(sql)
    
    conn.commit()
    print("Execution SUCCESS.")
    
except Exception as e:
    print(f"Execution FAILED: {e}")
    if 'conn' in locals():
        conn.rollback()
finally:
    if 'conn' in locals():
        conn.close()
