# Investigación: Sincronización y Diagnóstico de Filtro de Estado de Pago en Producción

## Merge Strategy para Producción

- **Decision**: Ejecutar un Merge Commit de `feat/desarrollo-experto-elite` a `main` y un Push a remoto.
- **Rationale**: Railway está configurado para escuchar hooks de push sobre la rama `main`. Un merge limpio conservará el historial detallado de la rama de desarrollo (incluyendo los arreglos específicos del componente ComboBox) y desencadenará el pipeline.
- **Alternatives considered**: Rebase o Squash. Se descarta Squash porque en este proyecto es preferible conservar los commits atómicos (e.g. `feat`, `fix`, `docs`) para auditoría (ADR 011 / Gobernanza Git).
