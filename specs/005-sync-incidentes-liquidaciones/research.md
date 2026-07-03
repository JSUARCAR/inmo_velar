# Research: Sincronización Incidentes y Liquidaciones

## Investigación sobre el Flujo Actual de Incidentes y Liquidaciones

### Decisiones y Hallazgos

1. **Decisión: Relación entre Incidente y Plan de Pago**
   - **Hallazgo:** Actualmente, la entidad `PlanPagoIncidente` mantiene una relación 1 a 1 mediante `id_incidente` en la base de datos (tabla `PLAN_PAGO_INCIDENTE`).
   - **Razón:** Esto asegura que la cardinalidad está bien definida. El problema no es la falta de relación a nivel de base de datos, sino la falta de recuperación de estos datos al consultar un Incidente desde el frontend o los controladores.
   - **Acción:** Modificar el `ServicioIncidentes` y `RepositorioIncidentes` para adjuntar la información del Plan de Pago al modelo del Incidente al consultarlo, permitiendo su visualización en Reflex.

2. **Decisión: Relación entre Cuotas y Liquidación de Propietario**
   - **Hallazgo:** La generación de liquidaciones mensuales en `ServicioFinanciero` no recupera las cuotas pendientes en la tabla `CUOTA_INCIDENTE` correspondientes a la propiedad.
   - **Razón:** El método `generar_liquidacion_mensual` inyecta valores predeterminados o vacíos en `gastos_reparaciones` desde `datos_adicionales`.
   - **Acción:** Antes de calcular los totales de la liquidación, el servicio financiero deberá utilizar `RepositorioCuota` para buscar todas las cuotas en estado "Pendiente" asociadas a la propiedad del contrato actual. Las cuotas recuperadas se sumarán al campo `valor_incidentes`.

3. **Decisión: Cambio de Estado de la Cuota**
   - **Hallazgo:** Al asociar una cuota a una liquidación, la cuota transita al estado "Asociada". Sin embargo, faltan los triggers lógicos para cambiar este estado a "Pagada/Descontada" una vez que la liquidación pase a estado "Finalizada" o "Pagada".
   - **Razón:** El estado de la cuota no cambiará automáticamente sin una intervención en los flujos de actualización de liquidaciones.
   - **Acción:** En el flujo donde se aprueba y finaliza una liquidación, añadir una llamada al servicio de cuotas para transitar su estado a "Pagada" si están relacionadas mediante `INCIDENTE_LIQUIDACION` o directamente por su `id_liquidacion`.

4. **Decisión: Persistencia Inicial del Plan de Pago**
   - **Hallazgo:** El sistema requiere que el plan de pago y sus respectivas cuotas se creen *en el mismo momento* en el que la cotización del incidente es aprobada.
   - **Razón:** Evita planes de pago huérfanos o inconsistencias temporales.
   - **Acción:** Asegurar que `ServicioPlanPagoIncidente.crear_plan_con_cuotas` se invoque dentro de la misma transacción en la que el estado del Incidente pasa a "Aprobado".

### Alternativas Consideradas

- *Agregar los campos del plan de pago directamente en la entidad Incidente*: Rechazado. Violaría la normalización actual que utiliza una tabla separada `PLAN_PAGO_INCIDENTE`.
- *Dejar que el usuario ingrese manualmente el valor de los incidentes en la liquidación*: Rechazado. Es propenso a errores y rompe el objetivo de automatización del sistema.
