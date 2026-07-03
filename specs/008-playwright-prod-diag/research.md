# Research: playwright-prod-diag

## 1. Captura de Tráfico de Red y Errores (Ingeniería Inversa)

**Decision**: Se utilizarán los event listeners integrados de Playwright (`page.on('response')`, `page.on('requestfailed')`, `page.on('console')`) dentro de las pruebas para capturar anomalías en tiempo real.

**Rationale**: Al estar diagnosticando un entorno de producción (caja negra), el DOM puede fallar en actualizarse debido a excepciones silenciosas en JS o endpoints que retornan 400/500, bloqueando el estado en Reflex. Capturar estos eventos permite adjuntarlos al reporte de diagnóstico.

**Alternatives considered**: 
- Utilizar el archivo HAR de Playwright: Rechazado por generar archivos binarios pesados que dificultan la inspección rápida, prefiriendo logs en consola/stdout filtrados para Reflex.

## 2. Ejecución Headed vs Headless

**Decision**: Se forzará el modo `headed=True` y se puede inyectar un retraso ligero (`slow_mo=500`) en la inicialización del contexto.

**Rationale**: Requisito explícito del usuario para poder visualizar el comportamiento asíncrono y los saltos de interfaz que ocurren en producción. El `slow_mo` compensará la latencia real y permitirá el renderizado visual completo de las animaciones Radix.

## 3. Manejo de Credenciales en Producción

**Decision**: Se inyectarán mediante variables de entorno `$env:PLAYWRIGHT_PROD_USER` y `$env:PLAYWRIGHT_PROD_PASS`, en lugar de plasmarlas en código.

**Rationale**: Cumplimiento del mandato Zero Leak del `constitution.md`.
