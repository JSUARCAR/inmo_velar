import os
import re

pages_dir = r'C:\Users\PC\OneDrive\Desktop\inmobiliaria velar\PYTHON-REFLEX\src\presentacion_reflex\pages'

infinitive_map = {
    'Exportar Periodo (ZIP)': 'Exportar periodo en ZIP',
    'Exportar Datos': 'Exportar datos',
    'Exportar CSV': 'Exportar a CSV',
    'Exportar EXCEL': 'Exportar a EXCEL',
    'Ver Detalles': 'Ver detalles',
    'Editar': 'Editar registro',
    'Eliminar': 'Eliminar registro',
    'Generar PDF': 'Generar archivo PDF',
    'Nueva Liquidación': 'Crear nueva liquidación',
    'Masiva': 'Crear registros masivos',
    'Actualizar': 'Recargar datos',
    'Registrar Pago': 'Registrar un nuevo pago',
    'Generar Pagos Masivos': 'Generar pagos masivos',
    'Limpiar Filtros': 'Limpiar filtros de búsqueda',
    'Pagar': 'Pagar',
    'Anular': 'Anular'
}

for root, _, files in os.walk(pages_dir):
    for file in files:
        if not file.endswith('.py'):
            continue
        filepath = os.path.join(root, file)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        changed = False

        if 'rx.tooltip(' in content:
            content = content.replace('rx.tooltip(', 'neuro_tooltip(')
            changed = True
            
        def replace_content(match):
            val = match.group(1)
            new_val = infinitive_map.get(val, val)
            return f'text="{new_val}"'

        if changed:
            content = re.sub(r'content="([^"]+)"', replace_content, content)

        if changed:
            if 'from src.presentacion_reflex.components.neuro_elements import (' in content:
                if 'neuro_tooltip' not in content:
                    content = content.replace(
                        'from src.presentacion_reflex.components.neuro_elements import (',
                        'from src.presentacion_reflex.components.neuro_elements import (\n    neuro_tooltip,'
                    )
            elif 'from src.presentacion_reflex.components.neuro_elements import ' in content:
                if 'neuro_tooltip' not in content:
                    content = content.replace(
                        'from src.presentacion_reflex.components.neuro_elements import ',
                        'from src.presentacion_reflex.components.neuro_elements import neuro_tooltip, '
                    )

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f'Updated {file}')
