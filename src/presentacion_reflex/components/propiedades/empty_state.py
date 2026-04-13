import reflex as rx

from src.presentacion_reflex import styles


def estado_vacio(
    titulo: str = "No se encontraron propiedades",
    mensaje: str = "Intenta ajustar los filtros o registra una nueva propiedad.",
    icono: str = "search-x",
    accion: rx.Component = None,
    **kwargs,
) -> rx.Component:
    """Estado vacío reutilizable para módulos de lista."""
    return rx.center(
        rx.vstack(
            rx.icon(icono, size=64, color=styles.TEXT_TERTIARY),
            rx.text(titulo, size="5", weight="bold", color=styles.TEXT_PRIMARY),
            rx.text(
                mensaje, size="3", color=styles.TEXT_SECONDARY, text_align="center"
            ),
            accion,
            spacing="4",
            align="center",
        ),
        role="status",
        aria_label=f"{titulo}. {mensaje}",
        height="400px",
        width="100%",
        border=f"2px dashed {styles.BORDER_DEFAULT}",
        border_radius="16px",
        background=styles.BG_APP,
        **kwargs,
    )


def estado_cargando(mensaje: str = "Cargando inventario...") -> rx.Component:
    """Estado de carga con spinner."""
    return rx.center(
        rx.vstack(
            rx.spinner(size="3", color=styles.ACCENT_COLOR),
            rx.text(mensaje, color=styles.TEXT_SECONDARY),
            spacing="4",
        ),
        height="400px",
        width="100%",
    )
