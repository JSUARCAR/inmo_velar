# Research: Auditoría de Tooltips Faltantes

## Decisión: Estrategia de Búsqueda y Reemplazo

**Decision**: Utilizar un script Python de búsqueda mediante expresiones regulares para identificar componentes `neuro_button`, `rx.button`, y `rx.icon_button` que no estén precedidos o envueltos por un llamado a `neuro_tooltip` o `rx.tooltip`.

**Rationale**: Dado que la aplicación consta de múltiples páginas Reflex (más de 15 módulos), una auditoría exclusivamente manual es propensa a errores y omisiones. Un escaneo de texto/código (AST simple o regex multilínea) garantiza que ningún botón sea omitido en el reporte inicial, permitiendo una inyección de código rápida y segura.

**Alternatives considered**: 
- **Auditoría visual manual**: Consiste en ejecutar la aplicación y recorrer módulo por módulo. Se descartó como método principal por consumir mucho tiempo, aunque se utilizará como mecanismo de verificación final.
- **Sobrescritura total con LLM**: Modificar los archivos completos uno a uno con la IA. Se descartó por riesgo de sobrescribir lógica de negocio importante (infringiendo las directivas de Cirugía Técnica del proyecto).
