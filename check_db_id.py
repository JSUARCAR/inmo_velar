import psycopg2
conn = psycopg2.connect('postgresql://postgres:tBltIuhaUSMqQFvUMtSqIPFQZdXwpPtU@hopper.proxy.rlwy.net:12937/railway')
cursor = conn.cursor()
cursor.execute('''
SELECT a.ID_ASESOR FROM ASESORES a
JOIN PERSONAS per ON a.ID_PERSONA = per.ID_PERSONA
WHERE per.NOMBRE_COMPLETO ILIKE '%CRISTIAN%JAMIOY%'
''')
id_asesor = cursor.fetchone()[0]
print('ID ASESOR:', id_asesor)
cursor.execute('''
SELECT DISTINCT ON (ca.ID_CONTRATO_A)
    ca.ID_CONTRATO_A
FROM CONTRATOS_ARRENDAMIENTOS ca
JOIN PROPIEDADES p ON ca.ID_PROPIEDAD = p.ID_PROPIEDAD
JOIN CONTRATOS_MANDATOS cm ON ca.ID_PROPIEDAD = cm.ID_PROPIEDAD
    AND cm.ESTADO_CONTRATO_M = 'ACTIVO'
    AND cm.ID_ASESOR = %s
LEFT JOIN ARRENDATARIOS arr ON ca.ID_ARRENDATARIO = arr.ID_ARRENDATARIO
LEFT JOIN SEGUROS seg ON arr.ID_SEGURO = seg.ID_SEGURO
WHERE ca.ESTADO_CONTRATO_A = 'ACTIVO'
ORDER BY ca.ID_CONTRATO_A, cm.ID_CONTRATO_M DESC
''', (id_asesor,))
print('Corrected query count:', len(cursor.fetchall()))
