
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv("DATABASE_URL")

def diagnose_financials():
    conn = psycopg2.connect(DB_URL)
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            address = "CR 44 CL 50-86 TO 7 APT 401, CJT RES CAMINO DEL PUERTO"
            cur.execute("SELECT ID_PROPIEDAD FROM PROPIEDADES WHERE DIRECCION_PROPIEDAD ILIKE %s", (f"%{address}%",))
            prop = cur.fetchone()
            prop_id = prop['id_propiedad']

            print(f"--- FINANCIAL DIAGNOSTIC FOR PROP {prop_id} ---")
            
            cur.execute("""
                SELECT l.ID_LIQUIDACION, l.PERIODO, l.ESTADO_LIQUIDACION, 
                       l.TOTAL_INGRESOS, l.TOTAL_EGRESOS, l.NETO_A_PAGAR,
                       l.GASTOS_ADMINISTRACION
                FROM liquidaciones l
                JOIN CONTRATOS_MANDATOS cm ON l.ID_CONTRATO_M = cm.ID_CONTRATO_M
                WHERE cm.ID_PROPIEDAD = %s
                ORDER BY l.PERIODO DESC
            """, (prop_id,))
            liqs = cur.fetchall()
            for l in liqs:
                print(f"Liq {l['id_liquidacion']} ({l['periodo']}): State={l['estado_liquidacion']}, Ingresos={l['total_ingresos']}, Admin={l['gastos_administracion']}, Neto={l['neto_a_pagar']}")

            cur.execute("""
                SELECT r.ID_RECAUDO, rc.PERIODO, r.ESTADO_RECAUDO, r.VALOR_TOTAL
                FROM RECAUDOS r
                JOIN RECAUDO_CONCEPTOS rc ON r.ID_RECAUDO = rc.ID_RECAUDO
                JOIN CONTRATOS_ARRENDAMIENTOS ca ON r.ID_CONTRATO_A = ca.ID_CONTRATO_A
                WHERE ca.ID_PROPIEDAD = %s
                ORDER BY rc.PERIODO DESC
            """, (prop_id,))
            recaudos = cur.fetchall()
            print("\nRecaudos:")
            for r in recaudos:
                print(f"  - Recaudio {r['id_recaudo']} ({r['periodo']}): State={r['estado_recaudo']}, Total={r['valor_total']}")

    finally:
        conn.close()

if __name__ == "__main__":
    diagnose_financials()
