# Quickstart Validation: Columnas Financieras Liquidaciones

**Date**: 2026-07-11
**Feature**: 048-columnas-financieras-liquidaciones

## Prerequisites

1. PostgreSQL ejecutándose con tabla LIQUIDACIONES
2. Datos de prueba insertados (ver sección Data Setup)
3. Entorno Reflex configurado (`reflex init` completado)
4. Dependencias instaladas (`pip install -r requirements.txt`)

## Data Setup

```sql
-- Insertar liquidación de prueba con todos los campos financieros
INSERT INTO liquidaciones (
    periodo, propiedad_id, ciclo_operativo, canon_bruto,
    otros_ingresos, gastos_administracion, gastos_servicios,
    gastos_reparaciones, valor_incidentes, pago_predial,
    otros_egresos, iva_comision, neto_a_pagar,
    estado_recaudo, estado
) VALUES (
    '2026-01', 1, 'Mensual', 5000000,
    250000, 150000, 80000,
    120000, 50000, 200000,
    30000, 95000, 4425000,
    'Pendiente', 'Activa'
);

-- Insertar liquidación con valores vacíos
INSERT INTO liquidaciones (
    periodo, propiedad_id, ciclo_operativo, canon_bruto,
    otros_ingresos, gastos_administracion, gastos_servicios,
    gastos_reparaciones, valor_incidentes, pago_predial,
    otros_egresos, iva_comision, neto_a_pagar,
    estado_recaudo, estado
) VALUES (
    '2026-02', 2, 'Mensual', 3000000,
    0, 0, 0,
    0, 0, 0,
    0, 0, 3000000,
    'Pendiente', 'Activa'
);
```

## Validation Scenarios

### Scenario 1: Visualización de Columnas

**Command**:
```bash
reflex run --env dev
# Navegar a http://localhost:3000/liquidaciones
```

**Expected Outcome**:
- Tabla muestra 17 columnas (9 existentes + 8 nuevas)
- Columnas nuevas aparecen después de "Canon" en orden correcto
- Valores monetarios formateados: $5.000.000, $250.000, etc.
- Valores vacíos muestran: $0

### Scenario 2: Ordenamiento

**Command**:
```bash
# Click en encabezado de "Otros Ingresos"
# Click nuevamente para cambiar dirección
```

**Expected Outcome**:
- Primera vez: Ordena ascendente (menor a mayor)
- Segunda vez: Ordena descendente (mayor a menor)
- Icono de flecha indica dirección actual

### Scenario 3: Filtros Avanzados

**Command**:
```bash
# Abrir filtros avanzados
# Seleccionar rango para "Gastos Administración": min=100000, max=200000
```

**Expected Outcome**:
- Solo se muestran liquidaciones con gastos_admin entre $100.000 y $200.000
- Badge de filtro activo muestra count
- Botón "Limpiar" resetea el filtro

### Scenario 4: Exportación

**Command**:
```bash
# Click en botón de exportar
# Seleccionar formato Excel
```

**Expected Outcome**:
- Archivo Excel descargado
- Columnas financieras incluidas con headers correctos
- Valores formateados consistentemente

### Scenario 5: Búsqueda

**Command**:
```bash
# En campo de búsqueda, ingresar "500000"
```

**Expected Outcome**:
- Se filtran liquidaciones que contienen "500000" en cualquier campo de texto
- Columnas financieras no participan en búsqueda de texto

### Scenario 6: Scroll Horizontal

**Command**:
```bash
# En viewport pequeño (< 1200px)
# Hacer scroll horizontal
```

**Expected Outcome**:
- Todas las columnas son accesibles via scroll
- Columnas fijas (ID, Acciones) se mantienen visibles
- Formato monetario se mantiene consistente

## Performance Validation

**Command**:
```bash
# Medir tiempo de carga con 1000+ registros
time reflex run --env dev
# Navegar a /liquidaciones
# Abrir DevTools → Network → medir tiempo de carga
```

**Expected Outcome**:
- Tiempo de carga < 3 segundos
- Sin degradación perceptible vs tabla original

## Regression Testing

**Command**:
```bash
# Ejecutar tests existentes
pytest tests/ -v
```

**Expected Outcome**:
- Todos los tests existentes pasan
- No hay regresiones en funcionalidades previas

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Columnas no aparecen | Verificar que LiquidacionDict tiene los campos |
| Valores $0 en todas las columnas | Verificar query SQL incluye los campos |
| Formato incorrecto | Verificar uso de format_currency() |
| Filtros no funcionan | Verificar mapeo de column_key en state |
