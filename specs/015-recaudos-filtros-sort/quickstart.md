# Quickstart Validation Guide: Recaudos - Filtros Avanzados y Ordenamiento de Tabla

**Date**: 2026-07-05
**Feature**: 015-recaudos-filtros-sort

## Prerequisites

- Servidor de desarrollo Reflex ejecutándose (`reflex run --env dev`)
- Base de datos con al menos:
  - 5 contratos de arrendamiento activos
  - 20 recaudos de prueba con diferentes estados, fechas y valores
- Usuario con permisos "Recaudos" > "CREAR", "EDITAR", "ELIMINAR", "APLICAR", "REVERSAR"

## Validation Scenarios

### Scenario 1: Filtro Pago Contrato

1. Navegar a `/recaudos`
2. Verificar que el dropdown "Pago Contrato" aparece en la toolbar con opciones de contratos activos
3. Seleccionar un contrato específico
4. **Expected**: La tabla muestra solo recaudos de ese contrato; paginación en página 1
5. Cambiar a otro contrato
6. **Expected**: La tabla se actualiza con los nuevos resultados

### Scenario 2: Filtro Estado

1. En `/recaudos`, seleccionar "Pendiente" en el filtro Estado
2. **Expected**: Solo aparecen recaudos con estado Pendiente
3. Seleccionar "Todos"
4. **Expected**: Aparecen todos los recaudos

### Scenario 3: Homologación visual con Liquidaciones

1. Abrir `/liquidaciones` en una pestaña
2. Abrir `/recaudos` en otra pestaña
3. Comparar visualmente la sección de filtros
4. **Expected**: Misma distribución (Search + dropdowns en grupo de filtros, acciones separadas), mismos componentes (`neuro_input`, `neuro_select_root`), mismo estilo visual

### Scenario 4: Botón Limpiar Filtros

1. Aplicar filtros (Pago Contrato + Estado + búsqueda)
2. Hacer clic en el botón de limpiar filtros (icono "x" o "filter-x")
3. **Expected**: Todos los filtros se restablecen a valores por defecto; tabla muestra todos los registros; paginación en página 1

### Scenario 5: Ordenamiento de columnas

1. Hacer clic en el encabezado "Fecha Pago"
2. **Expected**: Tabla ordenada por fecha descendente (icono chevron-down)
3. Hacer clic nuevamente en "Fecha Pago"
4. **Expected**: Tabla ordenada por fecha ascendente (icono chevron-up)
5. Hacer clic en "Valor"
6. **Expected**: Tabla ordenada por valor descendente; la columna "Fecha Pago" vuelve a icono inactivo

### Scenario 6: Columna Acciones no ordenable

1. Hacer clic en el encabezado "Acciones"
2. **Expected**: No se produce ningún cambio de ordenamiento

### Scenario 7: Empty state (sin resultados)

1. Seleccionar un filtro que no tenga resultados (ej. un contrato sin pagos)
2. **Expected**: Aparece un `rx.callout` con icono "search" y mensaje "No se encontraron recaudos"

### Scenario 8: Persistencia de sort + filtros

1. Aplicar filtro Estado = "Pendiente"
2. Ordenar por "Valor" ascendente
3. Navegar a página 2
4. **Expected**: El ordenamiento por Valor se mantiene; el filtro Pendiente se mantiene

### Scenario 9: Rendimiento

1. Con una tabla con >1000 registros, cambiar filtros y ordenar
2. **Expected**: Respuesta percibida < 3 segundos; sin errores en consola del navegador

## Regression Checks

- Verificar que la funcionalidad de crear/editar/eliminar recaudos no se afectó
- Verificar que los botones de acción (Aplicar Pago, Reversar Pago, PDF) siguen funcionando
- Verificar que la paginación sigue funcionando correctamente
- Verificar que el modal de detalle de recaudo se abre correctamente
