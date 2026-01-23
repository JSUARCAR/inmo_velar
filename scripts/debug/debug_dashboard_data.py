import sqlite3
import os

DB_PATH = "c:\\Users\\PC\\OneDrive\\Desktop\\inmobiliaria velar\\PYTHON-FLET\\DB_Inmo_Velar.db"
OUTPUT_FILE = "debug_output_dashboard.txt"

def inspect_db():
    if not os.path.exists(DB_PATH):
        with open(OUTPUT_FILE, "w") as f:
            f.write(f"ERROR: Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    with open(OUTPUT_FILE, "w", encoding='utf-8') as f:
        f.write("--- DASHBOARD DEBUG DATA ---\n\n")

        # 1. Contratos Status
        cursor.execute("SELECT ID_CONTRATO_A, ESTADO_CONTRATO_A FROM CONTRATOS_ARRENDAMIENTOS")
        rows = cursor.fetchall()
        f.write(f"CONTRATOS_ARRENDAMIENTOS (Count: {len(rows)}):\n")
        for row in rows:
            f.write(f"  ID: {row[0]}, ESTADO: '{row[1]}'\n")
        
        # 2. Propiedades Availability
        cursor.execute("SELECT ID_PROPIEDAD, DISPONIBILIDAD_PROPIEDAD, ESTADO_REGISTRO FROM PROPIEDADES")
        rows = cursor.fetchall()
        f.write(f"\nPROPIEDADES (Count: {len(rows)}):\n")
        for row in rows:
            f.write(f"  ID: {row[0]}, DISPONIBILIDAD: {row[1]}, ESTADO_REGISTRO: {row[2]}\n")

        # 3. View Exists?
        cursor.execute("SELECT name FROM sqlite_master WHERE type='view' AND name='VW_ALERTA_MORA_DIARIA'")
        view = cursor.fetchone()
        f.write(f"\nView VW_ALERTA_MORA_DIARIA exists: {view is not None}\n")

        if view:
            cursor.execute("SELECT * FROM VW_ALERTA_MORA_DIARIA")
            rows = cursor.fetchall()
            f.write(f"VW_ALERTA_MORA_DIARIA rows ({len(rows)}):\n")
            for row in rows:
                f.write(f"  {row}\n")

        # 4. Check Recaudos Dates
        cursor.execute("SELECT ID_RECAUDO, FECHA_RECAUDO, ESTADO_RECAUDO FROM RECAUDO_ARRENDAMIENTO")
        rows = cursor.fetchall()
        f.write(f"\nRECAUDO_ARRENDAMIENTO ({len(rows)}):\n")
        for row in rows:
            f.write(f"  ID: {row[0]}, FECHA: '{row[1]}', ESTADO: '{row[2]}'\n")

    conn.close()
    print(f"Debug output written to {OUTPUT_FILE}")

if __name__ == "__main__":
    inspect_db()
