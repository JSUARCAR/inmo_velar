# Contract: Reporte de Liquidaciones

**Date**: 2026-07-13

## Interface: Repository → Service

### Method Signature

```python
def obtener_reporte_liquidaciones(
    self,
    asesor_id: Optional[int] = None,
    busqueda: Optional[str] = None,
    page: int = 1,
    limit: int = 50
) -> Tuple[List[Dict[str, Any]], int]:
```

### Response Format

```python
# Returns tuple of (data, total_count)
# data is List[Dict] where each dict has the following keys:

{
    # Existing columns (unchanged)
    "ID_LIQUIDACION": int,
    "ID_CONTRATO_M": int,
    "Direccion_Predio": str,
    "Nombre_Propietario": str,
    
    # New owner identification columns
    "NUMERO_DOCUMENTO_PROPIETARIO": Optional[str],  # Empty string if null
    "TELEFONO_PROPIETARIO": Optional[str],           # Empty string if null
    
    # New banking columns
    "BANCO": Optional[str],                          # Empty string if null
    "NUMERO_CUENTA": Optional[str],                  # Empty string if null
    "TIPO_CUENTA": Optional[str],                    # Empty string if null
    "NOMBRE_CONSIGNATARIO": Optional[str],           # Empty string if null
    "DOCUMENTO_CONSIGNATARIO": Optional[str],        # Empty string if null
    
    # Existing columns (unchanged)
    "Nombre_Asesor": str,
    "PERIODO": str,
    "FECHA_GENERACION": str,
    "CANON_BRUTO": float,
    "OTROS_INGRESOS": float,
    "TOTAL_INGRESOS": float,
    "COMISION_PORCENTAJE": float,
    "COMISION_MONTO": float,
    "IVA_COMISION": float,
    "IMPUESTO_4X1000": float,
    "Seguro_Arrendamiento": float,
    "GASTOS_ADMINISTRACION": float,
    "GASTOS_SERVICIOS": float,
    "GASTOS_REPARACIONES": float,
    "PAGO_PREDIAL": float,
    "OTROS_EGRESOS": float,
    "TOTAL_EGRESOS": float,
    "Valor_Incidentes": float,
    "NETO_A_PAGAR": float,
    "ESTADO_LIQUIDACION": str,
    "FECHA_PAGO": Optional[str],
    "METODO_PAGO": Optional[str],
    "REFERENCIA_PAGO": Optional[str],
    "OBSERVACIONES": Optional[str]
}
```

## Interface: Service → State

### Method Signature

```python
def obtener_datos_reporte(
    self,
    report_id: str,
    filtros: Optional[Dict[str, Any]] = None,
    pagina: int = 1,
    limite: int = 50,
    es_exportacion: bool = False
) -> Tuple[List[Dict[str, Any]], List[str], int]:
```

### Response Format

```python
# Returns tuple of (data, headers, total_count)
# data: Same as repository response
# headers: List[str] of column names in display order
# total_count: Total records matching filters

# headers for "liquidaciones" report (35 items):
[
    "ID_LIQUIDACION",
    "ID_CONTRATO_M",
    "Direccion_Predio",
    "Nombre_Propietario",
    "NUMERO_DOCUMENTO_PROPIETARIO",  # NEW
    "TELEFONO_PROPIETARIO",          # NEW
    "BANCO",                         # NEW
    "NUMERO_CUENTA",                 # NEW
    "TIPO_CUENTA",                   # NEW
    "NOMBRE_CONSIGNATARIO",          # NEW
    "DOCUMENTO_CONSIGNATARIO",       # NEW
    "Nombre_Asesor",
    "PERIODO",
    # ... remaining existing columns
]
```

## Interface: State → UI

### State Variables

```python
class ReportesState(rx.State):
    preview_data: List[Dict[str, Any]] = []  # Row data
    preview_headers: List[str] = []          # Column headers in order
    preview_total: int = 0                   # Total records
```

### UI Contract

The UI table (`reportes.py`) renders columns dynamically:
- Headers: `rx.foreach(ReportesState.preview_headers, lambda h: rx.table.column_header_cell(h))`
- Body: `rx.foreach(row, lambda h: rx.table.cell(row[h]))`

**No UI changes required** - new columns appear automatically.

## Interface: CSV Export

### Sanitization Rules

```python
# Columns requiring Excel text literal formatting (prevent truncamento)
EXCEL_SANITIZE_COLUMNS = [
    "NUMERO_CUENTA",                    # NEW - bank account numbers
    "NUMERO_DOCUMENTO_PROPIETARIO",     # NEW - document numbers
    "DOCUMENTO_CONSIGNATARIO",          # NEW - consignatario documents
    # Existing columns already handled:
    "NUMERO_CUENTA_PROPIETARIO",
    "NUMERO_DOCUMENTO_PROPIETARIO",
    "NUMERO_DOCUMENTO_ARRENDATARIO",
    "NUMERO_DOCUMENTO",
    "DOCUMENTO_CONSIGNATARIO_PROPIETARIO"
]

# Format: If value starts with "0" or is all digits → wrap as ="value"
```

### CSV Output Format

```
UTF-8 with BOM (\ufeff)
Comma-separated values
Headers as first row
Filename: reporte_liquidaciones_YYYYMMDD_HHMMSS.csv
```
