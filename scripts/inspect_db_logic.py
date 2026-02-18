import os
import sys

# Add root directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.infraestructura.persistencia.database import db_manager

def inspect_db():
    print("=== Inspecting DB Logic ===")
    
    try:
        with db_manager.obtener_conexion() as conn:
            cursor = db_manager.get_dict_cursor(conn)
            
            # 1. Check VW definition if possible (Postgres specific)
            print("\n[INFO] View Definition (VW_ALERTA_VENCIMIENTO_CONTRATOS):")
            try:
                cursor.execute("SELECT definition FROM pg_views WHERE viewname = 'vw_alerta_vencimiento_contratos'")
                row = cursor.fetchone()
                if row:
                    print(row['definition'])
                else:
                    print("View definition not found in pg_views.")
            except Exception as e:
                print(f"Error getting view def: {e}")

            # 2. Check Raw Data for Arrendamientos
            print("\n[INFO] Raw CONTRATOS_ARRENDAMIENTOS (First 5):")
            cursor.execute("SELECT ID_CONTRATO_A, FECHA_FIN_CONTRATO_A, ESTADO_CONTRATO_A FROM CONTRATOS_ARRENDAMIENTOS LIMIT 5")
            for r in cursor.fetchall():
                print(r)
                
            # 3. Check what the Python Query would miss
            print("\n[INFO] Testing Python Logic Constraints:")
            cursor.execute("SELECT DISTINCT ESTADO_CONTRATO_A FROM CONTRATOS_ARRENDAMIENTOS")
            print("Estados presentes:", cursor.fetchall())

    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    inspect_db()
