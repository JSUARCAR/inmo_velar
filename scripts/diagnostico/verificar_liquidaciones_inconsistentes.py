import sys
import os
import decimal

# Asegurar que el path incluya el directorio raíz para importar migraciones.database_config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from migraciones.database_config import get_database_connection

def verificar_liquidaciones():
    print("=== VERIFICANDO LIQUIDACIONES INCONSISTENTES ===")
    conn = get_database_connection()
    cursor = conn.cursor()
    
    query = """
    SELECT 
        l.ID_LIQUIDACION,
        l.VALOR_INCIDENTES,
        l.NETO_A_PAGAR,
        (l.TOTAL_INGRESOS - l.TOTAL_EGRESOS - COALESCE(l.VALOR_INCIDENTES, 0)) as NETO_CORRECTO,
        ABS(l.NETO_A_PAGAR - (l.TOTAL_INGRESOS - l.TOTAL_EGRESOS - COALESCE(l.VALOR_INCIDENTES, 0))) as DIFERENCIA
    FROM LIQUIDACIONES l
    WHERE ABS(l.NETO_A_PAGAR - (l.TOTAL_INGRESOS - l.TOTAL_EGRESOS - COALESCE(l.VALOR_INCIDENTES, 0))) > 0.01
    ORDER BY DIFERENCIA DESC;
    """
    
    try:
        cursor.execute(query)
        inconsistentes = cursor.fetchall()
        
        if not inconsistentes:
            print("✅ No se encontraron liquidaciones con inconsistencias.")
        else:
            print(f"⚠️ Se encontraron {len(inconsistentes)} liquidaciones inconsistentes:")
            print(f"{'ID':<10} | {'V. INCIDENTES':<15} | {'NETO A PAGAR':<15} | {'NETO CORRECTO':<15} | {'DIFERENCIA':<15}")
            print("-" * 80)
            for row in inconsistentes:
                id_liq = row[0]
                valor_inc = float(row[1]) if row[1] is not None else 0.0
                neto_pagar = float(row[2]) if row[2] is not None else 0.0
                neto_correcto = float(row[3]) if row[3] is not None else 0.0
                diferencia = float(row[4]) if row[4] is not None else 0.0
                print(f"{id_liq:<10} | ${valor_inc:<14.2f} | ${neto_pagar:<14.2f} | ${neto_correcto:<14.2f} | ${diferencia:<14.2f}")
    except Exception as e:
        print(f"Error al verificar liquidaciones: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    verificar_liquidaciones()
