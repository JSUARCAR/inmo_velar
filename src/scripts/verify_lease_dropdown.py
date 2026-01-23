import sys
import os
sys.path.append(os.getcwd())

from src.infraestructura.persistencia.database import db_manager

def verify_logic():
    print(f"{'ID':<5} | {'Address':<40} | {'Active Mandate?':<15} | {'Active Lease?':<15} | {'ELIGIBLE?':<10}")
    print("-" * 100)
    
    with db_manager.obtener_conexion() as conn:
        cursor = db_manager.get_dict_cursor(conn)
        
        # 1. Get all properties
        cursor.execute("SELECT ID_PROPIEDAD, DIRECCION_PROPIEDAD FROM PROPIEDADES WHERE ESTADO_REGISTRO = TRUE")
        props = cursor.fetchall()
        
        eligible_count = 0
        
        for p in props:
            # Handle case sensitivity helper
            p_dict = dict(p) if hasattr(p, 'keys') else p
            p_id = p_dict.get('ID_PROPIEDAD') or p_dict.get('id_propiedad')
            address = p_dict.get('DIRECCION_PROPIEDAD') or p_dict.get('direccion_propiedad')
            
            # 2. Check Active Mandate
            cursor.execute("""
                SELECT 1 FROM CONTRATOS_MANDATOS 
                WHERE ID_PROPIEDAD = %s AND ESTADO_CONTRATO_M = 'Activo'
            """ % db_manager.get_placeholder(), (p_id,))
            has_mandate = cursor.fetchone() is not None
            
            # 3. Check Active Lease
            cursor.execute("""
                SELECT 1 FROM CONTRATOS_ARRENDAMIENTOS 
                WHERE ID_PROPIEDAD = %s AND ESTADO_CONTRATO_A = 'Activo'
            """ % db_manager.get_placeholder(), (p_id,))
            has_lease = cursor.fetchone() is not None
            
            # 4. Determine Eligibility
            eligible = has_mandate and not has_lease
            
            if eligible:
                eligible_count += 1
            
            elig_str = "YES" if eligible else "NO"
            print(f"{p_id:<5} | {address[:40]:<40} | {str(has_mandate):<15} | {str(has_lease):<15} | {elig_str:<10}")

    print("-" * 100)
    print(f"Total Eligible Properties found in DB: {eligible_count}")

if __name__ == "__main__":
    verify_logic()
