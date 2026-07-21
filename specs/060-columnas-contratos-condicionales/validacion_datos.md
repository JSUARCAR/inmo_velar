# Resultados de Validación de Integridad de Datos

**Fecha**: 2026-07-21

## Mandatos
- Mandatos con información de consignatario incompleta: 3
  - Contrato ID 48: Consignatario=None, Banco=BANCOLOMBIA, Cuenta=67814123275
  - Contrato ID 93: Consignatario=None, Banco=BANCOLOMBIA, Cuenta=91264891375
  - Contrato ID 45: Consignatario=None, Banco=DAVIVIENDA, Cuenta=488453374388

*Nota: La aplicación maneja correctamente estos casos mostrando la información disponible o "No registrado" en caso de que todo esté vacío.*

## Arrendamientos
- Arrendamientos con codeudor huérfano (sin persona): 0

**Conclusión**: Las relaciones de bases de datos son estructuralmente íntegras y no hay codeudores huérfanos. Los casos de Mandatos sin consignatario son manejados elegantemente en la UI.
