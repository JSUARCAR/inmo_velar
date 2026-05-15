
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Load env from root
load_dotenv()

DB_URL = os.getenv("DATABASE_URL")

def diagnose_property():
    if not DB_URL:
        print("DATABASE_URL not found in env")
        return

    conn = psycopg2.connect(DB_URL)
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            address = "CR 44 CL 50-86 TO 7 APT 401, CJT RES CAMINO DEL PUERTO"
            
            print(f"--- DIAGNOSTIC FOR: {address} ---")
            
            # 1. Propiedad
            cur.execute("SELECT ID_PROPIEDAD, DIRECCION_PROPIEDAD, ESTADO_REGISTRO FROM PROPIEDADES WHERE DIRECCION_PROPIEDAD ILIKE %s", (f"%{address}%",))
            prop = cur.fetchone()
            if not prop:
                print("Property not found!")
                return
            
            prop_id = prop['id_propiedad']
            print(f"Property ID: {prop_id}, State: {prop['estado_registro']}")

            # 2. Mandatos
            cur.execute("SELECT ID_CONTRATO_M, ESTADO_CONTRATO_M, FECHA_INICIO_CONTRATO_M FROM CONTRATOS_MANDATOS WHERE ID_PROPIEDAD = %s", (prop_id,))
            mandatos = cur.fetchall()
            print(f"\nMandatos ({len(mandatos)}):")
            for m in mandatos:
                print(f"  - ID: {m['id_contrato_m']}, State: '{m['estado_contrato_m']}', Start: {m['fecha_inicio_contrato_m']}")

            # 3. Arrendamientos
            cur.execute("SELECT ID_CONTRATO_A, ESTADO_CONTRATO_A, FECHA_INICIO_CONTRATO_A FROM CONTRATOS_ARRENDAMIENTOS WHERE ID_PROPIEDAD = %s", (prop_id,))
            arriendos = cur.fetchall()
            print(f"\nArrendamientos ({len(arriendos)}):")
            for a in arriendos:
                print(f"  - ID: {a['id_contrato_a']}, State: '{a['estado_contrato_a']}', Start: {a['fecha_inicio_contrato_a']}")

            # 4. Liquidaciones
            cur.execute("""
                SELECT l.ID_LIQUIDACION, l.ID_CONTRATO_M, l.PERIODO, l.ESTADO_LIQUIDACION 
                FROM liquidaciones l
                JOIN CONTRATOS_MANDATOS cm ON l.ID_CONTRATO_M = cm.ID_CONTRATO_M
                WHERE cm.ID_PROPIEDAD = %s
                ORDER BY l.PERIODO DESC
            """, (prop_id,))
            liqs = cur.fetchall()
            print(f"\nLiquidaciones ({len(liqs)}):")
            for l in liqs[:5]:
                print(f"  - ID: {l['id_liquidacion']}, Mandate: {l['id_contrato_m']}, Period: {l['periodo']}, State: {l['estado_liquidacion']}")

            # 5. Recaudos
            cur.execute("""
                SELECT r.ID_RECAUDO, r.ID_CONTRATO_A, rc.PERIODO, r.ESTADO_RECAUDO
                FROM RECAUDOS r
                JOIN RECAUDO_CONCEPTOS rc ON r.ID_RECAUDO = rc.ID_RECAUDO
                JOIN CONTRATOS_ARRENDAMIENTOS ca ON r.ID_CONTRATO_A = ca.ID_CONTRATO_A
                WHERE ca.ID_PROPIEDAD = %s
                ORDER BY rc.PERIODO DESC
            """, (prop_id,))
            recaudos = cur.fetchall()
            print(f"\nRecaudos ({len(recaudos)}):")
            for r in recaudos[:5]:
                print(f"  - ID: {r['id_recaudo']}, Arriendo: {r['id_contrato_a']}, Period: {r['periodo']}, State: {r['estado_recaudo']}")

    finally:
        conn.close()

if __name__ == "__main__":
    diagnose_property()
