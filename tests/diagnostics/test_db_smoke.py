import os
import sys

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from src.infraestructura.persistencia.database import DatabaseManager

db = DatabaseManager()

query = """
    SELECT 
        r.ID_RECAUDO,
        cm.GRUPO_OPERATIVO
    FROM RECAUDOS r
    JOIN CONTRATOS_ARRENDAMIENTOS ca ON r.ID_CONTRATO_A = ca.ID_CONTRATO_A
    LEFT JOIN LATERAL (
        SELECT GRUPO_OPERATIVO
        FROM CONTRATOS_MANDATOS
        WHERE ID_PROPIEDAD = ca.ID_PROPIEDAD
          AND ESTADO_CONTRATO_M = 'ACTIVO'
        ORDER BY FECHA_INICIO_CONTRATO_M DESC
        LIMIT 1
    ) cm ON true
    LIMIT 5
"""

try:
    with db.obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()
        print("Success! Rows:", rows)
except Exception as e:
    print("Database Error:", str(e))
