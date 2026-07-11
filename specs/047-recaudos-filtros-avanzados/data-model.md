# Data Model: Filtros Avanzados Recaudos

**Date**: 2026-07-11

## Entidades Relacionadas

### Recaudo → Contrato de Arrendamiento

```
RECAUDOS.ID_CONTRATO_A  →  CONTRATOS_ARRENDAMIENTOS.ID_CONTRATO_A
```

**Tipo**: FK directa, many-to-one (muchos recaudos apuntan a un contrato)

### Contrato de Arrendamiento → Propiedad

```
CONTRATOS_ARRENDAMIENTOS.ID_PROPIEDAD  →  PROPIEDADES.ID_PROPIEDAD
```

**Tipo**: FK directa, many-to-one

### Propiedad ← Contrato de Mandato

```
CONTRATOS_MANDATOS.ID_PROPIEDAD  ←  PROPIEDADES.ID_PROPIEDAD
WHERE ESTADO_CONTRATO_M = 'ACTIVO'
ORDER BY FECHA_INICIO_CONTRATO_M DESC
LIMIT 1
```

**Tipo**: LATERAL JOIN (un contrato de mandato activo más reciente por propiedad)

## Campo: Día de Pago (Pago Contrato)

**Fuente**: `CONTRATOS_ARRENDAMIENTOS`

**Expresión SQL**:
```sql
COALESCE(NULLIF(ca.FECHA_PAGO, ''), EXTRACT(DAY FROM ca.FECHA_INICIO_CONTRATO_A::DATE)::TEXT)
```

**Lógica**:
1. Si `FECHA_PAGO` no es nulo ni vacío → usar `FECHA_PAGO`
2. Si es nulo o vacío → extraer el día del mes de `FECHA_INICIO_CONTRATO_A`
3. Si ambos son nulos → el registro no tiene día de pago

**Tipo de dato resultante**: TEXT (día como string, ej: "1", "15", "31")

**Validación**: El valor resultante debe ser un número entero entre 1 y 31.

## Campo: Ciclo Operativo

**Fuente**: `CONTRATOS_MANDATOS.GRUPO_OPERATIVO`

**Expresión SQL** (subconsulta LATERAL):
```sql
LEFT JOIN LATERAL (
    SELECT GRUPO_OPERATIVO
    FROM CONTRATOS_MANDATOS
    WHERE ID_PROPIEDAD = ca.ID_PROPIEDAD
      AND ESTADO_CONTRATO_M = 'ACTIVO'
    ORDER BY FECHA_INICIO_CONTRATO_M DESC
    LIMIT 1
) cm ON true
```

**Lógica**:
1. Buscar el contrato de mandato activo más reciente para la propiedad del recaudo
2. Tomar su `GRUPO_OPERATIVO`
3. Si no existe contrato activo → el recaudo no tiene ciclo operativo

**Tipo de dato resultante**: INTEGER (número del grupo, ej: 1, 2, 3, 4)

**Presentación en UI**: `"Grupo {GRUPO_OPERATIVO}"` (ej: "Grupo 1")

## Tabla de Filtros (FiltrosRecaudo)

**Archivo**: `src/dominio/interfaces/repositorio_recaudo.py`

**Cambios necesarios**:

```python
@dataclass(frozen=True)
class FiltrosRecaudo:
    estado: Optional[EstadoRecaudo] = None
    fecha_desde: Optional[str] = None
    fecha_hasta: Optional[str] = None
    dia_pago: Optional[List[str]] = None      # CAMBIO: str → List[str] para multi-select
    ciclo_operativo: Optional[List[str]] = None  # NUEVO: multi-select
    busqueda: Optional[str] = None
    sort_by: str = "fecha_pago"
    sort_order: str = "desc"
    page: int = 1
    page_size: int = 25
```

## Patrón de Composición de Filtros

```
WHERE 1=1
  AND r.ESTADO_RECAUDO = %s           -- filter_estado (AND)
  AND COALESCE(...) IN (%s, %s, ...)  -- filter_dia_pago (OR intra-filtro)
  AND cm.GRUPO_OPERATIVO IN (%s, %s, ...)  -- filter_ciclo_operativo (OR intra-filtro)
  AND r.FECHA_PAGO >= %s             -- filter_fecha_desde (AND)
  AND r.FECHA_PAGO <= %s             -- filter_fecha_hasta (AND)
  AND (búsqueda multi-columna OR)     -- busqueda (AND)
```

**Regla**: AND entre diferentes filtros, OR dentro de cada filtro multi-select.
