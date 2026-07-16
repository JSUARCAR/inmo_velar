# Implementation Plan: Fix Estado Cuenta PDF - Incidentes

**Branch**: `051-fix-estado-cuenta-pdf-incidentes` | **Date**: 2026-07-15 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/051-fix-estado-cuenta-pdf-incidentes/spec.md`

## Summary

Ingeniería inversa del módulo Liquidaciones para corregir la inclusión del valor de Incidentes en el Estado de Cuenta PDF. El campo `valor_incidentes` existe en la entidad Liquidación y se calcula correctamente (`neto_a_pagar = total_ingresos - total_egresos - valor_incidentes`), pero la capa de mapeo de datos para PDF (`mapear_consolidado_a_pdf_elite`) y la consulta consolidada (`obtener_consolidado_propietario`) no propagan este valor a la plantilla. La corrección requiere modificaciones en 3 capas: Persistencia → Aplicación → Infraestructura PDF.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: Reflex (UI), ReportLab (PDF generation), Pydantic (DTOs/validations), psycopg2 (PostgreSQL)

**Storage**: PostgreSQL (entity `LIQUIDACIONES` with column `VALOR_INCIDENTES`)

**Testing**: pytest, pruebas de renderizado Reflex

**Target Platform**: Linux server (Railway deployment)

**Project Type**: web-service (Reflex full-stack)

**Performance Goals**: SC-005: tiempo de generación del PDF no se incrementa en más del 5%

**Constraints**: No introducir regresiones en otros documentos PDF. Mantener consistencia UI-PDF.

**Scale/Scope**: Modificación quirúrgica en 3 archivos existentes + 1 archivo de dominio (ya correcto)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Estado | Notas |
|-----------|--------|-------|
| Clean Architecture (capas unidireccionales) | ✅ Pasa | Cambios en Persistencia → Aplicación → Infraestructura (dirección correcta) |
| Dominio sin dependencias | ✅ Pasa | `liquidacion.py` ya tiene `valor_incidentes` y `calcular_totales()` correctos |
| PostgreSQL nativo (placeholders %s) | ✅ Pasa | No hay cambios en queries SQL; el campo ya se retorna en `obtener_datos_para_pdf` |
| IDIOMA 100% ESPAÑOL | ✅ Pasa | Nombres de funciones, variables y comentarios en español |
| Zero Guessing | ✅ Pasa | La spec tiene 4 clarificaciones que resuelven todos los casos límite |
| Contract-First | ✅ Pasa | El contrato de datos (`data-model.md`) se define antes de la implementación |
| Validación de Assets PDF | ✅ Pasa | La plantilla Elite ya valida logos/fuentes; no se agregan nuevos assets |
| Cambios Atómicos | ✅ Pasa | El cambio se puede dividir en 3 commits: repo → service → template |

**Violations**: Ninguna.

## Project Structure

### Documentation (this feature)

```text
specs/051-fix-estado-cuenta-pdf-incidentes/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (NOT created by /speckit.plan)
```

### Source Code (affected files)

```text
src/
├── dominio/entidades/
│   └── liquidacion.py                    # YA CORRECTO: valor_incidentes + calcular_totales()
├── infraestructura/persistencia/
│   └── repositorio_liquidacion_postgres.py  # FIX: agregar valor_incidentes a obtener_consolidado_propietario()
├── aplicacion/servicios/
│   └── servicio_financiero.py             # FIX: actualizar mapear_consolidado_a_pdf_elite()
├── infraestructura/servicios/pdf_elite/templates/
│   └── estado_cuenta_elite.py             # FIX: agregar línea de Incidentes en detalle y resumen
└── presentacion_reflex/                   # NO CAMBIA: UI ya muestra valor_incidentes correctamente
```

**Structure Decision**: Se modifica la estructura existente de Clean Architecture. No se crean nuevos módulos ni archivos de dominio. Los cambios son quirúrgicos en las capas de Persistencia, Aplicación y Infraestructura.

## Complexity Tracking

> No hay violaciones de constitución que justificar.

| Violación | Por qué se necesita | Alternativa más simple rechazada porque |
|-----------|---------------------|----------------------------------------|
| N/A | N/A | N/A |
