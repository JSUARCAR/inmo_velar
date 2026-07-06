# Research: Tooltips en Filtros Avanzados

## 1. Reflex `rx.tooltip` y Dispositivos Móviles
- **Decision:** Se utilizará el componente nativo `rx.tooltip` de Reflex, pero se debe asegurar que se oculta en dispositivos móviles para no interferir con los eventos de tap, según la especificación.
- **Rationale:** Reflex envuelve componentes de Radix UI. Para ocultar tooltips en dispositivos táctiles, Radix a menudo permite configuraciones de `delayDuration` o se puede usar CSS puro para ocultarlo en pantallas pequeñas (`display: "none"` en media queries o estilos condicionales basados en ancho de pantalla, aunque lo ideal es detectar touch). Reflex soporta utilidades responsive como `display=["none", "none", "block"]` (oculto en móvil/tablet, visible en desktop).
- **Alternatives considered:** Crear un componente Tooltip custom, pero esto viola la directiva de usar componentes nativos o existentes si aplican, y añade complejidad innecesaria.

## 2. Aplicación de Estilos Globales (Z-Index y Pointer Events)
- **Decision:** El z-index del tooltip debe ser `1100` y el `pointer-events: auto` (si aplica) de acuerdo al `BASE_STYLE` y `Z_TOOLTIP` de `src.presentacion_reflex.styles`.
- **Rationale:** La constitución dicta que los modales, popovers y tooltips deben seguir la escala estricta de z-index y manejar explícitamente `pointer-events` debido a Radix UI. Se deben pasar estas propiedades (e.g. `z_index=Z_TOOLTIP`) o asegurarse de que el componente base ya las tiene inyectadas de manera global.
- **Alternatives considered:** Ignorar el z-index, pero esto resultaría en tooltips ocultos detrás de modales de filtros o diálogos superpuestos.

## 3. Identificación de Botones de Filtros Avanzados
- **Decision:** Se debe inspeccionar cada módulo para ubicar la botonera de filtros (generalmente un `rx.hstack` o `rx.button` de limpieza/búsqueda).
- **Rationale:** El requerimiento pide abarcar 15 módulos diferentes. La estructura del código de los módulos bajo `src/presentacion_reflex/pages/` o `src/presentacion_reflex/components/` debe ser refactorizada para envolver cada botón pertinente con `rx.tooltip(text="Verbo en infinitivo", side="top")`.
- **Alternatives considered:** N/A. Es mandatorio por especificación.
