"""
Script simple para diagnosticar asesores
"""
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from src.infraestructura.persistencia.database import db_manager

def test_advisor_query():
    print("="*80)
    print("DIAGNOSTICO: Carga de Asesores")
    print("="*80)
    
    query_asesores = """
    SELECT DISTINCT
        a.ID_ASESOR,
        p.NOMBRE_COMPLETO,
        a.COMISION_PORCENTAJE_ARRIENDO,
        a.ESTADO,
        cm.ESTADO_CONTRATO_M
    FROM ASESORES a
    INNER JOIN PERSONAS p ON a.ID_PERSONA = p.ID_PERSONA
    INNER JOIN CONTRATOS_MANDATOS cm ON a.ID_ASESOR = cm.ID_ASESOR
    WHERE a.ESTADO = TRUE
        AND cm.ESTADO_CONTRATO_M = 'Activo'
    ORDER BY p.NOMBRE_COMPLETO
    """
    
    try:
        with db_manager.obtener_conexion() as conn:
            cursor = db_manager.get_dict_cursor(conn)
            
            print("\nEjecutando query...")
            cursor.execute(query_asesores)
            rows = cursor.fetchall()
            
            print(f"Registros encontrados: {len(rows)}\n")
            
            if len(rows) == 0:
                print("NO SE ENCONTRARON ASESORES CON CONTRATOS ACTIVOS")
                print("\nVerificando datos base:")
                
                cursor.execute("SELECT COUNT(*) as total FROM ASESORES WHERE ESTADO = TRUE")
                total_asesores = cursor.fetchone()
                print(f"Asesores activos: {total_asesores.get('total', total_asesores.get('TOTAL', 0))}")
                
                cursor.execute("SELECT COUNT(*) as total FROM CONTRATOS_MANDATOS WHERE ESTADO_CONTRATO_M = 'Activo'")
                total_mandatos = cursor.fetchone()
                print(f"Contratos mandato activos: {total_mandatos.get('total', total_mandatos.get('TOTAL', 0))}")
                
                print("\nListando todos los asesores:")
                cursor.execute("SELECT a.ID_ASESOR, p.NOMBRE_COMPLETO, a.ESTADO FROM ASESORES a INNER JOIN PERSONAS p ON a.ID_PERSONA = p.ID_PERSONA")
                all_asesores = cursor.fetchall()
                for asesor in all_asesores:
                    id_val = asesor.get('id_asesor', asesor.get('ID_ASESOR'))
                    nombre_val = asesor.get('nombre_completo', asesor.get('NOMBRE_COMPLETO'))
                    estado_val = asesor.get('estado', asesor.get('ESTADO'))
                    print(f"  ID: {id_val}, Nombre: {nombre_val}, Estado: {estado_val}")
                
            else:
                print("Asesores con contratos activos:")
                for row in rows:
                    id_val = row.get('id_asesor', row.get('ID_ASESOR'))
                    nombre_val = row.get('nombre_completo', row.get('NOMBRE_COMPLETO'))
                    comision_val = row.get('comision_porcentaje_arriendo', row.get('COMISION_PORCENTAJE_ARRIENDO'))
                    print(f"  ID: {id_val}, Nombre: {nombre_val}, Comision: {comision_val}")
            
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("="*80)

if __name__ == "__main__":
    test_advisor_query()
