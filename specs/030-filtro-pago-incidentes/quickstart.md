# Quickstart Validation: Filtro de Pago en Incidentes

Este documento describe cómo validar funcionalmente el nuevo filtro de estados de pago tras su implementación.

## Prerrequisitos
- Base de datos PostgreSQL en local (`test_db` o similar) con la estructura migrada y datos de prueba.
- Aplicación corriendo localmente: `reflex run --env dev`
- Existencia de al menos 2 incidentes que tengan liquidaciones con estados distintos (e.g., uno con liquidación "Pagada" y otro con "Pendiente").

## Pasos de Validación

### Escenario 1: Poblamiento Dinámico del ComboBox
1. Abre el navegador y dirígete al módulo de **Incidentes**.
2. Despliega la sección de **Filtros Avanzados**.
3. Revisa el ComboBox etiquetado como "Estado de Pago del Incidente".
4. **Criterio de Éxito**: El ComboBox debe mostrar únicamente los estados de pago que existan actualmente en las liquidaciones asociadas de la base de datos (Ej: "Pagada", "Pendiente").

### Escenario 2: Filtrado por Estado Específico
1. Selecciona el estado "Pagada" en el ComboBox de Estado de Pago.
2. Aplica los filtros.
3. **Criterio de Éxito**: La tabla de incidentes debe actualizarse instantáneamente (< 1s) mostrando SOLO los incidentes que posean al menos una liquidación en estado "Pagada".

### Escenario 3: Limpiar el Filtro (Comportamiento por Defecto)
1. Borra la selección del ComboBox dejándolo vacío.
2. Aplica los filtros.
3. **Criterio de Éxito**: La tabla debe volver a mostrar todos los incidentes originales sin restringir por estado de pago.

### Escenario 4: Combinación de Filtros
1. Selecciona un "Estado de Pago" (ej. "Pendiente").
2. Selecciona un "Ciclo" o "Inmueble" en los otros filtros de la UI.
3. Aplica los filtros.
4. **Criterio de Éxito**: La tabla muestra los incidentes que cumplen *ambas* condiciones de manera estricta.
