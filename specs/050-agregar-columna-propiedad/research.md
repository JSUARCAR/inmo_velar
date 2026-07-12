# Research: Agregar Columna PROPIEDAD a Tabla de Recaudos

**Date**: 2026-07-11
**Feature**: 050-agregar-columna-propiedad

## Hallazgos Clave

### 1. Estado Actual de la Columna PROPIEDAD

**Decisión**: La columna PROPIEDAD **ya existe** en el código fuente.

**Evidencia**:
- Archivo: `src/presentacion_reflex/pages/recaudos.py`
- Header: Línea 259 - `"Propiedad"` con ID sortable `direccion`
- Body: Líneas 292-299 - Muestra `rec["direccion"]` + `rec["matricula"]` en VStack

**Posible causa del error reportado**:
- La columna puede estar oculta por CSS o breakpoints responsive
- Puede haber un problema de datos (campo `direccion` vacío en algunos registros)
- Puede estar en una posición diferente a la esperada por el usuario

### 2. Orden de Columnas Actual vs Esperado

| Actual (en código) | Esperado (por usuario) |
|--------------------|------------------------|
| ID | ID |
| Fecha Pago | PERIODO |
| Pago Contrato | CICLO OPERATIVO |
| Ciclo Operativo | **PROPIEDAD** |
| **Propiedad** | CANON |
| Arrendatario | IVA |
| Habitante | COMISIÓN |
| Valor | OTROS INGRESOS |
| Metodo | GASTOS ADMIN |
| Estado | GASTOS SERV |
| Acciones | GASTOS REP |
| | V. INCIDENTES |
| | PAGO PREDIAL |
| | OTROS EGRESOS |
| | NETO A PAGAR |
| | ESTADO RECAUDO |
| | ESTADO |
| | ACCIONES |

**Observación**: El usuario espera columnas financieras (CANON, IVA, COMISIÓN, etc.) que no existen en la tabla actual. Esto sugiere que la tabla necesita una reestructuración significativa o el usuario está describiendo una tabla de liquidaciones, no de recaudos.

### 3. Implementación de Sorting

- Helper: `header_cell_sortable()` (líneas 224-247)
- State: `RecaudosState.toggle_sort(column_id)` (líneas 221-230)
- Backend: `FiltrosRecaudo.sort_by` se aplica en query SQL

### 4. Implementación de Filtering

- Toolbar: `recaudos_toolbar()` (líneas 103-221)
- Filtros disponibles: Estado, Pago Contrato, Ciclo Operativo, Fechas
- **No hay filtro específico para Propiedad** - esto necesita implementarse

## Decisiones

| Decisión | Alternativa | Justificación |
|----------|-------------|---------------|
| Mantener columna existente | Reordenar columnas | La columna ya existe con datos correctos |
| Agregar filtro de propiedad | No agregar filtro | REQ-005 lo especifica |
| Usar `direccion` como nombre visible | Usar otro campo | Clarificación del usuario confirma esto |

## Riesgos Identificados

1. **Discrepancia de columnas**: El usuario espera columnas financieras que no existen en la tabla de recaudos. Verificar si esto es un error en la especificación o si la tabla necesita ser extendida.

2. **Datos faltantes**: Si `direccion` está vacío para algunos recaudos, mostrar "Sin nombre" como fallback.

3. **Performance**: JOIN con tabla de propiedades puede impactar performance si hay muchos registros.

## Recomendaciones

1. **Verificar con usuario**: Confirmar si la tabla de recaudos es la correcta o si se refiere a otra vista (liquidaciones).

2. **Implementar filtro de propiedad**: Agregar `multi_select_popover` para propiedad en el toolbar.

3. **Validar datos**: Verificar que todos los recaudos tienen `propiedad_id` válido antes de mostrar la columna.
