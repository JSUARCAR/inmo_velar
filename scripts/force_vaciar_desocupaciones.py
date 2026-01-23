import sqlite3
import os

DB_PATH = "DB_Inmo_Velar.db"  # Ruta relativa desde el directorio del proyecto

def force_vaciar_desocupaciones():
    if not os.path.exists(DB_PATH):
        print(f"ERROR: No existe la DB en {DB_PATH}")
        return

    conn = None
    try:
        conn = sqlite3.connect(DB_PATH, timeout=10)
        cursor = conn.cursor()
        
        print(f"Abriendo base de datos: {DB_PATH}")
        print("Desactivando Foreign Keys...")
        cursor.execute("PRAGMA foreign_keys = OFF;")
        
        print("Iniciando borrado de tabla DESOCUPACIONES...")
        cursor.execute("BEGIN TRANSACTION;")
        
        tabla = "DESOCUPACIONES"
        conversacion_triggers = []
        try:
            # Verificar si la tabla existe
            cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{tabla}';")
            if cursor.fetchone():
                # 1. Backup y Drop Triggers
                cursor.execute(f"SELECT name, sql FROM sqlite_master WHERE type='trigger' AND tbl_name='{tabla}';")
                triggers = cursor.fetchall()
                for name, sql in triggers:
                    print(f"   [TRIGGER] Desactivando temporalmente: {name}")
                    conversacion_triggers.append((name, sql))
                    cursor.execute(f"DROP TRIGGER IF EXISTS {name};")

                # 2. Delete Data
                count_before = cursor.execute(f"SELECT COUNT(*) FROM {tabla}").fetchone()[0]
                cursor.execute(f"DELETE FROM {tabla};")
                count_after = cursor.execute(f"SELECT COUNT(*) FROM {tabla}").fetchone()[0]
                print(f"[OK] {tabla}: {count_before} -> {count_after}")

                # 3. Restore Triggers
                for name, sql in conversacion_triggers:
                    try:
                        cursor.execute(sql)
                        # print(f"   [TRIGGER] Restaurado: {name}")
                    except Exception as e_trig:
                        print(f"   [ERROR] Falló al restaurar trigger {name}: {e_trig}")

            else:
                print(f"[SKIP] Tabla no encontrada: {tabla}")
        except Exception as e_table:
            print(f"[ERROR] Falló al vaciar {tabla}: {e_table}")
            # Intentar restaurar triggers si falló el borrado pero se borraron triggers
            for name, sql in conversacion_triggers:
                try:
                    cursor.execute(sql)
                except: pass

        conn.commit()
        print("Transacción confirmada.")
        
        print("Reactivando Foreign Keys...")
        cursor.execute("PRAGMA foreign_keys = ON;")
        
        print("=== PROCESO COMPLETADO EXITOSAMENTE ===")
        
    except sqlite3.OperationalError as e:
        print(f"FATAL ERROR (Operational): {e}")
        if "locked" in str(e):
            print("LA BASE DE DATOS ESTÁ BLOQUEADA. CIERRE LA APLICACIÓN.")
    except Exception as e:
        print(f"FATAL ERROR: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    force_vaciar_desocupaciones()
