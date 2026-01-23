
import sqlite3
import json

def inspect_db():
    conn = sqlite3.connect('DB_Inmo_Velar.db')
    cursor = conn.cursor()
    
    # Obtener todas las tablas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tablas = [t[0] for t in cursor.fetchall() if t[0] != 'sqlite_sequence']
    
    esquema = {}
    
    for tabla in tablas:
        # Obtener info de columnas: (cid, name, type, notnull, dflt_value, pk)
        cursor.execute(f"PRAGMA table_info({tabla})")
        columnas = cursor.fetchall()
        
        info_tabla = []
        for col in columnas:
            info_tabla.append({
                "nombre": col[1],
                "tipo": col[2],
                "notnull": bool(col[3]),
                "pk": bool(col[5])
            })
        esquema[tabla] = info_tabla
        
    conn.close()
    
    # Escribir a archivo
    with open("esquema_dump.json", "w", encoding="utf-8") as f:
        json.dump(esquema, f, indent=2)

if __name__ == "__main__":
    inspect_db()
