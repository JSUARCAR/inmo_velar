import sqlite3

conn = sqlite3.connect('DB_Inmo_Velar.db')
cursor = conn.cursor()
try:
    with open('columns_repr.txt', 'w') as f:
        f.write("MANDATOS_COLUMNS_REPR:\n")
        cursor.execute("PRAGMA table_info(CONTRATOS_MANDATOS)")
        for row in cursor.fetchall():
            col_name = row[1]
            f.write(f"'{col_name}' : {ascii(col_name)} : {list(col_name.encode('utf-8'))}\n")
            
        f.write("\nPROPIETARIOS_COLUMNS_REPR:\n")
        cursor.execute("PRAGMA table_info(PROPIETARIOS)")
        for row in cursor.fetchall():
            col_name = row[1]
            f.write(f"'{col_name}' : {ascii(col_name)} : {list(col_name.encode('utf-8'))}\n")

except Exception as e:
    with open('columns_repr.txt', 'w') as f:
        f.write(str(e))
finally:
    conn.close()
