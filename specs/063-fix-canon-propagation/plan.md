# Implementation Plan: Corrección de Propagación de Canon en Renovaciones

**Branch**: `063-fix-canon-propagation` | **Date**: 2026-07-22 | **Spec**: [spec.md](spec.md)

**Input**: Feature specification from `/specs/063-fix-canon-propagation/spec.md`

## Summary

Corregir la propagación del canon de arrendamiento desde Contratos hacia los módulos de Liquidación de Propietarios y Recaudos durante una renovación contractual. Actualmente, el cascade sync solo actualiza Mandatos y Propiedades, dejando Liquidaciones y Recaudos con valores desactualizados. La corrección incluye: (1) integrar la actualización de `canon_bruto` en LIQUIDACIONES y `valor_total` en RECAUDOS durante la renovación, (2) definir "registros futuros" como aquellos con `fecha_generacion` > fecha_renovacion, y (3) ejecutar las actualizaciones en una transacción atómica con rollback completo.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: psycopg2 (PostgreSQL driver), Reflex (UI framework)

**Storage**: PostgreSQL en Railway

**Testing**: pytest

**Target Platform**: Web application (Reflex/React frontend + Python backend)

**Project Type**: web-service (Clean Architecture: Dominio → Aplicación → Infraestructura → Presentación)

**Performance Goals**: <30 segundos para verificación de integridad con 100 registros

**Constraints**: Transacciones atómicas con rollback completo; 100% español en código y documentación

**Scale/Scope**: Sistema inmobiliario con múltiples contratos, liquidaciones periódicas y recaudos

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Estado | Notas |
|-----------|--------|-------|
| Clean Architecture (dependencias unidireccionales) | ✅ Pasa | Cambio en capa de Aplicación (servicio) e Infraestructura (repositorio) |
| 100% Español | ✅ Pasa | Todo el código y documentación en español |
| Type Hints obligatorios | ✅ Pasa | Se aplicarán en todo el código nuevo |
| PostgreSQL Native (%s placeholders) | ✅ Pasa | Consultas SQL con %s |
| Zero Leaking (seguridad) | ✅ Pasa | Sin credenciales en código |
| Commits con convenciones | ✅ Pasa | Se usará `fix(modulo): descripcion` |
| Contract-First | ✅ Pasa | Interfaces definidas antes de implementación |
| Stop-the-Line | ✅ Pasa | Se verificará que no haya tests fallidos |

**Resultado**: ✅ GATE PASSED - Sin violaciones que justificar

## Project Structure

### Documentation (this feature)

```text
specs/063-fix-canon-propagation/
├── plan.md              # Este archivo
├── research.md          # Phase 0 output ✅ COMPLETADO
├── data-model.md        # Phase 1 output ✅ COMPLETADO
├── quickstart.md        # Phase 1 output ✅ COMPLETADO
├── contracts/           # Phase 1 output ✅ COMPLETADO
│   ├── interfaces.md
│   └── sql-queries.md
└── tasks.md             # Phase 2 output (no creado por /speckit.plan)
```

### Source Code (repository root)

```text
src/
├── dominio/
│   └── entidades/
├── aplicacion/
│   └── servicios/
│       └── servicio_contrato_arrendamiento.py  # MODIFICAR: agregar cascade sync a Liquidaciones/Recaudos
├── infraestructura/
│   └── repositorios/
└── presentacion_reflex/

scripts/
└── diagnostico/
    └── audit_renovaciones_2026.py  # REFERENCIA: script de auditoría existente
```

**Structure Decision**: Se modifica el existente `servicio_contrato_arrendamiento.py` en la capa de Aplicación para integrar la propagación del canon a Liquidaciones y Recaudos durante el cascade sync de renovación. No se crean nuevos archivos de servicio, solo se extiende la lógica existente.
