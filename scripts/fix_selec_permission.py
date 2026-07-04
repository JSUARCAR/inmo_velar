#!/usr/bin/env python3
"""Fix SELECCIONAR_INCIDENTES permission - name too long for VARCHAR(20)"""
import os
import sys
import psycopg2

def fix():
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        print("ERROR: DATABASE_URL not set")
        sys.exit(1)
    
    conn = psycopg2.connect(db_url)
    conn.autocommit = True
    cur = conn.cursor()
    
    # Check column length
    cur.execute("""
        SELECT character_maximum_length 
        FROM information_schema.columns 
        WHERE table_name = 'permisos' AND column_name = 'accion'
    """)
    max_len = cur.fetchone()[0]
    print(f"Columna ACCION: longitud maxima = {max_len}")
    
    # Check if SELEC_INCIDENTES already exists
    cur.execute("SELECT COUNT(*) FROM permisos WHERE modulo = 'Liquidaciones' AND accion = 'SELEC_INCIDENTES'")
    if cur.fetchone()[0] > 0:
        print("Permiso Liquidaciones:SELEC_INCIDENTES ya existe")
    else:
        cur.execute("""
            INSERT INTO PERMISOS (MODULO, RUTA, ACCION, DESCRIPCION, CATEGORIA)
            VALUES ('Liquidaciones', '/liquidaciones', 'SELEC_INCIDENTES', 
                    'Seleccionar incidentes para asociar a liquidaciones', 'Gestion')
        """)
        print("Permiso Liquidaciones:SELEC_INCIDENTES registrado")
    
    # List all Liquidaciones permissions
    print("\nPermisos de Liquidaciones:")
    cur.execute("SELECT MODULO, ACCION FROM PERMISOS WHERE MODULO = 'Liquidaciones' ORDER BY ACCION")
    for modulo, accion in cur.fetchall():
        print(f"  - {modulo}:{accion}")
    
    # List all Incidentes permissions
    print("\nPermisos de Incidentes:")
    cur.execute("SELECT MODULO, ACCION FROM PERMISOS WHERE MODULO = 'Incidentes' ORDER BY ACCION")
    for modulo, accion in cur.fetchall():
        print(f"  - {modulo}:{accion}")
    
    conn.close()
    print("\nDone!")

if __name__ == "__main__":
    fix()
