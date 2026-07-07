# Data Model: Filtro de Pago en Incidentes

Este documento detalla el impacto en el modelo de datos y las consultas PostgreSQL necesarias para soportar la funcionalidad de filtrado de incidentes por estado de pago.

## Entidades Relevantes

### 1. Incidente (Existente)
Representa el evento base que se muestra en la tabla.
*   **Campos clave involucrados**: `id`, `fecha_creacion`, etc.
*   **Relación**: Un incidente tiene de 0 a N `Liquidaciones` asociadas.

### 2. Liquidacion (Existente)
Contiene la información transaccional/financiera.
*   **Campos clave involucrados**: `id`, `incidente_id`, `estado`.
*   **El `estado`** en la liquidación dicta el estado de pago del incidente. (Ej: "Pagada", "Pendiente").

## DTOs y State (Nuevos/Modificados)

### 1. Opciones de Filtro (Aplicación / Presentación)
Se requiere transportar la lista de estados dinámicos desde la BD hasta el ComboBox de Reflex.
*   `lista_estados_pago: list[str]` en `IncidentesState`.

### 2. Parámetros de Consulta (Aplicación / Infraestructura)
Los DTOs de búsqueda (como un `IncidentesFiltroDTO`) deben ser ampliados:
*   `estado_pago: str | None = None`

## Modificaciones de Consultas (Infraestructura)

### 1. Extracción Dinámica de Estados
Consulta para poblar el ComboBox:
```sql
SELECT DISTINCT l.estado 
FROM liquidaciones l
JOIN incidentes i ON l.incidente_id = i.id
WHERE l.estado IS NOT NULL;
```
*(Se usarán los mecanismos de conexión y cursores ya existentes en la capa de persistencia con `%s`)*.

### 2. Filtrado de Incidentes
Consulta principal de incidentes modificada para soportar el parámetro `estado_pago`:
```sql
SELECT i.* 
FROM incidentes i
WHERE (%s IS NULL OR EXISTS (
    SELECT 1 FROM liquidaciones l 
    WHERE l.incidente_id = i.id AND l.estado = %s
))
-- + otros filtros existentes...
```
*(Nota: El paso de parámetros nulos requiere precaución con `%s`, el manejador en Python determinará si se anexa la cláusula SQL condicionalmente)*.
