#!/usr/bin/env python3
"""Assign SELEC_INCIDENTES permission to Administrador role"""
import os
import sys
import psycopg2

def assign_permission():
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        print("ERROR: DATABASE_URL not set")
        sys.exit(1)
    
    conn = psycopg2.connect(db_url)
    conn.autocommit = True
    cur = conn.cursor()
    
    # Get the id_permiso for SELEC_INCIDENTES
    cur.execute("""
        SELECT id_permiso FROM permisos 
        WHERE modulo = 'Liquidaciones' AND accion = 'SELEC_INCIDENTES'
    """)
    result = cur.fetchone()
    if not result:
        print("ERROR: SELEC_INCIDENTES permission not found in permisos table")
        sys.exit(1)
    
    permiso_id = result[0]
    print(f"Found SELEC_INCIDENTES permission with id: {permiso_id}")
    
    # Check if already assigned
    cur.execute("""
        SELECT COUNT(*) FROM rol_permisos 
        WHERE rol = 'Administrador' AND id_permiso = %s
    """, (permiso_id,))
    count = cur.fetchone()[0]
    
    if count > 0:
        print("Permission already assigned to Administrador role")
    else:
        # Assign the permission
        cur.execute("""
            INSERT INTO rol_permisos (rol, id_permiso, activo, created_by)
            VALUES ('Administrador', %s, True, 'SYSTEM')
        """, (permiso_id,))
        print("Assigned SELEC_INCIDENTES to Administrador role")
    
    # Verify all Liquidaciones permissions for Administrador
    cur.execute("""
        SELECT p.modulo, p.accion
        FROM rol_permisos rp
        JOIN permisos p ON rp.id_permiso = p.id_permiso
        WHERE rp.rol = 'Administrador'
        AND p.modulo = 'Liquidaciones'
        ORDER BY p.accion
    """)
    print("\nAll Liquidaciones permissions for Administrador:")
    for modulo, accion in cur.fetchall():
        print(f"  - {modulo}:{accion}")
    
    conn.close()

if __name__ == "__main__":
    assign_permission()
