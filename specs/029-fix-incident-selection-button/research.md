# Research: fix-incident-selection-button

**Date**: 2026-07-06 | **Branch**: `029-fix-incident-selection-button`

## Resumen de Investigación

Se realizó ingeniería inversa completa del flujo de selección de incidentes en el módulo de Liquidaciones.

---

## Hallazgo 1: Incompatibilidad de Firma — `justificacion` Faltante

- **Decision**: Corregir la llamada al servicio en `liquidaciones_state.py` L2136-2142 para incluir el parámetro `justificacion`.
- **Rationale**: La firma del método `ServicioIncidenteLiquidacion.asociar_incidente()` requiere 6 parámetros posicionales incluyendo `justificacion: str` (L162-170 del servicio). El handler del state solo pasa 5 parámetros, lo que genera un `TypeError` en runtime que se captura en el `except` genérico y muestra un error opaco al usuario.
- **Alternatives considered**:
  - Hacer `justificacion` opcional en el servicio → Rechazado: viola regla de negocio documentada.
  - Generar un valor por defecto en el state → **Seleccionado**: usar `f"Asociación desde liquidación {id_liquidacion}"` como justificación automática.

## Hallazgo 2: Botón Ausente en Formulario de Creación

- **Decision**: NO agregar el botón al formulario de creación en esta iteración.
- **Rationale**: Asociar incidentes requiere un `id_liquidacion` válido (existente en BD). Durante la creación, la liquidación aún no tiene ID. Agregar esta funcionalidad implicaría un flujo de 2 pasos (crear → guardar → abrir selector) que es complejo y fuera del alcance del fix de regresión.
- **Alternatives considered**:
  - Crear la liquidación primero y luego abrir el modal → Complejidad adicional innecesaria para un fix.
  - Usar un ID temporal → Rechazado: rompe la integridad referencial en PostgreSQL.

## Hallazgo 3: Rendering del Botón en Formulario de Edición

- **Decision**: El botón está presente en el código (`liquidacion_edit_form.py` L151-163) y se renderiza incondicionalmente cuando `show_edit_modal` es `True`.
- **Rationale**: La regresión no es de renderizado sino de **ejecución**. El botón sí se muestra, pero al hacer clic, el handler `open_seleccion_incidentes_modal` falla debido al bug de firma (Hallazgo 1). Sin embargo, el error se captura silenciosamente y no hay feedback visible.
- **Alternatives considered**: N/A — confirmado por inspección de código.

## Hallazgo 4: Problemas Potenciales de `pointer-events` en Dialog Anidado

- **Decision**: Verificar en vivo si el modal de incidentes (Dialog dentro de Dialog) hereda `pointer-events: none` del DismissableLayer de Radix UI.
- **Rationale**: El componente `modal_seleccion_incidentes.py` L192 ya tiene `"pointer_events": "auto"` aplicado. Esto debería funcionar según el protocolo de Portals del proyecto (Constitution §16).
- **Alternatives considered**: N/A — ya implementado correctamente.

## Hallazgo 5: Conexión No Liberada en Handler

- **Decision**: Refactorizar el handler `open_seleccion_incidentes_modal` para usar context manager `with` en la conexión de BD.
- **Rationale**: En L1973, la conexión se obtiene con `conn = dm.obtener_conexion()` sin `with`, lo que puede dejar conexiones abiertas si ocurre un error antes del cierre. El patrón correcto en el proyecto es `with db_manager.obtener_conexion() as conn:`.
- **Alternatives considered**: N/A — es un fix de higiene obligatorio.

---

## Matriz de Impacto

| Archivo | Tipo de Cambio | Líneas Afectadas | Riesgo |
|---------|---------------|------------------|--------|
| `liquidaciones_state.py` | Fix firma + justificación | L2136-2142 | Bajo |
| `liquidaciones_state.py` | Fix conexión sin `with` | L1973-1998 | Bajo |
| `liquidacion_edit_form.py` | Sin cambios necesarios | N/A | Ninguno |
| `modal_seleccion_incidentes.py` | Sin cambios necesarios | N/A | Ninguno |
| `servicio_incidente_liquidacion.py` | Sin cambios necesarios | N/A | Ninguno |

## Decisiones Clave

1. **No modificar la firma del servicio** — la justificación es un requisito de negocio válido.
2. **No agregar el botón al formulario de creación** — fuera de alcance para este fix.
3. **Cambios mínimos y quirúrgicos** — solo 2 bloques de código en 1 archivo.
