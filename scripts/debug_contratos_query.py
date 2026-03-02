
from src.infraestructura.persistencia.database import db_manager

def debug_contratos():
    print("--- DIAGNÓSTICO DE CONTRATOS ---")
    conn = db_manager.obtener_conexion()
    cursor = db_manager.get_dict_cursor(conn)
    
    # 1. Conteo base
    cursor.execute("SELECT COUNT(*) as count FROM CONTRATOS_ARRENDAMIENTOS")
    total_ca = cursor.fetchone()["COUNT"]
    print(f"Total en CONTRATOS_ARRENDAMIENTOS: {total_ca}")
    
    # 2. Probar JOIN a PROPIEDADES
    cursor.execute("""
        SELECT COUNT(*) as count 
        FROM CONTRATOS_ARRENDAMIENTOS ca
        JOIN PROPIEDADES p ON ca.ID_PROPIEDAD = p.ID_PROPIEDAD
    """)
    total_prop = cursor.fetchone()["COUNT"]
    print(f"Total con JOIN PROPIEDADES: {total_prop}")
    
    # 3. Probar JOIN a ARRENDATARIOS
    cursor.execute("""
        SELECT COUNT(*) as count 
        FROM CONTRATOS_ARRENDAMIENTOS ca
        JOIN ARRENDATARIOS arr ON ca.ID_ARRENDATARIO = arr.ID_ARRENDATARIO
    """)
    total_arr = cursor.fetchone()["COUNT"]
    print(f"Total con JOIN ARRENDATARIOS: {total_arr}")
    
    # 4. Probar JOIN a PERSONAS
    cursor.execute("""
        SELECT COUNT(*) as count 
        FROM CONTRATOS_ARRENDAMIENTOS ca
        JOIN ARRENDATARIOS arr ON ca.ID_ARRENDATARIO = arr.ID_ARRENDATARIO
        JOIN PERSONAS per ON arr.ID_PERSONA = per.ID_PERSONA
    """)
    total_per = cursor.fetchone()["COUNT"]
    print(f"Total con JOIN PERSONAS: {total_per}")
    
    # 5. Verificar estados Activos
    cursor.execute("SELECT DISTINCT ESTADO_CONTRATO_A FROM CONTRATOS_ARRENDAMIENTOS")
    estados = [r["ESTADO_CONTRATO_A"] for r in cursor.fetchall()]
    print(f"Estados presentes en BD: {estados}")
    
    # 6. Total Activos Arrendamientos
    cursor.execute("""
        SELECT COUNT(*) as count
        FROM CONTRATOS_ARRENDAMIENTOS ca
        JOIN PROPIEDADES p ON ca.ID_PROPIEDAD = p.ID_PROPIEDAD
        JOIN ARRENDATARIOS arr ON ca.ID_ARRENDATARIO = arr.ID_ARRENDATARIO
        JOIN PERSONAS per ON arr.ID_PERSONA = per.ID_PERSONA
        WHERE ca.ESTADO_CONTRATO_A = 'Activo'
    """)
    total_activos = cursor.fetchone()["COUNT"]
    print(f"Total Arrendamientos Activos con todos los JOINs: {total_activos}")

    print("\n--- DIAGNÓSTICO DE MANDATOS ---")
    # 7. Conteo base Mandatos
    cursor.execute("SELECT COUNT(*) as count FROM CONTRATOS_MANDATOS")
    total_cm = cursor.fetchone()["COUNT"]
    print(f"Total en CONTRATOS_MANDATOS: {total_cm}")

    # 8. Probar JOIN a PROPIEDADES
    cursor.execute("""
        SELECT COUNT(*) as count 
        FROM CONTRATOS_MANDATOS cm
        JOIN PROPIEDADES p ON cm.ID_PROPIEDAD = p.ID_PROPIEDAD
    """)
    total_prop_m = cursor.fetchone()["COUNT"]
    print(f"Total Mandatos con JOIN PROPIEDADES: {total_prop_m}")

    # 9. Probar JOIN a PROPIETARIOS
    cursor.execute("""
        SELECT COUNT(*) as count 
        FROM CONTRATOS_MANDATOS cm
        JOIN PROPIETARIOS prop ON cm.ID_PROPIETARIO = prop.ID_PROPIETARIO
    """)
    total_prop_ent = cursor.fetchone()["COUNT"]
    print(f"Total Mandatos con JOIN PROPIETARIOS: {total_prop_ent}")

    # 10. Probar JOIN a PERSONAS (Propietarios)
    cursor.execute("""
        SELECT COUNT(*) as count 
        FROM CONTRATOS_MANDATOS cm
        JOIN PROPIETARIOS prop ON cm.ID_PROPIETARIO = prop.ID_PROPIETARIO
        JOIN PERSONAS per ON prop.ID_PERSONA = per.ID_PERSONA
    """)
    total_per_m = cursor.fetchone()["COUNT"]
    print(f"Total Mandatos con JOIN PERSONAS (Propietarios): {total_per_m}")

    # 11. Ejecutar query exacta de listar_paginado Mandatos (simplificada)
    cursor.execute("""
        SELECT COUNT(*) as count
        FROM CONTRATOS_MANDATOS cm
        JOIN PROPIEDADES p ON cm.ID_PROPIEDAD = p.ID_PROPIEDAD
        JOIN PROPIETARIOS prop ON cm.ID_PROPIETARIO = prop.ID_PROPIETARIO
        JOIN PERSONAS per ON prop.ID_PERSONA = per.ID_PERSONA
        WHERE cm.ESTADO_CONTRATO_M = 'Activo'
    """)
    total_mandatos_activos = cursor.fetchone()["COUNT"]
    print(f"Total Mandatos Activos con todos los JOINs: {total_mandatos_activos}")

    conn.close()

if __name__ == "__main__":
    debug_contratos()
