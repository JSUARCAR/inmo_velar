import reflex as rx

from src.presentacion_reflex.state.personas_state import PersonasState
from src.presentacion_reflex import styles


def progreso_asistente() -> rx.Component:
    """Indicador de progreso premium para el asistente multi-paso con estetica Claude (Anthropic)."""

    def indicador_paso(num_paso: int, etiqueta: str) -> rx.Component:
        """Circulo indicador de paso individual con profundidad basada en anillos."""
        es_actual = PersonasState.modal_step == num_paso
        esta_completado = PersonasState.modal_step > num_paso

        return rx.vstack(
            # Circulo del paso esculpido
            rx.box(
                rx.cond(
                    esta_completado,
                    rx.icon("check", size=20, color=styles.BRAND_PRIMARY),
                    rx.text(
                        str(num_paso),
                        size="3",
                        weight="bold",
                        color=rx.cond(
                            es_actual, styles.BRAND_PRIMARY, styles.TEXT_TERTIARY
                        ),
                    ),
                ),
                width="42px",
                height="42px",
                border_radius="full",
                display="flex",
                align_items="center",
                justify_content="center",
                style={
                    "background": rx.cond(es_actual, "white", styles.BG_PANEL),
                    "transition": styles.GLOBAL_TRANSITION,
                    "box_shadow": rx.cond(
                        esta_completado | es_actual,
                        styles.SHADOW_INSET,
                        styles.SHADOW_RING,
                    ),
                    "border": rx.cond(
                        es_actual,
                        f"2px solid {styles.BRAND_PRIMARY}",
                        f"1px solid {styles.BORDER_DEFAULT}",
                    ),
                    "transform": rx.cond(es_actual, "scale(1.1)", "scale(1)"),
                },
            ),
            # Etiqueta del paso
            rx.text(
                etiqueta,
                size="2",
                weight=rx.cond(es_actual, "bold", "medium"),
                color=rx.cond(es_actual, styles.TEXT_PRIMARY, styles.TEXT_TERTIARY),
                text_align="center",
            ),
            spacing="2",
            align="center",
        )

    def conector() -> rx.Component:
        """Linea conectora con estilo editorial."""
        return rx.box(
            width=["30px", "50px", "70px"],
            height="1px",
            margin_top="21px",
            background=styles.BORDER_DEFAULT,
            style={
                "transition": styles.GLOBAL_TRANSITION,
            },
        )

    return rx.hstack(
        indicador_paso(1, "Información Básica"),
        conector(),
        indicador_paso(2, "Roles"),
        conector(),
        indicador_paso(3, "Detalles"),
        justify="center",
        align="start",
        width="100%",
        padding="4",
        spacing="3",
    )
