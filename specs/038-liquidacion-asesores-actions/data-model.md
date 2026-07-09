# Data Model: Disponibilidad de Acciones por Estado - Liquidacion Asesores

**Feature**: 038-liquidacion-asesores-actions
**Date**: 2026-07-08

## Entities

### 1. LiquidacionAsesor (MODIFICADA)

**Table**: `LIQUIDACIONES_ASESORES`

**New Column**:

| Column | Type | Default | Description |
|--------|------|---------|-------------|
| ELIMINADA | BOOLEAN | FALSE | Flag de soft delete |

**SQL Migration**:
```sql
ALTER TABLE LIQUIDACIONES_ASESORES 
ADD COLUMN ELIMINADA BOOLEAN DEFAULT FALSE;

CREATE INDEX idx_liquidaciones_asesor_eliminada 
ON LIQUIDACIONES_ASESORES(ELIMINADA);
```

**Existing Columns** (referencia):

| Column | Type | Description |
|--------|------|-------------|
| ID_LIQUIDACION_ASESOR | INTEGER PK | Identificador único |
| ID_CONTRATO_A | INTEGER FK | Contrato de arrendamiento |
| ID_ASESOR | INTEGER FK | Asesor inmobiliario |
| PERIODO_LIQUIDACION | TEXT | Formato: YYYY-MM |
| CANON_ARRENDAMIENTO_LIQUIDADO | INTEGER | Canon del mes |
| PORCENTAJE_COMISION | INTEGER | 0-10000 (0.00%-100.00%) |
| COMISION_BRUTA | INTEGER | Calculada: canon × (pct/10000) |
| TOTAL_DESCUENTOS | INTEGER | Suma de descuentos |
| TOTAL_BONIFICACIONES | INTEGER | Suma de bonificaciones |
| VALOR_NETO_ASESOR | INTEGER | Comisión + bonificaciones - descuentos |
| ESTADO_LIQUIDACION | TEXT | Pendiente, Aprobada, Pagada, Anulada |
| MODO_COMISION | TEXT | ASESOR, CONTRATO_MANDATO |
| OBSERVACIONES_LIQUIDACION | TEXT | Notas |
| MOTIVO_ANULACION | TEXT | Razón de anulación |
| FECHA_APROBACION | TIMESTAMP | Cuándo se aprobó |
| USUARIO_APROBADOR | VARCHAR | Quién aprobó |
| CREATED_AT | TIMESTAMP | Auto |
| CREATED_BY | VARCHAR | Creador |
| UPDATED_AT | TIMESTAMP | Última actualización |
| UPDATED_BY | VARCHAR | Último editor |

**State Transitions** (nuevo flujo):

```
                    ┌──────────────────────────────────────────┐
                    │                                          │
                    ▼                                          │
              ┌──────────┐     aprobar      ┌──────────┐      │
              │ Pendiente │ ──────────────► │ Aprobada │      │
              └──────────┘                  └──────────┘      │
                    │                         │     │          │
                    │ eliminar                │     │          │
                    │ (soft delete)           │     │ pagar    │
                    ▼                         │     ▼          │
              ┌──────────┐                   │ ┌──────────┐   │
              │ Eliminada │                   │ │  Pagada  │   │
              └──────────┘                   │ └──────────┘   │
                                             │                 │
                                             │ reversar_pago   │
                                             │ (Pagada→Aprob) │
                                             │                 │
                                             ▼                 │
                                       ┌──────────┐           │
                                       │ Aprobada │ ◄─────────┘
                                       └──────────┘
                                             │
                                             │ reversar
                                             │ (Aprob→Pend)
                                             ▼
                                       ┌──────────┐
                                       │ Pendiente │
                                       └──────────┘

              ┌──────────┐     anular      ┌──────────┐
              │ Pendiente │ ──────────────► │ Anulada  │ ◄───┐
              │ Aprobada  │ ──────────────► │          │     │
              └──────────┘                  └──────────┘     │
                                            reversar         │
                                            (Anulada→Pend) ──┘
```

### 2. DescuentoAsesor (SIN CAMBIOS)

**Table**: `DESCUENTOS_ASESORES`

No requiere modificaciones. Ya tiene `ON DELETE CASCADE` en FK.

### 3. PagoAsesor (SIN CAMBIOS)

**Table**: `PAGOS_ASESORES`

No requiere modificaciones. Ya tiene `ON DELETE CASCADE` en FK.

### 4. LiquidacionContrato (SIN CAMBIOS)

**Table**: `LIQUIDACIONES_CONTRATOS`

No requiere modificaciones.

## Validation Rules

### Eliminar

| Rule | Layer | Description |
|------|-------|-------------|
| Estado == "Pendiente" | Service + UI | Solo liquidaciones pendientes |
| No tiene descuentos | Service | Rechazar si existen DESCUENTOS_ASESORES |
| No tiene pagos | Service | Rechazar si existen PAGOS_ASESORES |
| No está eliminada | Service | Idempotente |

### Reversar

| Rule | Layer | Description |
|------|-------|-------------|
| Estado != "Pendiente" | Service + UI | No reversar pendientes |
| Motivo >= 10 chars | Service + UI | Para Pagada y Anulada |
| Estado válido para reversión | Service | Aprobada→Pend, Pagada→Aprob, Anulada→Pend |

## Indexes (nuevo)

```sql
-- Para queries de soft delete
CREATE INDEX idx_liquidaciones_asesor_eliminada 
ON LIQUIDACIONES_ASESORES(ELIMINADA);

-- Para filtrar eliminadas en queries existentes
-- Agregar a queries existentes: AND ELIMINADA = FALSE
```

## Query Updates

Todas las queries existentes deben agregar `AND ELIMINADA = FALSE`:

```sql
-- Ejemplo: listar_paginado
SELECT ... FROM LIQUIDACIONES_ASESORES la
WHERE la.ELIMINADA = FALSE
  AND (... filtros existentes ...)
```
