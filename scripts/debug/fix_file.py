import os

file_path = r'src/aplicacion/servicios/servicio_contratos.py'

clean_query = """        query = \"\"\"
        SELECT 
            m.ID_CONTRATO_M,
            p.ID_PROPIEDAD,
            p.DIRECCION_PROPIEDAD, 
            p.MATRICULA_INMOBILIARIA,
            m.ID_PROPIETARIO,
            per_prop.NOMBRE_COMPLETO as NOMBRE_PROPIETARIO,
            m.ID_ASESOR,
            per_ases.NOMBRE_COMPLETO as NOMBRE_ASESOR,
            m.FECHA_INICIO_CONTRATO_M,
            m.FECHA_FIN_CONTRATO_M,
            m.DURACION_CONTRATO_M,
            m.CANON_MANDATO,
            m.COMISION_PORCENTAJE_CONTRATO_M,
            m.ESTADO_CONTRATO_M,
            m.CREATED_AT,
            m.CREATED_BY
        FROM CONTRATOS_MANDATOS m
        JOIN PROPIEDADES p ON m.ID_PROPIEDAD = p.ID_PROPIEDAD
        JOIN PROPIETARIOS rp ON m.ID_PROPIETARIO = rp.ID_PROPIEDARIO
        JOIN PERSONAS per_prop ON rp.ID_PERSONA = per_prop.ID_PERSONA
        JOIN ASESORES ra ON m.ID_ASESOR = ra.ID_ASESOR
        JOIN PERSONAS per_ases ON ra.ID_PERSONA = per_ases.ID_PERSONA
        WHERE m.ID_CONTRATO_M = ?
        \"\"\""""

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Identify start and end of the block to replace
start_marker = 'def obtener_detalle_mandato_ui(self, id_contrato: int) -> Optional[Dict[str, Any]]:'
end_marker = 'with self.db.obtener_conexion() as conn:'

start_idx = content.find(start_marker)
end_idx = content.find(end_marker, start_idx)

if start_idx != -1 and end_idx != -1:
    # Find the query assignment inside this block
    # We want to replace everything from `        query = """` up to the line before `with self...`
    
    # Locate `query = """` after start_marker
    query_start = content.find('query = """', start_idx)
    
    # Locate the closing `"""` before end_marker
    # We need to be careful. The query ends with `"""` and newline.
    # We can just look for the last `"""` before `end_marker`
    query_end = content.rfind('"""', start_idx, end_idx) + 3
    
    if query_start != -1 and query_end != -1:
        print(f"Found query block from {query_start} to {query_end}")
        
        # Construct new content
        new_content = content[:query_start] + clean_query.strip() + content[query_end:]
        
        # Verify if it looks right (basic check)
        # print(new_content[query_start:query_start+len(clean_query)+50])
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("File updated successfully.")
    else:
        print("Could not locate query block specifics.")
else:
    print("Could not locate function boundaries.")
