# Implementation Plan: [FEATURE]

**Branch**: `[###-feature-name]` | **Date**: [DATE] | **Spec**: [link]

**Input**: Feature specification from `/specs/[###-feature-name]/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary
 
 Diagnóstico y corrección del error de navegación en Reflex que aborta el enrutamiento y devuelve al Dashboard tras el login. La solución técnica elimina los bloqueos síncronos (`yield` vacíos) y delega la carga pesada a tareas de segundo plano (`@rx.event(background=True)`), con renderizado inmediato de *skeletons* para retroalimentación UX e identificadores de "generación" para descartar promesas concurrentes caducadas.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.11

**Primary Dependencies**: Reflex, PostgreSQL

**Storage**: N/A for this fix (Frontend state manipulation only)

**Testing**: Manual UI Testing (Reflex preview)

**Target Platform**: Web application (Reflex)

**Project Type**: Web application

**Performance Goals**: < 1s visual response transition

**Constraints**: Must use `@rx.event(background=True)` with native asyncio (no Redis required for MVP). Must use `rx.spinner()` for loading visual states. Must implement a Graceful Rollback to Dashboard on timeout.

**Scale/Scope**: Refactoring `PersonasState`, `AlertasState`, `AlertasDashboardState`, and `AuthState`. Additionally, introducing a server-side generation timestamp system to prevent race conditions during rapid navigation (< 500ms clicks) and assuming P90 network latency < 500ms.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] Usar Reflex y PostgreSQL estrictamente. No Flet/SQLite.
- [x] Usar `snake_case` para variables y `PascalCase` para componentes Reflex.
- [x] Asegurar no mutar listas in-place, garantizando correcta hidratación en UI.
- [x] Resolver deuda técnica de inmediato (eliminar el anti-patrón de `yield` vacío).
- Todos los lineamientos arquitectónicos de Reflex y UI del sistema están cubiertos y no hay violaciones documentadas.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)
```text
src/
└── presentacion_reflex/
    └── state/
        ├── auth_state.py
        ├── personas_state.py
        ├── alertas_state.py
        └── alertas_dashboard_state.py
```

**Structure Decision**: Single project using Option 1. The fix is confined to modifying four specific State files inside the `presentacion_reflex` layer to adhere to the architecture.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |

