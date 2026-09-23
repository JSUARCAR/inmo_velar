# Research: Corrección del error de producción tras el inicio de sesión (TypeError en protección de rutas)

**Fecha**: 2026-09-23
**Feature**: [spec.md](spec.md)

## Objetivo

Resolver los desconocidos técnicos necesarios para diseñar la corrección de raíz del
`TypeError: NavigationGenerationMixin.end_navigation_generation() takes 1 positional argument but 2 were given`
que se muestra en producción como "An error occurred. Contact the website administrator.", sin violar la
constitución (§13: Reproducir → Localizar → Reducir → Corregir Raíz → **Blindar**).

La causa raíz ya está confirmada en el spec (Contexto): la línea `auth_state.py:215` invoca
`self.end_navigation_generation(gen_id)` pero la firma del mixin no recibe argumentos. La investigación
verifica el contrato del mixin, el estado de los tests existentes, el inventario de rutas protegidas y el
patrón de logging seguro requerido por FR-009, para que la Phase 1 (design) fije contratos verificables.

## Environment

- **Lenguaje / Runtime**: Python 3.11 en despliegue (`runtime.txt`); la máquina local usa Python 3.12.6.
- **Framework UI**: `reflex==0.8.28.post1` (definido en el catálogo de paquetes; feature 077).
- **Base de datos**: PostgreSQL vía `psycopg2-binary`; **sin** DML ni cambios de esquema (esta feature).
- **Testing**: `pytest` (asyncio auto), integraciones contra BD de prueba, E2E Playwright (`playwright@^1.60`).
- **Lint/Type**: `ruff` (E,F,I; line-length 100), `black` (line-length 100), `mypy`.

## Hallazgos

### Hallazgo 1 — Contrato verificado del `NavigationGenerationMixin` (`navigation_mixin.py`)

| Método | Firma real | Responsabilidad |
|--------|------------|-----------------|
| `start_navigation_generation` | `(self) -> str` | Asigna `current_generation = uuid4()` y `is_loading = True`; retorna el id |
| `end_navigation_generation` | `(self) -> None` | Solo restablece `is_loading = False`. **NO recibe argumentos** |
| `validate_generation` | `(self, generation_id: str) -> bool` | Compara `current_generation`; si no coincide, descarta (warning `[DROP]`) |
| `trigger_graceful_rollback` | `(self) -> list[rx.event.EventSpec]` | Toast + redirect a `/`; restablece `is_loading` |

- **Decision**: La corrección es únicamente la invocación `self.end_navigation_generation()` (sin argumento)
  en `auth_state.py:215`. Se verifica la firma real (sin argumentos) como fuente de verdad; el mixin NO cambia (FR-004).
- **Rationale**: El contrato del mixin es estable y compartido por `personas_state.py:341` y
  `alertas_dashboard_state.py:92`, que ya invocan el método correctamente sin argumento; el error es un
  solo llamador (`auth_state.py`).
- **Alternatives considered**: Pasar `gen_id` opcional al mixin → se descarta (rompería el contrato común
  y violaría FR-004; Chesterton's Fence, constitución §12).

### Hallazgo 2 — Los tests existentes codifican (y no detectan) la firma errónea

- `tests/unit/test_proteccion_rutas.py:15` **mockea** `end_navigation_generation` y además **afirma la firma
  errónea**: `mock_end.assert_called_with("test-gen-1")` (líneas 27 y 37). Un mock acepta cualquier llamada,
  por lo que el `TypeError` real no se manifiesta. Tras la corrección, esa aserción FALLARÁ (la llamada ya no
  lleva argumento) y debe actualizarse a `assert_called_once_with()`.
- `tests/integration/test_auth_login.py:106` también parchea `end_navigation_generation`; no puede servir
  como guardia contra la regresión de firma.
- **Decision**: El test de regresión dedicado (FR-008) DEBE ejercitar el **método real del mixin** (sin
  mockear `end_navigation_generation`), llamando `AuthState.require_login_background.fn(state, gen_id)` con
  `_validate_session` y `validate_generation` controlados, y verificar que termina sin `TypeError` y con
  `is_loading == False`. Además, actualizar las aserciones de los tests existentes (Hallazgo 2) al contrato correcto.
- **Rationale**: Blinda el contrato del mixin (constitución §13 "Corregir Raíz → **Blindar**") e impide que
  el `TypeError` reintroducido pase por greens falsos (mocks que aceptan cualquier firma).
- **Alternatives considered**: Confiar en la matriz E2E Playwright → insuficiente (SC-004/SC-006 exigen
  guardia en suite, y el deck Playwright no está ejecutable hoy, ver T042 pendiente de 077).

### Hallazgo 3 — Inventario de rutas protegidas (criterio objetivo de FR-003/SC-003)

Se considerará "ruta protegida" toda página cuyo `on_load` ejecuta `AuthState.require_login` (spec §FR-003).
Confirmadas por inspección del código (`grep "AuthState.require_login" src/presentacion_reflex/pages/`):
18 rutas: `/dashboard`, `/personas`, `/propiedades`, `/contratos`, `/liquidaciones`, `/liquidacion_asesores`,
`/recaudos`, `/recibos`, `/propiedad_horizontal`, `/usuarios`, `/seguros`, `/saldos_favor`, `/proveedores`,
`/incrementos`, `/incidentes`, `/desocupaciones`, `/configuracion`, `/auditoria`.

- **Decision**: El plan de validación (SC-003) usará este inventario de 18 rutas como universo mínimo de
  navegación automatizada; el criterio objetivo (cualquier `on_load` con `AuthState.require_login`) permite
  extenderlo si se añaden páginas nuevas.
- **Rationale**: El spec (Clarificación Q2) fijó el criterio objetivo y delegó la lista al plan, sin
  petrificar el inventario en el spec.
- **Alternatives considered**: Enumerar en el spec → descartada por decisión del usuario (Q2).

### Hallazgo 4 — FR-009 requiere un log de producción propio (el `_debug` no sirve)

`_debug` (`auth_state.py:33`) está gateado por `IS_PROD` (líneas 177 y 365 lo condicionan): en producción no
emite salida. Para corroborar la ausencia del `TypeError` (SC-002) se necesita una línea de log **de
producción**, segura (sin credenciales), siguiendo la plantilla ya existente `logger.error("Error de
validación de sesión...")` en `_validate_session` (líneas 182-185).

- **Decision**: Registrar el desenlace del protector en los dos caminos terminales de `require_login_background`
  (acceso permitido / acceso denegado → redirección) con `logger` de módulo y nivel informativo, **sin** ningún
  dato del usuario, token ni credencial; el desenlace "tarea descartada" (generación obsoleta) no requiere log
  (el mixin ya emite el warning `[DROP]`).
- **Rationale**: Hace medible SC-002 desde los logs de Railway sin exponer datos sensibles (protocolo Zero Leak,
  constitución §4) y sin añadir dependencias ni monitoreo activo (opción B elegida por el usuario en Q1).
- **Alternatives considered**: Monitoreo/alerta activa → descartada en clarify (Q1, opción C no elegida);
  reutilizar `_debug` → descartado (no emite en producción).

### Hallazgo 5 — Corrección de una línea, quirúrgica e idempotente

El fix es `self.end_navigation_generation(gen_id)` → `self.end_navigation_generation()` (`auth_state.py:215`).
`end_navigation_generation()` solo asigna `is_loading = False`, por lo que la invocación es idempotente
(llamar cuando ya es `False` no tiene efecto ni error) → no se añade guardia condicional ni escenario de doble
invocación en FR-008 (Clarificación Q3). El patrón existente `validate_generation(gen_id)` protegiendo la tarea
antes del llamado se conserva; el cambio no altera `validate_generation`, `_validate_session`, ni los demás
consumidores del mixin (FR-006/FR-007).

## Constitución / Gates (validados)

| Gate | Estado | Evidencia |
|------|--------|-----------|
| Sin Flet/SQLite en código nuevo | Cumple | Solo `presentacion_reflex/state/auth_state.py` + tests; transporte intocable |
| Idioma 100% español | Cumple | Textos canónicos y artefactos en español |
| Clean architecture (dependencia unidireccional) | Cumple | Cambio en presentación; sin capas nuevas |
| Tipado explícito + UPPER_SNAKE + docstrings Google | Cumple | Se respeta en el módulo y tests |
| Excepciones tipadas de dominio (no genéricas supresivas) | Cumple | No se añaden `except` nuevos |
| Persistencia PostgreSQL (%s, RETURNING, sin magic numbers) | N/A | Sin DML nuevo |
| Tests: dominio 100%, lógica nueva >90%, unit sin I/O | Cumple | TDD: unit del contrato (FR-008) sin I/O |
| Verificación en navegador + regresión visual | Cumple | E2E SC-003 sobre inventario (Hallazgo 3) |
| Zero leak + RBAC | Cumple | FR-009 sin credenciales (Hallazgo 4); RBAC no se modifica |
| Cirugía técnica (replace/sed sobre rewrite) | Cumple | 1 línea en `auth_state.py:215`; no se reescribe el estado |

## Unknowns resueltos

1. Contrato real del mixin → `end_navigation_generation(self)` sin argumentos (Hallazgo 1).
2. ¿Los tests actuales blindan contra la regresión de firma? → No; codifican y enmascaran la firma errónea (Hallazgo 2).
3. ¿Cuántas rutas protegidas y cuáles? → 18 confirmadas + criterio objetivo (Hallazgo 3).
4. ¿Cómo verificar SC-002 en producción sin fuga de datos? → log de producción seguro en el protector (Hallazgo 4).
5. ¿Alcance de la corrección? → 1 línea quirúrgica, idempotente, sin guardias (Hallazgo 5).