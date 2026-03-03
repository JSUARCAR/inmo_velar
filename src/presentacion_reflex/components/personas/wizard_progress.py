import reflex as rx

from src.presentacion_reflex.state.personas_state import PersonasState
from src.presentacion_reflex import styles


def wizard_progress() -> rx.Component:
    """Premium progress indicator for multi-step wizard with Neumorphism sculpting."""

    def step_indicator(step_num: int, label: str) -> rx.Component:
        """Individual step circle with pneumatic depth."""
        is_current = PersonasState.modal_step == step_num
        is_completed = PersonasState.modal_step > step_num

        return rx.vstack(
            # Step circle sculpted
            rx.box(
                rx.cond(
                    is_completed,
                    rx.icon("check", size=20, color="var(--green-9)"),
                    rx.text(
                        str(step_num),
                        size="3",
                        weight="bold",
                        color=rx.cond(is_current, styles.ACCENT_COLOR, styles.TEXT_TERTIARY),
                    ),
                ),
                width="42px",
                height="42px",
                border_radius="full",
                display="flex",
                align_items="center",
                justify_content="center",
                style={
                    "background": styles.BG_PANEL,
                    "transition": "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
                    "box_shadow": rx.cond(
                        is_completed | is_current,
                        styles.NEU_INSET, # Completed/Current look "sculpted in"
                        styles.NEU_SHADOW, # Pending look "raised"
                    ),
                    "border": rx.cond(
                        is_current,
                        f"2px solid {styles.ACCENT_COLOR}",
                        "none"
                    ),
                },
            ),
            # Step label
            rx.text(
                label,
                size="2",
                weight=rx.cond(is_current, "bold", "medium"),
                color=rx.cond(is_current, styles.TEXT_PRIMARY, styles.TEXT_TERTIARY),
                text_align="center",
            ),
            spacing="2",
            align="center",
        )

    return rx.hstack(
        step_indicator(1, "Información Básica"),
        # Connector line with depth
        rx.box(
            width=["30px", "50px", "70px"],
            height="6px",
            margin_top="19px",
            border_radius="full",
            style={
                "background": styles.BG_PANEL,
                "box_shadow": rx.cond(
                    PersonasState.modal_step > 1,
                    "inset 1px 1px 2px rgba(0,0,0,0.1), inset -1px -1px 2px rgba(255,255,255,0.5)",
                    styles.NEU_INSET,
                ),
                "transition": styles.GLOBAL_TRANSITION,
            },
        ),
        step_indicator(2, "Roles"),
        # Connector line 2-3
        rx.box(
            width=["30px", "50px", "70px"],
            height="6px",
            margin_top="19px",
            border_radius="full",
            style={
                "background": styles.BG_PANEL,
                "box_shadow": rx.cond(
                    PersonasState.modal_step > 2,
                    "inset 1px 1px 2px rgba(0,0,0,0.1), inset -1px -1px 2px rgba(255,255,255,0.5)",
                    styles.NEU_INSET,
                ),
                "transition": styles.GLOBAL_TRANSITION,
            },
        ),
        step_indicator(3, "Detalles"),
        justify="center",
        align="start",
        width="100%",
        padding="4",
        spacing="3",
    )
