# Quickstart: Validación de Búsqueda con Tecla ENTER

**Date**: 2026-07-08
**Feature**: 001-search-enter-key

## Prerrequisitos

- Servidor de desarrollo Reflex ejecutándose: `reflex run --env dev`
- Base de datos PostgreSQL accesible con datos de prueba
- Navegador web abierto en `http://localhost:3000`

## Escenarios de Validación

### V1: Búsqueda con ENTER en Personas

1. Navegar a `/personas`
2. Escribir "Juan" en el campo "Buscar"
3. Presionar ENTER
4. **Resultado esperado**: Se muestran personas filtradas por "Juan"
5. **Comparar**: Hacer clic en "Limpiar", escribir "Juan" nuevamente, y verificar que los resultados son idénticos a los del paso 3

### V2: Búsqueda con ENTER en Propiedades

1. Navegar a `/propiedades`
2. Escribir "apartamento" en "Buscar"
3. Presionar ENTER
4. **Resultado esperado**: Propiedades filtradas por "apartamento"

### V3: Búsqueda con ENTER en Contratos

1. Navegar a `/contratos`
2. Escribir "001" en "Buscar"
3. Presionar ENTER
4. **Resultado esperado**: Contratos filtrados por "001"

### V4: Búsqueda con ENTER en Liquidaciones

1. Navegar a `/liquidaciones`
2. Escribir un criterio en "Buscar"
3. Presionar ENTER
4. **Resultado esperado**: Liquidaciones filtradas por el criterio

### V5: Búsqueda con ENTER en Liquidación de Asesores

1. Navegar a `/liquidacion-asesores`
2. Escribir un nombre de asesor en "Buscar"
3. Presionar ENTER
4. **Resultado esperado**: Liquidaciones del asesor filtrado

### V6: Búsqueda con ENTER en Recaudos

1. Navegar a `/recaudos`
2. Escribir un criterio en "Buscar"
3. Presionar ENTER
4. **Resultado esperado**: Recaudos filtrados

### V7: Búsqueda con ENTER en Incidentes

1. Navegar a `/incidentes`
2. Escribir "fuga" en "Buscar"
3. Presionar ENTER
4. **Resultado esperado**: Incidentes filtrados por "fuga"

### V8: Combinación con filtros avanzados

1. Navegar a cualquier módulo (ej. Personas)
2. Seleccionar un filtro avanzado (ej. Estado = "Activo")
3. Escribir "María" en "Buscar"
4. Presionar ENTER
5. **Resultado esperado**: Resultados filtrados por "María" Y estado "Activo"

### V9: Campo vacío + ENTER

1. Navegar a cualquier módulo
2. Dejar "Buscar" vacío
3. Presionar ENTER
4. **Resultado esperado**: Se muestran todos los registros (o los filtrados por filtros avanzados)

### V10: Pulsación repetida de ENTER

1. Navegar a cualquier módulo
2. Escribir "test" en "Buscar"
3. Presionar ENTER 5 veces rápidamente
4. **Resultado esperado**: Se ejecuta la búsqueda sin errores, resultados consistentes

## Criterio de Aprobación

- [ ] Todos los escenarios V1-V10 pasan
- [ ] Los resultados de ENTER son idénticos a los del botón "Limpiar" + re-búsqueda
- [ ] No hay errores en consola del navegador
- [ ] No hay errores en logs del servidor Reflex
- [ ] El comportamiento es consistente en los 7 módulos
