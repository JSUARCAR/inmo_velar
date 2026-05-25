import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from migraciones.database_config import get_database_connection

def run_remediation():
    conn = get_database_connection()
    cursor = conn.cursor()
    
    query_check = """
        SELECT ID_PROPIEDAD, DIRECCION_PROPIEDAD
        FROM PROPIEDADES p
        WHERE p.DISPONIBILIDAD_PROPIEDAD = FALSE
          AND NOT EXISTS (
              SELECT 1 FROM CONTRATOS_ARRENDAMIENTOS ca
              WHERE ca.ID_PROPIEDAD = p.ID_PROPIEDAD
                AND ca.ESTADO_CONTRATO_A = 'ACTIVO'
          )
    """
    try:
        cursor.execute(query_check)
        rows = cursor.fetchall()
        print(f"Propiedades ocupadas sin arrendamiento activo encontradas: {len(rows)}")
        
        if len(rows) > 0:
            for row in rows:
                print(f" - Corrigiendo ID_PROPIEDAD {row[0]}")
                cursor.execute("UPDATE PROPIEDADES SET DISPONIBILIDAD_PROPIEDAD = TRUE WHERE ID_PROPIEDAD = %s", (row[0],))
            
            conn.commit()
            print("Corrección completada y guardada.")
        else:
            print("No se requiere corrección.")
            
    except Exception as e:
        print(f"Error ejecutando remedición: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    run_remediation()
