# Research: Mejorar UI Filtros Liquidaciones

## Unknowns Resolved

Ninguna, los requerimientos son estrictamente sobre la disposición de los componentes de interfaz en Reflex (Layout/CSS).

## Layout Approach

- **Decision**: Utilizar `rx.flex` con `wrap="wrap"` y `gap="4"` o `gap="5"` de manera consistente. Reorganizar los botones y el toggle de vista.
- **Rationale**: El solapamiento ocurre porque en resoluciones medianas/pequeñas, los elementos no tienen espacio para fluir o el gap es muy pequeño. Mejorando el layout de flexbox, aseguramos responsividad nativa sin media queries complejas.
- **Alternatives considered**: Ajustar el tamaño (width) de los inputs para forzarlos en una línea. Descartado porque no es escalable si se añaden más filtros.
