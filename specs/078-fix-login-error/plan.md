# Implementation Plan: Corrección del error de producción tras el inicio de sesión (TypeError en protección de rutas)

**Branch**: `bugfix/078-fix-login-error` | **Date**: 2026-09-23 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/078-fix-login-error/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Corregir de raíz la regresión de firma introducida por la feature 077: `auth_state.py:215` invoca
`self.end_navigation_generation(gen_id)` pero `NavigationGenerationMixin.end_navigation_generation()`
(`navigation_mixin.py:22`) NO recibe argumentos. En producción cada `on_load` de ruta protegida dispara
`require_login_background`, que lanza `TypeError` → Reflex muestra "An error occurred. Contact the website
administrator." y deja el sistema inoperable tras el login. La feature requiere (a) la corrección quirúrgica
de una línea (invocación sin argumento), (b) un test de regresión dedicado (FR-008) que ejercite el **método
real del mixin** cubriendo los **tres caminos terminales** del protector (permitido, denegado, DROP de
generación obsoleta) con la invariante `is_loading == False`, (c) un log seguro de desenlace en producción
(FR-009) verificado por **búsqueda activa** del patrón `TypeError` en los logs (SC-002), (d) validación E2E
del inventario de 18 rutas **incluida la recarga** `page.reload()` (SC-003/SC-005), y (e) validación en local
y desplegado, con la fase desplegada **bloqueante** (SC-001/SC-002/FR-009), siguiendo la práctica de la 077.
Spec con las 12 Q→A de la sesión 2026-09-23 integradas (checklists: requirements 16/16, auth 32/32,
test 32/32).

## Technical Context

**Language/Version**: Python 3.11 (runtime.txt; local 3.12.6)

**Primary Dependencies**: `reflex==0.8.28.post1`, `pytest`, `playwright@^1.60` (E2E); sin dependencias nuevas

**Storage**: PostgreSQL (Railway) via `DatabaseManager`; sin DML ni cambios de esquema

**Testing**: `pytest` (asyncio auto; `pytest.ini`), unitarios sin I/O, integración con BD de prueba, E2E Playwright (`tests/e2e/`)

**Target Platform**: Web (despliegue Railway `inmovelar-production.up.railway.app`)

**Project Type**: Web application (frontend Reflex + backend Python in-process, clean architecture)

**Performance Goals**: N/A — los límites temporales de 5/10 s pertenecen a la 077 y quedan FUERA del alcance (Assumptions)

**Constraints**: `end_navigation_generation()` se invoca SIN argumento (FR-001); el mixin NO cambia (FR-004,
sin guardia condicional — invocación idempotente, Clarificación Q3); log seguro sin credenciales (FR-009,
Zero Leak); fix quirúrgico de 1 línea (cirugía técnica, §6); la validación desplegada es BLOQUEANTE
(Clarificación Q4); FR-008 exige los TRES caminos terminales (el DROP de generación obsoleta NO invoca
`end_navigation_generation`); SC-003/SC-005 exigen `page.reload()` sobre el inventario de rutas;
SC-002 exige búsqueda ACTIVA del patrón `TypeError` y de las líneas FR-009 en los logs (no solo ausencia
visual); FR-010 fija la acción determinista de des-mockear los tests que codifican la firma errónea

**Scale/Scope**: 18 rutas protegidas confirmadas (contrato §4; criterio objetivo FR-003); cambio pequeño
(1 línea + tests + log), cirugía técnica

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Gate | Estado | Evidencia |
|------|--------|-----------|
| Sin Flet/SQLite en lógica nueva | Pasado | Solo `presentacion_reflex/state/auth_state.py` + tests; transporte intocable |
| Idioma 100% español | Pasado | Textos canónicos y artefactos en español |
| Clean architecture (dependencias unidireccionales) | Pasado | Cambio en presentación; sin capas nuevas |
| Tipado explícito + UPPER_SNAKE + docstrings Google | Pasado | Respeta convenciones vigentes en `auth_state.py` |
| Excepciones tipadas de dominio (no genéricas supresivas) | Pasado | No se añaden `except` nuevos |
| Persistencia PostgreSQL (%s, RETURNING, sin magic numbers) | N/A | Sin DML nuevo |
| Tests (dominio 100%, lógica nueva >90%, unit sin I/O) | Pasado | TDD primero: unit del contrato (FR-008), sin I/O |
| Verificación en navegador + regresión visual | Pasado | E2E SC-003 sobre inventario de 18 rutas + capturas antes/después |
| Zero leak + RBAC | Pasado | FR-009 sin credenciales; RBAC no se modifica |
| Cirugía técnica (replace/sed sobre rewrite) | Pasado | 1 línea en `auth_state.py:215`; no se reescribe el estado |

**Re-check post-design (Phase 1)**: los artefactos `data-model.md`, `contracts/proteccion_rutas.md` y
`quickstart.md` (regenerados con las 12 Q→A: 3 caminos terminales, recarga E2E, búsqueda activa SC-002,
FR-010 determinista) no introducen capas nuevas, ni transporte nuevo, ni dependencias externas: los gates
permanecen PASADOS. No se requiere tabla de Complexity Tracking (sin violaciones justificables).

## Project Structure

### Documentation (this feature)

```text
specs/078-fix-login-error/
├── spec.md              # Feature specification (12 Q→A integradas; requirements 16/16, auth 32/32, test 32/32)
├── plan.md              # Este archivo
├── research.md          # Phase 0: contrato mixin verificado, tests que enmascaran el bug, inventario rutas, log FR-009
├── data-model.md        # Phase 1: generación de navegación (runtime), transiciones del protector, log seguro
├── quickstart.md        # Phase 1: guion de validación SC-001..SC-006 (matriz 1-7)
├── contracts/
│   └── proteccion_rutas.md   # Contrato del ciclo require_login/require_login_background + firma mixin + log FR-009
└── tasks.md             # Phase 2 output (/speckit.tasks - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
└── presentacion_reflex/
    └── state/
        └── auth_state.py        # línea 215: end_navigation_generation(gen_id) → end_navigation_generation()
                                 # + log seguro de desenlace (FR-009): acceso permitido/denegado

tests/
├── unit/
│   ├── test_proteccion_rutas.py        # actualizar aserciones: assert_called_once() (sin argumento, FR-010)
│   └── test_regresion_firma_proteccion.py  # (nuevo, FR-008) método real: 3 caminos terminales + is_loading False
└── integration/
    └── test_auth_login.py              # des-mockear el patch de end_navigation_generation
                                        # (acción determinista FR-010 / T006 — sin opción de "mantener el patch")

tests/e2e/
└── navegacion_rutas_protegidas.spec.mjs  # (nuevo, SC-003/SC-005) inventario 18 rutas + page.reload()
```

**Structure Decision**: Se mantiene la estructura monolítica por capas vigente. No se crea proyecto, paquete
ni capa nueva: el cambio es cirugía sobre una línea del protector de rutas y sus tests, siguiendo la
arquitectura actual y evitando imports circulares (constitución §6).

## Complexity Tracking

> Ninguna violación de la constitución exige justificación: no hay proyectos, capas ni patrones nuevos.
> Table intentionally omitted (validado en Constitution Check).

## Notas de ejecución (resumen de fases)

- **Phase 0 (research)**: completada en `research.md` — contrato del mixin verificado en código (Hallazgo 1),
  tests existentes que enmascaran y codifican la firma errónea (Hallazgo 2), inventario de 18 rutas protegidas
  (Hallazgo 3, criterio objetivo FR-003), patrón de log de producción seguro para FR-009 (Hallazgo 4), alcance
  quirúrgico de 1 línea e idempotencia (Hallazgo 5). Unknowns resueltos.
- **Phase 1 (design)**: completada — `data-model.md`, `contracts/proteccion_rutas.md`, `quickstart.md`.
  Re-check post-design: gates de la constitución permanecen PASADOS (sin capas, tablas ni dependencias nuevas).
  No existe script de contexto de agentes en `.specify/scripts/` → actualización de agente omitida.
- **Clarificaciones integradas (sesión 2026-09-23, 12 Q→A)**: 3 caminos terminales del protector en FR-008
  (DROP sin llamado a `end_navigation_generation`), recarga `page.reload()` en SC-003/SC-005, búsqueda activa
  del `TypeError` en SC-002, des-mockeo determinista de los tests en FR-010, harness E2E en alcance (T042 de
  la 077 asumido) y validación desplegada bloqueante.
- **Phase 2 (tasks)**: `/speckit.tasks` genera `tasks.md` (24 tareas, 7 fases, ordenado por dependencias)
  sobre estas bases.
- TDD: el test FR-008 (método real, sin mock) debe fallar con el bug presente y pasar tras el fix
  (STOP-THE-LINE, constitución §13: Corregir Raíz → **Blindar**). En el camino (3) DROP, el test dispone la
  generación activa ya finalizada (`is_loading` en `False`): la tarea descartada NO invoca
  `end_navigation_generation` (contract §1/§2) — la invariante `is_loading == False` se verifica sobre el
  estado que la generación activa deja al finalizar.