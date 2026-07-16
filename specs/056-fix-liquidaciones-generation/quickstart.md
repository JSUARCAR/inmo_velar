# Quickstart: Validación de Corrección de Liquidaciones

**Date**: 2026-07-15
**Feature**: 056-fix-liquidaciones-generation

## Prerrequisitos

- Base de datos PostgreSQL con datos de producción (o datos de prueba similares)
- Al menos 2 propietarios con Contratos de Mandato activos
- Al menos 1 propiedad sin liquidación para el período de prueba
- Al menos 1 propiedad con liquidación existente para el período de prueba

## Escenarios de Validación

### Escenario 1: Generación Individual - Propiedad Elegible

**Setup**: La propiedad "BRR EL SILENCIO ET 2 MZ D CS 4" tiene Contrato de Mandato activo.

**Pasos**:
1. Navegar a la página de Liquidaciones
2. Hacer clic en "Nueva Liquidación"
3. Seleccionar "BRR EL SILENCIO ET 2 MZ D CS 4" en el combobox de propiedad
4. Verificar que se cargue: ID del contrato, canon de mandato, dirección, nombre del propietario
5. Seleccionar un período (YYYY-MM)
6. Hacer clic en "Guardar"

**Resultado esperado**:
- Toast: "Liquidación guardada correctamente"
- La liquidación aparece en la tabla con estado "En Proceso"
- Los valores financieros son correctos (comisión, IVA, gastos de administración)

### Escenario 2: Generación Individual - Propiedad sin Contrato Activo

**Setup**: Una propiedad NO tiene Contrato de Mandato activo.

**Pasos**:
1. Navegar a la página de Liquidaciones
2. Hacer clic en "Nueva Liquidación"
3. Intentar buscar la propiedad en el combobox

**Resultado esperado**:
- La propiedad NO aparece en las opciones del combobox
- Solo se muestran propiedades con Contrato de Mandato activo

### Escenario 3: Generación Masiva - Período Nuevo

**Setup**: Ninguna propiedad tiene liquidación para el período seleccionado.

**Pasos**:
1. Navegar a la página de Liquidaciones
2. Hacer clic en "Generar Masiva"
3. Seleccionar un período nuevo (sin liquidaciones existentes)
4. Confirmar la generación

**Resultado esperado**:
- Toast: "N generadas" (donde N = cantidad de contratos activos)
- Todas las liquidaciones aparecen en la tabla con estado "En Proceso"

### Escenario 4: Generación Masiva - Período Ya Procesado

**Setup**: Todas las propiedades ya tienen liquidación para el período seleccionado.

**Pasos**:
1. Navegar a la página de Liquidaciones
2. Hacer clic en "Generar Masiva"
3. Seleccionar un período que ya tiene liquidaciones
4. Confirmar la generación

**Resultado esperado**:
- Toast: "0 generadas, N ya existían" (informativo, no de error)
- NO se muestra "Hubo errores generando todas las liquidaciones"

### Escenario 5: Generación Masiva - Mixto

**Setup**: Algunas propiedades tienen liquidación, otras no.

**Pasos**:
1. Navegar a la página de Liquidaciones
2. Hacer clic en "Generar Masiva"
3. Seleccionar un período parcialmente procesado
4. Confirmar la generación

**Resultado esperado**:
- Toast: "X generadas, Y ya existían"
- Las nuevas liquidaciones aparecen en la tabla
- Las existentes no se duplican

### Escenario 6: Generación Masiva - Con Errores Reales

**Setup**: Un propietario tiene datos inválidos que causan error.

**Pasos**:
1. Navegar a la página de Liquidaciones
2. Hacer clic en "Generar Masiva"
3. Seleccionar un período
4. Confirmar la generación

**Resultado esperado**:
- Toast: "X generadas, Y ya existían, Z con error"
- Las liquidaciones válidas se crean correctamente
- Los errores se registran en logs del servidor con ID del propietario y causa

## Verificación de Logs

Para verificar que los errores se registran correctamente:

```bash
# En el servidor de Railway, revisar logs de la aplicación
# Buscar mensajes que contengan:
# "Error generando liquidacion para propietario ID={id}: {causa}"
```

## Criterios de Aceptación

- [ ] Escenario 1: Generación individual funciona para "BRR EL SILENCIO ET 2 MZ D CS 4"
- [ ] Escenario 2: Propiedades sin contrato activo no aparecen en el formulario
- [ ] Escenario 3: Generación masiva crea todas las liquidaciones nuevas
- [ ] Escenario 4: Generación masiva no muestra error cuando todo ya existe
- [ ] Escenario 5: Generación masiva muestra conteos correctos (generadas + omitidas)
- [ ] Escenario 6: Errores reales se registran en logs y se muestran en el toast
