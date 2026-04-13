import reflex as rx

from src.presentacion_reflex.state.propiedades_state import PropiedadesState
from src.presentacion_reflex import styles


def indicador_paso(step: int, paso_actual: int, label: str, icon: str) -> rx.Component:
    """Indicador de paso individual para el asistente de creación."""

    esta_activo = paso_actual == step
    esta_completado = paso_actual > step

    return rx.vstack(
        rx.center(
            rx.icon(
                icon,
                size=20,
                color=rx.cond(
                    esta_activo | esta_completado, "white", styles.TEXT_TERTIARY
                ),
            ),
            width="40px",
            height="40px",
            border_radius="full",
            background=styles.BG_PANEL,
            box_shadow=rx.cond(
                esta_activo | esta_completado,
                styles.SHADOW_RING,
                styles.SHADOW_WHISPER,
            ),
            opacity=rx.cond(esta_activo | esta_completado, "1", "0.6"),
            border=rx.cond(esta_activo, f"2px solid {styles.BRAND_PRIMARY}", "none"),
            transition="all 0.3s ease",
            style={
                "transform": rx.cond(esta_activo, "scale(1.1)", "scale(1)"),
            },
        ),
        rx.text(
            label,
            size="2",
            weight=rx.cond(esta_activo, "bold", "medium"),
            color=rx.cond(
                esta_activo,
                styles.BRAND_PRIMARY,
                rx.cond(esta_completado, styles.BRAND_PRIMARY, styles.TEXT_SECONDARY),
            ),
        ),
        spacing="3",
        align="center",
        flex="1",
        cursor="pointer",
        on_click=lambda: PropiedadesState.set_modal_step(step),
    )


def linea_conectora(activa: bool) -> rx.Component:
    """Línea visual entre pasos del asistente."""
    return rx.box(
        height="2px",
        flex="1",
        background=styles.BG_PANEL,
        box_shadow=styles.SHADOW_RING,
        margin_top="20px",
        transition=styles.GLOBAL_TRANSITION,
        margin_x="2",
    )


def progreso_asistente() -> rx.Component:
    """Barra de progreso del asistente de creación de propiedades."""

    paso_actual = PropiedadesState.modal_step

    return rx.box(
        rx.hstack(
            indicador_paso(1, paso_actual, "Básico", "home"),
            linea_conectora(paso_actual > 1),
            indicador_paso(2, paso_actual, "Detalles", "layout-dashboard"),
            linea_conectora(paso_actual > 2),
            indicador_paso(3, paso_actual, "Financiero", "dollar-sign"),
            linea_conectora(paso_actual > 3),
            indicador_paso(4, paso_actual, "Documentos", "files"),
            width="100%",
            spacing="0",
            align="start",
        ),
        width="100%",
        padding_y="6",
        padding_x="4",
        style={
            "background": styles.BG_APP,
            "border_bottom": f"1px solid {styles.BORDER_DEFAULT}",
        },
    )
