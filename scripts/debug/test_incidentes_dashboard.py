"""
Script de diagnóstico para verificar datos de incidentes en la base de datos
"""

from src.infraestructura.persistencia.database import DatabaseManager

db = DatabaseManager()

with db.obtener_conexion() as conn:
    cursor = conn.cursor()
    
    print("=== SCHEMA DE TABLA INCIDENTES ===")
    cursor.execute("PRAGMA table_info(INCIDENTES)")
    for row in cursor.fetchall():
        print(row)
    
    print("\n=== TODOS LOS INCIDENTES ===")
    cursor.execute("SELECT ID_INCIDENTE, ESTADO, CREATED_AT FROM INCIDENTES")
    rows = cursor.fetchall()
    print(f"Total incidentes: {len(rows)}")
    for row in rows:
        print(row)
    
    print("\n=== QUERY DEL DASHBOARD ===")
    cursor.execute("""
        SELECT ESTADO, COUNT(*)
        FROM INCIDENTES
        GROUP BY ESTADO
    """)
    for row in cursor.fetchall():
        print(f"Estado: '{row[0]}', Count: {row[1]}")
    
    print("\n=== VALORES ÚNICOS DE ESTADO ===")
    cursor.execute("SELECT DISTINCT ESTADO FROM INCIDENTES")
    for row in cursor.fetchall():
        print(f"'{row[0]}'")
