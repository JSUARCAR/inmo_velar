# Phase 0: Research & Technical Decisions

**Feature**: playwright-validation
**Date**: 2026-07-03

## Research Tasks Resolved

### 1. Manejo de Credenciales y Zero Leak
**Decision**: Utilizar variables de entorno (`PLAYWRIGHT_TEST_USER`, `PLAYWRIGHT_TEST_PASSWORD`) y una fixture de `pytest` (en `conftest.py`) que inyecte de manera segura las credenciales sin imprimirlas nunca en los reportes de consola ni trazas de Playwright en texto plano.
**Rationale**: El mandato 4 de la Constitución exige cero filtraciones. Los passwords no deben quemarse en código ni aparecer en `print()`.
**Alternatives considered**: Usar un archivo de configuración local cifrado, pero las variables de entorno son más estándar para integraciones CI/CD.

### 2. Formato de Recolección de Evidencia
**Decision**: Activar la grabación de trazas (Playwright Tracing) al primer reintento fallido, y tomar screenshots en puntos críticos de validación (ej. cuando se muestra el plan de pago, o se abre el modal).
**Rationale**: Playwright Traces contiene un volcado de DOM, capturas de red y consola para diagnóstico exhaustivo ("Evidencia como Dato").
**Alternatives considered**: Hacer solo grabaciones en video (muy pesadas y sin el contexto de la consola de red) o capturas de pantalla estáticas (insuficientes para debugear flujos HTTP asíncronos).

### 3. Aislamiento del Test Destructivo (Eliminar Liquidación)
**Decision**: Confiar en la propiedad especificada en el Spec ("Calle Falsa 123 - Test Renov") como Sandbox. El test navegará a esta liquidación, verificará la habilitación del botón "Eliminar", interactuará con el modal y asertará la petición a red (interceptando el Response).
**Rationale**: Clarificación explícita recibida; es un entorno de pruebas seguro. No se requiere rollback manual de base de datos.
**Alternatives considered**: Interceptar la petición de borrado (Mocking) abortando el request, pero esto no probaría la integración real E2E backend-base de datos.

## Best Practices Established

1. **Localizadores Robustos**: Preferir `page.get_by_role()`, `page.get_by_text()` y selectores visibles para evitar que los tests se rompan si Reflex cambia los IDs/clases autogenerados de Radix UI.
2. **Espera de Estado**: Usar `expect(locator).to_be_visible()` y `page.wait_for_response()` en lugar de sleeps fijos explícitos (ej. `time.sleep()`), que generan flakiness.
3. **Manejo de Modales Reflex**: Considerar que los Modales/Popovers de Radix UI en Reflex utilizan Portals. A veces el overlay bloquea el clic si se intenta automatizar demasiado rápido. Es necesario esperar a que el estado visual de la transición CSS (ej. `opacity: 1`) finalice o hacer clic forzado (`force=True`) solo cuando esté justificado.
