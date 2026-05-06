import sqlite3
conn = sqlite3.connect('DB_Inmo_Velar.db')
cursor = conn.cursor()
try:
    with open('schema_columns.txt', 'w') as f:
        f.write("PROPIETARIOS_COLUMNS:\n")
        cursor.execute("PRAGMA table_info(PROPIETARIOS)")
        for row in cursor.fetchall():
            f.write(f"{row[1]}\n")
except Exception as e:
    with open('schema_columns.txt', 'w') as f:
        f.write(str(e))
finally:
    conn.close()
