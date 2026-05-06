import os

file_path = r'src/aplicacion/servicios/servicio_contratos.py'

# Query WITHOUT aliases
clean_query = """        query = \"\"\"
        SELECT 
            CONTRATOS_MANDATOS.ID_CONTRATO_M,
            PROPIEDADES.ID_PROPIEDAD,
            PROPIEDADES.DIRECCION_PROPIEDAD, 
            PROPIEDADES.MATRICULA_INMOBILIARIA,
            CONTRATOS_MANDATOS.ID_PROPIETARIO,
            per_prop.NOMBRE_COMPLETO as NOMBRE_PROPIETARIO,
            CONTRATOS_MANDATOS.ID_ASESOR,
            per_ases.NOMBRE_COMPLETO as NOMBRE_ASESOR,
            CONTRATOS_MANDATOS.FECHA_INICIO_CONTRATO_M,
            CONTRATOS_MANDATOS.FECHA_FIN_CONTRATO_M,
            CONTRATOS_MANDATOS.DURACION_CONTRATO_M,
            CONTRATOS_MANDATOS.CANON_MANDATO,
            CONTRATOS_MANDATOS.COMISION_PORCENTAJE_CONTRATO_M,
            CONTRATOS_MANDATOS.ESTADO_CONTRATO_M,
            CONTRATOS_MANDATOS.CREATED_AT,
            CONTRATOS_MANDATOS.CREATED_BY
        FROM CONTRATOS_MANDATOS
        JOIN PROPIEDADES ON CONTRATOS_MANDATOS.ID_PROPIEDAD = PROPIEDADES.ID_PROPIEDAD
        JOIN PROPIETARIOS ON CONTRATOS_MANDATOS.ID_PROPIETARIO = PROPIETARIOS.ID_PROPIETARIO
        JOIN PERSONAS per_prop ON PROPIETARIOS.ID_PERSONA = per_prop.ID_PERSONA
        JOIN ASESORES ON CONTRATOS_MANDATOS.ID_ASESOR = ASESORES.ID_ASESOR
        JOIN PERSONAS per_ases ON ASESORES.ID_PERSONA = per_ases.ID_PERSONA
        WHERE CONTRATOS_MANDATOS.ID_CONTRATO_M = ?
        \"\"\""""

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

start_marker = 'def obtener_detalle_mandato_ui(self, id_contrato: int) -> Optional[Dict[str, Any]]:'
end_marker = 'with self.db.obtener_conexion() as conn:'

start_idx = content.find(start_marker)
end_idx = content.find(end_marker, start_idx)

if start_idx != -1 and end_idx != -1:
    query_start = content.find('query = """', start_idx)
    query_end = content.rfind('"""', start_idx, end_idx) + 3
    
    if query_start != -1 and query_end != -1:
        print(f"Found query block from {query_start} to {query_end}")
        new_content = content[:query_start] + clean_query.strip() + content[query_end:]
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print("File updated with NO-ALIAS query.")
    else:
        print("Could not locate query block specifics.")
else:
    print("Could not locate function boundaries.")
