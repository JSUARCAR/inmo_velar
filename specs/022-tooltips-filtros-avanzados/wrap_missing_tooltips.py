import os
import re

pages_dir = r'C:\Users\PC\OneDrive\Desktop\inmobiliaria velar\PYTHON-REFLEX\src\presentacion_reflex\pages'

for root, _, files in os.walk(pages_dir):
    for file in files:
        if not file.endswith('.py'):
            continue
        filepath = os.path.join(root, file)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        changed = False

        # Find buttons with rx.icon("x", ...) not already wrapped in neuro_tooltip
        # A simple string search/replace for common patterns
        
        # Pattern 1: Limpiar Filtros
        limpiar_pattern = r'(\s*)neuro_button\(\s*rx\.icon\("x",.*?\),\s*on_click=\w+\.clear_filters,.*?\),'
        if re.search(limpiar_pattern, content, re.DOTALL):
            # Make sure it's not already wrapped
            def wrap_limpiar(m):
                indent = m.group(1)
                inner = m.group(0).strip()
                return f'{indent}neuro_tooltip(\n{indent}    {inner}\n{indent}    text="Limpiar filtros",\n{indent}),'
            
            # but wait, I can't just replace safely if it's already wrapped
            if "text=\"Limpiar filtros\"" not in content:
                content = re.sub(r'(\s*)(neuro_button\(\s*rx\.icon\("x"[^)]*\),\s*on_click=[^)]+\.clear_filters,[\s\S]*?\n\s*\)),', wrap_limpiar, content)
                changed = True

        # Pattern 2: Refresh
        refresh_pattern = r'(\s*)(neuro_button\(\s*rx\.icon\("refresh-cw"[^)]*\),\s*on_click=[^)]+,\n\s*\)),'
        if re.search(refresh_pattern, content, re.DOTALL):
            def wrap_refresh(m):
                indent = m.group(1)
                inner = m.group(2)
                return f'{indent}neuro_tooltip(\n{indent}    {inner},\n{indent}    text="Recargar datos",\n{indent}),'
            
            if "text=\"Recargar datos\"" not in content:
                content = re.sub(refresh_pattern, wrap_refresh, content)
                changed = True

        if changed:
            # check imports
            if 'from src.presentacion_reflex.components.neuro_elements import (' in content:
                if 'neuro_tooltip' not in content:
                    content = content.replace(
                        'from src.presentacion_reflex.components.neuro_elements import (',
                        'from src.presentacion_reflex.components.neuro_elements import (\n    neuro_tooltip,'
                    )
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f'Wrapped missing tooltips in {file}')
