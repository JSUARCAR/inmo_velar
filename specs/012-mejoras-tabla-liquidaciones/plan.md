# Implementation Plan: Mejoras en Tabla de Liquidaciones

**Branch**: `[###-mejoras-tabla-liquidaciones]` | **Date**: 2026-07-04 | **Spec**: [spec.md](file:///C:/Users/PC/OneDrive/Desktop/inmobiliaria%20velar/PYTHON-REFLEX/specs/012-mejoras-tabla-liquidaciones/spec.md)

**Input**: Feature specification from `/specs/012-mejoras-tabla-liquidaciones/spec.md`

## Summary

Implementar funcionalidad de ordenamiento (ascendente y descendente) en las columnas de la tabla de Liquidaciones y añadir un filtro por "Ciclo Operativo". Además, corregir superposiciones y alinear correctamente la sección de filtros avanzados aplicando los lineamientos del Claude Design System.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: Reflex

**Storage**: PostgreSQL

**Testing**: pytest

**Target Platform**: Web application (Reflex)

**Project Type**: Web application

**Performance Goals**: Filtrado y ordenamiento con latencia de UI imperceptible (< 200ms para actualizaciones de estado)

**Constraints**: Adherencia estricta a Clean Architecture (Dominio -> Aplicación -> Infraestructura -> Presentación) y uso de PostgreSQL nativo. Manejo de estados de Reflex centralizado (mutaciones atómicas). No Flet, No SQLite.

**Scale/Scope**: Limitado al componente y estado de la tabla de Liquidaciones y la UI de Filtros Avanzados.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Arquitectura de Capas**: Aprobado. Las modificaciones de ordenamiento y filtrado de la UI solo afectarán la capa `Presentación` (Estado Reflex) y `Aplicación/Infraestructura` (métodos de consulta que acepten los nuevos parámetros). No se rompe el dominio.
- **Validación de Tipos y Lingüística**: Aprobado. Se usará tipado estricto, `snake_case` y `PascalCase` correspondientes.
- **Protocolo Zero Leak**: Aprobado. No hay exposición de credenciales.
- **Frontend UI Engineering**: Aprobado. Las correcciones visuales se basarán en los lineamientos de Claude Design System.
- **Manejo de Estados**: Aprobado. Mutaciones de variables de estado sin mutaciones in-place prohibidas por Reflex.
- **Base de datos**: Aprobado. PostgreSQL `%s` si se toca el repositorio (aunque se asume que se reutilizará / adaptará la query para pasar `ORDER BY`).

## Project Structure

### Documentation (this feature)

```text
specs/012-mejoras-tabla-liquidaciones/
├── plan.md              
├── research.md          
├── data-model.md        
└── quickstart.md        
```

### Source Code (repository root)

```text
src/
├── aplicacion/
│   └── (Servicios asociados a la obtención de liquidaciones para aceptar order_by y filtros extra)
├── infraestructura/
│   └── (Repositorio de liquidaciones para adaptar querys con ordenamiento)
└── presentacion_reflex/
    ├── estados/
    │   └── (EstadoLiquidacion: variables para columna_orden, tipo_orden, ciclo_operativo_filtro)
    └── paginas/
        └── (Vista de liquidaciones y componente de filtros)
```

**Structure Decision**: El proyecto sigue el modelo de Clean Architecture definido en el protocolo élite. Las modificaciones cruzarán desde la Presentación (Reflex UI y State) hacia Infraestructura (si es necesario modificar el Repository para aplicar ordenamiento en base de datos).

## Complexity Tracking

No aplica justificación de violaciones. No hay desviaciones de la constitución.
