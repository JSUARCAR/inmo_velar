# Implementation Plan: Corrección del Estado Recaudo

**Branch**: `bugfix/043-fix-estado-recaudo` | **Date**: 2026-07-11 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/043-fix-estado-recaudo/spec.md`

## Summary

Corregir la lógica de negocio que determina el valor mostrado en la columna **Estado Recaudo** del módulo Liquidaciones. La causa raíz es que las subqueries SQL no filtran recaudos reversados ni ordenan por fecha, provocando que se muestre un estado incorrecto o de otro período.

**Enfoque técnico**: Modificar las queries SQL en el repositorio de liquidaciones para:
1. Filtrar recaudos con estado `Reversado`
2. Ordenar por `FECHA_PAGO DESC` (más reciente primero)
3. Aplicar `LIMIT 1` después del filtro y orden

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: Reflex (Framework UI), psycopg2 (PostgreSQL driver)

**Storage**: PostgreSQL

**Testing**: Pruebas manuales + verificación SQL (no hay suite automatizada para esta funcionalidad)

**Target Platform**: Web application (Railway deployment)

**Project Type**: Web application (Reflex frontend + Python backend)

**Performance Goals**: Sin degradación significativa (queries ya optimizadas con índices)

**Constraints**: 
- Retrocompatible con funcionalidad existente
- Sin migraciones de BD
- Mantener integridad referencial

**Scale/Scope**: 
- ~50-100 liquidaciones por consulta paginada
- 2 archivos principales a modificar

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Estado | Notas |
|-----------|--------|-------|
| Clean Architecture | ✅ | Cambio en capa de Infraestructura (repositorio) |
| Idioma Español | ✅ | Queries y código en español |
| Type Hints | ✅ | Ya existentes en el código |
| Zero Guessing | ✅ | Ambigüedades resueltas en clarify |
| PostgreSQL Native | ✅ | Usando %s placeholders |
| Sin Flet/SQLite | ✅ | Solo PostgreSQL |

**Resultado**: ✅ PASS - Sin violaciones

## Project Structure

### Documentation (this feature)

```text
specs/043-fix-estado-recaudo/
├── plan.md              # Este archivo
├── research.md          # Fase 0: Descubrimientos y decisiones
├── data-model.md        # Fase 1: Modelo de datos y relaciones
├── quickstart.md        # Fase 1: Guía de validación
└── spec.md              # Especificación original
```

### Source Code (repository root)

```text
src/
├── dominio/
│   ├── entidades/
│   │   ├── liquidacion.py          # Entidad Liquidacion (sin cambios)
│   │   └── recaudo.py              # Entidad Recaudo (sin cambios)
│   └── constantes/
│       └── recaudo.py              # Enum EstadoRecaudo (sin cambios)
├── infraestructura/
│   └── persistencia/
│       ├── repositorio_liquidacion_postgres.py  # ← CAMBIAR
│       └── repositorio_recaudo.py               # ← VERIFICAR
├── aplicacion/
│   └── servicios/
│       └── servicio_financiero.py  # Sin cambios
└── presentacion_reflex/
    ├── pages/
    │   └── liquidaciones.py        # Sin cambios (badges ya correctos)
    └── state/
        └── liquidaciones_state.py  # Sin cambios
```

**Structure Decision**: Se mantiene la estructura existente. Los cambios son quirúrgicos en el repositorio de persistencia.

## Complexity Tracking

No hay violaciones que justificar. El cambio es de baja complejidad.

## Fases de Implementación

### Fase 0: Research ✅

**Archivo**: `research.md`

Descubrimientos clave:
- Causa raíz: `LIMIT 1` sin `ORDER BY` ni filtro de reversados
- Estados reales: Pendiente/Aplicado/Reversado/Vencido (no los de la spec original)
- 2 archivos a modificar: `repositorio_liquidacion_postgres.py` y `repositorio_recaudo.py`

### Fase 1: Design ✅

**Archivos**: `data-model.md`, `quickstart.md`

- Modelo de datos documentado
- Relación Liquidación ↔ Recaudo por período
- 6 escenarios de validación definidos

### Fase 2: Tasks (próximo comando `/speckit-tasks`)

Tareas pendientes de generar:
1. Corregir subquery en `listar_paginado()`
2. Corregir batch query en `_obtener_estados_recaudo_por_grupos()`
3. Verificar `obtener_estado_pago_actual()`
4. Ejecutar pruebas de regresión
5. Validar en UI los 6 escenarios

## Criterios de Éxito

1. **Precisión**: Estado Recaudo siempre refleja el recaudo vigente (más reciente, no reversado)
2. **Consistencia**: UI muestra exactamente lo que retorna la query
3. **Escenarios**: Los 6 casos de prueba pasan exitosamente
4. **No Regresión**: Otros módulos no se afectan
5. **Performance**: Sin degradación medible en tiempos de respuesta
