import reflex as rx

from src.presentacion_reflex.state.propiedades_state import PropiedadesState
from src.presentacion_reflex import styles


def step_indicator(step: int, current_step: int, label: str, icon: str) -> rx.Component:
    """Indicador de paso individual para el wizard."""

    is_active = current_step == step
    is_completed = current_step > step

    return rx.vstack(
        # Círculo con icono
        rx.center(
            rx.icon(
                icon,
                size=20,
                color=rx.cond(is_active | is_completed, "white", "var(--gray-9)"),
            ),
            width="40px",
            height="40px",
            border_radius="full",
            background=styles.BG_PANEL,
            box_shadow=rx.cond(
                is_active | is_completed,
                styles.NEU_INSET,
                styles.NEU_SHADOW,
            ),
            opacity=rx.cond(is_active | is_completed, "1", "0.6"),
            border=rx.cond(
                is_active,
                f"2px solid {styles.ACCENT_COLOR}",
                "none"
            ),
            transition="all 0.3s ease",
            style={
                "transform": rx.cond(is_active, "scale(1.1)", "scale(1)"),
            },
        ),
        # Etiqueta
        rx.text(
            label,
            size="2",
            weight=rx.cond(is_active, "bold", "medium"),
            color=rx.cond(
                is_active,
                "var(--purple-9)",
                rx.cond(is_completed, "var(--purple-9)", "var(--gray-10)"),
            ),
        ),
        spacing="3",
        align="center",
        flex="1",
        cursor="pointer",
        on_click=lambda: PropiedadesState.set_modal_step(step),  # Navegación directa opcional
    )


def connector_line(active: bool) -> rx.Component:
    """Línea conectora entre pasos."""
    return rx.box(
        height="2px",
        flex="1",
        background=styles.BG_PANEL,
        box_shadow="inset 1px 1px 2px rgba(0,0,0,0.1), inset -1px -1px 2px rgba(255,255,255,0.5)",
        margin_top="20px",
        transition=styles.GLOBAL_TRANSITION,
        margin_x="2",
    )


def wizard_progress() -> rx.Component:
    """Componente de barra de progreso del wizard."""

    current_step = PropiedadesState.modal_step

    return rx.box(
        rx.hstack(
            step_indicator(1, current_step, "Básico", "home"),
            connector_line(current_step > 1),
            step_indicator(2, current_step, "Detalles", "layout-dashboard"),
            connector_line(current_step > 2),
            step_indicator(3, current_step, "Financiero", "dollar-sign"),
            connector_line(current_step > 3),
            step_indicator(4, current_step, "Documentos", "files"),
            width="100%",
            spacing="0",
            align="start",
        ),
        width="100%",
        padding_y="6",
        padding_x="4",
        style={
            "background": "var(--gray-2)",
            "border_bottom": "1px solid var(--gray-4)",
        },
    )
