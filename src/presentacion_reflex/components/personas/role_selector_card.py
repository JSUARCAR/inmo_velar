import reflex as rx

from src.presentacion_reflex.state.personas_state import PersonasState


def role_selector_card(rol: str) -> rx.Component:
    """Interactive card for role selection in wizard."""

    # Role metadata
    role_config = {
        "Propietario": {"icon": "home", "color": "blue", "description": "Dueño de propiedades"},
        "Arrendatario": {
            "icon": "user-check",
            "color": "green",
            "description": "Inquilino de propiedades",
        },
        "Asesor": {"icon": "briefcase", "color": "purple", "description": "Asesor inmobiliario"},
        "Codeudor": {"icon": "shield", "color": "orange", "description": "Garante de contrato"},
        "Proveedor": {"icon": "wrench", "color": "cyan", "description": "Proveedor de servicios"},
    }

    config = role_config.get(rol, {"icon": "user", "color": "gray", "description": ""})
    is_selected = PersonasState.selected_roles.contains(rol)

    return rx.card(
        rx.vstack(
            rx.hstack(
                # Icon
                rx.box(
                    rx.icon(
                        config["icon"],
                        size=24,
                        color=rx.cond(is_selected, "white", f"var(--{config['color']}-9)"),
                    ),
                    width="48px",
                    height="48px",
                    border_radius="50%",
                    display="flex",
                    align_items="center",
                    justify_content="center",
                    style={
                        "background": rx.cond(
                            is_selected,
                            f"var(--{config['color']}-9)",
                            f"var(--{config['color']}-3)",
                        ),
                        "transition": "all 0.3s ease",
                    },
                ),
                rx.spacer(),
                # Check icon when selected
                rx.cond(
                    is_selected,
                    rx.icon("circle-check", size=20, color=f"var(--{config['color']}-9)"),
                    rx.box(
                        width="20px",
                        height="20px",
                        border_radius="50%",
                        border="2px solid var(--gray-6)",
                    ),
                ),
                width="100%",
                align="center",
            ),
            rx.vstack(
                rx.text(
                    rol,
                    size="4",
                    weight="bold",
                    color="var(--gray-12)",
                ),
                rx.text(
                    config["description"],
                    size="2",
                    color="var(--gray-10)",
                ),
                spacing="1",
                align="start",
                width="100%",
            ),
            spacing="3",
            width="100%",
        ),
        # Card  styling
        padding="4",
        width="100%",
        on_click=lambda: PersonasState.toggle_rol(rol, ~is_selected),
        cursor="pointer",
        # Border highlighting when selected
        style={
            "border": rx.cond(
                is_selected, f"2px solid var(--{config['color']}-8)", "1px solid var(--gray-6)"
            ),
            "transition": "all 0.2s ease",
        },
        _hover={
            "transform": "scale(1.02)",
            "box_shadow": rx.cond(
                is_selected, f"0 4px 12px var(--{config['color']}-4)", "0 2px 8px var(--gray-4)"
            ),
        },
    )
