# Implementation Plan: Agregar Columna PROPIEDAD a Tabla de Recaudos

**Branch**: `050-agregar-columna-propiedad` | **Date**: 2026-07-11 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/050-agregar-columna-propiedad/spec.md`

## Summary

Agregar la columna PROPIEDAD (dirección de la propiedad) a la tabla de recaudos, mostrando la dirección de la propiedad asociada a través del campo `propiedad_id`. La columna debe ser ordenable, filtrable, y estar ubicada después de CICLO OPERATIVO y antes de CANON.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: Reflex (Framework UI), PostgreSQL (Base de datos)

**Storage**: PostgreSQL con esquema existente de propiedades y recaudos

**Testing**: pytest, tests de renderizado Reflex

**Target Platform**: Web (Railway deployment)

**Project Type**: Web application (Inmobiliaria management system)

**Performance Goals**: <50ms adicional en carga de tabla

**Constraints**: Clean Architecture, 100% español, Design System Claude/Anthropic

**Scale/Scope**: Sistema de gestión inmobiliaria multi-usuario

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Estado | Notas |
|-----------|--------|-------|
| Clean Architecture (Dominio → Aplicación → Infraestructura → Presentación) | ✅ PASS | Cambio solo en capa de Presentación (UI) |
| Idioma 100% español | ✅ PASS | Todo el código y documentación en español |
| Naming conventions (snake_case, PascalCase) | ✅ PASS | Se mantendrán las convenciones existentes |
| Type hints obligatorios | ✅ PASS | Se agregarán type hints en nuevos métodos |
| PostgreSQL native (placeholders %s) | ✅ PASS | Sin cambios en persistencia |
| Design System Claude/Anthropic | ✅ PASS | Columna seguirá el sistema de diseño existente |
| Zero Leak (seguridad) | ✅ PASS | Sin credenciales ni datos sensibles |
| Testing >90% cobertura | ✅ PASS | Tests de UI para nueva columna |
| Commits Conventional | ✅ PASS | feat(ui): agregar columna propiedad a tabla recaudos |

**Resultado**: Todos los gates PASAN. No hay violaciones que justificar.

## Project Structure

### Documentation (this feature)

```text
specs/050-agregar-columna-propiedad/
├── spec.md              # Especificación de la feature
├── plan.md              # Este archivo
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
src/
├── dominio/                    # Entidades y Value Objects
├── aplicacion/                 # Servicios de orquestación
├── infraestructura/            # Repositorios PostgreSQL
│   └── persistencia/
│       └── repositorio_recaudo.py
└── presentacion_reflex/        # UI con Reflex
    ├── components/             # Componentes reutilizables
    ├── pages/                  # Páginas/vistas
    │   └── recaudos/           # Vista de recaudos
    └── styles.py               # Estilos globales
```

**Structure Decision**: Estructura Clean Architecture existente. El cambio se concentra en la capa de Presentación (UI) y posiblemente en Aplicación (servicio de datos).

## Complexity Tracking

No hay violaciones de constitución que justificar. Feature de bajo complejidad (agregar columna a tabla existente).
