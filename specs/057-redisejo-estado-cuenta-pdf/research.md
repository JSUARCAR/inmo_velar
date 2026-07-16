# Research: Rediseño Estado de Cuenta PDF Liquidaciones

**Feature**: 057-redisejo-estado-cuenta-pdf
**Date**: 2026-07-15

## R1: Flujo de datos de valor_incidentes al PDF

**Decision**: El campo `valor_incidentes` NO se pasa directamente al template. Actualmente, el transformador `_transform_individual_to_pdf_format()` calcula incidentes como `gastos_rep + otros_egr`, que es una suma de dos campos de egresos, NO el valor de incidentes propiamente dicho.

**Rationale**: El campo `valor_incidentes` en la tabla `LIQUIDACIONES` se actualiza automáticamente via triggers al asociar/desasociar incidentes. Sin embargo, el transformador actual usa `gastos_rep + otros_egr` como proxy. Para el rediseño, se debe usar directamente `valor_incidentes` del campo de la liquidación.

**Alternatives considered**:
- Mantener el cálculo `gastos_rep + otros_egr`: Rechazado porque no refleja el valor real de incidentes de la liquidación.
- Usar `valor_incidentes` directamente: Seleccionado porque es la fuente oficial de datos en PostgreSQL.

**Impacto**: Cambiar la fuente de datos en `_transform_individual_to_pdf_format()` y `_transform_consolidated_to_pdf_format()` para usar `valor_incidentes` en lugar de `gastos_rep + otros_egr`.

## R2: Estructura actual del Resumen Financiero

**Decision**: El resumen actual tiene 4 filas + 1 condicional + NETO. Se reemplazará por 8 filas en el orden especificado.

**Current order**:
1. Total Ingresos
2. Total Egresos
3. Honorarios Administración
4. Otros Descuentos
5. (-) Incidentes (solo si > 0)
6. NETO A PAGAR (destacado)

**New order** (from spec):
1. Total Ingresos
2. Comisión (X%)
3. IVA 19%
4. Administración
5. Servicios
6. Predial
7. Incidentes
8. NETO A PAGAR (destacado)

**Rationale**: El nuevo orden sigue la lógica financiera: ingresos → comisión + impuestos → gastos operativos → incidentes → neto.

## R3: Mecanismo de deshabilitación del QR

**Decision**: Simplemente eliminar la llamada a `enable_verification_qr()` en `EstadoCuentaElite.generate()`.

**Rationale**: Los defaults de `BaseDocumentTemplate.__init__()` son `include_qr=False` y `qr_data=None`. El gate en `_header_footer_with_features()` (línea 142) verifica `self.include_qr and self.qr_data`, por lo que nunca se ejecutará `_add_qr_to_page()`. No se necesita modificar `base_template.py`.

**Alternatives considered**:
- Agregar un parámetro `enable_qr=False` al constructor: innecesario porque el default ya es False.
- Modificar `_header_footer_with_features()`: innecesario porque el gate ya funciona correctamente.

## R4: Transformación de comisión_porcentaje a porcentaje legible

**Decision**: Dividir `comision_porcentaje` por 100 para obtener el porcentaje legible.

**Rationale**: El campo se almacena en base 10000 (ej. 500 = 5%, 1200 = 12%). Para mostrar `Comisión (12%)`, se divide entre 100.

**Formato**: `Comisión ({comision_porcentaje / 100:.0f}%)` — sin decimales, ya que los porcentajes son enteros (500, 800, 1200).

**Alternatives considered**:
- Mostrar con decimales: `Comisión (12.00%)` — rechazado porque los porcentajes son enteros en el sistema.
- Mostrar como fracción: `Comisión (12/100)` — rechazado por claridad visual.

## R5: Manejo de observaciones vacías/nulas

**Decision**: Mostrar siempre la sección OBSERVACIONES. Si el campo es null o vacío, mostrar un mensaje por defecto.

**Rationale**: La clarificación del usuario indica que la sección debe mostrarse siempre. Esto simplifica la lógica del template (no necesita condicional).

**Mensaje por defecto**: "Sin observaciones registradas." cuando `observaciones` es None o string vacío.

## R6: Determinación de propiedad horizontal

**Decision**: Usar `gastos_administracion > 0` como indicador de propiedad horizontal.

**Rationale**: Clarificación del usuario. Es el enfoque más simple que no requiere JOIN adicional con tablas de propiedades horizontales.

**Impacto**: En el Resumen Financiero, si `gastos_administracion = 0`, se muestra `$0` para Administración.
