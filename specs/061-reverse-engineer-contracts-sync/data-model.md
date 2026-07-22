# Data Model: Ingeniería Inversa - Sincronización Contratos, Liquidaciones y Recaudos

**Date**: 2026-07-22
**Feature**: 061-reverse-engineer-contracts-sync

## Entities

### ContratoArrendamiento
Acuerdo de alquiler entre Inmobiliaria y Arrendatario.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Identificador único |
| id_propiedad | UUID | FK → Propiedad | Propiedad asociada |
| canon_arrendamiento | Decimal | NOT NULL | Canon de arrendamiento actual |
| fecha_inicio | Date | NOT NULL | Fecha de inicio del contrato |
| fecha_fin | Date | NOT NULL | Fecha de fin del contrato |
| estado | Enum | NOT NULL | Activo, Inactivo, Terminado |
| created_at | Timestamp | NOT NULL | Fecha de creación |

**Validation Rules**:
- canon_arrendamiento > 0
- fecha_fin > fecha_inicio
- Estado debe ser válido

**State Transitions**:
- Activo → Inactivo (suspendido)
- Activo → Terminado (vencimiento o rescisión)
- Inactivo → Activo (reactivación)

---

### ContratoMandato
Acuerdo entre Propietario e Inmobiliaria para administrar una propiedad.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Identificador único |
| id_propiedad | UUID | FK → Propiedad | Propiedad asociada |
| canon_mandato | Decimal | NOT NULL | Canon de mandato actual |
| fecha_inicio | Date | NOT NULL | Fecha de inicio del mandato |
| fecha_fin | Date | NOT NULL | Fecha de fin del mandato |
| estado | Enum | NOT NULL | Activo, Inactivo, Terminado |
| created_at | Timestamp | NOT NULL | Fecha de creación |

**Validation Rules**:
- canon_mandato > 0
- fecha_fin > fecha_inicio
- Debe estar sincronizado con ContratoArrendamiento de la misma propiedad

**State Transitions**:
- Same as ContratoArrendamiento

---

### Propiedad
Inmueble administrado por la inmobiliaria.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Identificador único |
| direccion | String | NOT NULL | Dirección del inmueble |
| canon_arrendamiento_estimado | Decimal | NOT NULL | Canon estimado (debe coincidir con mandato) |
| estado | Enum | NOT NULL | Disponible, Ocupada, En Mantenimiento |
| created_at | Timestamp | NOT NULL | Fecha de creación |

**Validation Rules**:
- canon_arrendamiento_estimado > 0
- Debe coincidir con canon_mandato del ContratoMandato activo

---

### RenovacionContrato
Registro histórico de renovaciones de contrato.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Identificador único |
| id_contrato_arrendamiento | UUID | FK → ContratoArrendamiento | Contrato renovado |
| canon_anterior | Decimal | NOT NULL | Canon antes de la renovación |
| canon_nuevo | Decimal | NOT NULL | Canon después de la renovación |
| porcentaje_incremento | Decimal | NOT NULL | Porcentaje de incremento aplicado |
| fecha_renovacion | Timestamp | NOT NULL | Fecha y hora de la renovación |
| motivo | String | OPTIONAL | Motivo de la renovación |

**Validation Rules**:
- canon_nuevo > 0
- porcentaje_incremento >= 0
- canon_nuevo = canon_anterior * (1 + porcentaje_incremento/100)

---

### Liquidacion
Estado de cuenta mensual del propietario.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Identificador único |
| id_propiedad | UUID | FK → Propiedad | Propiedad asociada |
| periodo | String | NOT NULL | Formato: YYYY-MM |
| canon_bruto | Decimal | NOT NULL | Canon bruto al momento de creación |
| descuentos | Decimal | DEFAULT 0 | Descuentos aplicados |
| valor_neto | Decimal | NOT NULL | Valor neto a pagar |
| estado | Enum | NOT NULL | Pendiente, Procesada, Pagada |
| created_at | Timestamp | NOT NULL | Fecha de creación |

**Validation Rules**:
- canon_bruto > 0
- valor_neto = canon_bruto - descuentos
- periodo formato YYYY-MM
- **CRÍTICO**: canon_bruto NO debe modificarse después de creación

**State Transitions**:
- Pendiente → Procesada (al generar recaudo)
- Procesada → Pagada (al registrar pago)

---

### Recaudo
Pago recibido del inquilino.

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | Identificador único |
| id_contrato_arrendamiento | UUID | FK → ContratoArrendamiento | Contrato asociado |
| periodo | String | NOT NULL | Formato: YYYY-MM |
| valor_total | Decimal | NOT NULL | Valor total al momento de creación |
| fecha_pago | Date | NOT NULL | Fecha del pago |
| estado | Enum | NOT NULL | Pendiente, Aplicado, Rechazado |
| created_at | Timestamp | NOT NULL | Fecha de creación |

**Validation Rules**:
- valor_total > 0
- fecha_pago válido
- **CRÍTICO**: valor_total NO debe modificarse después de creación

**State Transitions**:
- Pendiente → Aplicado (al confirmar pago)
- Pendiente → Rechazado (al rechazar pago)

---

## Relationships

```text
ContratoArrendamiento (1) ──── (1) ContratoMandato
        │                               │
        │                               │
        └─────── (N) Propiedad (N) ─────┘
                        │
                        │
                (N) Liquidacion
                        │
                        │
                (N) Recaudo
```

**Key Relationships**:
1. ContratoArrendamiento ↔ ContratoMandato: 1:1 por propiedad
2. Propiedad → Liquidacion: 1:N (una propiedad tiene muchas liquidaciones)
3. ContratoArrendamiento → Recaudo: 1:N (un contrato tiene muchos recaudos)
4. ContratoArrendamiento → RenovacionContrato: 1:N (un contrato tiene muchas renovaciones)

## Validation Queries

### Q1: Cascada de Renovación
```sql
-- Verificar que mandato y propiedad tienen el mismo canon que el contrato
SELECT
    ca.id,
    ca.canon_arrendamiento,
    cm.canon_mandato,
    p.canon_arrendamiento_estimado
FROM CONTRATOS_ARRENDAMIENTOS ca
JOIN PROPIEDADES p ON ca.id_propiedad = p.id
LEFT JOIN CONTRATOS_MANDATOS cm ON cm.id_propiedad = p.id AND cm.estado = 'Activo'
WHERE ca.estado = 'Activo'
AND (
    ca.canon_arrendamiento != cm.canon_mandato
    OR ca.canon_arrendamiento != p.canon_arrendamiento_estimado
);
```

### Q2: Preservación de Históricos
```sql
-- Verificar que liquidaciones antiguas no fueron modificadas
SELECT
    l.id,
    l.periodo,
    l.canon_bruto,
    l.created_at
FROM LIQUIDACIONES l
WHERE l.created_at < :fecha_renovacion
AND l.canon_bruto != :canon_anterior;
```

### Q3: Generación con Canon Actualizado
```sql
-- Verificar que liquidaciones futuras usan el canon nuevo
SELECT
    l.id,
    l.periodo,
    l.canon_bruto,
    :canon_nuevo as esperado
FROM LIQUIDACIONES l
WHERE l.created_at > :fecha_renovacion
AND l.canon_bruto != :canon_nuevo;
```

### Q4: Consistencia entre Módulos
```sql
-- Verificar que no hay discrepancias entre módulos
SELECT
    ca.id as contrato_id,
    ca.canon_arrendamiento,
    cm.canon_mandato,
    p.canon_arrendamiento_estimado,
    CASE
        WHEN ca.canon_arrendamiento = cm.canon_mandato
         AND ca.canon_arrendamiento = p.canon_arrendamiento_estimado
        THEN 'OK'
        ELSE 'DISCREPANCIA'
    END as estado
FROM CONTRATOS_ARRENDAMIENTOS ca
JOIN PROPIEDADES p ON ca.id_propiedad = p.id
LEFT JOIN CONTRATOS_MANDATOS cm ON cm.id_propiedad = p.id AND cm.estado = 'Activo';
```
