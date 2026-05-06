import os
import sys

# Añadir el raíz para poder importar los módulos de src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.infraestructura.persistencia.database import DatabaseManager

def aplicar_data_patch():
    db_manager = DatabaseManager()
    
    print("Iniciando FASE 1: Data Patch INC-18")
    
    try:
        with db_manager.transaccion() as conn:
            cursor = db_manager.get_dict_cursor(conn)
            
            # Paso A: Obtener la cotización aprobada para el incidente 18
            # Verificando además que sea LENARDO GAS, o simplemente la que esté 'Aprobada'
            query_cotizacion = """
                SELECT ID_COTIZACION, ID_PROVEEDOR, VALOR_TOTAL
                FROM COTIZACIONES
                WHERE ID_INCIDENTE = %s AND ESTADO_COTIZACION = 'Aprobada'
                LIMIT 1
            """
            cursor.execute(query_cotizacion, (18,))
            cotizacion = cursor.fetchone()
            
            if not cotizacion:
                print("FAIL FAST: No se encontró ninguna cotización 'Aprobada' vinculada al Incidente 18.")
                raise Exception("Operación abortada por integridad (FAIL FAST).")
            
            id_cotizacion = cotizacion["ID_COTIZACION"]
            id_proveedor = cotizacion["ID_PROVEEDOR"]
            valor_total = cotizacion["VALOR_TOTAL"]
            
            print(f"Cotización Aprobada Encontrada: ID={id_cotizacion}, Proveedor={id_proveedor}, Valor={valor_total}")
            
            # Paso B: Actualizar el incidente
            query_update = """
                UPDATE INCIDENTES
                SET ESTADO = 'Aprobado',
                    ID_COTIZACION_APROBADA = %s,
                    ID_PROVEEDOR_ASIGNADO = %s,
                    COSTO_INCIDENTE = %s,
                    UPDATED_AT = CURRENT_TIMESTAMP
                WHERE ID_INCIDENTE = %s AND ESTADO != 'Aprobado'
            """
            
            cursor.execute(query_update, (id_cotizacion, id_proveedor, valor_total, 18))
            
            if cursor.rowcount == 0:
                print("ADVERTENCIA: El incidente 18 ya está 'Aprobado' o no existe.")
            else:
                print("Paso B exitoso: INC-18 actualizado. Comiteando transacción (Unit of Work).")
                
    except Exception as e:
        print(f"ERROR DURANTE DATA PATCH: {e}")
        print("Rollback automático aplicado.")
        sys.exit(1)

if __name__ == "__main__":
    aplicar_data_patch()
