# Specification: Fix Grupo de Pago Contratos (Migración y Calibración)

## 1. Context and Problem Statement
El sistema presenta una inconsistencia de datos en el módulo de Contratos de Mandato y Arrendamiento. Específicamente, algunos contratos (ej. ID 56, ID 47, ID 55) que iniciaron el día 20 están asignados al "Grupo 2" con día de pago "20", cuando según la nueva regla de negocio (Versión 2.0), deberían pertenecer al "Grupo 3" con día de pago "30".

**Causa Raíz Identificada:**
Mediante auditoría del código (`CalculadoraContratos.calcular_ciclo_pago_mandato`) y el historial de cambios, se constató que la regla de negocio fue actualizada recientemente para usar los rangos (28-7: Grupo 1, 8-17: Grupo 2, 18-27: Grupo 3). Sin embargo, los registros existentes en la base de datos de PostgreSQL que fueron creados bajo la regla antigua (donde los días 11-20 eran Grupo 2) no fueron migrados ni recalibrados. El motor de cálculo en el código está correcto, pero los datos almacenados están desactualizados.

## 2. Actors
*   **Propietarios/Inquilinos**: Afectados por la asignación incorrecta de fechas de pago.
*   **Asesores/Administradores**: Visualizan información inconsistente en la plataforma.
*   **Sistema (PostgreSQL)**: Repositorio de los datos desincronizados.

## 3. User Scenarios & Testing
*   **Escenario 1: Recalibración Masiva (Migración)**
    *   *Dado* que existen contratos en la base de datos con asignaciones de grupo de pago correspondientes a reglas antiguas.
    *   *Cuando* se ejecuta el script de migración/calibración de base de datos.
    *   *Entonces* todos los contratos activos son reevaluados utilizando la regla oficial (28-7 -> G1, 8-17 -> G2, 18-27 -> G3) y los campos `grupo_operativo` y `fecha_pago` se actualizan a los valores correctos de forma atómica.
*   **Escenario 2: Actualización manual de fecha**
    *   *Dado* un contrato existente.
    *   *Cuando* un administrador modifica la `fecha_inicio_contrato_m`.
    *   *Entonces* el sistema recalcula atómicamente el grupo y día de pago mediante la función oficial y guarda los cambios consistentemente, sin requerir intervención manual en otros módulos.

## 4. Functional Requirements
*   **Req 1**: Desarrollar un script de migración en Python (grado industrial) que lea todos los contratos en estado ACTIVO de la tabla `CONTRATOS_MANDATOS`.
*   **Req 2**: El script debe comparar los valores actuales de `grupo_operativo` y `fecha_pago` con los valores esperados según `CalculadoraContratos.calcular_ciclo_pago_mandato`.
*   **Req 3**: El script debe actualizar de manera masiva y atómica (transacción) aquellos registros que presenten discrepancias, para alinearlos con la regla Versión 2.0.
*   **Req 4**: El proceso de actualización en el frontend/UI (vía `ServicioContratoMandato.actualizar_mandato`) debe garantizar atomicidad usando `db.transaccion()`. (El código actual ya incluye esta validación, se requiere certificar su efectividad).
*   **Req 5**: Las operaciones de actualización no deben crear estados intermedios inconsistentes. Se debe usar un rollback en caso de fallo durante la migración de datos.

## 5. Non-Functional Requirements & Constraints
*   **Atomicidad y Consistencia**: La migración debe ejecutarse en una única transacción de base de datos (`COMMIT` completo o `ROLLBACK` total).
*   **Rendimiento**: El script de migración debe ser capaz de procesar cientos de registros sin bloquear excesivamente las tablas.
*   **Trazabilidad**: El script de migración debe imprimir en consola/log los contratos afectados (ID, valores viejos, valores nuevos) antes y después de aplicar el cambio, como reporte de auditoría.

## Clarifications
### Session 2026-09-02
- Q: ¿La migración debe modificar contratos que ya están Finalizados/Cancelados, o debe restringirse estrictamente a los contratos en estado ACTIVO para evitar alterar el historial financiero? → A: Recalibrar ÚNICAMENTE los contratos en estado ACTIVO.
- Q: ¿Debe el script de migración aplicar también recalibración sobre los Contratos de Arrendamiento, o la desincronización y nueva regla aplican exclusivamente a los Contratos de Mandato? → A: Aplicar ÚNICAMENTE a Contratos de Mandato.

## 6. Assumptions
*   La lógica actual en `CalculadoraContratos.calcular_ciclo_pago_mandato` es la fuente única y final de la verdad para las reglas del Grupo 1, Grupo 2 y Grupo 3.
*   La base de datos en uso es PostgreSQL.
*   El script de recalibración restringirá su alcance de forma estricta a los contratos en estado 'ACTIVO', preservando inmutables los contratos históricos, cancelados o finalizados para no alterar la coherencia de reportes pasados.

## 7. Success Criteria
*   **Criterio 1**: El 100% de los contratos reportados con error (ID 47, 55, 56) y cualquier otro contrato con discrepancias, son actualizados en PostgreSQL al Grupo 3, día de pago 30.
*   **Criterio 2**: La auditoría sobre la tabla `CONTRATOS_MANDATOS` reporta 0 discrepancias entre el valor guardado y el valor calculado por la regla oficial tras la migración.
*   **Criterio 3**: La actualización de la fecha de inicio desde el UI recalcula el grupo y guarda exitosamente en BD, manteniendo 0 discrepancias post-edición.

## 8. Key Entities
*   `ContratoMandato` (Tabla `CONTRATOS_MANDATOS`)
