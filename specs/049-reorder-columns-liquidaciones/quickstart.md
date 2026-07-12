# Quickstart Validation: Reordenar Columnas Tabla Liquidaciones

**Date**: 2026-07-11

## Prerrequisitos

- Aplicación corriendo en modo desarrollo (`reflex run --env dev`)
- Acceso al módulo Liquidaciones con datos de prueba
- Navegador web actualizado

## Escenarios de Validación

### V1: Orden de Columnas — Vista Individual

1. Navegar al módulo Liquidaciones
2. Verificar que la tabla individual muestra las 16 columnas en este orden:
   - ID → Periodo → Ciclo Operativo → Canon → IVA Comisión → Otros Ingresos → Gastos Admin → Gastos Serv → Gastos Rep → V. Incidentes → Pago Predial → Otros Egresos → Neto a Pagar → Estado Recaudo → Estado → Acciones
3. **Resultado esperado**: Columnas visibles en el orden exacto, sin "Propiedad"

### V2: Orden de Columnas — Vista Agrupada

1. Activar la vista agrupada (toggle)
2. Verificar que las columnas muestran el patrón: Canon Total → Total IVA Com. → Total Otros Ing. → ...
3. **Resultado esperado**: IVA Comisión después de Canon Total

### V3: Funcionalidad de Ordenamiento

1. Hacer clic en el encabezado de "Canon" → orden ascendente
2. Hacer clic de nuevo → orden descendente
3. Hacer clic en "Neto a Pagar" → verificar ordenamiento
4. **Resultado esperado**: Ordenamiento funciona en todas las columnas

### V4: Búsqueda Rápida

1. Escribir un término en la búsqueda
2. Verificar que los resultados se filtran correctamente
3. **Resultado esperado**: Búsqueda opera sobre datos, no posición

### V5: Filtros Avanzados

1. Abrir filtros avanzados
2. Seleccionar un filtro financiero (ej. Canon min/max)
3. **Resultado esperado**: Filtros operan correctamente

### V6: Paginación

1. Navegar a página 2
2. Verificar que el orden de columnas se mantiene
3. **Resultado esperado**: Orden consistente entre páginas

### V7: Scroll Horizontal

1. Reducir ventana a 1280px
2. Verificar scroll horizontal
3. **Resultado esperado**: Scroll suave, Acciones accesible al final

### V8: Exportación PDF

1. Generar estado de cuenta PDF desde una fila
2. **Resultado esperado**: PDF se genera correctamente (layout propio, no afectado)

### V9: Consola del Navegador

1. Abrir DevTools → Console
2. Navegar por la tabla, ordenar, filtrar
3. **Resultado esperado**: Sin errores en consola

## Comandos de Ejecución

```bash
# Iniciar servidor de desarrollo
reflex run --env dev

# Navegar a liquidaciones
# URL: http://localhost:3000/liquidaciones
```

## Criterio de Aprobación

Todos los escenarios V1-V9 pasan sin errores. La tabla muestra exactamente las 16 columnas en el orden especificado.
