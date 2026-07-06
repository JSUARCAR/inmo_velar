# Quickstart: Validación de fix-incident-selection-button

**Date**: 2026-07-06 | **Branch**: `029-fix-incident-selection-button`

## Prerequisitos

1. Servidor Reflex corriendo (`reflex run --env dev`)
2. Base de datos PostgreSQL accesible con datos de prueba
3. Al menos 1 liquidación en estado "En Proceso" en el sistema
4. Al menos 1 incidente con:
   - Estado: `Aprobado`, `En Reparacion` o `Finalizado`
   - Estado de pago: diferente de `Pagado`
   - Plan de pago activo con al menos 1 cuota sin asociar

## Escenario 1: Verificar Visibilidad del Botón

1. Navegar a `http://localhost:3000/liquidaciones`
2. Localizar una liquidación con estado "En Proceso"
3. Hacer clic en el botón de editar (icono de lápiz)
4. **Resultado esperado**: El formulario de edición se abre y el botón "Seleccionar Incidentes" (naranja, con icono de link) es visible debajo de la sección "Egresos Variables"

## Escenario 2: Verificar Apertura del Modal

1. Continuar desde Escenario 1
2. Hacer clic en el botón "Seleccionar Incidentes"
3. **Resultado esperado**: Se abre un modal con título "Seleccionar Incidentes"
4. **Resultado esperado**: Se muestra spinner de carga seguido de una tabla con incidentes elegibles
5. **Verificar**: La tabla muestra columnas: Sel., ID, Descripción, Propiedad, Costo, Cuota, Valor Cuota, Estado Pago, Nota

## Escenario 3: Verificar Selección y Asociación

1. Continuar desde Escenario 2
2. Seleccionar uno o más incidentes mediante checkboxes
3. **Resultado esperado**: El resumen inferior muestra "Seleccionados: N | Total descuentos: $X"
4. Hacer clic en "Asociar Seleccionados"
5. **Resultado esperado**: Toast de éxito "N incidente(s) asociado(s) exitosamente"
6. **Resultado esperado**: La tabla de liquidaciones se recarga y el neto a pagar refleja el descuento

## Escenario 4: Verificar Persistencia en Base de Datos

```sql
-- Verificar la relación creada
SELECT * FROM INCIDENTE_LIQUIDACION WHERE ID_LIQUIDACION = <id_liquidacion>;

-- Verificar que valor_incidentes se actualizó
SELECT VALOR_INCIDENTES, NETO_A_PAGAR FROM LIQUIDACIONES WHERE ID_LIQUIDACION = <id_liquidacion>;

-- Verificar que la cuota se asoció
SELECT * FROM CUOTA_INCIDENTE WHERE ID_LIQUIDACION = <id_liquidacion>;
```

## Escenario 5: Verificar Edge Cases

1. **Sin incidentes elegibles**: Abrir el modal — debe mostrar "No hay incidentes disponibles para asociar."
2. **Incidente ya asociado**: Abrir el modal cuando ya hay incidentes vinculados — deben mostrarse como "Ya asociado" con checkbox deshabilitado
3. **Consola limpia**: Abrir DevTools > Console — no debe haber errores JS/Python durante todo el flujo

## Criterios de Validación Completada

- [ ] Botón "Seleccionar Incidentes" visible en formulario de edición
- [ ] Modal se abre correctamente al hacer clic
- [ ] Incidentes elegibles se cargan y muestran
- [ ] Selección múltiple funciona con resumen en tiempo real
- [ ] Asociación persiste en base de datos correctamente
- [ ] Neto a pagar se actualiza en la interfaz
- [ ] No hay errores en consola del navegador
- [ ] Flujo completo < 2 segundos bajo condiciones normales
