# Data Model: Corrección de Propagación de Canon en Renovaciones

**Date**: 2026-07-22
**Feature**: 063-fix-canon-propagation

## Entities

### Contrato de Arrendamiento (CONTRATOS_ARRENDAMIENTOS)

Tabla que contiene los contratos de arrendamiento activos y renovados.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id_contrato_a | SERIAL PRIMARY KEY | Identificador único del contrato |
| codigo | VARCHAR | Código del contrato |
| canon_arrendamiento | DECIMAL | Canon de arrendamiento vigente |
| arrendatario_id | INTEGER | FK a propietario |
| mandato_id | INTEGER | FK a contrato mandato |
| estado_contrato | VARCHAR | Estado del contrato |
| fecha_inicio | DATE | Fecha de inicio del contrato |
| fecha_fin | DATE | Fecha de fin del contrato |

### Renovación de Contrato (RENOVACIONES_CONTRATOS)

Tabla que registra las renovaciones de contratos con sus nuevos valores.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id_renovacion | SERIAL PRIMARY KEY | Identificador único de la renovación |
| id_contrato_a | INTEGER | FK al contrato de arrendamiento |
| canon_nuevo | DECIMAL | Nuevo canon de arrendamiento |
| fecha_renovacion | DATE | Fecha en que se aplicó la renovación |
| created_at | TIMESTAMP | Fecha de creación del registro |

### Liquidación de Propietarios (LIQUIDACIONES)

Tabla que contiene las liquidaciones financieras periódicas para propietarios.

| Campo | Tipo | Descripción | Relevante |
|-------|------|-------------|-----------|
| id_liquidacion | SERIAL PRIMARY KEY | Identificador único | No |
| id_contrato_m | INTEGER | FK al contrato mandato | Sí |
| canon_bruto | DECIMAL | Canon bruto de la liquidación | **SÍ - CAMPO A ACTUALIZAR** |
| periodo | VARCHAR | Período de la liquidación | No |
| estado_liquidacion | VARCHAR | Estado de la liquidación | No |
| fecha_generacion | VARCHAR | Fecha de generación (ISO 8601) | Sí - Para filtro de registros futuros |

### Recaudo (RECAUDOS)

Tabla que contiene los registros de cobros/pagos asociados a contratos.

| Campo | Tipo | Descripción | Relevante |
|-------|------|-------------|-----------|
| id_recaudo | SERIAL PRIMARY KEY | Identificador único | No |
| id_contrato_a | INTEGER | FK al contrato de arrendamiento | Sí |
| valor_total | DECIMAL | Valor total del recaudo | **SÍ - CAMPO A ACTUALIZAR** |
| fecha_pago | VARCHAR | Fecha de pago (ISO 8601) | Sí - Para filtro de registros futuros |
| estado_recaudo | VARCHAR | Estado del recaudo | No |

### Propiedad (PROPIEDADES)

Tabla que contiene las propiedades inmobiliarias asociadas a contratos.

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id_propiedad | SERIAL PRIMARY KEY | Identificador único |
| canon_arrendamiento_estimado | DECIMAL | Canon estimado de la propiedad |

### Contrato Mandato (CONTRATOS_MANDATOS)

Tabla que contiene los contratos de mandato (gestión de propiedades).

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id_contrato_m | SERIAL PRIMARY KEY | Identificador único |
| canon_mandato | DECIMAL | Canon del mandato |
| propiedad_id | INTEGER | FK a propiedad |

## Relationships

```
CONTRATOS_ARRENDAMIENTOS (1) ←── (N) RENOVACIONES_CONTRATOS
         │
         ├── (1) ←── (N) LIQUIDACIONES (vía id_contrato_m → CONTRATOS_MANDATOS)
         │
         └── (1) ←── (N) RECAUDOS (vía id_contrato_a)

CONTRATOS_MANDATOS (1) ←── (1) PROPIEDADES
```

## State Transitions

### Estados de Liquidación

```
PENDIENTE → PAGADA → CERRADA
    ↓
ANULADA
```

### Estados de Recaudo

```
PENDIENTE → PAGADO → CONFIRMADO
    ↓
ANULADO
```

## Validation Rules

1. **FR-003**: Actualizar `canon_bruto` solo en LIQUIDACIONES con `fecha_generacion::date > fecha_renovacion`
2. **FR-004**: Actualizar `valor_total` solo en RECAUDOS con `fecha_pago::date > fecha_renovacion`
3. **FR-005/FR-006**: NO modificar registros históricos (con fecha <= fecha_renovacion)
4. **FR-010**: Ejecutar todas las actualizaciones en una transacción atómica

## Indexes Recomendados

- `idx_liquidaciones_fecha_generacion` ON LIQUIDACIONES(fecha_generacion)
- `idx_recaudos_fecha_pago` ON RECAUDOS(fecha_pago)
- `idx_renovaciones_contrato` ON RENOVACIONES_CONTRATOS(id_contrato_a)
