# Quickstart Validation: Ciclo Operativo en Módulo Recaudos

**Date**: 2026-07-11

## Prerrequisitos

- Base de datos PostgreSQL con datos de prueba (mínimo: 1 recaudo con liquidación asociada)
- Aplicación Reflex corriendo en modo dev (`reflex run --env dev`)
- Propiedad de prueba: BRR BOSQUES DE PINARES MZ 4 CS 144 PI 1 (grupo operativo 1)

## Escenarios de Validación

### V1: Columna visible en tabla principal

1. Abrir la aplicación en el navegador
2. Navegar al módulo Recaudos
3. **Verificar**: La columna "Ciclo Operativo" aparece después de "Pago Contrato"
4. **Verificar**: Los recaudos con liquidación asociada muestran "Grupo N" (ej: "Grupo 1")

### V2: Caso de validación específico

1. Buscar la propiedad "BRR BOSQUES DE PINARES MZ 4 CS 144 PI 1" en la tabla de Recaudos
2. **Verificar**: La columna Ciclo Operativo muestra exactamente "Grupo 1"
3. Abrir la Liquidación de Propietarios correspondiente
4. **Verificar**: El ciclo operativo de la liquidación coincide con "Grupo 1"

### V3: Recaudos sin liquidación asociada

1. Identificar o crear un recaudo sin liquidación de propietarios asociada
2. **Verificar**: La columna Ciclo Operativo muestra un guion "-"
3. **Verificar**: La tabla opera normalmente (ordenar, filtrar, paginar)

### V4: Ordenamiento por ciclo operativo

1. Hacer clic en el header "Ciclo Operativo" para ordenar
2. **Verificar**: Los recaudos se agrupan por grupo operativo (1, 2, 3, 4, 5)
3. **Verificar**: El ordenamiento funciona ascendente y descendente

### V5: Exportación de datos

1. Exportar la tabla de Recaudos a Excel/CSV
2. **Verificar**: El archivo exportado incluye la columna "Ciclo Operativo"
3. **Verificar**: Los valores en la exportación coinciden con los de la UI

### V6: Consistencia entre módulos

1. Abrir el módulo Liquidaciones de Propietarios
2. Filtrar por un grupo operativo específico (ej: Grupo 1)
3. Abrir el módulo Recaudos
4. **Verificar**: Los recaudos de propiedades de Grupo 1 muestran "Grupo 1" en Ciclo Operativo
5. **Verificar**: No hay discrepancias entre los valores mostrados en ambos módulos

### V7: Rendimiento

1. Medir tiempo de carga de la tabla de Recaudos antes del cambio (baseline)
2. Aplicar el cambio y recargar
3. **Verificar**: El tiempo de carga no incrementa más de un 10%
4. **Verificar**: No hay errores en consola del navegador ni en logs del servidor

## Criterio de Aceptación Global

Todos los escenarios V1-V7 deben pasar. La columna Ciclo Operativo:
- Aparece en la posición correcta (después de Pago Contrato)
- Muestra valores correctos ("Grupo N" o "-")
- Es consistente con la Liquidación de Propietarios correspondiente
- No afecta rendimiento ni funcionalidad existente
- Incluye exportación
