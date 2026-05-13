import os
import sys

# Añadir la raíz del proyecto al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.infraestructura.persistencia.database import db_manager

def verify_trigger():
    print("Iniciando validación del trigger de sincronización de fechas...")
    
    # Datos identificados previamente
    id_propiedad = 100012
    id_contrato_a = 113
    id_contrato_m = 21
    
    nueva_fecha_inicio = '2026-05-15'
    nueva_fecha_fin = '2027-05-15'
    
    conn = db_manager.obtener_conexion()
    cursor = conn.cursor()
    
    try:
        # 1. Consultar estado inicial
        cursor.execute("SELECT FECHA_INICIO_CONTRATO_M, FECHA_FIN_CONTRATO_M FROM CONTRATOS_MANDATOS WHERE ID_CONTRATO_M = %s", (id_contrato_m,))
        mandato_inicial = cursor.fetchone()
        print(f"Mandato inicial: {mandato_inicial}")
        
        # 2. Actualizar fechas del contrato de arrendamiento
        print(f"Actualizando Contrato de Arrendamiento #{id_contrato_a} con fechas {nueva_fecha_inicio} a {nueva_fecha_fin}...")
        cursor.execute("""
            UPDATE CONTRATOS_ARRENDAMIENTOS 
            SET FECHA_INICIO_CONTRATO_A = %s, FECHA_FIN_CONTRATO_A = %s, UPDATED_BY = 'TEST_TRIGGER_GEMINI'
            WHERE ID_CONTRATO_A = %s
        """, (nueva_fecha_inicio, nueva_fecha_fin, id_contrato_a))
        
        # 3. Verificar sincronización en el mandato
        cursor.execute("SELECT FECHA_INICIO_CONTRATO_M, FECHA_FIN_CONTRATO_M FROM CONTRATOS_MANDATOS WHERE ID_CONTRATO_M = %s", (id_contrato_m,))
        mandato_final = cursor.fetchone()
        print(f"Mandato final: {mandato_final}")
        
        if mandato_final['FECHA_INICIO_CONTRATO_M'] == nueva_fecha_inicio and mandato_final['FECHA_FIN_CONTRATO_M'] == nueva_fecha_fin:
            print("¡VALIDACIÓN EXITOSA! Las fechas del mandato se sincronizaron automáticamente.")
        else:
            print("FALLO EN LA VALIDACIÓN: Las fechas del mandato no coinciden con las nuevas fechas del arrendamiento.")
            
        # Revertir cambios para no alterar la data real permanentemente
        print("Revirtiendo cambios para mantener integridad de datos...")
        cursor.execute("""
            UPDATE CONTRATOS_ARRENDAMIENTOS 
            SET FECHA_INICIO_CONTRATO_A = %s, FECHA_FIN_CONTRATO_A = %s, UPDATED_BY = 'REVERT_TEST_GEMINI'
            WHERE ID_CONTRATO_A = %s
        """, (mandato_inicial['FECHA_INICIO_CONTRATO_M'], mandato_inicial['FECHA_FIN_CONTRATO_M'], id_contrato_a))
        
        # Nota: El trigger también revertirá el mandato al revertir el arriendo (si las fechas coinciden exactamente)
        # Pero por seguridad forzamos la vuelta al estado original si el trigger falló o algo pasó
        cursor.execute("""
            UPDATE CONTRATOS_MANDATOS
            SET FECHA_INICIO_CONTRATO_M = %s, FECHA_FIN_CONTRATO_M = %s
            WHERE ID_CONTRATO_M = %s
        """, (mandato_inicial['FECHA_INICIO_CONTRATO_M'], mandato_inicial['FECHA_FIN_CONTRATO_M'], id_contrato_m))
        
        conn.commit()
        print("Cambios revertidos y transacción confirmada.")

    except Exception as e:
        conn.rollback()
        print(f"ERROR durante la validación: {e}")
    finally:
        cursor.close()
        # db_manager maneja el cierre del pool al finalizar el script

if __name__ == "__main__":
    verify_trigger()
