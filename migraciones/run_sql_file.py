import sqlite3
import sys

print(f"SQLite Version: {sqlite3.sqlite_version}")

try:
    with open('debug_query.sql', 'r', encoding='utf-8') as f:
        sql = f.read()
    
    print(f"SQL Length: {len(sql)}")
    # print(f"SQL Repr: {repr(sql)}")

    conn = sqlite3.connect('DB_Inmo_Velar.db')
    cursor = conn.cursor()
    
    print("Executing query...")
    cursor.execute(sql)
    print("Execution SUCCESS (Fetchone below):")
    print(cursor.fetchone())
    
except Exception as e:
    print(f"Execution FAILED: {e}")
finally:
    if 'conn' in locals(): conn.close()
