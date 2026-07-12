# Implementation Plan: Reordenar Columnas Tabla Liquidaciones

**Branch**: `049-reorder-columns-liquidaciones` | **Date**: 2026-07-11 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/049-reorder-columns-liquidaciones/spec.md`

## Summary

Reorganizar el orden de las 16 columnas de la tabla principal del módulo Liquidaciones para optimizar el análisis financiero. Cambio puramente de presentación: se elimina la columna "Propiedad" (no solicitada en el orden objetivo) y se mueve "IVA Comisión" de la posición 13 a la posición 5. No se requieren cambios en backend, base de datos ni lógica de negocio.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: Reflex (framework UI web full-stack)

**Storage**: PostgreSQL (sin cambios requeridos)

**Testing**: Validación visual en navegador + verificación de funcionalidades de tabla

**Target Platform**: Web application (desktop-first, 1280px+)

**Project Type**: web-application (Reflex full-stack)

**Performance Goals**: Sin degradación perceptible (cambio de orden de rendering)

**Constraints**: Mantener compatibilidad con todas las funcionalidades de tabla existentes

**Scale/Scope**: 1 archivo de UI principal, ~200 líneas de código afectadas

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| Clean Architecture (Dominio → Aplicación → Infraestructura → Presentación) | PASS | Cambio solo en capa de Presentación |
| 100% Español | PASS | Nombres de columnas ya están en español |
| Type Hints obligatorios | PASS | No se añaden funciones nuevas |
| Zero Filtración | PASS | Sin manejo de credenciales |
| Cambios Atómicos | PASS | Cambio pequeño (~200 líneas), un solo commit |
| Claridad sobre Cleverness | PASS | Reordenamiento lineal, sin trucos |
| Spec-Driven Development | PASS | Especificación completa antes de implementar |

**Resultado**: Todos los gates PASS. Sin violaciones que justificar.

## Project Structure

### Documentation (this feature)

```text
specs/049-reorder-columns-liquidaciones/
├── plan.md              # Este archivo
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── spec.md              # Especificación de la feature
```

### Source Code (repository root)

```text
src/presentacion_reflex/
├── pages/
│   └── liquidaciones.py          # Archivo principal a modificar
├── state/
│   └── liquidaciones_state.py    # Sin cambios (solo lectura)
├── components/
│   ├── liquidaciones/            # Sin cambios
│   ├── tablas.py                 # Sin cambios
│   └── shared/                   # Sin cambios
```

**Structure Decision**: Cambio aislado en `src/presentacion_reflex/pages/liquidaciones.py`. No se modifican state, components, ni backend.

## Complexity Tracking

> No hay violaciones de constitución. Sección omitida.

## Research Findings

### Análisis de Implementación Actual

**Tabla Individual** (`liquidaciones_table()`, líneas 327-519):
- 17 columnas actuales (incluyendo "Propiedad")
- Orden actual: ID → Periodo → **Propiedad** → Ciclo Operativo → Canon → Otros Ingresos → Gastos Admin → Gastos Serv → Gastos Rep → V. Incidentes → Pago Predial → Otros Egresos → **IVA Comision** → Neto a Pagar → Estado Recaudo → Estado → Acciones

**Tabla Agrupada** (`liquidaciones_table_agrupada()`, líneas 522-700):
- 16 columnas actuales (sin "Propiedad", usa "Propietario" y "Propiedades")
- Orden actual: Periodo → Propietario → Propiedades → Canon Total → Total Otros Ing. → Total Gastos Adm. → Total Gastos Serv. → Total Gastos Rep. → Total V. Incid. → Total Predial → Total Otros Egr. → Total IVA Com. → Neto Total → Estado Recaudo → Estado → Acciones

### Cambios Requeridos

**Tabla Individual** (17 → 16 columnas):
1. Eliminar columna "Propiedad" (posición 3)
2. Mover "IVA Comisión" de posición 13 a posición 5 (después de Canon)
3. Resultado: ID → Periodo → Ciclo Operativo → Canon → IVA Comisión → Otros Ingresos → Gastos Admin → Gastos Serv → Gastos Rep → V. Incidentes → Pago Predial → Otros Egresos → Neto a Pagar → Estado Recaudo → Estado → Acciones

**Tabla Agrupada** (16 columnas):
- Reordenar para alinearse con el patrón de ingresos → egresos → neto
- Mover "Total IVA Com." después de "Canon Total"
- Resultado: Periodo → Propietario → Propiedades → Canon Total → Total IVA Com. → Total Otros Ing. → Total Gastos Adm. → Total Gastos Serv. → Total Gastos Rep. → Total V. Incid. → Total Predial → Total Otros Egr. → Neto Total → Estado Recaudo → Estado → Acciones

### Puntos de Implementación

| Punto | Archivo | Líneas | Descripción |
|-------|---------|--------|-------------|
| Headers individuales | `pages/liquidaciones.py` | 332-349 | Reordenar celdas de encabezado, eliminar "Propiedad" |
| Body individuales | `pages/liquidaciones.py` | 357-513 | Reordenar celdas de datos, eliminar "Propiedad" |
| Headers agrupados | `pages/liquidaciones.py` | 528-545 | Reordenar celdas de encabezado agrupado |
| Body agrupados | `pages/liquidaciones.py` | 551-693 | Reordenar celdas de datos agrupados |

### Funcionalidades Afectadas (Verificación)

| Funcionalidad | Impacto | Notas |
|---------------|---------|-------|
| Ordenamiento | Ninguno | `column_id` no cambia, solo posición visual |
| Búsqueda rápida | Ninguno | Opera sobre datos, no posición de columnas |
| Filtros avanzados | Ninguno | `fin_column_options` no cambia |
| Paginación | Ninguno | Sin relación con orden de columnas |
| Scroll horizontal | Mejora | Una menos columna = mejor UX |
| Exportación PDF | Ninguno | PDF usa layout propio (no affected) |
| Exportación ZIP | Ninguno | Genera PDFs individuales |
| Config. columnas | Respeta existente | Default nuevo orden, config personal preservada |
