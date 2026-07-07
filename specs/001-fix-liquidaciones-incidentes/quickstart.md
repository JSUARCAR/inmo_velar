# Quickstart: Corrección de Selección de Incidentes en Liquidaciones

**Date**: 2026-07-06

## Prerrequisitos

- Python 3.11+
- PostgreSQL 14+
- Reflex 0.6.x
- Acceso a base de datos de prueba

## Escenarios de Validación

### SC1: Filtrado Correcto de Incidentes por Propiedad

**Objetivo**: Verificar que el modal muestra solo incidentes de la propiedad de la liquidación.

**Pasos**:
1. Acceder al módulo de Liquidaciones
2. Editar una liquidación existente (ej: Liquidación #573 - Calle Falsa 123)
3. Hacer clic en "Seleccionar Incidentes"
4. Verificar que solo aparecen incidentes de "Calle Falsa 123"

**Resultado Esperado**:
- ✅ Solo se muestran incidentes de la propiedad "Calle Falsa 123"
- ✅ No aparecen incidentes de otras propiedades
- ✅ El modal carga correctamente con el spinner

**Comando de Prueba**:
```bash
# Ejecutar tests de integración
pytest tests/integration/test_liquidacion_incidentes.py -v -k "test_filtrado_por_propiedad"
```

### SC2: Carga de Datos al Editar

**Objetivo**: Verificar que los campos Incidentes y Observaciones cargan valores existentes.

**Pasos**:
1. Acceder a una liquidación con incidentes previamente asociados
2. Hacer clic en "Editar"
3. Verificar campo "Incidentes" muestra el valor correcto
4. Verificar campo "Observaciones" carga el texto almacenado

**Resultado Esperado**:
- ✅ Campo "Incidentes" muestra el valor total de descuentos
- ✅ Campo "Observaciones" muestra el texto previamente guardado
- ✅ Los valores son editables

**Comando de Prueba**:
```bash
pytest tests/integration/test_liquidacion_incidentes.py -v -k "test_carga_datos_edicion"
```

### SC3: Selección Múltiple de Incidentes

**Objetivo**: Verificar que el usuario puede seleccionar múltiples incidentes.

**Pasos**:
1. Abrir modal de selección de incidentes
2. Seleccionar 2 o más incidentes usando checkboxes
3. Verificar que el contador de seleccionados se actualiza
4. Verificar que el total de descuentos se calcula correctamente
5. Hacer clic en "Asociar Seleccionados"

**Resultado Esperado**:
- ✅ Los checkboxes funcionan correctamente
- ✅ El contador muestra el número correcto de seleccionados
- ✅ El total de descuentos es la suma de las cuotas
- ✅ Los incidentes se asocian exitosamente

**Comando de Prueba**:
```bash
pytest tests/integration/test_liquidacion_incidentes.py -v -k "test_seleccion_multiple"
```

### SC4: Consistencia de Datos

**Objetivo**: Verificar que los datos son consistentes entre UI y base de datos.

**Pasos**:
1. Asociar un incidente a una liquidación
2. Consultar la tabla INCIDENTE_LIQUIDACION en la base de datos
3. Verificar que el registro existe con los valores correctos
4. Recargar la página y verificar que los datos persisten

**Resultado Esperado**:
- ✅ El registro en INCIDENTE_LIQUIDACION tiene los valores correctos
- ✅ El VALOR_INCIDENTES en LIQUIDACIONES se actualiza
- ✅ Los datos persisten después de recargar

**Comando de Prueba**:
```bash
pytest tests/integration/test_liquidacion_incidentes.py -v -k "test_consistencia_datos"
```

### SC5: Manejo de Estados Vacíos

**Objetivo**: Verificar el comportamiento cuando no hay incidentes disponibles.

**Pasos**:
1. Seleccionar una liquidación de una propiedad sin incidentes elegibles
2. Abrir modal de selección de incidentes
3. Verificar que se muestra mensaje de estado vacío

**Resultado Esperado**:
- ✅ Se muestra el mensaje "No hay incidentes disponibles para asociar"
- ✅ No se muestra la tabla de incidentes
- ✅ El botón "Asociar Seleccionados" está deshabilitado

**Comando de Prueba**:
```bash
pytest tests/integration/test_liquidacion_incidentes.py -v -k "test_estado_vacio"
```

### SC6: Manejo de Errores

**Objetivo**: Verificar el manejo de errores de conexión y validación.

**Pasos**:
1. Simular error de conexión a la base de datos
2. Verificar que se muestra mensaje de error
3. Verificar que se ofrece opción de reintentar

**Resultado Esperado**:
- ✅ Se muestra callout con mensaje de error
- ✅ El usuario puede cerrar el modal
- ✅ No se muestra información sensible del error

**Comando de Prueba**:
```bash
pytest tests/integration/test_liquidacion_incidentes.py -v -k "test_manejo_errores"
```

## Comandos de Ejecución

### Ejecutar Todos los Tests

```bash
# Tests de integración
pytest tests/integration/test_liquidacion_incidentes.py -v

# Tests unitarios
pytest tests/unit/test_liquidaciones_state.py -v

# Tests de renderizado
pytest tests/ui/test_liquidaciones_components.py -v
```

### Ejecutar en Modo Debug

```bash
# Iniciar servidor en modo desarrollo
reflex run --env dev

# Acceder a la aplicación
# http://localhost:3000/liquidaciones
```

### Verificar Consola del Navegador

1. Abrir herramientas de desarrollador (F12)
2. Pestaña "Console" - verificar que no hay errores
3. Pestaña "Network" - verificar que las llamadas API son exitosas

## Criterios de Aceptación

| Criterio | Métrica | Objetivo |
|----------|---------|----------|
| Filtrado correcto | % de incidentes correctos | 100% |
| Carga de datos | % de campos cargados | 100% |
| Tiempo de carga modal | Segundos | < 3s |
| Consistencia datos | % de synchronización | 100% |
| Cobertura tests | % de código cubierto | > 90% |

## Troubleshooting

### Problema: El modal no carga incidentes

**Causa probable**: Error en la consulta SQL o conexión a BD

**Solución**:
1. Verificar logs del servidor
2. Ejecutar consulta SQL directamente en PostgreSQL
3. Verificar que `ID_PROPIEDAD` se obtiene correctamente

### Problema: Los campos no se cargan al editar

**Causa probable**: El método `open_edit_modal` no está cargando los datos

**Solución**:
1. Verificar que `form_data` se llena correctamente
2. Verificar que los campos existen en la respuesta de la API
3. Depurar con `print()` en el método

### Problema: La selección múltiple no funciona

**Causa probable**: El método `toggle_seleccion_incidente` tiene un bug

**Solución**:
1. Verificar que el `id_incidente` se pasa correctamente
2. Verificar que la lista `seleccion_incidentes_seleccionados` se actualiza
3. Depurar con `print()` en el método