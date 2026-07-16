# Data Model: Reporte de Liquidaciones - Datos del Propietario y Contrato de Mandato

**Date**: 2026-07-13

## Entities Involved

### 1. LIQUIDACIONES (Base Table)

| Field | Type | Description |
|-------|------|-------------|
| ID_LIQUIDACION | SERIAL PK | Unique identifier |
| ID_CONTRATO_M | INTEGER FK | Links to CONTRATOS_MANDATOS |
| PERIODO | TEXT | Format: YYYY-MM |
| CANON_BRUTO | DECIMAL | Gross rent |
| TOTAL_INGRESOS | DECIMAL | Total income |
| COMISION_MONTO | DECIMAL | Commission amount |
| TOTAL_EGRESOS | DECIMAL | Total expenses |
| NETO_A_PAGAR | DECIMAL | Net amount to pay |
| ESTADO_LIQUIDACION | TEXT | Status: En Proceso/Aprobada/Pagada/Cancelada |

### 2. CONTRATOS_MANDATOS (Mandate Contracts)

| Field | Type | Description | Status |
|-------|------|-------------|--------|
| ID_CONTRATO_M | SERIAL PK | Unique identifier | - |
| ID_PROPIEDAD | INTEGER FK | Links to PROPIEDADES | - |
| ID_PROPIETARIO | INTEGER FK | Links to PROPIETARIOS | - |
| BANCO_PROPIETARIO | TEXT | Owner's bank name | **NEW TO REPORT** |
| NUMERO_CUENTA_PROPIETARIO | TEXT | Bank account number | **NEW TO REPORT** |
| TIPO_CUENTA | TEXT | Account type (Ahorro/Corriente) | **NEW TO REPORT** |
| CONSIGNATARIO | TEXT | Consignatario name | **NEW TO REPORT** |
| DOCUMENTO_CONSIGNATARIO | TEXT | Consignatario document | **NEW TO REPORT** |

### 3. PROPIETARIOS (Owners)

| Field | Type | Description |
|-------|------|-------------|
| ID_PROPIETARIO | SERIAL PK | Unique identifier |
| ID_PERSONA | INTEGER FK | Links to PERSONAS |

### 4. PERSONAS (People)

| Field | Type | Description | Status |
|-------|------|-------------|--------|
| ID_PERSONA | SERIAL PK | Unique identifier | - |
| NOMBRE_COMPLETO | TEXT | Full name | Already in report |
| NUMERO_DOCUMENTO | TEXT | Document number (CC/NIT/etc) | **NEW TO REPORT** |
| TELEFONO_PRINCIPAL | TEXT | Phone number | **NEW TO REPORT** |

## Relationships

```
LIQUIDACIONES (1) ──→ (N) CONTRATOS_MANDATOS
    via LIQUIDACIONES.ID_CONTRATO_M = CONTRATOS_MANDATOS.ID_CONTRATO_M

CONTRATOS_MANDATOS (N) ──→ (1) PROPIEDADES
    via CONTRATOS_MANDATOS.ID_PROPIEDAD = PROPIEDADES.ID_PROPIEDAD

CONTRATOS_MANDATOS (N) ──→ (1) PROPIETARIOS
    via CONTRATOS_MANDATOS.ID_PROPIETARIO = PROPIETARIOS.ID_PROPIETARIO

PROPIETARIOS (N) ──→ (1) PERSONAS
    via PROPIETARIOS.ID_PERSONA = PERSONAS.ID_PERSONA
```

## New Columns in Report

### Position: After Nombre_Propietario (Column 4)

| # | SQL Expression | Alias | Source Entity | Source Field |
|---|----------------|-------|---------------|--------------|
| 5 | `per_prop.NUMERO_DOCUMENTO` | `NUMERO_DOCUMENTO_PROPIETARIO` | PERSONAS | NUMERO_DOCUMENTO |
| 6 | `per_prop.TELEFONO_PRINCIPAL` | `TELEFONO_PROPIETARIO` | PERSONAS | TELEFONO_PRINCIPAL |
| 7 | `cm.BANCO_PROPIETARIO` | `BANCO` | CONTRATOS_MANDATOS | BANCO_PROPIETARIO |
| 8 | `cm.NUMERO_CUENTA_PROPIETARIO` | `NUMERO_CUENTA` | CONTRATOS_MANDATOS | NUMERO_CUENTA_PROPIETARIO |
| 9 | `cm.TIPO_CUENTA` | `TIPO_CUENTA` | CONTRATOS_MANDATOS | TIPO_CUENTA |
| 10 | `cm.CONSIGNATARIO` | `NOMBRE_CONSIGNATARIO` | CONTRATOS_MANDATOS | CONSIGNATARIO |
| 11 | `cm.DOCUMENTO_CONSIGNATARIO` | `DOCUMENTO_CONSIGNATARIO` | CONTRATOS_MANDATOS | DOCUMENTO_CONSIGNATARIO |

## Updated Column Order (35 total)

```
 1. ID_LIQUIDACION
 2. ID_CONTRATO_M
 3. Direccion_Predio
 4. Nombre_Propietario
 5. NUMERO_DOCUMENTO_PROPIETARIO    ← NEW
 6. TELEFONO_PROPIETARIO            ← NEW
 7. BANCO                           ← NEW
 8. NUMERO_CUENTA                   ← NEW
 9. TIPO_CUENTA                     ← NEW
10. NOMBRE_CONSIGNATARIO            ← NEW
11. DOCUMENTO_CONSIGNATARIO         ← NEW
12. Nombre_Asesor
13. PERIODO
14. FECHA_GENERACION
15. CANON_BRUTO
16. OTROS_INGRESOS
17. TOTAL_INGRESOS
18. COMISION_PORCENTAJE
19. COMISION_MONTO
20. IVA_COMISION
21. IMPUESTO_4X1000
22. Seguro_Arrendamiento
23. GASTOS_ADMINISTRACION
24. GASTOS_SERVICIOS
25. GASTOS_REPARACIONES
26. PAGO_PREDIAL
27. OTROS_EGRESOS
28. TOTAL_EGRESOS
29. Valor_Incidentes
30. NETO_A_PAGAR
31. ESTADO_LIQUIDACION
32. FECHA_PAGO
33. METODO_PAGO
34. REFERENCIA_PAGO
35. OBSERVACIONES
```

## Validation Rules

| Field | Rule | Null Handling |
|-------|------|---------------|
| NUMERO_DOCUMENTO_PROPIETARIO | Alphanumeric, max 20 chars | Show empty string |
| TELEFONO_PROPIETARIO | Numeric with optional dash/plus | Show empty string |
| BANCO | Text, max 100 chars | Show empty string |
| NUMERO_CUENTA | Alphanumeric, max 30 chars | Show empty string |
| TIPO_CUENTA | Enum: Ahorro/Corriente | Show empty string |
| NOMBRE_CONSIGNATARIO | Text, max 200 chars | Show empty string |
| DOCUMENTO_CONSIGNATARIO | Alphanumeric, max 20 chars | Show empty string |

## Data Flow

```
PostgreSQL Query (repositorio_reportes.py)
    ↓ Returns List[Dict] with 35 keys
ServicioReportes.obtener_datos_reporte()
    ↓ Extracts headers from data[0].keys()
ReportesState._fetch_data()
    ↓ Applies _sanitize_value() to each cell
    ↓ Excel sanitization for: NUMERO_CUENTA, NUMERO_DOCUMENTO_PROPIETARIO, DOCUMENTO_CONSIGNATARIO
UI Table (reportes.py)
    ↓ Dynamic rendering via rx.foreach
CSV Export (reportes_state.py)
    ↓ csv.DictWriter with fieldnames=headers
```
