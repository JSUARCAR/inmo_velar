# Data Model: Corrección GROUP BY en Módulo Incidentes

**Date**: 2026-07-08
**Feature**: 036-fix-incidents-group-by

## Entidades Involucradas

### INCIDENTES (Tabla Principal)

| Campo | Tipo | Constraints | Descripción |
|-------|------|-------------|-------------|
| ID_INCIDENTE | INTEGER | PK, AUTOINCREMENT | Identificador único |
| ID_PROPIEDAD | INTEGER | NOT NULL, FK → PROPIEDADES | Propiedad asociada |
| ID_CONTRATO_M | INTEGER | FK → CONTRATOS_MANDATOS | Contrato de mandato |
| DESCRIPCION_INCIDENTE | TEXT | NOT NULL | Descripción del incidente |
| COSTO_INCIDENTE | INTEGER | DEFAULT 0, CHECK ≥ 0 | Costo total |
| FECHA_INCIDENTE | TEXT | NOT NULL | Fecha del incidente |
| PRIORIDAD | TEXT | DEFAULT 'Media', CHECK IN (Baja, Media, Alta, Urgente) | Nivel de prioridad |
| ORIGEN_REPORTE | TEXT | DEFAULT 'Inquilino', CHECK IN (Inquilino, Propietario, Inmobiliaria) | Origen del reporte |
| RESPONSABLE_PAGO | TEXT | CHECK IN (Inquilino, Propietario, Inmobiliaria, Aseguradora) | Responsable del pago |
| ID_PROVEEDOR_ASIGNADO | INTEGER | FK → PROVEEDORES | Proveedor asignado |
| ID_COTIZACION_APROBADA | INTEGER | FK → COTIZACIONES | Cotización aprobada |
| ESTADO | TEXT | DEFAULT 'Reportado', CHECK IN (Reportado, En Revision, Cotizado, Aprobado, En Reparacion, Finalizado, Cancelado) | Estado actual |
| DIAS_SIN_RESOLVER | INTEGER | DEFAULT 0 | Días sin resolución |
| MOTIVO_CANCELACION | TEXT | | Motivo si se cancela |
| CREATED_AT | TEXT | DEFAULT datetime('now','localtime') | Fecha creación |
| CREATED_BY | TEXT | | Usuario creador |
| UPDATED_AT | TEXT | DEFAULT datetime('now','localtime') | Última actualización |
| UPDATED_BY | TEXT | | Usuario que actualizó |

**Índices**:
- `idx_incidentes_fecha`: (ID_PROPIEDAD, FECHA_INCIDENTE)
- `idx_incidentes_estado`: (ESTADO)
- `idx_incidentes_pendientes`: (ESTADO, DIAS_SIN_RESOLVER) WHERE ESTADO IN (...)

### COTIZACIONES (Tabla Relacionada)

| Campo | Tipo | Constraints | Descripción |
|-------|------|-------------|-------------|
| ID_COTIZACION | INTEGER | PK, AUTOINCREMENT | Identificador único |
| ID_INCIDENTE | INTEGER | NOT NULL, FK → INCIDENTES | Incidente asociado |
| ID_PROVEEDOR | INTEGER | NOT NULL, FK → PROVEEDORES | Proveedor que cotiza |
| VALOR_MATERIALES | INTEGER | DEFAULT 0, CHECK ≥ 0 | Costo materiales |
| VALOR_MANO_OBRA | INTEGER | DEFAULT 0, CHECK ≥ 0 | Costo mano de obra |
| VALOR_TOTAL | INTEGER | NOT NULL, CHECK ≥ 0 | Costo total |
| DESCRIPCION_TRABAJO | TEXT | | Descripción del trabajo |
| DIAS_ESTIMADOS | INTEGER | DEFAULT 1 | Días estimados |
| FECHA_COTIZACION | TEXT | DEFAULT datetime('now','localtime') | Fecha de cotización |
| ESTADO_COTIZACION | TEXT | DEFAULT 'Pendiente', CHECK IN (Pendiente, Aprobada, Rechazada) | Estado de la cotización |
| CREATED_AT | TEXT | DEFAULT datetime('now','localtime') | Fecha creación |
| CREATED_BY | TEXT | | Usuario creador |

### Relación INCIDENTES → COTIZACIONES

**Tipo**: One-to-Many (Un incidente tiene múltiples cotizaciones)

**Cardinalidad**:
- 1 INCIDENTE → 0..N COTIZACIONES
- 1 COTIZACION → 1 INCIDENTE

**En la consulta SQL**:
```sql
LEFT JOIN LATERAL (
    SELECT JSON_AGG(
        JSON_BUILD_OBJECT(
            'id_cotizacion', C.ID_COTIZACION,
            'id_proveedor', C.ID_PROVEEDOR,
            'valor_total', C.VALOR_TOTAL,
            'estado', C.ESTADO_COTIZACION
        ) ORDER BY C.FECHA_COTIZACION DESC
    ) as cotizaciones
    FROM COTIZACIONES C 
    WHERE C.ID_INCIDENTE = I.ID_INCIDENTE
) cot ON TRUE
```

**Salida JSON esperada por incidente**:
```json
{
    "id_incidente": 1,
    "cotizaciones": [
        {"id_cotizacion": 3, "id_proveedor": 2, "valor_total": 500000, "estado": "Aprobada"},
        {"id_cotizacion": 1, "id_proveedor": 1, "valor_total": 450000, "estado": "Rechazada"}
    ],
    "plan_pago": {"id_plan_pago": 1, "num_cuotas": 1, "valor_cuota": 500000, ...}
}
```

## Estructura de Respuesta del Repositorio

El método `listar_con_filtros` retorna:
```python
{
    "items": List[Incidente],  # Lista de incidentes mapeados
    "total": int               # Total de registros (para paginación)
}
```

Cada `Incidente` contiene:
- `cotizaciones_resumen`: Lista de diccionarios JSON con resumen de cotizaciones
- `plan_pago`: Diccionario JSON con el plan de pago activo

## Cambios en el Data Model

**No se requieren cambios en el schema de base de datos.** El fix es puramente en la consulta SQL (eliminación del `GROUP BY` redundante).

Las tablas, columnas, relaciones e índices permanecen intactos.
