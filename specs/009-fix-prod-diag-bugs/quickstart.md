# Quickstart & Validation Guide: fix-prod-diag-bugs

## Propósito
Esta guía provee las instrucciones exactas para validar que las correcciones sobre la saturación de websockets, el fallo de modales y el bloqueo de interacciones funcionan en el entorno local antes de hacer el merge y despliegue a Railway.

## Prerrequisitos
- Base de datos PostgreSQL local corriendo (o variable de entorno local configurada hacia la de producción temporalmente en modo lectura).
- Entorno local activo: `source .venv/bin/activate` (o equivalente en Windows).

## Paso 1: Ejecutar el Script de Backfill
Para validar la mitigación de los nulos:
```bash
python scripts/diagnostico/backfill_liquidaciones_nulas.py
```
- **Resultado Esperado**: El script debe conectarse, reportar cuántos registros tenían campos nulos, actualizarlos y cerrar. No debe haber errores.

## Paso 2: Validación Visual (Reflex App)
Inicia la aplicación de Reflex localmente:
```bash
reflex run
```
1. Ingresa a `http://localhost:3000/incidentes`
2. **Validación de Paginación**: La tabla debe cargar inmediatamente. En la parte inferior, deberías ver botones de "Anterior" y "Siguiente". Verifica que al cambiar de página, los datos cambien sin desconectar la aplicación.
3. Ingresa a `http://localhost:3000/liquidaciones`
4. **Validación Modal**: Haz clic en el botón Editar de una fila. El modal debe abrirse instantáneamente (el DTO ahora procesa los valores de forma defensiva y el backfill los limpió).
5. **Validación Punteros**: Cierra el modal e intenta hacer hover/click sobre el botón "Eliminar". Si el ratón cambia de forma y logra iniciar el Popover de confirmación, el override `pointer-events: auto` fue inyectado correctamente en el estado global.

## Paso 3: Validación Automática
Ejecuta la suite E2E de Playwright que fallaba previamente:
```bash
# Setear variables de entorno (pueden apuntar a DB de desarrollo si el puerto del backend es distinto)
$env:PLAYWRIGHT_PROD_USER="jsuarcar"
$env:PLAYWRIGHT_PROD_PASS="velarjoan2026"

pytest tests/diagnostics/test_prod_diag.py --headed --slowmo=500 -v -s
```
- **Resultado Esperado**: Las 3 pruebas deben pasar (100% SUCCESS) ya que los selectores y la estabilidad visual han sido reparados.
