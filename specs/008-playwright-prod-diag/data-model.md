# Data Model: playwright-prod-diag

*Nota: Esta funcionalidad consta exclusivamente de un script de diagnóstico y pruebas E2E, por lo que no introduce ni modifica entidades en la base de datos de dominio.*

## Entidades Observadas (Solo Lectura)

1. **Incidente**:
   - Atributos relevantes a observar en el DOM: Estado de pago, valor asociado a la cotización, cuotas generadas (Plan de Pago).
   
2. **Liquidación**:
   - Atributos relevantes a observar en el DOM: Estado de la liquidación, botón de edición, vinculación con incidentes elegibles.

Cualquier alteración a los datos se realizará estrictamente sobre la propiedad designada como Sandbox ("Calle Falsa 123 - Test Renov").
