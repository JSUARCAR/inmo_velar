# Modelo de Datos - Ingeniería Inversa Estado de Cuenta PDF

**Date**: 2026-07-16
**Feature**: 058-reverse-engineer-pdf-statement

## Entidades Afectadas

### Liquidacion

Representa la liquidación mensual de un contrato de mandato para un propietario.

| Campo | Tipo | Descripción | Afectado por Feature |
|-------|------|-------------|---------------------|
| `id` | Integer | Identificador único | No |
| `contrato_mandato_id` | Integer | FK al contrato de mandato | No |
| `total_ingresos` | Decimal | Total de ingresos (canon) | Sí (renderización) |
| `comision_monto` | Decimal | Monto de comisión calculado | Sí (renderización) |
| `iva_comision` | Decimal | IVA sobre comisión | Sí (renderización) |
| `gastos_administracion` | Decimal | Gastos de administración | Sí (renderización) |
| `gastos_servicios` | Decimal | Gastos de servicios públicos | Sí (renderización) |
| `pago_predial` | Decimal | Pago de impuesto predial | Sí (renderización) |
| `valor_incidentes` | Decimal | Valor total de incidentes | Sí (renderización) |
| `valor_neto` | Decimal | Valor neto a pagar | Sí (renderización) |
| `observaciones` | Text | Observaciones de la liquidación | No |

### ContratoMandato

Contrato que establece el canon de mandato y el porcentaje de comisión.

| Campo | Tipo | Descripción | Afectado por Feature |
|-------|------|-------------|---------------------|
| `id` | Integer | Identificador único | No |
| `comision_porcentaje` | Integer | Porcentaje de comisión (base 10000) | Sí (renderización) |
| `canon_mandato` | Decimal | Canon de mandato mensual | No |

**Nota**: `comision_porcentaje` se almacena en base 10000:
- 500 = 5%
- 800 = 8%
- 1200 = 12%

## Relaciones

```
ContratoMandato (1) ───── (N) Liquidacion
       │
       └── comision_porcentaje → Se muestra en RESUMEN FINANCIERO
```

## Flujo de Datos para Renderización

```
1. Liquidacion → ServicioFinanciero
   └── obtener_datos_liquidacion_para_pdf(id)
       └── Consulta SQL con JOIN a ContratoMandato

2. ServicioFinanciero → PDFState
   └── _transform_individual_to_pdf_format(datos)
       └── Incluye comision_porcentaje en resumen

3. PDFState → EstadoCuentaElite
   └── generate(data)
       └── _add_resumen_financiero(data)
           └── Renderiza textos descriptivos y porcentaje
```

## Estructura de Datos para Template

```python
data = {
    "modo": "individual",
    "resumen": {
        "total_ingresos": 747000,        # Canon de mandato
        "comision_porcentaje": 800,       # 8% en base 10000
        "comision_monto": 88893,          # total_ingresos * (comision_porcentaje / 10000)
        "iva_comision": 14193,            # comision_monto * 0.16 (o 0.19 según config)
        "gastos_administracion": 0,       # 0 si no es propiedad horizontal
        "gastos_servicios": 0,            # Suma de energía, agua, gas
        "pago_predial": 0,                # Impuesto predial
        "valor_incidentes": 282000,       # Total de incidentes
        "valor_neto": 373107              # total_ingresos - egresos - incidentes
    }
}
```

## Reglas de Negocio

### Cálculo de Porcentaje para Mostrar

```python
# Formato actual (PROBLEMA: requiere verificación)
comision_pct = resumen.get("comision_porcentaje", 0) / 100

# Si comision_porcentaje = 800 (8% en base 10000)
# Entonces comision_pct = 800 / 100 = 8 ✓

# Si comision_porcentaje = 5 (5% directo)
# Entonces comision_pct = 5 / 100 = 0.05 ✗
```

**Decisión**: Verificar en BD el formato exacto antes de implementar.

### Textos Descriptivos

| Concepto | Texto Descriptivo |
|----------|-------------------|
| Total Ingresos | (Total Canon Mandato) |
| Comisión | Sin texto adicional |
| IVA 19% | (Gravamen sobre la comisión) |
| Administración | (Solo aplica para propiedad horizontal) |
| Servicio | (Solo aplica para Energía, Agua y Gas) |
| Predial | (Pago anual del impuesto predial de la vivienda) |
| Incidentes | (Valor del incidente; aquí se puede presentar el valor total o parcial del mismo) |
| NETO A PAGAR | Sin texto descriptivo |

## Validación de Integridad

### Queries de Verificación

```sql
-- 1. Verificar que comision_porcentaje existe en contratos
SELECT cm.id, cm.comision_porcentaje
FROM contrato_mandato cm
WHERE cm.comision_porcentaje > 0
LIMIT 5;

-- 2. Verificar que liquidaciones tienen contrato asociado
SELECT l.id, l.contrato_mandato_id, cm.comision_porcentaje
FROM liquidaciones l
JOIN contrato_mandato cm ON cm.id = l.contrato_mandato_id
WHERE l.estado = 'generada'
LIMIT 5;

-- 3. Verificar valores financieros en liquidación
SELECT 
    l.id,
    l.total_ingresos,
    l.comision_monto,
    l.iva_comision,
    l.valor_incidentes,
    l.valor_neto
FROM liquidaciones l
WHERE l.valor_incidentes > 0
LIMIT 5;
```

## Impacto en Persistencia

**NO HAY CAMBIOS EN PERSISTENCIA**

La feature solo afecta la capa de renderización (template PDF). No se modifican:
- Esquema de base de datos
- Repositorios
- Servicios de negocio
- Entidades de dominio

Los datos ya existen correctamente en PostgreSQL.