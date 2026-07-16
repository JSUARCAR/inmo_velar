# Quickstart Validation: Fix Estado Cuenta PDF - Incidentes

**Date**: 2026-07-15 | **Feature**: 051-fix-estado-cuenta-pdf-incidentes

## Prerrequisitos

- PostgreSQL corriendo con datos de prueba (al menos 1 liquidación con incidentes asociados)
- Python 3.11+ con dependencias instaladas (`pip install -r requirements.txt`)
- ReportLab instalado
- Entorno `.env` configurado con `DATABASE_URL`

## Escenarios de Validación

### Escenario 1: PDF con incidentes (Happy Path)

**Precondición**: Liquidación con `valor_incidentes = 500000` y `neto_a_pagar` calculado correctamente.

**Comando**:
```bash
cd src
python -c "
from infraestructura.persistencia.repositorio_liquidacion_postgres import RepositorioLiquidacionPostgres
from aplicacion.servicios.servicio_financiero import ServicioFinanciero

repo = RepositorioLiquidacionPostgres()
svc = ServicioFinanciero(repo)
datos = svc.obtener_datos_liquidacion_para_pdf(ID_LIQUIDACION_CON_INCIDENTES)
pdf_data = svc.mapear_consolidado_a_pdf_elite(datos)
print('valor_incidentes en detalle:', pdf_data.get('detalle_propiedades', [{}])[0].get('valor_incidentes'))
print('valor_neto en resumen:', pdf_data.get('resumen', {}).get('valor_neto'))
"
```

**Resultado esperado**:
- `valor_incidentes` aparece en el diccionario mapeado
- `valor_neto` refleja la deducción

**Validación visual**: Abrir el PDF generado y verificar:
1. Línea "(-) Incidentes: $500.000" visible en el detalle
2. Línea "(-) Incidentes: $500.000" visible en el resumen financiero
3. "Valor Neto" = total_ingresos - total_egresos - 500000

---

### Escenario 2: PDF sin incidentes (Caso borde)

**Precondición**: Liquidación con `valor_incidentes = 0`.

**Comando**: Mismo que Escenario 1 con ID de liquidación sin incidentes.

**Resultado esperado**:
- `valor_incidentes = 0` en el diccionario
- Línea de Incidentes NO visible en el detalle del PDF
- Línea de Incidentes NO visible en el resumen financiero
- `valor_neto` sin afectación

---

### Escenario 3: PDF en lote (ZIP)

**Precondición**: Múltiples liquidaciones, algunas con incidentes y otras sin.

**Comando**:
```bash
cd src
python -c "
from infraestructura.persistencia.repositorio_liquidacion_postgres import RepositorioLiquidacionPostgres
from aplicacion.servicios.servicio_financiero import ServicioFinanciero

repo = RepositorioLiquidacionPostgres()
svc = ServicioFinanciero(repo)
ruta_zip = svc.exportar_estados_cuenta_periodo_zip('2026-01')
print('ZIP generado en:', ruta_zip)
"
```

**Resultado esperado**:
- ZIP se genera sin errores
- Cada PDF individual contiene o no la línea de Incidentes según su liquidación
- No hay resumen consolidado de incidentes en el ZIP

---

### Escenario 4: Valores grandes y decimales

**Precondición**: Liquidación con `valor_incidentes = 1500500500` (>$999M) y otra con `valor_incidentes = 150500.50` (decimal).

**Resultado esperado**:
- Valor grande: formateado como `$1.500.500.500` (separadores de miles, sin decimales)
- Valor decimal: redondeado a `$150.501` antes de formatear

---

### Escenario 5: Regresión — Otros tipos de PDF

**Comando**: Generar al menos 1 PDF de cada tipo existente en el sistema (contrato, reporte, etc.).

**Resultado esperado**:
- Todos los PDFs se generan sin errores
- No hay cambios visuales en documentos no afectados

---

### Escenario 6: Consistencia UI ↔ PDF

**Precondición**: Liquidación con incidentes visible en la UI.

**Comando**: Comparar visualmente los valores en la tabla de liquidaciones de la UI con los valores del PDF generado.

**Resultado esperado**:
- `valor_incidentes` en UI = `valor_incidentes` en PDF (tolerancia: $0)
- `neto_a_pagar` en UI = `valor_neto` en PDF (tolerancia: $0)

---

## Comandos de Verificación Rápida

```bash
# Verificar que el campo existe en la DB
psql $DATABASE_URL -c "SELECT ID, VALOR_INCIDENTES, NETO_A_PAGAR FROM LIQUIDACIONES WHERE VALOR_INCIDENTES > 0 LIMIT 5;"

# Ejecutar tests de regresión
pytest tests/ -v --tb=short

# Verificar lint y tipos
ruff check src/
mypy src/
```

## Archivos Modificados (Referencia)

| Archivo | Cambio | Verificación |
|---------|--------|--------------|
| `repositorio_liquidacion_postgres.py` | Agregar `valor_incidentes` a `obtener_consolidado_propietario()` | Escenario 1, 3 |
| `servicio_financiero.py` | Separar `valor_incidentes` en `mapear_consolidado_a_pdf_elite()` | Escenario 1, 2 |
| `estado_cuenta_elite.py` | Agregar línea de Incidentes en detalle y resumen | Escenario 1, 2, 4 |
