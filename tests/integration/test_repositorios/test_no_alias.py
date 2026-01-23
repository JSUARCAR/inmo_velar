import sqlite3
import sys

# Query with NO aliases
sql = """
SELECT 
    CONTRATOS_MANDATOS.ID_CONTRATO_M,
    PROPIEDADES.ID_PROPIEDAD,
    PROPIEDADES.DIRECCION_PROPIEDAD, 
    PROPIEDADES.MATRICULA_INMOBILIARIA
FROM CONTRATOS_MANDATOS
JOIN PROPIEDADES ON CONTRATOS_MANDATOS.ID_PROPIEDAD = PROPIEDADES.ID_PROPIEDAD
JOIN PROPIETARIOS ON CONTRATOS_MANDATOS.ID_PROPIETARIO = PROPIETARIOS.ID_PROPIETARIO
WHERE CONTRATOS_MANDATOS.ID_CONTRATO_M = 1
"""

try:
    conn = sqlite3.connect('DB_Inmo_Velar.db')
    cursor = conn.cursor()
    
    print("Executing query WITHOUT ALIASES...")
    cursor.execute(sql)
    print("Execution SUCCESS")
    
except Exception as e:
    print(f"Execution FAILED: {e}")
finally:
    if 'conn' in locals(): conn.close()
