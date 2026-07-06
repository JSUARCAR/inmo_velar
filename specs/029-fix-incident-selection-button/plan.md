# Implementation Plan: fix-incident-selection-button

**Branch**: `029-fix-incident-selection-button` | **Date**: 2026-07-06 | **Spec**: [spec.md](file:///c:/Users/PC/OneDrive/Desktop/inmobiliaria%20velar/PYTHON-REFLEX/specs/029-fix-incident-selection-button/spec.md)

**Input**: Feature specification from `specs/029-fix-incident-selection-button/spec.md`

## Summary

Se identificó la causa raíz de la regresión del botón "Seleccionar Incidentes" en el módulo de Liquidaciones: un **`TypeError` en runtime** causado por un parámetro faltante (`justificacion`) en la llamada al servicio `ServicioIncidenteLiquidacion.asociar_incidente()`. Adicionalmente, se detectó una conexión a BD sin context manager que puede causar leaks. El fix es **quirúrgico** (2 bloques de código en 1 archivo).

## Technical Context

**Language/Version**: Python 3.12 + Reflex Framework

**Primary Dependencies**: Reflex (UI/State), psycopg2 (PostgreSQL), Pydantic (DTOs)

**Storage**: PostgreSQL (Railway). Tablas: `LIQUIDACIONES`, `INCIDENTES`, `PLAN_PAGO_INCIDENTE`, `CUOTA_INCIDENTE`, `INCIDENTE_LIQUIDACION`

**Testing**: Validación manual en vivo + verificación SQL directa

**Target Platform**: Web (Reflex SSR)

**Project Type**: Web application (ERP inmobiliario)

**Performance Goals**: Modal de incidentes carga en < 2 segundos

**Constraints**: Cambios mínimos (< 20 líneas), cero regresiones

**Scale/Scope**: 1 archivo modificado, 2 bloques de código

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Estado | Detalle |
|-----------|--------|---------|
| §2.2 Nomenclatura | ✅ PASS | Nombres en español, snake_case |
| §2.3 PostgreSQL Native | ✅ PASS | Usa `%s`, no `?`. Usa `RETURNING id` |
| §4 Zero Leak | ✅ FIX | Conexión sin `with` → se corregirá |
| §7 Zero Guessing | ✅ PASS | Causa raíz confirmada por inspección de código |
| §8 Cambios Atómicos | ✅ PASS | < 20 líneas modificadas |
| §13 Stop-the-Line | ✅ PASS | Fix de regresión, no feature nueva |
| §16 Portals/z-index | ✅ PASS | `pointer-events: auto` ya aplicado en modal |

**Post-Design Re-check**: ✅ Todos los gates pasan. Sin violaciones.

## Project Structure

### Documentation (this feature)

```text
specs/029-fix-incident-selection-button/
├── spec.md              ✅ Spec completada
├── plan.md              ✅ Este archivo
├── research.md          ✅ Investigación completada
├── data-model.md        ✅ Modelo documentado
├── quickstart.md        ✅ Guía de validación
├── checklists/
│   └── requirements.md  ✅ Checklist de calidad
└── tasks.md             ⬜ Generado por /speckit-tasks
```

### Source Code (cambios)

```text
src/presentacion_reflex/state/
└── liquidaciones_state.py    # FIX: 2 bloques
    ├── L1973-1998  → Refactorizar conexión BD con `with`
    └── L2136-2142  → Agregar parámetro `justificacion`
```

## Cambios Detallados

### Fix 1: Conexión BD sin Context Manager (L1973-1998)

**Problema**: `conn = dm.obtener_conexion()` sin `with`, riesgo de leak.

**Antes**:
```python
conn = dm.obtener_conexion()
cursor = dm.get_dict_cursor(conn)
placeholder = dm.get_placeholder()

query = f"""..."""
cursor.execute(query, ...)
rows = cursor.fetchall()
```

**Después**:
```python
with dm.obtener_conexion() as conn:
    cursor = dm.get_dict_cursor(conn)
    placeholder = dm.get_placeholder()

    query = f"""..."""
    cursor.execute(query, ...)
    rows = cursor.fetchall()
```

### Fix 2: Parámetro `justificacion` Faltante (L2136-2142)

**Problema**: `servicio.asociar_incidente()` se llama con 5 argumentos pero la firma requiere 6 (falta `justificacion`).

**Antes**:
```python
resultado = servicio.asociar_incidente(
    id_incidente=incidente["id"],
    id_liquidacion=id_liquidacion,
    numero_cuota=incidente["num_cuota"],
    valor_descuento=incidente["valor_cuota"],
    asociado_por=usuario,
)
```

**Después**:
```python
resultado = servicio.asociar_incidente(
    id_incidente=incidente["id"],
    id_liquidacion=id_liquidacion,
    numero_cuota=incidente["num_cuota"],
    valor_descuento=incidente["valor_cuota"],
    asociado_por=usuario,
    justificacion=f"Asociación desde liquidación #{id_liquidacion}",
)
```

## Verificación

### Validación en Vivo
1. Navegar a `/liquidaciones`
2. Editar una liquidación "En Proceso"
3. Verificar botón "Seleccionar Incidentes" visible
4. Click → Modal se abre con incidentes
5. Seleccionar → Asociar → Toast de éxito
6. Verificar neto actualizado en tabla
7. Consultar BD para confirmar persistencia

### Consola Limpia
- Sin `TypeError` en logs del servidor
- Sin errores en consola del navegador

### Regresión
- Verificar que flujos existentes (crear, editar, aprobar, pagar, eliminar) siguen funcionando

## Complexity Tracking

> No hay violaciones de Constitution Check. No aplica.
