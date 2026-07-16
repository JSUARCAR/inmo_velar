# Data Model: Rediseño Estado de Cuenta PDF Liquidaciones

**Feature**: 057-redisejo-estado-cuenta-pdf
**Date**: 2026-07-15

## Entidades del Dominio

### Liquidacion (Entidad principal)

Campos relevantes para el PDF:

| Campo | Tipo | Descripción | Uso en PDF |
|---|---|---|---|
| `id_liquidacion` | int | PK | Identificador del documento |
| `canon_bruto` | int | Canon de mandato | Detalle: CANON |
| `comision_porcentaje` | int | Porcentaje en base 10000 | Resumen: Comisión (X%) |
| `comision_monto` | int | Monto de comisión | Detalle: COMISIÓN, Resumen: Comisión |
| `iva_comision` | int | IVA sobre comisión | Detalle: IVA, Resumen: IVA 19% |
| `gastos_administracion` | int | Gastos de administración PH | Detalle: ADMIN, Resumen: Administración |
| `gastos_servicios` | int | Servicios públicos | Detalle: SERV, Resumen: Servicios |
| `pago_predial` | int | Impuesto predial | Detalle: PREDIAL, Resumen: Predial |
| `valor_incidentes` | int | Total incidentes descontados | Detalle: INCIDENTES, Resumen: Incidentes |
| `total_ingresos` | int | Canon + otros ingresos | Resumen: Total Ingresos |
| `total_egresos` | int | Suma de todos los egresos | Cálculo interno |
| `neto_a_pagar` | int | Ingresos - Egresos - Incidentes | Detalle: NETO, Resumen: NETO A PAGAR |
| `observaciones` | str | Notas de la liquidación | Sección: OBSERVACIONES |

### ContratoMandato (Fuente de porcentaje de comisión)

| Campo | Tipo | Descripción | Uso en PDF |
|---|---|---|---|
| `comision_porcentaje` | int | Porcentaje en base 10000 | Resumen: Comisión (X%) |

### IncidenteLiquidacion (Relación incidente-liquidación)

| Campo | Tipo | Descripción | Uso en PDF |
|---|---|---|---|
| `id_incidente` | int | FK a INCIDENTES | Referencia en observaciones |
| `id_liquidacion` | int | FK a LIQUIDACIONES | Vínculo |
| `valor_descuento` | int | Valor descontado en esta cuota | Cálculo de valor_incidentes |

## Fórmulas de Cálculo (Inalteradas)

### NETO A PAGAR
```
neto_a_pagar = total_ingresos - total_egresos - valor_incidentes
```

### Total Ingresos
```
total_ingresos = canon_bruto + otros_ingresos
```

### Total Egresos
```
total_egresos = comision_monto + iva_comision + gastos_administracion 
                + gastos_servicios + gastos_reparaciones + pago_predial + otros_egresos
```

### Comisión
```
comision_monto = canon_bruto * (comision_porcentaje / 10000)
```

### IVA
```
iva_comision = comision_monto * 0.19
```

### Porcentaje legible
```
porcentaje_legible = comision_porcentaje / 100  # Ej: 1200 → 12%
```

## Transformación de Datos para PDF

### Transformador Individual (`_transform_individual_to_pdf_format`)

**Cambios requeridos:**

1. **Detalle propiedades**: Cambiar `"incidente": gastos_rep + otros_egr` por `"incidente": valor_incidentes`
2. **Resumen**: Reestructurar para el nuevo orden de conceptos
3. **Observaciones**: Pasar directamente (ya funciona)

### Transformador Consolidado (`_transform_consolidated_to_pdf_format`)

**Cambios requeridos:**

1. **Detalle propiedades**: Cambiar `"incidente": gastos_rep + otros_egr` por `"incidente": valor_incidentes`
2. **Resumen**: Reestructurar para el nuevo orden de conceptos

## Estructura del Dict para Template

### Detalle Propiedades (cada fila)

```python
{
    "id": int,           # ID del contrato
    "canon": int,        # Canon bruto
    "comision": int,     # Monto comisión
    "iva": int,          # IVA comisión
    "admin": int,        # Gastos administración
    "servicios": int,    # Gastos servicios
    "predial": int,      # Pago predial
    "incidentes": int,   # valor_incidentes (NUEVO campo renombrado)
    "total": int,        # neto_a_pagar
    "comision_porcentaje": int,  # Porcentaje en base 10000 (NUEVO campo)
}
```

### Resumen Financiero

```python
{
    "total_ingresos": int,
    "comision_monto": int,
    "comision_porcentaje": int,  # NUEVO
    "iva_comision": int,
    "gastos_administracion": int,
    "gastos_servicios": int,
    "pago_predial": int,
    "valor_incidentes": int,
    "valor_neto": int,           # neto_a_pagar
    "cuenta_bancaria": str,
}
```
