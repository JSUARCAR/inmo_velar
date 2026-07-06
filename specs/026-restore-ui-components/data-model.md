# Data Model & Interfaces

### Domain Entities
_No aplica._ Esta característica se limita exclusivamente a modificaciones en la capa de Presentación (UI) y no altera ninguna entidad del dominio de la aplicación ni repositorios.

### Interfaces
- Se requerirá modificar las firmas de las vistas (archivos en `src/presentacion_reflex/components/`) para invocar `neuro_floating_input`, `neuro_floating_select` o `neuro_icon_action_button`.
- Los inputs recibirán sus propiedades estándar: `placeholder`, `value`, `on_change`.
- Los botones requerirán inyectar `tooltip_content: str`.
