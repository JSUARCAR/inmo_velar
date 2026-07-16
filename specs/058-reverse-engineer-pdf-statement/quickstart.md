# Guía de Validación - Ingeniería Inversa Estado de Cuenta PDF

**Date**: 2026-07-16
**Feature**: 058-reverse-engineer-pdf-statement

## Prerrequisitos

1. **Base de datos**: PostgreSQL con datos de prueba
2. **Liquidación**: Al menos una liquidación con estado "generada"
3. **Contrato de mandato**: Asociado a la liquidación con porcentaje de comisión registrado
4. **Incidentes**: Al menos un incidente asociado a la liquidación (para probar `valor_incidentes`)

## Escenarios de Prueba

### Escenario 1: Textos Descriptivos Completos

**Entrada**: Liquidación con todos los conceptos financieros

**Pasos**:
1. Acceder a la vista individual de la liquidación
2. Generar el Estado de Cuenta PDF
3. Abrir el PDF generado
4. Verificar sección RESUMEN FINANCIERO

**Resultado Esperado**:

| Concepto | Texto Descriptivo Esperado |
|----------|---------------------------|
| Total Ingresos | (Total Canon Mandato) |
| Comisión (8%) | Sin texto adicional |
| IVA 19% | (Gravamen sobre la comisión) |
| Administración | (Solo aplica para propiedad horizontal) |
| Servicios | (Solo aplica para Energía, Agua y Gas) |
| Predial | (Pago anual del impuesto predial de la vivienda) |
| Incidentes | (Valor del incidente; aquí se puede presentar el valor total o parcial del mismo) |
| NETO A PAGAR | Sin texto descriptivo |

**Comando de Validación**:
```bash
# Abrir PDF generado y verificar visualmente
# Los textos descriptivos deben aparecer EN CADA FILA del resumen
```

### Escenario 2: Porcentaje de Comisión

**Entrada**: Contrato de mandato con comisión al 8%

**Pasos**:
1. Verificar en BD que `comision_porcentaje = 800` (base 10000)
2. Generar PDF
3. Verificar formato "Comisión (8%)"

**Resultado Esperado**: 
- Concepto muestra: "Comisión (8%)"
- Valor muestra: "$88,893.00" (o el monto calculado)

### Escenario 3: Comisión sin Registrar

**Entrada**: Contrato de mandato sin porcentaje de comisión

**Pasos**:
1. Verificar en BD que `comision_porcentaje = 0` o `NULL`
2. Generar PDF
3. Verificar valor por defecto

**Resultado Esperado**: "Comisión (0%)"

### Escenario 4: Comisión Decimal

**Entrada**: Contrato con comisión al 8.5%

**Pasos**:
1. Verificar en BD que `comision_porcentaje = 850`
2. Generar PDF
3. Verificar redondeo

**Resultado Esperado**: "Comisión (9%)" (redondeado al entero más cercano)

### Escenario 5: Propiedad Horizontal

**Entrada**: Liquidación con `gastos_administracion > 0`

**Pasos**:
1. Generar PDF
2. Verificar fila de Administración

**Resultado Esperado**: 
- Concepto: "Administración"
- Texto: "(Solo aplica para propiedad horizontal)"
- Valor: Monto real de gastos

### Escenario 6: Sin Propiedad Horizontal

**Entrada**: Liquidación con `gastos_administracion = 0`

**Pasos**:
1. Generar PDF
2. Verificar fila de Administración

**Resultado Esperado**:
- Concepto: "Administración"
- Texto: "(Solo aplica para propiedad horizontal)"
- Valor: "$0.00"

## Comandos de Validación

### Verificar Datos en BD

```sql
-- 1. Listar liquidaciones disponibles
SELECT l.id, l.estado, l.valor_incidentes, l.valor_neto
FROM liquidaciones l
WHERE l.estado = 'generada'
ORDER BY l.id DESC
LIMIT 10;

-- 2. Verificar contrato asociado
SELECT l.id as liquidacion_id, cm.comision_porcentaje
FROM liquidaciones l
JOIN contrato_mandato cm ON cm.id = l.contrato_mandato_id
WHERE l.id = <LIQUIDACION_ID>;

-- 3. Verificar valores financieros
SELECT 
    l.total_ingresos,
    l.comision_monto,
    l.iva_comision,
    l.gastos_administracion,
    l.gastos_servicios,
    l.pago_predial,
    l.valor_incidentes,
    l.valor_neto
FROM liquidaciones l
WHERE l.id = <LIQUIDACION_ID>;
```

### Generar PDF de Prueba

```python
# Script de prueba rápido
from src.infraestructura.servicios.pdf_elite.templates.estado_cuenta_elite import EstadoCuentaElite

# Datos de prueba
data = {
    "modo": "individual",
    "resumen": {
        "total_ingresos": 747000,
        "comision_porcentaje": 800,
        "comision_monto": 88893,
        "iva_comision": 14193,
        "gastos_administracion": 0,
        "gastos_servicios": 0,
        "pago_predial": 0,
        "valor_incidentes": 282000,
        "valor_neto": 373107
    }
}

# Generar PDF
generator = EstadoCuentaElite()
pdf_path = generator.generate(data)
print(f"PDF generado: {pdf_path}")
```

## Criterios de Aceptación

| # | Criterio | Verificación |
|---|----------|--------------|
| 1 | Todos los textos descriptivos se muestran | Visual en PDF |
| 2 | Porcentaje de comisión correcto | Comparar con BD |
| 3 | Valor por defecto cuando no hay comisión | Probar con contrato sin porcentaje |
| 4 | Redondeo de decimales | Probar con 8.5% → 9% |
| 5 | Sin regressiones | Generar PDFs existentes y comparar |

## Troubleshooting

### Problema: Textos no aparecen
**Causa**: Método `_add_resumen_financiero` no fue modificado
**Solución**: Verificar que el archivo `estado_cuenta_elite.py` fue actualizado

### Problema: Porcentaje incorrecto
**Causa**: Formato de `comision_porcentaje` no verificado
**Solución**: Ejecutar query SQL para verificar formato en BD

### Problema: PDF no se genera
**Causa**: Error en datos de entrada
**Solución**: Verificar que `data["resumen"]` contiene todos los campos requeridos