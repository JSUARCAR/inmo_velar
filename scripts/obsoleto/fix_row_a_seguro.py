"""Fix _row_a_seguro method to use dict access"""
import re

file_path = r"src\infraestructura\persistencia\repositorio_seguro_sqlite.py"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the _row_a_seguro method
old_method = r'''    def _row_a_seguro\(self, row: tuple\) -> Seguro:
        """
        Convierte una fila de la BD a entidad Seguro.
        
        Args:
            row: Tupla con datos de la BD
            
        Returns:
            Entidad Seguro
        """
        return Seguro\(
            id_seguro=row\[0\],
            nombre_seguro=row\[1\],
            fecha_inicio_seguro=row\[2\],
            porcentaje_seguro=row\[3\],
            estado_seguro=row\[4\],
            fecha_ingreso_seguro=row\[5\],
            motivo_inactivacion=row\[6\],
            created_at=row\[7\],
            created_by=row\[8\],
            updated_at=row\[9\],
            updated_by=row\[10\]
        \)'''

new_method = '''    def _row_a_seguro(self, row) -> Seguro:
        """
        Convierte una fila de la BD a entidad Seguro.
        
        Args:
            row: Dict con datos de la BD
            
        Returns:
            Entidad Seguro
        """
        # Manejo flexible de diccionarios
        if hasattr(row, 'keys'):
            data = dict(row)
        else:
            data = dict(row)
        
        # Helper para obtener valor ignorando mayúsculas/minúsculas
        def get_val(key):
            return data.get(key) or data.get(key.upper()) or data.get(key.lower())
        
        return Seguro(
            id_seguro=get_val('ID_SEGURO'),
            nombre_seguro=get_val('NOMBRE_SEGURO'),
            fecha_inicio_seguro=get_val('FECHA_INICIO_SEGURO'),
            porcentaje_seguro=get_val('PORCENTAJE_SEGURO'),
            estado_seguro=get_val('ESTADO_SEGURO'),
            fecha_ingreso_seguro=get_val('FECHA_INGRESO_SEGURO'),
            motivo_inactivacion=get_val('MOTIVO_INACTIVACION'),
            created_at=get_val('CREATED_AT'),
            created_by=get_val('CREATED_BY'),
            updated_at=get_val('UPDATED_AT'),
            updated_by=get_val('UPDATED_BY')
        )'''

content = re.sub(old_method, new_method, content, flags=re.MULTILINE)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Fixed _row_a_seguro method")
