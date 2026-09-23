# Implementation Plan: Correccion del flujo de inicio de sesion (spinner infinito)

**Branch**: `bugfix/077-fix-login-spinner` | **Date**: 2026-09-22 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/077-fix-login-spinner/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Corregir de raiz el bug del boton "Acceder al Panel" (spinner infinito) atacando la cadena de
desenlace del evento de login en Reflex 0.8.28.post1. La feature requiere (a) un diagnostico E2E
con evidencia que confirme cual de los hallazgos de `research.md` rompe la cadena (restablecimiento de
`is_loading`, generador con `yield`+`return`, background task que emite eventos UI dentro del lock,
o ausencia de `statement_timeout`), (b) una correccion con desenlace terminal garantizado en todas las
rutas (senal de carga dedicada `login_in_progress`, proteccion de rutas que cierra su generacion,
excepciones tipadas de dominio, textos canonicos, limites de recurso reales) y (c) validacion de los
10 puntos en local y desplegado, con evidencias E2E + traza + capturas antes/despues.

## Technical Context

**Language/Version**: Python 3.11 (runtime.txt; local 3.12.6)

**Primary Dependencies**: `reflex==0.8.28.post1`, `psycopg2-binary`, `bcrypt`, `pydantic`; E2E con `playwright@^1.60`

**Storage**: PostgreSQL (Railway) via `DatabaseManager` (pool min=1/max=20); conexion con `connect_timeout` (10 s, `DB_CONNECT_TIMEOUT`)

**Testing**: `pytest` (asyncio auto; `pytest.ini`), unitarios sin I/O, integracion con BD de prueba, E2E Playwright (`tests/e2e/`)

**Target Platform**: Web (despliegue Railway `inmovelar-production.up.railway.app`)

**Project Type**: Web application (frontend Reflex + backend Python in-process, clean architecture)

**Performance Goals**: login credencial→panel < 5 s local / < 10 s desplegado (SC-002)

**Constraints**: Queda PROHIBIDO timeout artificial de UI y ocultar el desenlace (FR-002, SC-006);
los limites de recurso producen un error real y visible (FR-009). Sin cambios de esquema.

**Scale/Scope**: ~22 rutas protegidas con `AuthState.require_login`; un solo handler de login; cambio pequeno (~<300 lineas, cirugia tecnica)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Gate | Estado | Evidencia |
|------|--------|-----------|
| Sin Flet/SQLite en logica nueva | Pasado | Solo `presentacion_reflex` + `dominio/aplicacion`; transporte intocable |
| Idioma 100% espanol | Pasado | Textos canonicos y artefactos en espanol |
| Clean architecture (dependencias unidireccionales) | Pasado | Excepciones tipadas en `dominio`; resultado en `aplicacion`; estado en `presentacion` |
| Tipado explicito + UPPER_SNAKE + docstrings Google | Pasado | Respeta convenciones vigentes en `auth_state.py` |
| Excepciones tipadas de dominio (no genericas supresivas) | Pasado | `except Exception` final solo como fallback loggeado y terminal |
| Persistencia PostgreSQL (%s, RETURNING, sin magic numbers) | Pasado | Sin DML nuevo; limites de recurso via config documentada |
| Tests (dominio 100%, logica nueva >90%, unit sin I/O) | Pasado | TDD primero (ver quickstart) |
| Verificacion en navegador + regresion visual | Pasado | Evidencia E2E + capturas antes/despues (Q3) |
| Zero leak + RBAC | Pasado | Logs sin credenciales; RBAC no se modifica |
| Cirugia tecnica (replace/sed sobre rewrite) | Pasado | Cambios puntuales en handlers; no se reescribe el estado |

**Re-check post-design (Phase 1)**: Los artefactos `data-model.md` y `contracts/` no introducen capas
nuevas, ni transporte nuevo, ni dependencias externas: los gates permanecen PASADOS. No se requiere
tabla de Complexity Tracking (sin violaciones justificables).

## Project Structure

### Documentation (this feature)

```text
specs/077-fix-login-spinner/
├── spec.md              # Feature specification (validada en clarify; 14/14 checklist)
├── plan.md              # Este archivo
├── research.md          # Phase 0: environment, hallazgos, candidatas de causa raiz, gates
├── data-model.md        # Phase 1: entidades, estados runtime, errores tipados, config limites
├── quickstart.md        # Phase 1: guion de validacion de los 10 puntos (antes/despues)
├── contracts/
│   ├── errores_autenticacion.md   # Catalogo unico de textos canonicos + formato de log
│   └── flujo_login.md             # Contrato del evento login + proteccion de rutas (Reflex 0.8)
└── tasks.md             # Phase 2 output (/speckit.tasks - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── dominio/
│   └── excepciones/
│       └── excepciones_base.py        # +ErrorCredencialesInvalidas, ErrorUsuarioInactivo, ErrorRecurso, ErrorPoliticaIntentos
│       └── resultado_autenticacion.py # (nuevo) ExitoAutenticacion + clases de error tipadas
├── aplicacion/
│   └── servicios/
│       └── servicio_autenticacion.py  # elevar errores tipados (inactivo vs invalidas vs recurso)
├── infraestructura/
│   └── persistencia/
│       └── database.py                # +statement_timeout (DB_STATEMENT_TIMEOUT)
└── presentacion_reflex/
    ├── state/
    │   ├── navigation_mixin.py        # helpers de cierre garantizado de generacion
    │   └── auth_state.py              # login_in_progress; login() terminal; require_login_background sin yield en lock
    └── pages/
        └── login.py                   # boton loading=AuthState.login_in_progress

tests/
├── unit/                              # TDD: excepciones/mensajes, mixin cierre de generacion
├── integration/                       # login con BD de prueba, timeout por recurso, RBAC
└── e2e/                               # Playwright: matriz de 10 puntos + capturas
```

**Structure Decision**: Se mantiene la estructura monolistica por capas vigente (src/dominio,
src/aplicacion, src/infraestructura, src/presentacion_reflex). No se crea proyecto, paquete ni capa
nueva: el cambio es cirugia sobre los dos handlers de autenticacion y su catalogo de errores,
siguiendo la arquitectura actual y evitando imports circulares (constitucion §6).

## Complexity Tracking

> Ninguna violacion de la constitucion exige justificacion: no hay proyectos, capas ni patrones nuevos.
> Table intentionally omitted (validado en Constitution Check).

## Notas de ejecucion (resumen de fases)

- **Phase 0 (research)**: completada en `research.md` — hallazgos 1–4 (candidatas de causa raiz),
  unknown resueltos, gates validados.
- **Phase 1 (design)**: completada — `data-model.md`, `contracts/` (errores + flujo login), `quickstart.md`.
- **Phase 2 (tasks)**: `/speckit.tasks` genera `tasks.md` (ordenado por dependencias) sobre estas bases.
- La confirmacion empirica de la causa raiz (FR-001/SC-008) ejecuta durante la implementacion con
  repro E2E + traza + capturas antes de tocar codigo (STOP-THE-LINE, constitucion §13).