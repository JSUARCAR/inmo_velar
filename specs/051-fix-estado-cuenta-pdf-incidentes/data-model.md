# Data Model: Fix Estado Cuenta PDF - Incidentes

**Date**: 2026-07-15 | **Feature**: 051-fix-estado-cuenta-pdf-incidentes

## Entidades Afectadas

### 1. Liquidación (Entidad de Dominio — YA EXISTE, NO se modifica)

**Archivo**: `src/dominio/entidades/liquidacion.py`

```python
class Liquidacion:
    # Campos financieros relevantes
    total_ingresos: int
    total_egresos: int
    valor_incidentes: int = 0   # Descuentos por incidentes
    neto_a_pagar: int

    def calcular_totales(self):
        self.total_egresos = (
            self.comision_monto + self.iva_comision + self.gastos_administracion
            + self.gastos_servicios + self.gastos_reparaciones
            + (self.pago_predial or 0) + (self.otros_egresos or 0)
        )
        self.neto_a_pagar = (
            self.total_ingresos - self.total_egresos - self.valor_incidentes
        )
```

**Fórmula financiera (fuente de verdad)**:
```
neto_a_pagar = total_ingresos - total_egresos - valor_incidentes
```

**Relaciones**:
- `Liquidacion` ← N:1 → `ContratoMensual`
- `Liquidacion` ← N:1 → `Propiedad`
- `Liquidacion` ← N:N → `Incidente` (a través de tabla pivote `INCIDENTE_LIQUIDACION`)

---

### 2. Incidente-Liquidación (Tabla Pivote — YA EXISTE, NO se modifica)

Asocia cuotas de incidentes con liquidaciones específicas, registrando el valor de descuento aplicado.

---

### 3. Datos para PDF (DTO de Persistencia — CAMBIO REQUERIDO)

**Archivo**: `src/infraestructura/persistencia/repositorio_liquidacion_postgres.py`

#### 3a. `obtener_datos_para_pdf()` (Línea 1283) — YA INCLUYE `valor_incidentes`

```python
# Retorna (entre otros campos):
"valor_incidentes": row.get("VALOR_INCIDENTES") or 0,
"neto_pagar": row.get("NETO_A_PAGAR")
```

**Estado**: ✅ Correcto. No requiere cambios.

#### 3b. `obtener_consolidado_propietario()` (Línea 1400) — FALTA `valor_incidentes`

**Campo actual en `propiedades_formateadas`** (línea 1486-1506):
```python
propiedades_formateadas.append({
    "id": prop.get("ID"),
    "direccion": prop.get("DIRECCION"),
    "canon": prop.get("CANON") or 0,
    "otros_ingresos": prop.get("OTROS_INGRESOS") or 0,
    "comision_monto": prop.get("COMISION_MONTO") or 0,
    "iva_comision": prop.get("IVA_COMISION") or 0,
    "impuesto_4x1000": prop.get("IMPUESTO_4X1000") or 0,
    "gastos_admin": prop.get("GASTOS_ADMIN") or 0,
    "gastos_serv": prop.get("GASTOS_SERV") or 0,
    "gastos_rep": prop.get("GASTOS_REP") or 0,
    "pago_predial": prop.get("PAGO_PREDIAL") or 0,
    "seguro_monto": prop.get("SEGURO_MONTO") or 0,
    "otros_egr": prop.get("OTROS_EGR") or 0,
    "neto": prop.get("NETO") or 0,
    "porcentaje_seguro": prop.get("PORCENTAJE_SEGURO") or 0,
    # ❌ FALTA: "valor_incidentes": prop.get("VALOR_INCIDENTES") or 0,
})
```

**Cambio requerido**: Agregar `"valor_incidentes": prop.get("VALOR_INCIDENTES") or 0` al diccionario.

---

### 4. Mapeo a PDF (DTO de Aplicación — CAMBIO REQUERIDO)

**Archivo**: `src/aplicacion/servicios/servicio_financiero.py`

**Función**: `mapear_consolidado_a_pdf_elite()` (Línea 712)

#### 4a. Campo `incidente` en `detalle_propiedades` (Línea 756)

**Actual**:
```python
"incidente": (prop.get("gastos_rep", 0) or 0) + (prop.get("otros_egr", 0) or 0),
```

**Cambio requerido**: Separar `valor_incidentes` como campo independiente:
```python
"valor_incidentes": prop.get("valor_incidentes", 0) or 0,
```

Mantener `incidente` como `gastos_rep + otros_egr` (son conceptos diferentes).

#### 4b. Resumen financiero (Línea 769)

**Actual**:
```python
"valor_neto": datos.get("neto_pagar", 0) or 0,
```

**Estado**: ✅ Correcto. `neto_pagar` de la DB ya incluye la deducción de `valor_incidentes`.

**Cambio requerido**: Agregar `valor_incidentes` al resumen para que el template pueda mostrarlo:
```python
"valor_incidentes": datos.get("valor_incidentes", 0) or 0,
```

---

### 5. Template PDF (Infraestructura — CAMBIO REQUERIDO)

**Archivo**: `src/infraestructura/servicios/pdf_elite/templates/estado_cuenta_elite.py`

#### 5a. Tabla de detalle (`_add_detalle_propiedades`, Línea 273)

**Cambio requerido**: Agregar columna "INCIDENTES" después de la columna existente, o renombrar "OTRO" a un nombre más descriptivo y agregar `valor_incidentes` como línea separada.

**Comportamiento**: Si `valor_incidentes > 0`, mostrar la línea. Si es $0, ocultar.

#### 5b. Resumen financiero (`_add_resumen_financiero`, Línea 360)

**Cambio requerido**: Agregar línea "(-) Incidentes: $X.XXX" antes del "Valor Neto" si `valor_incidentes > 0`.

---

## Diagrama de Flujo de Datos (Corregido)

```
PostgreSQL (LIQUIDACIONES.VALOR_INCIDENTES)
    │
    ▼
obtener_datos_para_pdf() ──────────────────► [OK, ya incluye]
obtener_consolidado_propietario() ─────────► [FIX: agregar campo]
    │
    ▼
mapear_consolidado_a_pdf_elite() ──────────► [FIX: separar valor_incidentes]
    │
    ▼
estado_cuenta_elite.py (template) ─────────► [FIX: agregar línea + resumen]
    │
    ▼
PDF generado con Incidentes incluidos
```

## Reglas de Validación

| Campo | Regla | Origen |
|-------|-------|--------|
| `valor_incidentes` | `>= 0`, tipo `int` | DB column `VALOR_INCIDENTES` |
| `neto_a_pagar` | `= total_ingresos - total_egresos - valor_incidentes` | DB column `NETO_A_PAGAR` |
| Formato moneda | Separadores de miles, sin decimales, redondeo al entero | Configuración del template |
| Ocultar línea | Si `valor_incidentes == 0`, no mostrar en detalle | Clarificación spec |
