# Data Model: Corrección Generación de Liquidaciones

**Date**: 2026-07-15
**Feature**: 056-fix-liquidaciones-generation

## Entidades Afectadas

### Liquidacion (sin cambios en estructura)

La entidad `Liquidacion` no sufre modificaciones estructurales. El fix afecta la **lógica de generación**, no el modelo de datos.

| Campo | Tipo | Descripción | Restricción |
|-------|------|-------------|-------------|
| id_liquidacion | INT | Identificador único | PK, AUTO_INCREMENT |
| id_contrato_m | INT | FK a ContratoMandato | FK, NOT NULL |
| periodo | VARCHAR(7) | Período YYYY-MM | NOT NULL |
| canon_bruto | DECIMAL | Canon de mandato | NOT NULL |
| comision_porcentaje | DECIMAL | Porcentaje de comisión (base 10000) | NOT NULL |
| comision_monto | DECIMAL | Monto de comisión calculado | NOT NULL |
| iva_comision | DECIMAL | IVA sobre comisión | NOT NULL |
| gastos_administracion | DECIMAL | Gastos de administración | DEFAULT 0 |
| valor_incidentes | DECIMAL | Valor de incidentes asociados | DEFAULT 0 |
| neto_a_pagar | DECIMAL | Neto a pagar al propietario | COMPUTED |
| estado_liquidacion | VARCHAR(20) | Estado de la liquidación | ENUM |
| eliminada | BOOLEAN | Soft delete | DEFAULT FALSE |

**Restricción UNIQUE**: `UNIQUE(ID_CONTRATO_M, PERIODO)` - una liquidación por contrato por período.

### ResultadoGeneracion (NUEVO - Value Object de retorno)

**Decision**: Crear un Value Object de retorno para `generar_liquidacion_propietario()` que encapsule los tres contadores.

```python
@dataclass(frozen=True)
class ResultadoGeneracionPropietario:
    """Resultado de la generación de liquidaciones para un propietario."""
    generadas: int = 0      # Liquidaciones creadas exitosamente
    omitidas: int = 0       # Contratos que ya tenían liquidación para el período
    errores: int = 0        # Fallos reales (datos inválidos, conexiones, etc.)
```

**Rationale**: Permite al caller (handler masivo) distinguir entre los tres estados sin mezclar lógica de negocio con presentación.

**Alternatives considered**:
- Retornar `int` con contador de generadas: Rechazado porque no distingue omitidas de errores.
- Retornar `Dict[str, int]`: Rechazado porque no tiene type safety.
- Lanzar excepción para "omitidas": Rechazado porque las excepciones deben ser para errores.

## State Transitions (sin cambios)

El flujo de estados de `Liquidacion` no cambia:

```
En Proceso → Aprobada → Pagada
    ↓           ↓
Cancelada   En Proceso (reversar)
    ↓
Pagada → Aprobada (reversar_pago)
```

## Consultas SQL Afectadas

### Query de propietarios activos (sin cambios)

```sql
SELECT DISTINCT prop.ID_PROPIETARIO
FROM PROPIETARIOS prop
INNER JOIN CONTRATOS_MANDATOS cm ON prop.ID_PROPIETARIO = cm.ID_PROPIETARIO
WHERE cm.ESTADO_CONTRATO_M = 'ACTIVO'
```

### Query de contratos por propietario (sin cambios)

```sql
SELECT ID_CONTRATO_M 
FROM CONTRATOS_MANDATOS
WHERE ID_PROPIETARIO = %s AND ESTADO_CONTRATO_M = 'ACTIVO'
```

### Query de validación de duplicado (sin cambios)

```sql
SELECT 1 FROM LIQUIDACIONES 
WHERE ID_CONTRATO_M = %s AND PERIODO = %s AND ELIMINADA = FALSE
```

## Integridad de Datos

- La restricción `UNIQUE(ID_CONTRATO_M, PERIODO)` previene duplicados a nivel de base de datos.
- El soft delete (`eliminada = FALSE`) preserva el historial.
- No se requieren migraciones de esquema para este fix.
