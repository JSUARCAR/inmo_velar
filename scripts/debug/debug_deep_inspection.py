"""
Deep inspection of database values to identify exact data types
and values causing the dashboard to show 0.
"""
import sqlite3
import os

DB_PATH = "DB_Inmo_Velar.db"
OUTPUT_FILE = "debug_deep_inspection_output.txt"

def inspect():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    with open(OUTPUT_FILE, "w", encoding='utf-8') as f:
        f.write("=== DEEP DATABASE INSPECTION ===\n\n")

        # 1. Check CONTRATOS_ARRENDAMIENTOS: ESTADO_CONTRATO_A
        f.write("--- 1. CONTRATOS_ARRENDAMIENTOS ---\n")
        try:
            cursor.execute("SELECT ID_CONTRATO_A, ESTADO_CONTRATO_A, typeof(ESTADO_CONTRATO_A), length(ESTADO_CONTRATO_A), hex(ESTADO_CONTRATO_A) FROM CONTRATOS_ARRENDAMIENTOS")
            rows = cursor.fetchall()
            for row in rows:
                f.write(f"  ID: {row[0]}, ESTADO: '{row[1]}', Type: {row[2]}, Len: {row[3]}, Hex: {row[4]}\n")

            # Check if 'Activo' matches (case-sensitive)
            cursor.execute("SELECT COUNT(*) FROM CONTRATOS_ARRENDAMIENTOS WHERE ESTADO_CONTRATO_A = 'Activo'")
            count = cursor.fetchone()[0]
            f.write(f"  Matches ESTADO_CONTRATO_A = 'Activo': {count}\n")

            cursor.execute("SELECT COUNT(*) FROM CONTRATOS_ARRENDAMIENTOS WHERE UPPER(TRIM(ESTADO_CONTRATO_A)) = 'ACTIVO'")
            count_upper = cursor.fetchone()[0]
            f.write(f"  Matches UPPER(TRIM(ESTADO_CONTRATO_A)) = 'ACTIVO': {count_upper}\n")
        except Exception as e:
            f.write(f"  Error: {e}\n")

        # 2. Check PROPIEDADES: DISPONIBILIDAD_PROPIEDAD, ESTADO_REGISTRO
        f.write("\n--- 2. PROPIEDADES ---\n")
        try:
            cursor.execute("SELECT ID_PROPIEDAD, DISPONIBILIDAD_PROPIEDAD, typeof(DISPONIBILIDAD_PROPIEDAD), ESTADO_REGISTRO, typeof(ESTADO_REGISTRO) FROM PROPIEDADES")
            rows = cursor.fetchall()
            for row in rows:
                f.write(f"  ID: {row[0]}, DISP: {row[1]} (Type: {row[2]}), EST_REG: {row[3]} (Type: {row[4]})\n")
            
            # Check query match
            cursor.execute("""
                SELECT 
                    SUM(CASE WHEN DISPONIBILIDAD_PROPIEDAD = 1 THEN 1 ELSE 0 END) as disponibles,
                    SUM(CASE WHEN DISPONIBILIDAD_PROPIEDAD = 0 THEN 1 ELSE 0 END) as ocupadas
                FROM PROPIEDADES
                WHERE ESTADO_REGISTRO = 1
            """)
            result = cursor.fetchone()
            f.write(f"  Query Result: Disponibles={result[0]}, Ocupadas={result[1]}\n")
        except Exception as e:
            f.write(f"  Error: {e}\n")

        # 3. Check LIQUIDACIONES_ASESORES: ESTADO_LIQUIDACION
        f.write("\n--- 3. LIQUIDACIONES_ASESORES ---\n")
        try:
            # First get column names
            cursor.execute("PRAGMA table_info(LIQUIDACIONES_ASESORES)")
            cols = cursor.fetchall()
            col_names = [c[1] for c in cols]
            f.write(f"  Columns: {col_names}\n")
            
            # Check for ESTADO_LIQUIDACION or similar
            estado_col = None
            for c in col_names:
                if 'ESTADO' in c.upper():
                    estado_col = c
                    break
            
            if estado_col:
                cursor.execute(f"SELECT * FROM LIQUIDACIONES_ASESORES LIMIT 5")
                rows = cursor.fetchall()
                for row in rows:
                    f.write(f"  {row}\n")
            else:
                f.write("  No ESTADO column found.\n")
        except Exception as e:
            f.write(f"  Error: {e}\n")

        # 4. Check VW_ALERTA_VENCIMIENTO_CONTRATOS
        f.write("\n--- 4. VW_ALERTA_VENCIMIENTO_CONTRATOS ---\n")
        try:
            cursor.execute("SELECT * FROM VW_ALERTA_VENCIMIENTO_CONTRATOS LIMIT 5")
            rows = cursor.fetchall()
            if rows:
                cols = [description[0] for description in cursor.description]
                f.write(f"  Columns: {cols}\n")
                for row in rows:
                    f.write(f"  {row}\n")
            else:
                f.write("  View is empty.\n")
        except Exception as e:
            f.write(f"  Error: {e}\n")

        # 5. Check RECIBOS_PUBLICOS
        f.write("\n--- 5. RECIBOS_PUBLICOS ---\n")
        try:
            cursor.execute("PRAGMA table_info(RECIBOS_PUBLICOS)")
            cols = cursor.fetchall()
            col_names = [c[1] for c in cols]
            f.write(f"  Columns: {col_names}\n")
            
            cursor.execute("SELECT * FROM RECIBOS_PUBLICOS LIMIT 5")
            rows = cursor.fetchall()
            if rows:
                for row in rows:
                    f.write(f"  {row}\n")
            else:
                f.write("  No recibos found.\n")
        except Exception as e:
            f.write(f"  Error: {e}\n")

        # 6. Check Canon from active contracts (for "Meta" calculation)
        f.write("\n--- 6. CONTRATOS_ARRENDAMIENTOS CANON ---\n")
        try:
            cursor.execute("SELECT SUM(CANON_ARRENDAMIENTO) FROM CONTRATOS_ARRENDAMIENTOS WHERE ESTADO_CONTRATO_A = 'Activo'")
            result = cursor.fetchone()[0]
            f.write(f"  SUM(CANON_ARRENDAMIENTO) where Activo: {result}\n")
        except Exception as e:
            f.write(f"  Error: {e}\n")

    conn.close()
    print(f"Deep inspection complete. Results in {OUTPUT_FILE}")

if __name__ == "__main__":
    inspect()
