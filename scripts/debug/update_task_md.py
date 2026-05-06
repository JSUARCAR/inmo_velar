
import os

file_path = "task.md"
new_content = """
## Fase 16: Filtros Avanzados para Dashboard (Implementación Completada)

### Fase 16.1: Análisis y Diseño
- [x] Analizar métodos de ServicioDashboard para parametrización
- [x] Diseñar UI para componente `DashboardFilters` (Mes, Año, Asesor)

### Fase 16.2: Backend - Adaptación de Servicio
- [x] Modificar `obtener_flujo_caja_mes` para aceptar filtros (Mes, Año, Asesor)
- [x] Modificar `obtener_total_contratos_activos` para aceptar filtros (Asesor)
- [x] Modificar `obtener_comisiones_pendientes` para aceptar filtros (Asesor)
- [x] Modificar `obtener_tasa_ocupacion` para aceptar filtros (Asesor)

### Fase 16.3: Frontend - Componentes y Vistas
- [x] Crear componente `src/presentacion/components/dashboard_filters.py`
- [x] Integrar `DashboardFilters` en `dashboard_view.py`
- [x] Implementar lógica de actualización en `refrescar_dashboard`
- [x] Conectar botón "Aplicar" con recarga de datos

### Fase 16.4: Verificación
- [x] Validar filtro por Fecha (Mes/Año pasados)
- [x] Validar filtro por Asesor (Contratos propios)
- [x] Validar limpieza de filtros (Reset a global)
"""

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find the start of the section
try:
    start_index = -1
    for i, line in enumerate(lines):
        if "## Fase 16:" in line:
            start_index = i
            break
            
    if start_index != -1:
        # Keep everything before section 16
        final_lines = lines[:start_index]
        # Append new content
        final_lines.append(new_content)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(final_lines)
            
        print("Successfully updated task.md")
    else:
        print("Could not find section 16 start. Appending to end.")
        with open(file_path, 'a', encoding='utf-8') as f:
            f.write("\n" + new_content)

except Exception as e:
    print(f"Error: {e}")
