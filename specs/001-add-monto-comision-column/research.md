# Research: Agregar Columna MONTO COMISIÓN a Liquidaciones

**Date**: 2026-07-11
**Feature**: 001-add-monto-comision-column

## Research Items

### 1. Campo COMISION_MONTO en Base de Datos

**Decision**: El campo `COMISION_MONTO` ya existe en la tabla `LIQUIDACIONES` como `INTEGER NOT NULL DEFAULT 0`.

**Rationale**: No se requiere migración de BD. El campo se calcula automáticamente a partir del porcentaje de comisión sobre el canon de mandato y ya se almacena en cada registro de liquidación.

**Alternatives considered**:
- Crear un campo nuevo → Rechazado: el campo ya existe y se usa internamente en el cálculo del NETO A PAGAR.

### 2. Campo COMISION_PORCENTAJE para Tooltip

**Decision**: El campo `COMISION_PORCENTAJE` (base 10000, ej. 1500 = 15.00%) ya existe en la entidad `Liquidacion` pero NO se incluye en el query `listar_paginado`. Se debe agregar al SELECT para soportar el tooltip.

**Rationale**: El tooltip muestra "XX.XX% sobre canon". El porcentaje se almacena como entero base 10000 para preservar precisión (evitar floats). Se divide entre 100 para mostrar como porcentaje decimal.

**Alternatives considered**:
- Calcular el porcentaje desde el monto y el canon → Rechazado: innecesario y propenso a errores de redondeo cuando canon es 0.

### 3. Formato de Moneda COP

**Decision**: Reutilizar `format_currency()` de `utils/formatters.py` que formatea como `$X.XXX.XXX` (pesos colombianos, sin decimales, punto como separador de miles).

**Rationale**: Consistente con el formato usado por todas las demás columnas monetarias de la tabla. No se requiere decimales para valores en pesos colombianos.

**Alternatives considered**:
- Agregar decimales (.00) → Rechazado: inconsistente con el formato existente en la tabla.

### 4. Scroll Horizontal

**Decision**: Envolver la tabla en un contenedor con `overflow_x="auto"` para soportar scroll horizontal cuando el contenido exceda el viewport.

**Rationale**: La tabla ya tiene 17 columnas. Agregar una más incrementa el ancho. El scroll horizontal es la convención estándar en tablas de datos financieros con muchas columnas.

**Alternatives considered**:
- Ocultar columnas en pantallas pequeñas → Rechazado: el usuario necesita ver todos los datos financieros.
- Ancho fijo por columna → Rechazado: no escala bien con diferentes tamaños de pantalla.

### 5. Tooltips en Celdas de Datos

**Decision**: Usar `rx.tooltip` envolviendo el contenido de la celda, similar al patrón ya usado para botones de acción en la tabla.

**Rationale**: Consistente con el sistema de tooltips existente. El tooltip se muestra al pasar el cursor y desaparece al salir, sin interacción adicional requerida.

**Alternatives considered**:
- Popover con más detalles → Rechazado: sobre-ingeniería para un dato simple (porcentaje).
- Icono de info junto al valor → Rechazado: agrega ruido visual innecesario.

### 6. Manejo de NULL vs $0

**Decision**: Mostrar `$0` tanto para valores NULL como para 0. El campo tiene `DEFAULT 0` en BD, así que los registros nuevos siempre tendrán un valor. Los históricos sin cálculo mostrarán 0.

**Rationale**: Simplifica la lógica de display. No hay diferencia práctica entre "no calculado" y "comisión es cero" para el usuario final.

**Alternatives considered**:
- Mostrar guión (—) para NULL → Rechazado: el usuario indicó que prefiere $0.00 para ambos casos.
