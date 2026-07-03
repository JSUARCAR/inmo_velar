# Data Model: Sincronización Incidentes y Liquidaciones

El modelo de datos no requiere la creación de nuevas entidades ni tablas, pero sí la integración efectiva de las relaciones ya definidas en el esquema PostgreSQL actual.

## Entidades Existentes Involucradas

### 1. Incidente (`INCIDENTES`)
- **Atributos Relevantes**: `id_incidente`, `estado` (Reportado, ..., Aprobado, Finalizado).
- **Relaciones**: 
  - 1 a 1 (o 1 a N, típicamente 1 activo) con `PlanPagoIncidente`.

### 2. PlanPagoIncidente (`PLAN_PAGO_INCIDENTE`)
- **Atributos Relevantes**: 
  - `id_plan_pago` (PK)
  - `id_incidente` (FK a INCIDENTES)
  - `num_cuotas`
  - `valor_cuota`
  - `total_plan`
  - `estado` (Activo, Completado, Cancelado)
- **Relaciones**:
  - 1 a N con `CuotaIncidente`.

### 3. CuotaIncidente (`CUOTA_INCIDENTE`)
- **Atributos Relevantes**:
  - `id_cuota` (PK)
  - `id_plan_pago` (FK a PLAN_PAGO_INCIDENTE)
  - `id_liquidacion` (FK opcional a LIQUIDACIONES_PROPIETARIOS)
  - `valor_cuota`
  - `estado_pago` (Pendiente, Asociada, Pagada)

### 4. LiquidacionPropietario (`LIQUIDACIONES_PROPIETARIOS`)
- **Atributos Relevantes**:
  - `id_liquidacion` (PK)
  - `id_contrato_m` (FK a CONTRATOS_MANDATOS)
  - `valor_incidentes` (Columna de suma de cuotas asociadas)
  - `estado_liquidacion` (En Proceso, Aprobada, Pagada, Cancelada)
- **Relaciones**:
  - 1 a N con `CuotaIncidente` (a través de `id_liquidacion` en la cuota).

## Modificaciones Estructurales

- **En Entidad `Incidente`**: Exponer en la lógica de negocio y consultas de infraestructura un atributo adicional o propiedad que incluya un objeto o diccionario con la representación de su `PlanPagoIncidente` activo, para que sea mapeado y consumido por la capa de Presentación Reflex.

## Flujos de Estado (State Transitions)

1. **Aprobación de Cotización**:
   - Incidente pasa a `estado = 'Aprobado'`.
   - Se inserta nuevo registro en `PLAN_PAGO_INCIDENTE` (`estado = 'Activo'`).
   - Se insertan `N` registros en `CUOTA_INCIDENTE` (`estado_pago = 'Pendiente'`).

2. **Generación de Liquidación**:
   - Al crear una nueva Liquidación, el sistema busca todas las `CUOTA_INCIDENTE` en estado `'Pendiente'` asociadas a la propiedad/contrato correspondiente al Incidente.
   - Las cuotas actualizan su `id_liquidacion` al ID generado y su `estado_pago` cambia a `'Asociada'`.
   - `LiquidacionPropietario.valor_incidentes` es la suma de `valor_cuota` de las cuotas asociadas.

3. **Finalización de Liquidación**:
   - Liquidación pasa a `estado_liquidacion = 'Pagada'` o `'Aprobada'`.
   - Automáticamente, las cuotas con dicho `id_liquidacion` cambian su `estado_pago = 'Pagada'`.
