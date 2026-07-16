# Quickstart: Rediseño Estado de Cuenta PDF Liquidaciones

**Feature**: 057-redisejo-estado-cuenta-pdf
**Date**: 2026-07-15

## Prerrequisitos

- PostgreSQL corriendo con datos de liquidaciones de prueba
- Python 3.11+ con dependencias instaladas (`pip install -r requirements.txt`)
- ReportLab instalado
- Logos de empresa en `assets/` (membrete)

## Escenarios de Validación

### Escenario 1: Liquidación con Incidentes

**Setup**: Crear liquidación con `valor_incidentes = 50000`

**Comando**:
```bash
python -c "
from src.infraestructura.servicios.servicio_pdf_facade import ServicioPDFFacade
from src.presentacion_reflex.state.pdf_state import PDFState

# Generar PDF
state = PDFState()
state.generar_liquidacion_pdf(id_liquidacion=1)
print('PDF generado exitosamente')
"
```

**Validación**:
- [ ] Columna INCIDENTES aparece con valor `$50.000`
- [ ] Resumen Financiero muestra "Incidentes" con valor `$50,000`
- [ ] NETO A PAGAR incluye el descuento de incidentes
- [ ] No aparece fila TOTAL en tabla de detalle

### Escenario 2: Liquidación sin Incidentes

**Setup**: Crear liquidación con `valor_incidentes = 0`

**Validación**:
- [ ] Columna INCIDENTES aparece con valor `$0`
- [ ] Resumen Financiero muestra "Incidentes" con valor `$0,00`
- [ ] NETO A PAGAR no tiene descuento por incidentes

### Escenario 3: Eliminación del QR

**Setup**: Cualquier liquidación

**Validación**:
- [ ] No aparece código QR en el documento
- [ ] Encabezado se redistribuye correctamente
- [ ] No hay espacios en blanco residuales

### Escenario 4: Resumen Financiero Reorganizado

**Setup**: Liquidación con todos los conceptos (comisión, IVA, administración, servicios, predial, incidentes)

**Validación**:
- [ ] Orden: Total Ingresos → Comisión (X%) → IVA 19% → Administración → Servicios → Predial → Incidentes → NETO A PAGAR
- [ ] Comisión muestra porcentaje correcto: `Comisión (12%)` para `comision_porcentaje = 1200`
- [ ] Administración muestra valor cuando `gastos_administracion > 0`
- [ ] Administración muestra `$0` cuando `gastos_administracion = 0`

### Escenario 5: Observaciones

**Setup**: Liquidación con observaciones largas (200+ caracteres)

**Validación**:
- [ ] Sección OBSERVACIONES aparece siempre
- [ ] Texto completo se muestra sin truncamiento
- [ ] Saltos de línea se renderizan correctamente
- [ ] Diseño del PDF se adapta al contenido

### Escenario 6: Observaciones Vacías

**Setup**: Liquidación con `observaciones = None` o `""`

**Validación**:
- [ ] Sección OBSERVACIONES aparece con mensaje "Sin observaciones registradas"
- [ ] Pie legal aparece después de observaciones

### Escenario 7: Consistencia de Datos

**Setup**: Generar PDF y comparar con valores en PostgreSQL

**Comando**:
```bash
python -c "
import psycopg2
conn = psycopg2.connect('tu_url DATABASE')
cur = conn.cursor()
cur.execute('SELECT valor_incidentes, neto_a_pagar, comision_monto FROM LIQUIDACIONES WHERE ID_LIQUIDACION = 1')
row = cur.fetchone()
print(f'BD: incidentes={row[0]}, neto={row[1]}, comision={row[2]}')
# Comparar con valores en el PDF
"
```

**Validación**:
- [ ] Valor de incidentes en PDF = `valor_incidentes` en BD
- [ ] NETO A PAGAR en PDF = `neto_a_pagar` en BD
- [ ] Comisión en PDF = `comision_monto` en BD
- [ ] IVA en PDF = `iva_comision` en BD

### Escenario 8: Generación por Lotes (ZIP)

**Setup**: Generar ZIP de múltiples estados de cuenta

**Validación**:
- [ ] Todos los PDFs del ZIP no tienen QR
- [ ] Todos los PDFs tienen columna INCIDENTES
- [ ] Todos los PDFs tienen Resumen Financiero reorganizado

## Archivos a Verificar

| Archivo | Cambio Esperado |
|---|---|
| `estado_cuenta_elite.py` | Columna INCIDENTES siempre visible, fila TOTAL eliminada, resumen reorganizado, QR eliminado, observaciones siempre visibles |
| `pdf_state.py` | Transformadores actualizados para pasar `valor_incidentes` y `comision_porcentaje` |
| `base_template.py` | Sin cambios necesarios (QR se deshabilita por no llamar `enable_verification_qr()`) |

## Comandos de Build

```bash
# Verificar sintaxis
python -m py_compile src/infraestructura/servicios/pdf_elite/templates/estado_cuenta_elite.py
python -m py_compile src/presentacion_reflex/state/pdf_state.py

# Ejecutar tests (si existen)
pytest tests/ -k "estado_cuenta" -v

# Ejecutar servidor en modo debug
reflex run --env dev
```
