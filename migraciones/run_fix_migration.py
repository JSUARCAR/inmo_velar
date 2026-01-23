import sqlite3

print("=== MIGRACION: Corregir Foreign Key de LIQUIDACIONES_ASESORES ===\n")

# Conectar a la base de datos CORRECTA
conn = sqlite3.connect('DB_Inmo_Velar.db')
cursor = conn.cursor()

try:
    # Leer el script SQL
    with open('fix_liquidaciones_fk.sql', 'r', encoding='utf-8') as f:
        sql_script = f.read()
    
    print("Ejecutando migracion...")
    cursor.executescript(sql_script)
    conn.commit()
    print("[OK] Migracion completada exitosamente\n")
    
    # Verificar el foreign key corregido
    print("=== Verificando Foreign Keys Corregidos ===\n")
    cursor.execute("PRAGMA foreign_key_list(LIQUIDACIONES_ASESORES)")
    fks = cursor.fetchall()
    
    for fk in fks:
        print(f"  - FK {fk[0]}: {fk[3]} -> {fk[2]}.{fk[4]}")
    
    print("\n[OK] Foreign keys corregidos!")
    
except Exception as e:
    print(f"[ERROR] {e}")
    import traceback
    traceback.print_exc()
    conn.rollback()
finally:
    conn.close()

print("\n=== Migracion completada ===")
