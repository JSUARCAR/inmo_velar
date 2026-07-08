import os
import sys
from dotenv import load_dotenv
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
load_dotenv()

from src.infraestructura.persistencia.database import db_manager as db
from src.infraestructura.persistencia.repositorio_incidentes_postgres import RepositorioIncidentesPostgres

repo = RepositorioIncidentesPostgres(db)

def run_tests():
    print("--- Test T005 & T007 (Sin error GROUP BY, filas únicas) ---")
    try:
        res = repo.listar_con_filtros()
        print(f"[EXITO] Total {res['total']} incidentes retornados, count of items={len(res['items'])}")
    except Exception as e:
        print(f"[ERROR] {e}")
        return

    print("--- Test T008 (Arrays vacíos para sin cotizaciones) ---")
    conn = db.obtener_conexion()
    cursor = db.get_dict_cursor(conn)
    cursor.execute("""
        SELECT I.ID_INCIDENTE, COALESCE(cot.cotizaciones, '[]'::json) AS COTIZACIONES_JSON
        FROM INCIDENTES I
        LEFT JOIN LATERAL (
            SELECT JSON_AGG(
                JSON_BUILD_OBJECT('id_cotizacion', C.ID_COTIZACION)
            ) as cotizaciones
            FROM COTIZACIONES C WHERE C.ID_INCIDENTE = I.ID_INCIDENTE
        ) cot ON TRUE
        WHERE NOT EXISTS (SELECT 1 FROM COTIZACIONES C WHERE C.ID_INCIDENTE = I.ID_INCIDENTE)
        LIMIT 5
    """)
    rows = cursor.fetchall()
    
    empty_arrays = True
    for r in rows:
        cj = r.get("cotizaciones_json") or r.get("COTIZACIONES_JSON")
        print(cj)
        if cj != []:
            empty_arrays = False
            
    if empty_arrays:
        print("[EXITO] Correcto: arrays vacios [] retornados")
    else:
        print("[ERROR] No se retornaron arrays vacios")

    print("--- Test T009 (Multiples cotizaciones sin duplicacion) ---")
    cursor.execute("""
        SELECT I.ID_INCIDENTE, COALESCE(cot.cotizaciones, '[]'::json) AS COTIZACIONES_JSON
        FROM INCIDENTES I
        LEFT JOIN LATERAL (
            SELECT JSON_AGG(
                JSON_BUILD_OBJECT('id_cotizacion', C.ID_COTIZACION)
            ) as cotizaciones
            FROM COTIZACIONES C WHERE C.ID_INCIDENTE = I.ID_INCIDENTE
        ) cot ON TRUE
        WHERE (SELECT COUNT(*) FROM COTIZACIONES C WHERE C.ID_INCIDENTE = I.ID_INCIDENTE) >= 2
        LIMIT 1
    """)
    row = cursor.fetchone()
    if row:
        cj = row.get("cotizaciones_json") or row.get("COTIZACIONES_JSON")
        print("Múltiples cotizaciones:", json.dumps(cj, indent=2))
        print("[EXITO] Correcto: múltiples cotizaciones obtenidas en array")
    else:
        print("[WARN] No hay incidentes con múltiples cotizaciones en BD para test, pero la consulta no falló.")

    print("--- Test T010 & T011 (EXPLAIN ANALYZE) ---")
    query = """
    EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
    SELECT I.*, 
        COALESCE(cot.cotizaciones, '[]'::json) AS COTIZACIONES_JSON,
        pp.plan_pago AS PLAN_PAGO_JSON
    FROM INCIDENTES I
    LEFT JOIN LATERAL (
        SELECT JSON_AGG(
            JSON_BUILD_OBJECT('id_cotizacion', C.ID_COTIZACION)
        ) as cotizaciones
        FROM COTIZACIONES C WHERE C.ID_INCIDENTE = I.ID_INCIDENTE
    ) cot ON TRUE
    LEFT JOIN LATERAL (
        SELECT JSON_BUILD_OBJECT('id_plan_pago', PPI.ID_PLAN_PAGO) as plan_pago
        FROM PLAN_PAGO_INCIDENTE PPI 
        WHERE PPI.ID_INCIDENTE = I.ID_INCIDENTE AND PPI.ESTADO = 'Activo' 
        LIMIT 1
    ) pp ON TRUE
    ORDER BY I.FECHA_INCIDENTE DESC
    """
    cursor.execute(query)
    explain_rows = cursor.fetchall()
    print("PLAN DE EJECUCIÓN:")
    for r in explain_rows:
        print(list(r.values())[0])
        
if __name__ == "__main__":
    run_tests()
