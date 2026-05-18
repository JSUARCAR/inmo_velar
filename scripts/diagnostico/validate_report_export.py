import sys
import os
import json

# Añadir root al path
sys.path.append(os.getcwd())

from src.infraestructura.persistencia.database import db_manager

def validate_report_export():
    print("VALIDACIÓN ÉLITE: Generación y Exportación de Reporte de Liquidaciones")
    try:
        conn = db_manager.obtener_conexion()
        cur = db_manager.get_dict_cursor(conn)
        
        # 1. Inspeccionar descripciones reales
        cur.execute("SELECT DISTINCT DESCRIPCION_DESCUENTO FROM DESCUENTOS_ASESORES")
        descripciones = [r['DESCRIPCION_DESCUENTO'] for r in cur.fetchall()]
        print(f"Descripciones encontradas: {descripciones}")

        # 2. Ejecutar la query del reporte con ILIKE para máxima compatibilidad
        query = """
            SELECT 
                la.ID_LIQUIDACION_ASESOR AS "ID",
                (SELECT COALESCE(SUM(VALOR_DESCUENTO), 0) FROM DESCUENTOS_ASESORES WHERE ID_LIQUIDACION_ASESOR = la.ID_LIQUIDACION_ASESOR AND DESCRIPCION_DESCUENTO ILIKE '%%4x1000%%') AS "Descuento_4x1000",
                (SELECT COALESCE(SUM(VALOR_DESCUENTO), 0) FROM DESCUENTOS_ASESORES WHERE ID_LIQUIDACION_ASESOR = la.ID_LIQUIDACION_ASESOR AND DESCRIPCION_DESCUENTO ILIKE '%%Seguro%%') AS "Descuento_Seguro"
            FROM LIQUIDACIONES_ASESORES la
            ORDER BY la.ID_LIQUIDACION_ASESOR DESC
            LIMIT 10
        """
        cur.execute(query)
        rows = cur.fetchall()
        
        if rows:
            print(f"\nKeys retornadas por el driver: {list(rows[0].keys())}")
            
        print("\n--- Resultado Query Reporte (Últimos 10) ---")
        for r in rows:
            # Búsqueda de llaves case-insensitive por si acaso
            def gv(k): return r.get(k) or r.get(k.upper()) or r.get(k.lower()) or 0
            print(f"Liq ID {gv('ID')}: 4x1000={gv('Descuento_4x1000')}, Seguro={gv('Descuento_Seguro')}")

    except Exception as e:
        print(f"❌ Error en validación: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db_manager.shutdown()

if __name__ == "__main__":
    validate_report_export()
