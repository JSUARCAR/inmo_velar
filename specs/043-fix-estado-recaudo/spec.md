# Especificación: Corrección del Estado Recaudo en Liquidaciones

## Resumen

Corregir la lógica de negocio que determina el valor mostrado en la columna **Estado Recaudo** del módulo **Liquidaciones**, garantizando que refleje exclusivamente el estado del recaudo vigente asociado a la misma liquidación y al mismo período operativo, eliminando inconsistencias causadas por la consideración de recaudos de otros períodos o estados reversados.

## Clarifications

### Session 2026-07-11
- Q: ¿Qué criterio define el recaudo vigente cuando existen múltiples para el mismo período? → A: El recaudo más reciente por fecha de creación
- Q: ¿Cuáles son todos los estados válidos de un recaudo? → A: Solo 4 estados: Pendiente, Pagado, Reversado, En proceso
- Q: ¿Cómo se vincula un recaudo a una liquidación en la BD? → A: Por período operativo (coincidencia de campo período, no FK directa)

## Contexto

El sistema actual presenta inconsistencias en la columna **Estado Recaudo** del módulo de Liquidaciones. Se han identificado casos donde:
- Se muestran recaudos pertenecientes a períodos diferentes al de la liquidación
- Se consideran recaudos reversados cuando ya existe uno vigente
- Se ignora la relación entre liquidación y período operativo
- Se seleccionan incorrectamente recaudos cuando existen múltiples registros para el mismo período

Esto afecta la toma de decisiones operativas y financieras, generando confusión en los usuarios sobre el estado real del recaudo asociado a cada liquidación.

## Objetivo

Garantizar que la columna **Estado Recaudo** refleje de forma precisa, consistente y automática el estado del recaudo **vigente** correspondiente a la **misma liquidación** y al **mismo período operativo**, contemplando correctamente todos los escenarios funcionales relacionados con la ausencia de recaudos, recaudos reversados y múltiples recaudos para un mismo período.

## Requisitos Funcionales

### RF-001: Determinación del Estado Recaudo
**Descripción**: El sistema deberá determinar el Estado Recaudo basándose únicamente en el recaudo vigente asociado a la misma liquidación y al mismo período operativo.

**Criterios de Aceptación**:
- El Estado Recaudo siempre deberá corresponder al recaudo vigente asociado a la misma liquidación y al mismo período operativo
- Nunca deberán utilizarse recaudos pertenecientes a otros períodos para calcular este estado
- La información presentada en la interfaz deberá ser completamente consistente con la información almacenada en PostgreSQL y con las reglas de negocio definidas

### RF-002: Escenario Liquidación sin Recaudo Asociado
**Descripción**: Si para el período de la liquidación no existe ningún recaudo registrado, la columna Estado Recaudo deberá mostrar "Sin recaudo".

**Criterios de Aceptación**:
- Cuando no exista ningún recaudo para el período correspondiente, deberá mostrarse "Sin recaudo"
- Este estado indica que aún no se ha generado ningún recaudo para el período correspondiente

### RF-003: Escenario Recaudo Reversado
**Descripción**: Si el único recaudo asociado al período de la liquidación fue Reversado y no existe un nuevo recaudo válido para ese mismo período, la columna Estado Recaudo deberá mostrar "Reversado".

**Criterios de Aceptación**:
- Si el único recaudo existente fue reversado, deberá mostrarse "Reversado"
- Este estado deberá mantenerse hasta que exista un nuevo recaudo vigente para el mismo período
- Los recaudos reversados deberán conservarse únicamente como información histórica y no deberán influir en el estado mostrado de la liquidación

### RF-004: Escenario Recaudo Reversado Reemplazado
**Descripción**: Si para un mismo período existe un recaudo Reversado, pero posteriormente se genera un nuevo recaudo válido, la columna Estado Recaudo deberá ignorar el recaudo reversado y mostrar únicamente el estado del recaudo vigente.

**Criterios de Aceptación**:
- Si existe un recaudo reversado y posteriormente se genera un nuevo recaudo válido para el mismo período, deberá mostrarse únicamente el estado del nuevo recaudo vigente
- Ejemplos: Reversado → Pendiente → Mostrar Pendiente; Reversado → Pagado → Mostrar Pagado; Reversado → En proceso → Mostrar En proceso

### RF-005: Escenario Múltiples Recaudos Válidos
**Descripción**: Si por alguna regla de negocio existen múltiples recaudos asociados al mismo período, el sistema deberá identificar cuál corresponde al recaudo vigente utilizando los criterios funcionales definidos por el negocio.

**Criterios de Aceptación**:
- La lógica implementada deberá garantizar que únicamente se considere el recaudo vigente para determinar el Estado Recaudo
- El recaudo vigente se identifica por ser el **más reciente por fecha de creación** entre todos los recaudos válidos (no reversados) para el mismo período

### RF-006: Consistencia entre PostgreSQL, Backend y UI
**Descripción**: La información obtenida desde PostgreSQL deberá ser consistente y el backend expondrá correctamente el estado calculado. La interfaz UI/UX representará exactamente el estado devuelto por el backend.

**Criterios de Aceptación**:
- El backend expondrá correctamente el estado calculado
- La interfaz UI/UX representará exactamente el estado devuelto por el backend, sin transformaciones que alteren el resultado
- La información será consistente en todo el flujo: PostgreSQL → Backend → UI

### RF-007: No Regresiones
**Descripción**: La solución no deberá introducir regresiones en los módulos Liquidaciones, Recaudos ni en cualquier otro proceso relacionado.

**Criterios de Aceptación**:
- La solución no deberá afectar otros procesos relacionados con los módulos Liquidaciones y Recaudos
- Se deberán ejecutar pruebas funcionales, de integración y de regresión para asegurar que la solución no afecte otros procesos

## Escenarios de Prueba

### CP-001: Liquidación sin Recaudo
- **Dado**: Una liquidación para el período mayo 2026 sin recaudos asociados
- **Cuando**: Se visualiza la liquidación en la tabla
- **Entonces**: La columna Estado Recaudo muestra "Sin recaudo"

### CP-002: Liquidación con Recaudo Reversado Único
- **Dado**: Una liquidación para el período junio 2026 con un único recaudo en estado "Reversado"
- **Cuando**: Se visualiza la liquidación en la tabla
- **Entonces**: La columna Estado Recaudo muestra "Reversado"

### CP-003: Liquidación con Recaudo Reversado y Nuevo Válido
- **Dado**: Una liquidación para el período julio 2026 con un recaudo "Reversado" y un nuevo recaudo "Pendiente" para el mismo período
- **Cuando**: Se visualiza la liquidación en la tabla
- **Entonces**: La columna Estado Recaudo muestra "Pendiente" (ignora el reversado)

### CP-004: Liquidación con Múltiples Recaudos Válidos
- **Dado**: Una liquidación para el período agosto 2026 con múltiples recaudos válidos para el mismo período
- **Cuando**: Se visualiza la liquidación en la tabla
- **Entonces**: La columna Estado Recaudo muestra el estado del recaudo vigente según los criterios de negocio definidos

### CP-005: Liquidación con Recaudo de Período Diferente
- **Dado**: Una liquidación para el período septiembre 2026 con un recaudo asociado al período octubre 2026
- **Cuando**: Se visualiza la liquidación en la tabla
- **Entonces**: La columna Estado Recaudo muestra "Sin recaudo" (no considera el recaudo de otro período)

### CP-006: Verificación de Consistencia UI
- **Dado**: Una liquidación con un recaudo vigente en estado "Pagado" para el mismo período
- **Cuando**: Se visualiza la liquidación en la tabla y se compara con la información en PostgreSQL
- **Entonces**: El estado mostrado en la UI coincide exactamente con el estado almacenado en PostgreSQL

## Restricciones

- La solución debe ser completamente retrocompatible con la funcionalidad existente
- No se deben modificar las estructuras de tablas existentes en PostgreSQL a menos que sea estrictamente necesario
- La solución debe mantener la integridad referencial entre liquidaciones y recaudos
- El rendimiento de las consultas no debe degradarse significativamente

## Supuestos

- La relación entre liquidaciones y recaudos se establece por **coincidencia de período operativo** (ambos comparten un campo de período, ej. "2026-05"), no por FK directa
- Los recaudos tienen un campo que indica su estado con exactamente 4 valores posibles: **Pendiente**, **Pagado**, **Reversado**, **En proceso**
- Los recaudos tienen un campo que indica el período al que pertenecen
- Existe un mecanismo para identificar qué recaudo está "vigente" para un período determinado
- La interfaz UI actual ya tiene la columna Estado Recaudo definida

## Alcance

### Incluido
- Corrección de la lógica de negocio para determinar el Estado Recaudo
- Implementación de los escenarios funcionales descritos
- Verificación de consistencia entre PostgreSQL, Backend y UI
- Pruebas de regresión para garantizar que no se afectan otros procesos

### No Incluido
- Modificaciones a la estructura de tablas existentes (a menos que sea estrictamente necesario)
- Nuevas funcionalidades más allá de la corrección del Estado Recaudo
- Cambios en otros módulos no relacionados con Liquidaciones y Recaudos

## Criterios de Éxito

1. **Precisión**: El Estado Recaudo siempre refleja el recaudo vigente correspondiente a la misma liquidación y período operativo
2. **Consistencia**: La información es idéntica en PostgreSQL, Backend y UI
3. **Escenarios Cubiertos**: Todos los escenarios funcionales (sin recaudo, reversado, reemplazado, múltiples) funcionan correctamente
4. **No Regresión**: No se afectan otros procesos existentes
5. **Validación**: Se ejecutan pruebas funcionales, de integración y de regresión exitosamente

## Entregables

1. Código corregido en el backend para la lógica de determinación del Estado Recaudo
2. Verificación de la consistencia en la UI
3. Pruebas de regresión ejecutadas y documentadas
4. Documentación de los cambios realizados
