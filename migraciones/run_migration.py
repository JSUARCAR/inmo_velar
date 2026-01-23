import sqlite3

# Conectar a la base de datos
conn = sqlite3.connect('inmobiliaria_velar.db')
cursor = conn.cursor()

# Leer el script SQL
with open('create_liquidaciones_tables.sql', 'r', encoding='utf-8') as f:
    sql_script = f.read()

print("=== Ejecutando script de creacion de tablas ===\n")

# Ejecutar el script SQL
try:
    cursor.executescript(sql_script)
    conn.commit()
    print("[OK] Tablas creadas exitosamente\n")
    
    # Verificar las tablas creadas
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%ASESOR%' ORDER BY name")
    tables = cursor.fetchall()
    
    print("=== Tablas de asesores en la base de datos ===")
    for table in tables:
        print(f"  - {table[0]}")
        
        # Mostrar el schema de cada tabla
        cursor.execute(f"PRAGMA table_info({table[0]})")
        columns = cursor.fetchall()
        print(f"    Columnas: {len(columns)}")
        
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
finally:
    conn.close()

print("\n=== Script completado ===")
