import os
import sys

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.infraestructura.persistencia.database import db_manager

def check_view():
    print("=== Verificando Vista VW_ALERTA_VENCIMIENTO_CONTRATOS ===")
    
    if not db_manager.use_postgresql:
        print("[WARN] No usando PostgreSQL. Usando SQLite local.")

    try:
        with db_manager.obtener_conexion() as conn:
            cursor = db_manager.get_dict_cursor(conn)
            
            # 1. Conteo por rango
            print("\n[INFO] Conteo por rangos (simula dashboard):")
            cursor.execute("""
                SELECT 
                    SUM(CASE WHEN DIAS_RESTANTES <= 30 THEN 1 ELSE 0 END) AS VENCE_30,
                    SUM(CASE WHEN DIAS_RESTANTES > 30 AND DIAS_RESTANTES <= 60 THEN 1 ELSE 0 END) AS VENCE_60,
                    SUM(CASE WHEN DIAS_RESTANTES > 60 AND DIAS_RESTANTES <= 90 THEN 1 ELSE 0 END) AS VENCE_90
                FROM VW_ALERTA_VENCIMIENTO_CONTRATOS
            """)
            counts = cursor.fetchone()
            print(f"  - 30 días: {counts['VENCE_30']}")
            print(f"  - 60 días: {counts['VENCE_60']}")
            print(f"  - 90 días: {counts['VENCE_90']}")
            
            # 2. Listado detallado
            print("\n[INFO] Detalle de contratos próximos a vencer:")
            cursor.execute("""
                SELECT TIPO_CONTRATO, DIRECCION, INQUILINO_PROPIETARIO, FECHA_FIN, DIAS_RESTANTES 
                FROM VW_ALERTA_VENCIMIENTO_CONTRATOS 
                ORDER BY DIAS_RESTANTES ASC
                LIMIT 10
            """)
            rows = cursor.fetchall()
            for r in rows:
                print(f"  [{r['DIAS_RESTANTES']} dias] {r['TIPO_CONTRATO']} - {r['DIRECCION']} ({r['INQUILINO_PROPIETARIO']})")
                
    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    check_view()
