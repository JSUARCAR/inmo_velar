# Data Model Updates

No modifications to the underlying PostgreSQL schema or Pydantic entity models are required for this fix. The persistence layer correctly handles the `save_liquidacion` and `save_recaudo` commands when they receive valid data.

## Relevant Existing Entities (Context)

### Liquidacion
- Affected fields during edit: `otros_ingresos`, `gastos_administracion`, `gastos_servicios`, `valor_incidentes`, `pago_predial`, `otros_egresos`, `observaciones`.
- Handled by: `ServicioFinanciero.actualizar_liquidacion`.

### Recaudo
- Affected fields during edit: `fecha_pago`, `valor_total`, `metodo_pago`, `referencia_bancaria`, `tipo_concepto`, `periodo`, `observaciones`.
- Handled by: `ServicioRecaudo.actualizar_pago`.
