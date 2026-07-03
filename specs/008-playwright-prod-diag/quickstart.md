# Quickstart: Diagnóstico en Producción

Sigue estos pasos para ejecutar la validación y obtener el diagnóstico del entorno de producción.

## 1. Configurar Credenciales (Zero Leak)

Antes de ejecutar la prueba, configura las credenciales de producción proporcionadas de forma temporal en tu terminal (PowerShell):

```powershell
$env:PLAYWRIGHT_PROD_USER="jsuarcar"
$env:PLAYWRIGHT_PROD_PASS="velarjoan2026"
```

## 2. Ejecutar Diagnóstico en Modo Visible (Headed)

Ejecuta pytest apuntando al script de diagnóstico, inyectando los argumentos de Playwright para mostrar el navegador y habilitar un pequeño retraso para seguimiento visual:

```powershell
pytest tests/diagnostics/test_prod_diag.py --headed --slowmo=500 -v -s
```

*Nota: El flag `-s` permite que la salida de la consola (donde se imprimirán los errores de red y de JS interceptados) se muestre directamente en la terminal en tiempo real.*

## 3. Revisión de Resultados

Al finalizar, la terminal entregará el informe de:
- **Flujos exitosos**: Casos que lograron completar el escenario.
- **Flujos fallidos**: El script registrará las URLs que retornaron códigos de error, excepciones en la consola JS del navegador y componentes DOM ausentes (Timeouts), que servirán como evidencia para la comparación Local vs Prod.
