# Phase 0: Research & Decisions

## Context
Restoring Floating Labels and Tooltips in the Reflex application.

## Decisions

- **Decision 1**: Utilizar `rx.tooltip` nativo de Reflex para los tooltips en los botones.
  - **Rationale**: Es el componente estándar de Reflex para este caso de uso y maneja automáticamente la accesibilidad básica y el z-index interno (al cual solo debemos asegurarle estar referenciado como `Z_TOOLTIP=1100` en estilos globales).
  - **Alternatives**: Usar `rx.hover_card` fue considerado, pero `tooltip` es semánticamente más apropiado para botones de acción con textos descriptivos cortos.

- **Decision 2**: Restaurar las clases CSS de transición en los inputs para Floating Labels.
  - **Rationale**: Reflex expone propiedades CSS directamente. El estado "flotante" (focus o filled) se controlará mediante selectores de estado o control de estado si el wrapper del input así lo determina.
  - **Alternatives**: Crear un estado de Python complejo para cada input fue descartado en favor de CSS/propiedades condicionales más ligeras para no sobrecargar el backend de Reflex.
