import os
import psycopg2
db_url = os.environ.get('DATABASE_URL')
if not db_url:
    raise ValueError("DATABASE_URL not set")
conn = psycopg2.connect(db_url)
cursor = conn.cursor()
cursor.execute('''
SELECT COUNT(DISTINCT ca.ID_CONTRATO_A) as total_elegibles
FROM CONTRATOS_ARRENDAMIENTOS ca
JOIN CONTRATOS_MANDATOS cm ON ca.ID_PROPIEDAD = cm.ID_PROPIEDAD
    AND cm.ESTADO_CONTRATO_M = 'ACTIVO'
JOIN ASESORES a ON cm.ID_ASESOR = a.ID_ASESOR
JOIN PERSONAS per ON a.ID_PERSONA = per.ID_PERSONA
WHERE per.NOMBRE_COMPLETO ILIKE '%CRISTIAN%JAMIOY%'
  AND ca.ESTADO_CONTRATO_A = 'ACTIVO'
''')
print('Direct count:', cursor.fetchone()[0])
cursor.execute('''
SELECT ca.ID_CONTRATO_A
FROM CONTRATOS_ARRENDAMIENTOS ca
JOIN CONTRATOS_MANDATOS cm ON ca.ID_PROPIEDAD = cm.ID_PROPIEDAD
JOIN PROPIEDADES p ON ca.ID_PROPIEDAD = p.ID_PROPIEDAD
JOIN ASESORES a ON cm.ID_ASESOR = a.ID_ASESOR
JOIN PERSONAS per ON a.ID_PERSONA = per.ID_PERSONA
WHERE per.NOMBRE_COMPLETO ILIKE '%CRISTIAN%JAMIOY%'
  AND ca.ESTADO_CONTRATO_A = 'ACTIVO'
  AND cm.ESTADO_CONTRATO_M = 'ACTIVO'
''')
print('Current query count:', len(cursor.fetchall()))
