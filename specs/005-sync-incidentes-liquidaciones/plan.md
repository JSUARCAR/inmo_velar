# Implementation Plan: Sincronización Incidentes y Liquidaciones

**Branch**: `[005-sync-incidentes-liquidaciones]` | **Date**: 2026-07-02 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/005-sync-incidentes-liquidaciones/spec.md`

## Summary

La feature busca resolver un problema de sincronización de información financiera entre el módulo de Incidentes y Liquidaciones de Propietario.
El plan técnico implica modificar `ServicioIncidentes` para adjuntar y persistir correctamente `PlanPagoIncidente` y actualizar `ServicioFinanciero` para que consulte el `RepositorioCuota` con el fin de obtener las cuotas pendientes que deben restarse a los pagos del propietario, cambiando luego su estado a pagada.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: Reflex (Frontend/UI), psycopg2 (o similar para base de datos)

**Storage**: PostgreSQL (Requerido por la política Élite, placeholders `%s`, clausulas `RETURNING id`)

**Testing**: Pytest

**Target Platform**: Railway/Cloud Platform (Linux)

**Project Type**: Web Application (Reflex Fullstack)

**Performance Goals**: Consultas a base de datos de Incidentes deben retornar datos de plan de pago en menos de 500ms.

**Constraints**: Usar estrictamente Clean Architecture. Nomenclatura en español, snake_case para variables/funciones, PascalCase para clases y componentes UI.

**Scale/Scope**: Limitado a corregir e implementar los flujos de persistencia y estado en repositorios y servicios ya existentes.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] ¿El código respeta el uso exclusivo de PostgreSQL, con placeholders `%s` y evitando `lastrowid`? **Sí**
- [x] ¿Se mantiene la dependencia unidireccional de capas (Dominio → Aplicación → Infraestructura → Presentación)? **Sí**
- [x] ¿El idioma del código, comentarios y UI es 100% español? **Sí**
- [x] ¿Se cumple la política de Zero Leakage de secretos/logs sucios? **Sí**
- [x] ¿Las transiciones de estado de cuotas respetan validaciones explícitas (Fail Fast)? **Sí**

## Project Structure

### Documentation (this feature)

```text
specs/005-sync-incidentes-liquidaciones/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
src/
├── aplicacion/
│   └── servicios/
│       ├── servicio_financiero.py
│       └── servicio_incidentes.py
├── dominio/
│   └── entidades/
│       ├── incidente.py
│       ├── cuota_incidente.py
│       └── liquidacion.py
├── infraestructura/
│   └── persistencia/
│       ├── repositorio_incidentes_postgres.py
│       └── repositorio_cuota_postgres.py
└── presentacion_reflex/
    ├── pages/
    │   └── incidentes/
    └── components/
```

**Structure Decision**: La lógica principal reside en los módulos de `aplicacion/servicios` e `infraestructura/persistencia` ya existentes. Se modificará el servicio financiero y de incidentes para orquestar correctamente el modelo de datos sin requerir nuevas capas.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No hay violaciones a los principios. El diseño se ajusta estrictamente a los requerimientos de la política.
