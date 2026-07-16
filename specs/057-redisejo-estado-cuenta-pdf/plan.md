# Implementation Plan: Rediseño Estado de Cuenta PDF Liquidaciones

**Branch**: `057-redisejo-estado-cuenta-pdf` | **Date**: 2026-07-15 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/057-redisejo-estado-cuenta-pdf/spec.md`

## Summary

Rediseñar el Estado de Cuenta PDF (vista individual) del módulo de Liquidaciones de Propietarios para: (1) agregar columna INCIDENTES siempre visible en el detalle financiero, (2) eliminar la fila TOTAL redundante, (3) reorganizar el Resumen Financiero con 8 conceptos en orden lógico, (4) eliminar el Código QR, (5) agregar sección OBSERVACIONES siempre visible, y (6) garantizar consistencia entre BD y PDF.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: ReportLab (PDF generation), Reflex (UI), PostgreSQL (storage)
**Storage**: PostgreSQL (LIQUIDACIONES, INCIDENTE_LIQUIDACION tables)
**Testing**: pytest, validación visual de PDFs
**Target Platform**: Web application (Reflex) + PDF generation server-side
**Project Type**: Web application (frontend + backend)
**Performance Goals**: Sin cambios en rendimiento (las modificaciones son de presentación)
**Constraints**: No modificar cálculos financieros existentes, solo presentación visual
**Scale/Scope**: ~3 archivos modificados, ~200 líneas de código

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|---|---|---|
| Clean Architecture (Dominio → Aplicación → Infraestructura → Presentación) | PASS | Cambios solo en Infraestructura (template PDF) y Presentación (transformadores) |
| 100% Español | PASS | Todo el código y documentación en español |
| Type Hints obligatorios | PASS | Se mantendrán en todas las firmas modificadas |
| PostgreSQL Native | PASS | No se modifican consultas SQL existentes |
| Zero Deferred Cleanup | PASS | Se eliminan código muerto (QR, fila TOTAL) |
| Cambios Atómicos | PASS | Los cambios son pequeños y acotados (~200 líneas) |
| Validación de Assets | PASS | Los logos y fuentes ya existen en el proyecto |

**Resultado**: Todos los gates PASS. No hay violaciones que justificar.

## Project Structure

### Documentation (this feature)

```text
specs/057-redisejo-estado-cuenta-pdf/
├── plan.md              # Este archivo
├── research.md          # Fase 0: Investigación de decisiones técnicas
├── data-model.md        # Fase 1: Modelo de datos y transformaciones
├── quickstart.md        # Fase 1: Guía de validación
├── contracts/           # Fase 1: Contratos de template
│   └── template-contract.md
├── checklists/
│   └── requirements.md  # Checklist de calidad de especificación
└── tasks.md             # Fase 2: Tareas de implementación (no creado por /speckit-plan)
```

### Source Code (repository root)

```text
src/
├── dominio/
│   └── entidades/
│       ├── liquidacion.py          # SIN CAMBIOS (entidad inmutable)
│       └── incidente_liquidacion.py # SIN CAMBIOS
├── aplicacion/
│   └── servicios/
│       ├── servicio_financiero.py   # SIN CAMBIOS
│       └── servicio_incidente_liquidacion.py # SIN CAMBIOS
├── infraestructura/
│   └── servicios/
│       ├── pdf_elite/
│       │   └── templates/
│       │       ├── estado_cuenta_elite.py  # CAMBIOS PRINCIPALES
│       │       └── base_template.py        # SIN CAMBIOS NECESARIOS
│       └── servicio_pdf_facade.py   # SIN CAMBIOS
└── presentacion_reflex/
    └── state/
        └── pdf_state.py             # CAMBIOS EN TRANSFORMADORES
```

**Structure Decision**: Se mantiene la estructura existente. Los cambios son mínimos y están acotados a 2 archivos principales + 1 archivo de transformadores.

## Complexity Tracking

> No hay violaciones de constitución que justificar.

## Fase 0: Investigación (Research)

Ver [research.md](./research.md) para detalles completos.

**Decisiones clave:**
1. Usar `valor_incidentes` directamente en lugar de `gastos_rep + otros_egr`
2. Resumen Financiero: 8 filas en orden específico
3. QR: Simplemente eliminar la llamada a `enable_verification_qr()`
4. Comisión: Dividir `comision_porcentaje / 100` para mostrar porcentaje legible
5. Observaciones: Siempre mostrar sección, mensaje por defecto si vacío
6. Administración: Usar `gastos_administracion > 0` como indicador de PH

## Fase 1: Diseño y Contratos

Ver [data-model.md](./data-model.md) para el modelo de datos completo.
Ver [contracts/template-contract.md](./contracts/template-contract.md) para el contrato del template.
Ver [quickstart.md](./quickstart.md) para la guía de validación.

### Cambios Diseñados

#### 1. Transformadores (pdf_state.py)

**`_transform_individual_to_pdf_format()`** (líneas 927-994):
- Cambiar `detalle["incidente"] = gastos_rep + otros_egr` → `detalle["incidentes"] = valor_incidentes`
- Agregar `detalle["comision_porcentaje"] = comision_porcentaje`
- Reestructurar `resumen` con nuevos campos

**`_transform_consolidated_to_pdf_format()`** (líneas 996-1060):
- Mismos cambios que el transformador individual

#### 2. Template (estado_cuenta_elite.py)

**`_add_detalle_propiedades()`** (líneas 273-365):
- Eliminar la condicional `if mostrar_incidentes:` — columna siempre visible
- Eliminar la fila TOTAL completa (líneas 340-353)
- Renombrar acceso de `d["incidente"]` a `d["incidentes"]`

**`_add_resumen_financiero()`** (líneas 367-408):
- Reemplazar las 4-5 filas actuales por 8 filas en el nuevo orden
- Agregar formato `Comisión ({X}%)` usando `comision_porcentaje`
- Mantener NETO A PAGAR como fila destacada

**`_add_notas()`** (líneas 410-421):
- Eliminar la condicional `if "observaciones" in data and data["observaciones"]:`
- Mostrar siempre la sección OBSERVACIONES
- Agregar mensaje por defecto si observaciones es None o vacío

**`generate()`** (líneas 59-110):
- Eliminar la línea 85: `self.enable_verification_qr("estado", data["estado_id"])`

#### 3. Base Template (base_template.py)

**Sin cambios necesarios.** El QR se deshabilita simplemente no llamando a `enable_verification_qr()`. Los defaults son `include_qr=False` y `qr_data=None`.

## Fase 2: Tareas

> Las tareas de implementación serán generadas por `/speckit-tasks`.
