import reflex as rx

from src.presentacion_reflex.state.personas_state import PersonasState


def wizard_progress() -> rx.Component:
    """Premium progress indicator for multi-step wizard."""

    def step_indicator(step_num: int, label: str) -> rx.Component:
        """Individual step circle with label."""
        is_current = PersonasState.modal_step == step_num
        is_completed = PersonasState.modal_step > step_num

        return rx.vstack(
            # Step circle
            rx.box(
                rx.cond(
                    is_completed,
                    rx.icon("check", size=20, color="white"),
                    rx.text(
                        str(step_num),
                        size="3",
                        weight="bold",
                        color=rx.cond(is_current, "white", "var(--gray-9)"),
                    ),
                ),
                width="40px",
                height="40px",
                border_radius="50%",
                display="flex",
                align_items="center",
                justify_content="center",
                style={
                    "background": rx.cond(
                        is_completed,
                        "linear-gradient(135deg, #11998e 0%, #38ef7d 100%)",
                        rx.cond(
                            is_current,
                            "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                            "var(--gray-4)",
                        ),
                    ),
                    "transition": "all 0.3s ease",
                    "box_shadow": rx.cond(
                        is_current, "0 4px 12px rgba(102, 126, 234, 0.4)", "none"
                    ),
                },
            ),
            # Step label
            rx.text(
                label,
                size="2",
                weight=rx.cond(is_current, "medium", "regular"),
                color=rx.cond(is_current, "var(--gray-12)", "var(--gray-10)"),
                text_align="center",
            ),
            spacing="2",
            align="center",
        )

    return rx.hstack(
        step_indicator(1, "Información Básica"),
        # Connector line 1-2
        rx.box(
            width=["40px", "60px", "80px"],
            height="2px",
            style={
                "background": rx.cond(
                    PersonasState.modal_step > 1,
                    "linear-gradient(90deg, #11998e 0%, #38ef7d 100%)",
                    "var(--gray-4)",
                ),
                "transition": "background 0.3s ease",
            },
        ),
        step_indicator(2, "Roles"),
        # Connector line 2-3
        rx.box(
            width=["40px", "60px", "80px"],
            height="2px",
            style={
                "background": rx.cond(
                    PersonasState.modal_step > 2,
                    "linear-gradient(90deg, #11998e 0%, #38ef7d 100%)",
                    "var(--gray-4)",
                ),
                "transition": "background 0.3s ease",
            },
        ),
        step_indicator(3, "Detalles"),
        justify="center",
        align="center",
        width="100%",
        padding="4",
        spacing="3",
    )
