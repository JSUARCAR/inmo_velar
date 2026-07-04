# Phase 1: Data Model & Test Objects

**Feature**: playwright-validation
**Date**: 2026-07-03

Dado que este desarrollo es puramente un arnés de pruebas (E2E), el "Data Model" en este contexto corresponde a los "Test Data Entities" que el automatizador espera visualizar y manipular en la interfaz, más que a modelos de SQLAlchemy/SQL.

## Test Data Entities (UI Representation)

### 1. Incidente (Detalle & Plan de Pago)
Representa un registro visible en el módulo `/incidentes`.

**Campos Clave a validar en UI**:
- `Propiedad`: "CONJ CIUDADELA COMFENALCO MZ H CS 29".
- `Plan de Pago (Acordeón o Tabla)`: Debe existir y estar expandido.
  - Lista de **Cuotas**.
- `Estado General`: Relativo a la liquidación.

### 2. Cuota (Dentro de Plan de Pago)
Representa el desglose de los pagos diferidos o fracciones acordadas.

**Validaciones Estrictas**:
- Cada fila representa una cuota generada.
- Debe coincidir el `Valor` de la cuota con el acordado.
- Debe tener una etiqueta visual de su `Estado de Pago` (ej. "Pendiente", "Pagado").

### 3. Liquidacion (Módulo Liquidaciones)
Registro mensual consolidado que se puede editar y eliminar. Ubicado en `/liquidaciones`.

**Campos Clave y Acciones**:
- `Propiedad`: "Calle Falsa 123 - Test Renov".
- Acción `Seleccionar Incidentes`: Botón que habilita un Modal.
- Selección en Modal: Checkboxes habilitados solo para incidentes no "Pagados".
- Acción `Eliminar`: Botón (ícono de papelera) que despliega un diálogo de confirmación `Radix UI Alert Dialog`.

## State Transitions to Validate

1. **Selección de Incidente**
   - *Initial*: Liquidación sin incidentes seleccionados. Modal cerrado.
   - *Event*: Clic "Seleccionar Incidentes" -> Seleccionar un item -> "Guardar/Confirmar".
   - *Final*: Modal cerrado, Input/Resumen en el formulario de la liquidación reflejando el número/detalle de incidentes añadidos.

2. **Eliminación de Liquidación**
   - *Initial*: Tabla muestra el registro "Calle Falsa 123 - Test Renov".
   - *Event*: Clic en Eliminar -> Clic en Confirmar en diálogo de advertencia.
   - *Final*: Petición POST/DELETE enviada y HTTP 200 OK recibido. Toast de éxito visible. El registro desaparece del DOM de la tabla.
