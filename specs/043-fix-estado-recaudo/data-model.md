# Data Model: Corrección del Estado Recaudo

**Fecha**: 2026-07-11
**Feature**: specs/043-fix-estado-recaudo

## Entidades Relacionadas

### LIQUIDACIONES

| Campo | Tipo | Descripción |
|-------|------|-------------|
| ID_LIQUIDACION | UUID/PK | Identificador único |
| ID_CONTRATO_M | UUID/FK | FK a CONTRATOS_MANDATOS |
| PERIODO | VARCHAR(7) | Formato YYYY-MM |
| ESTADO_LIQUIDACION | VARCHAR(20) | En Proceso/Aprobada/Pagada/Cancelada |
| eliminada | BOOLEAN | Soft delete |

### RECAUDOS

| Campo | Tipo | Descripción |
|-------|------|-------------|
| ID_RECAUDO | UUID/PK | Identificador único |
| ID_CONTRATO_A | UUID/FK | FK a CONTRATOS_ARRENDAMIENTOS |
| FECHA_PAGO | TIMESTAMP | Fecha de registro del recaudo |
| ESTADO_RECAUDO | VARCHAR(20) | Pendiente/Aplicado/Reversado/Vencido |
| VALOR_TOTAL | DECIMAL(12,2) | Valor total del recaudo |

### RECAUDO_CONCEPTOS

| Campo | Tipo | Descripción |
|-------|------|-------------|
| ID_RECAUDO_CONCEPTO | UUID/PK | Identificador único |
| ID_RECAUDO | UUID/FK | FK a RECAUDOS (CASCADE) |
| PERIODO | VARCHAR(7) | Formato YYYY-MM - **Este es el campo de vínculo** |
| TIPO_CONCEPTO | VARCHAR(20) | Canon/Administracion/Mora/Servicios/Otro |
| VALOR | DECIMAL(12,2) | Valor del concepto |

## Relación Liquidación ↔ Recaudo

```
LIQUIDACIONES.PERIODO ←→ RECAUDO_CONCEPTOS.PERIODO
         ↑                          ↑
         │                          │
    CONTRATOS_MANDATOS         RECAUDOS
         │                          │
         ↓                          ↓
      PROPIEDADES ←──────────→ PROPIEDADES
   (misma propiedad)
```

**Regla de vinculación**: Una liquidación se vincula con recaudos que:
1. Pertenecen a la **misma propiedad** (vía contratos)
2. Tienen el **mismo período** (en RECAUDO_CONCEPTOS.PERIODO)

## Enum: EstadoRecaudo

**Archivo**: `src/dominio/constantes/recaudo.py`

```python
class EstadoRecaudo(str, Enum):
    PENDIENTE = "Pendiente"
    APLICADO = "Aplicado"
    REVERSADO = "Reversado"
    VENCIDO = "Vencido"
```

## Jerarquía de Estados (Nueva Lógica)

Para determinar el `estado_recaudo` mostrado en liquidaciones:

1. **Sin Recaudo**: No existe ningún recaudo no-reversado para la propiedad+período
2. **Reversado**: Solo existen recaudos en estado `Reversado` para la propiedad+período
3. **Estado del vigente**: Existe al menos un recaudo no-reversado → mostrar su estado:
   - `Pendiente` → Pago registrado pero no procesado
   - `Aplicado` → Pago procesado y aplicado
   - `Vencido` → Pago vencido

**Regla clave**: El recaudo "vigente" es el **más reciente por FECHA_PAGO** entre los no-reversados.

## Cambios en Queries

### Filtros a Agregar

```sql
-- Filtro anti-reversado (NUEVO)
AND rrec_sub.ESTADO_RECAUDO != 'Reversado'

-- Ordenamiento por recencia (NUEVO)
ORDER BY rrec_sub.FECHA_PAGO DESC
```

### Sin Cambios en Esquema

No se requiere migración de BD. Los cambios son solo en las queries SQL.
