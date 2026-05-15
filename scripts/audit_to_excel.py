
import os
import sys
import pandas as pd

# Añadir el directorio raíz al path para importar desde migraciones
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from migraciones.database_config import get_database_connection, DB_MODE

def generate_excel_report():
    if DB_MODE != 'postgresql':
        print("ERROR: Este script requiere PostgreSQL (DB_MODE=postgresql)")
        return

    conn = get_database_connection()
    
    try:
        # Consulta para obtener los contratos de mandato y sus arriendos
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
        
        # Usar pandas para leer la SQL directamente
        df = pd.read_sql(query, conn)
        
        # Renombrar columnas para el reporte
        df.columns = [
            'ID_M', 'ID_A', 
            'Inicio Mandato', 'Inicio Arriendo', 
            'Fin Mandato', 'Fin Arriendo'
        ]
        
        # Función para determinar coincidencia
        def determinar_coincidencia(row):
            if pd.isna(row['ID_A']):
                return "Sin Arriendo"
            
            inicio_m = str(row['Inicio Mandato']) if row['Inicio Mandato'] else "N/A"
            inicio_a = str(row['Inicio Arriendo']) if row['Inicio Arriendo'] else "N/A"
            fin_m = str(row['Fin Mandato']) if row['Fin Mandato'] else "N/A"
            fin_a = str(row['Fin Arriendo']) if row['Fin Arriendo'] else "N/A"
            
            match_inicio = (inicio_m == inicio_a) and (inicio_m != "N/A")
            match_fin = (fin_m == fin_a) and (fin_m != "N/A")
            
            if match_inicio and match_fin:
                return "Total"
            elif match_inicio:
                return "Parcial (Solo Inicio)"
            elif match_fin:
                return "Parcial (Solo Fin)"
            else:
                return "Ninguna"

        # Aplicar lógica de coincidencia
        df['Coincidencia'] = df.apply(determinar_coincidencia, axis=1)
        
        # Formatear fechas como string para el Excel
        for col in ['Inicio Mandato', 'Inicio Arriendo', 'Fin Mandato', 'Fin Arriendo']:
            df[col] = df[col].astype(str).replace('None', 'N/A').replace('NaT', 'N/A')

        # Guardar en la raíz del proyecto
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output_path = os.path.join(root_dir, "reporte_coincidencia_contratos.xlsx")
        
        # Exportar a Excel
        df.to_excel(output_path, index=False, engine='openpyxl')
            
        print(f"Reporte Excel generado exitosamente en: {output_path}")

    except Exception as e:
        print(f"Error durante la generación del Excel: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    generate_excel_report()
