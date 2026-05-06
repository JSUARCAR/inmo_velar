import sqlite3
import os

DB_PATH = r"c:\Users\PC\OneDrive\Desktop\inmobiliaria velar\PYTHON-FLET\DB_Inmo_Velar.db"

def verify_empty_db():
    if not os.path.exists(DB_PATH):
        print(f"ERROR: No existe la DB en {DB_PATH}")
        return

    conn = None
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Obtener todas las tablas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall() if row[0] != 'sqlite_sequence']
        
        non_empty_tables = []
        total_tables_checked = 0
        
        print(f"=== VERIFICACIÓN DE BASE DE DATOS: {DB_PATH} ===")
        print(f"Total tablas encontradas: {len(tables)}\n")
        
        for table in tables:
            try:
                count = cursor.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                total_tables_checked += 1
                if count > 0:
                    # Excluir tablas de configuración/sistema si es necesario, 
                    # pero el usuario pidió verificar que las tablas solicitadas estén vacías.
                    # Asumiremos que reportamos TODO lo que no sea 0 para que el usuario decida.
                    print(f"[AHORA TIENE DATOS] Tabla '{table}' tiene {count} registros.")
                    non_empty_tables.append((table, count))
                else:
                    # Opcional: imprimir las vacías si se quiere verbosidad, o solo un punto
                    # print(f"[OK] {table} está vacía.")
                    pass
            except Exception as e:
                print(f"[ERROR] No se pudo leer tabla {table}: {e}")

        print("\n=== RESUMEN DE VERIFICACIÓN ===")
        if not non_empty_tables:
            print("✅ TODAS las tablas verificadas están VACÍAS (0 registros).")
            print("(Nota: 'sqlite_sequence' fue excluida del chequeo de registros)")
        else:
            print(f"⚠️ SE ENCONTRARON {len(non_empty_tables)} TABLAS CON DATOS:")
            for t, c in non_empty_tables:
                print(f"   - {t}: {c} registros")
                
    except Exception as e:
        print(f"FATAL ERROR durante verificación: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    verify_empty_db()
