# Quickstart: Sincronización Incidentes y Liquidaciones

Esta guía proporciona los pasos para validar el funcionamiento correcto de la sincronización de incidentes y la propagación de planes de pago a liquidaciones mediante pruebas manuales y scripts.

## Prerrequisitos

- Base de datos PostgreSQL en ejecución (`railway` local o remoto según config).
- Entorno de Python activado y dependencias instaladas (`pip install -r requirements.txt`).
- Reflex configurado (`reflex run`).

## Validaciones End-to-End

### Escenario 1: Verificación de UI en el Módulo de Incidentes

1. **Crear y Aprobar un Incidente**
   - Accede a la interfaz de Reflex en `http://localhost:3000`.
   - Navega al módulo de **Incidentes**.
   - Selecciona un incidente en estado `Cotizado`.
   - Aprueba la cotización. En la interfaz se debe mostrar inmediatamente la configuración del **Plan de Pago** (Número de cuotas, valor de cuota).

2. **Persistencia**
   - Verifica en la base de datos que se crearon los registros correspondientes.
   ```sql
   SELECT * FROM plan_pago_incidente WHERE id_incidente = [tu_id_incidente];
   SELECT * FROM cuota_incidente WHERE id_plan_pago = [el_id_generado];
   ```

### Escenario 2: Propagación de Cuotas a Liquidaciones

1. **Generar Liquidación Mensual**
   - Navega al módulo de **Liquidaciones de Propietario**.
   - Genera la liquidación para la propiedad/contrato asociado al incidente del Escenario 1.
   
2. **Verificar Descuentos**
   - Al ver el detalle de la liquidación en borrador ("En Proceso"), el campo de descuento por **Incidentes** debe mostrar el monto correspondiente a 1 cuota (o más, según aplicabilidad).
   - Verifica en base de datos que la cuota transitó al estado "Asociada":
   ```sql
   SELECT estado_pago, id_liquidacion FROM cuota_incidente WHERE id_plan_pago = [el_id_generado];
   ```

### Escenario 3: Finalización del Pago de la Cuota

1. **Aprobar y Pagar Liquidación**
   - En el módulo de liquidaciones, cambia el estado de la liquidación a "Pagada" o finalizada.
   
2. **Validar Cambio de Estado Automático**
   - Consulta nuevamente las cuotas del incidente. Su `estado_pago` debe reflejarse como "Pagada".
   ```sql
   SELECT estado_pago FROM cuota_incidente WHERE id_liquidacion = [id_liquidacion_pagada];
   ```
   El valor debe ser obligatoriamente `Pagada`.
