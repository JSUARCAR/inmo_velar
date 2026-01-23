import re
import sys

file_path = r'src/aplicacion/servicios/servicio_contratos.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

start_marker = 'def obtener_detalle_mandato_ui(self, id_contrato: int) -> Optional[Dict[str, Any]]:'
query_start_marker = 'query = """'
end_marker = '"""'

block_start = content.find(start_marker)
if block_start == -1: sys.exit("Function not found")

query_start = content.find(query_start_marker, block_start)
if query_start == -1: sys.exit("Query start not found")
query_start += len(query_start_marker)

query_end = content.find(end_marker, query_start)
if query_end == -1: sys.exit("Query end not found")

extracted_query = content[query_start:query_end]

# Replace ? with 1 for testing
runnable_query = extracted_query.replace('?', '1')

with open('debug_query.sql', 'w', encoding='utf-8') as f:
    f.write(runnable_query)

print("Query extracted to debug_query.sql")
