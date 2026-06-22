# Task 1 Report: Corrección de Case-Sensitivity en servicio_contratos.py

## What was implemented
- Se corrigió el error de case-sensitivity en `src/aplicacion/servicios/servicio_contratos.py`.
- En el método `obtener_kpis()`, se cambiaron los alias `ACTIVOs` e `inACTIVOs` por minúsculas `activos` e `inactivos` en las variables `query_mandatos` y `query_arriendos`.
- Se actualizó el acceso al diccionario devuelto de la base de datos para utilizar los nombres de clave corregidos en minúsculas en el diccionario de retorno.

## What was tested and test results
- Se ejecutó `python scripts/check_syntax.py`, obteniendo `Syntax OK`.
- Se ejecutó `python -m ruff check src/aplicacion/servicios/servicio_contratos.py`, confirmando que todas las reglas de linting pasaron.
- Se ejecutó `python -m black src/aplicacion/servicios/servicio_contratos.py`, lo cual aplicó el formato estándar al archivo (1 file reformatted).
- Al ejecutar `mypy`, se evidenció un error de configuración del proyecto independiente a este cambio (`Source file found twice under different module names: "aplicacion.servicios" and "src.aplicacion.servicios"`), lo cual impidió el análisis de tipos, pero al ser un error general no afecta la validez del cambio.

## Files changed
- `src/aplicacion/servicios/servicio_contratos.py`

## Self-review findings
- Completeness: Se implementó todo lo que especifica el brief. El cambio se alinea correctamente con la expectativa de la UI (que espera llaves en minúscula para evitar KPIs en 0).
- Quality: El código está limpio y `black` verificó el formateo correcto.
- Discipline: Solamente se afectó el método `obtener_kpis` resolviendo el requerimiento estricto de la tarea.
- Testing: Los chequeos sintácticos y de linters se completaron exitosamente, excluyendo el comportamiento ambiental ya existente de `mypy`.

## Any issues or concerns
- Existe un problema de resolución de módulos de Mypy en el proyecto en `src/aplicacion/servicios/__init__.py` debido a duplicidad de rutas detectada por mypy que debe resolverse en una tarea de configuración (`MYPYPATH` o `--explicit-package-bases`). Esto no concierne directamente al alcance de la tarea actual.
