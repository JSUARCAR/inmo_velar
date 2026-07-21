# Implementation Plan: Columnas Condicionales en Tabla de Contratos

**Branch**: `060-columnas-contratos-condicionales` | **Date**: 2026-07-21 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/060-columnas-contratos-condicionales/spec.md`

## Summary

Agregar una columna condicional "Información Adicional" a la tabla unificada de contratos que muestre datos específicos según el tipo:
- **Mandato**: `"Nombre Consignatario | Banco | Número Cuenta"` (campos ya existentes en `CONTRATOS_MANDATOS`)
- **Arrendamiento**: `"Nombre Codeudor | Teléfono"` (requiere JOIN con `CODEUDORES` → `PERSONA`)

## Technical Context

**Language/Version**: Python 3.11+, Reflex 0.6+

**Primary Dependencies**: Reflex (UI), psycopg2 (PostgreSQL), Pydantic (DTOs)

**Storage**: PostgreSQL (ya implementado)

**Testing**: Tests de renderizado Reflex, validación manual en `reflex run --env dev`

**Target Platform**: Web (Railway deployment)

**Project Type**: Web application (full-stack Reflex)

**Performance Goals**: <10% degradación en carga de tabla

**Constraints**: No modificar estructura de tablas existentes, solo consultas y UI

**Scale/Scope**: Tabla existente de contratos (~50-500 registros típicos)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Constitutional Rule | Status | Notes |
|---------------------|--------|-------|
| Clean Architecture (Dominio → Aplicación → Infraestructura → Presentación) | ✅ PASS | Cambios en UI (Presentación) y Repositorio (Infraestructura) sin afectar Dominio |
| 100% Español en código y docs | ✅ PASS | Todo el código existente y nuevo en español |
| PostgreSQL Native (placeholders %s) | ✅ PASS | Ya implementado en repositorios existentes |
| Mutaciones atómicas en State | ✅ PASS | Se usará pattern existente |
| Type Hints obligatorios | ✅ PASS | Se aplicarán en código nuevo |
| Sin dependencias circulares | ✅ PASS | Cambios en capas inferiores sin importar superiores |

## Project Structure

### Documentation (this feature)

```text
specs/060-columnas-contratos-condicionales/
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
├── dominio/
│   └── entidades/
│       ├── contrato_mandato.py      # Sin cambios (campos ya existen)
│       └── contrato_arrendamiento.py # Sin cambios (FK id_codeudor ya existe)
├── aplicacion/
│   └── servicios/
│       └── servicio_contratos.py    # Sin cambios necesarios
├── infraestructura/
│   └── persistencia/
│       ├── repositorio_contrato_mandato_postgres.py   # Sin cambios
│       └── repositorio_contrato_arrendamiento_postgres.py  # Revisar query
└── presentacion_reflex/
    ├── state/
    │   └── contratos_state.py       # Agregar campos a ContratoDict
    ├── pages/
    │   └── contratos.py             # Agregar columna a render_table_view()
    └── components/
        └── contratos/
            └── tarjeta_contrato.py  # Actualizar vista card si aplica
```

**Structure Decision**: Cambios mínimos en capas existentes. La columna se agrega directamente en la UI sin crear nuevas entidades ni servicios.

## Complexity Tracking

No hay violaciones constitucionales que justificar.

## Phase 0: Research

### Research Tasks

1. **Verificar estructura actual de ContratoDict** - Confirmar campos disponibles
2. **Analizar query de repositorio de Arrendamiento** - Verificar si ya retorna datos de codeudor
3. **Revisar render_table_view()** - Entender patrón de columnas existentes
4. **Validar campos de consignatario en Mandato** - Confirmar banco_propietario, numero_cuenta_propietario, consignatario

### Findings (to be consolidated in research.md)

Pending Phase 0 execution.

## Phase 1: Design

### data-model.md Content

**Entidades Relevantes (sin cambios)**:

| Entidad | Campos Relevantes | Tipo |
|---------|-------------------|------|
| ContratoMandato | consignatario, banco_propietario, numero_cuenta_propietario | str, str, str |
| ContratoArrendamiento | id_codeudor (FK) | int (nullable) |
| Codeudor | id_codeudor, id_persona (FK) | int, int |
| Persona | nombre, telefono | str, str |

**DTO Actualizado (ContratoDict)**:

```python
class ContratoDict(pydantic.BaseModel):
    # ... campos existentes ...
    # Nuevos campos para información adicional
    informacion_adicional: str | None = None  # Formato: "Campo1 | Campo2 | Campo3"
```

### quickstart.md Content

**Validación**:
1. Cargar tabla de contratos
2. Verificar columna "Información Adicional" visible
3. Contrato Mandato → muestra "Consignatario | Banco | Cuenta"
4. Contrato Arrendamiento → muestra "Nombre Codeudor | Teléfono"
5. Sin datos → muestra "No registrado"

## Phase 2: Tasks (deferred to /speckit.tasks)

Las tareas específicas se generarán con `/speckit-tasks`.
