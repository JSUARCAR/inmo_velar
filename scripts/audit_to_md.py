
import os
import sys

# Añadir el directorio raíz al path para importar desde migraciones
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from migraciones.database_config import get_database_connection, DB_MODE

def generate_md_report():
    if DB_MODE != 'postgresql':
        print("ERROR: Este script requiere PostgreSQL (DB_MODE=postgresql)")
        return

    conn = get_database_connection()
    cursor = conn.cursor()
    
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
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        # Construir el contenido Markdown
        md_content = "# Reporte de Coincidencia de Fechas (Mandato vs Arriendo)\n\n"
        md_content += "| ID_M | ID_A | Inicio Mandato | Inicio Arriendo | Fin Mandato | Fin Arriendo | Coincidencia |\n"
        md_content += "| :--- | :--- | :--- | :--- | :--- | :--- | :--- |\n"
        
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
                    
            md_content += f"| {id_m} | {id_a} | {inicio_m} | {inicio_a} | {fin_m} | {fin_a} | {coincidencia} |\n"

        # Guardar en la raíz del proyecto
        # Buscamos la ruta raíz correcta (un nivel arriba de scripts/)
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output_path = os.path.join(root_dir, "reporte_coincidencia_contratos.md")
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(md_content)
            
        print(f"Reporte generado exitosamente en: {output_path}")

    except Exception as e:
        print(f"Error durante la auditoría: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    generate_md_report()
