
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Añadir el directorio raíz al path para importar desde migraciones
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from migraciones.database_config import get_database_connection, DB_MODE

def run_audit():
    if DB_MODE != 'postgresql':
        print("ERROR: Este script requiere PostgreSQL (DB_MODE=postgresql)")
        return

    conn = get_database_connection()
    cursor = conn.cursor()
    
    try:
        # Consulta para obtener los contratos de mandato y sus arriendos (si existen)
        query = """
            SELECT 
                cm.ID_CONTRATO_M,
                ca.ID_CONTRATO_A,
                cm.FECHA_INICIO_CONTRATO_M,
                ca.FECHA_INICIO_CONTRATO_A,
                cm.FECHA_FIN_CONTRATO_M,
                ca.FECHA_FIN_CONTRATO_A
            FROM CONTRATOS_MANDATOS cm
            LEFT JOIN CONTRATOS_ARRENDAMIENTOS ca ON cm.ID_PROPIEDAD = ca.ID_PROPIEDAD
            ORDER BY cm.ID_CONTRATO_M, ca.ID_CONTRATO_A;
        """
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        # Preparar encabezado solicitado
        # ID_M	ID_A	Inicio Mandato	Inicio Arriendo	Fin Mandato	Fin Arriendo	Coincidencia
        header = f"{'ID_M':<6} | {'ID_A':<6} | {'Inicio Mandato':<14} | {'Inicio Arriendo':<15} | {'Fin Mandato':<14} | {'Fin Arriendo':<14} | {'Coincidencia':<20}"
        print(header)
        print("-" * len(header))
        
        for row in rows:
            id_m = row[0]
            id_a = row[1] if row[1] is not None else "N/A"
            
            inicio_m = str(row[2]) if row[2] else "N/A"
            inicio_a = str(row[3]) if row[3] else "N/A"
            fin_m = str(row[4]) if row[4] else "N/A"
            fin_a = str(row[5]) if row[5] else "N/A"
            
            coincidencia = ""
            
            if id_a == "N/A":
                coincidencia = "Sin Arriendo"
            else:
                match_inicio = (inicio_m == inicio_a) and (inicio_m != "N/A")
                match_fin = (fin_m == fin_a) and (fin_m != "N/A")
                
                if match_inicio and match_fin:
                    coincidencia = "Total"
                elif match_inicio:
                    coincidencia = "Parcial (Solo Inicio)"
                elif match_fin:
                    coincidencia = "Parcial (Solo Fin)"
                else:
                    coincidencia = "Ninguna"
                    
            print(f"{id_m:<6} | {id_a:<6} | {inicio_m:<14} | {inicio_a:<15} | {fin_m:<14} | {fin_a:<14} | {coincidencia:<20}")

    except Exception as e:
        print(f"Error durante la auditoría: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    run_audit()
