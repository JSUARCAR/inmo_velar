# Data Model: Restablecer Etiquetas Flotantes y Tooltips

> **Nota**: Esta característica aborda exclusivamente regresiones en la capa de Presentación UI (Reflex). No se introducen nuevas entidades de dominio ni se modifican repositorios o modelos de datos.

## Affected Components (Presentación)

- `Input`: Componente envoltorio (wrapper) de `rx.input` que gestiona las clases CSS para la etiqueta flotante (Floating Label).
- `Botones`: Botones de acción general (guardar, cancelar, eliminar, etc.) que envuelven `rx.button`. Serán integrados o envueltos por `rx.tooltip`.

No database schemas, Pydantic DTOs, or domain objects are affected by this specific change.
