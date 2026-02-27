import reflex as rx

from src.presentacion_reflex.state.auth_state import AuthState
from src.presentacion_reflex.state.personas_state import PersonasState


def person_card(persona: dict) -> rx.Component:
    """Elite card component for persona display in cards view."""

    # Get initials for avatar
    initials = persona["nombre"][:2]

    from src.presentacion_reflex import styles

    return rx.card(
        rx.vstack(
            # Avatar section with gradient background
            rx.hstack(
                rx.avatar(
                    fallback=initials,
                    size="4",
                    radius="full",
                    color_scheme="gray",
                ),
                rx.vstack(
                    rx.text(
                        persona["nombre"],
                        size="3",
                        weight="bold",
                        color="var(--gray-12)",
                    ),
                    rx.text(
                        persona["documento"],
                        size="1",
                        color="var(--gray-10)",
                    ),
                    spacing="0",
                    align="start",
                ),
                spacing="3",
                width="100%",
                align="center",
            ),
            # Contact info
            rx.vstack(
                rx.hstack(
                    rx.icon("mail", size=14, color="var(--gray-9)"),
                    rx.text(
                        rx.cond(persona["correo"] != "", persona["correo"], "No especificado"),
                        size="1",
                        color="var(--gray-11)",
                    ),
                    spacing="2",
                    width="100%",
                ),
                rx.hstack(
                    rx.icon("phone", size=14, color="var(--gray-9)"),
                    rx.text(
                        persona["contacto"],
                        size="1",
                        color="var(--gray-11)",
                    ),
                    spacing="2",
                    width="100%",
                ),
                spacing="2",
                width="100%",
                padding_y="2",
            ),
            # Roles badges
            rx.box(
                rx.foreach(
                    persona["roles"],
                    lambda r: rx.match(
                        r,
                        (
                            "Propietario",
                            rx.badge(rx.hstack(rx.icon("home", size=12), rx.text(r, size="1"), spacing="1", align="center"), color_scheme="blue", variant="soft", margin_right="1", margin_bottom="1", radius="full")
                        ),
                        (
                            "Arrendatario",
                            rx.badge(rx.hstack(rx.icon("user-check", size=12), rx.text(r, size="1"), spacing="1", align="center"), color_scheme="green", variant="soft", margin_right="1", margin_bottom="1", radius="full")
                        ),
                        (
                            "Asesor",
                            rx.badge(rx.hstack(rx.icon("briefcase", size=12), rx.text(r, size="1"), spacing="1", align="center"), color_scheme="purple", variant="soft", margin_right="1", margin_bottom="1", radius="full")
                        ),
                        (
                            "Codeudor",
                            rx.badge(rx.hstack(rx.icon("shield", size=12), rx.text(r, size="1"), spacing="1", align="center"), color_scheme="orange", variant="soft", margin_right="1", margin_bottom="1", radius="full")
                        ),
                        (
                            "Proveedor",
                            rx.badge(rx.hstack(rx.icon("wrench", size=12), rx.text(r, size="1"), spacing="1", align="center"), color_scheme="cyan", variant="soft", margin_right="1", margin_bottom="1", radius="full")
                        ),
                        rx.badge(rx.hstack(rx.icon("user", size=12), rx.text(r, size="1"), spacing="1", align="center"), color_scheme="gray", variant="soft", margin_right="1", margin_bottom="1", radius="full")
                    ),
                ),
                width="100%",
            ),
            rx.spacer(),
            # Footer: Status, Date & Actions
            rx.hstack(
                rx.cond(
                    persona["estado"] == "Activo",
                    rx.badge("Activo", color_scheme="green", variant="soft", radius="full"),
                    rx.badge("Inactivo", color_scheme="red", variant="soft", radius="full"),
                ),
                rx.spacer(),
                rx.hstack(
                    rx.text(
                        persona["fecha_creacion"],
                        size="1",
                        color="var(--gray-9)",
                        margin_right="2",
                    ),
                    rx.cond(
                        AuthState.check_action("Personas", "EDITAR"),
                        rx.tooltip(
                            rx.icon_button(
                                rx.icon("pencil", size=18),
                                on_click=lambda: PersonasState.open_edit_modal(persona),
                                variant="ghost",
                                size="2",
                                color_scheme="gray",
                                _hover={"background": "var(--gray-3)", "color": "var(--accent-9)"},
                            ),
                            content="Editar persona",
                        ),
                    ),
                    rx.cond(
                        AuthState.check_action("Personas", "ELIMINAR"),
                        rx.tooltip(
                            rx.icon_button(
                                rx.icon("trash-2", size=18),
                                # Pendiente: Implementar delete con confirmación
                                variant="ghost",
                                size="2",
                                color_scheme="red",
                                _hover={"background": "var(--red-3)", "color": "var(--red-9)"},
                            ),
                            content="Eliminar persona",
                        ),
                    ),
                    spacing="1",
                    align="center",
                ),
                width="100%",
                align="center",
                padding_top="1",
            ),
            spacing="3",
            width="100%",
            height="100%",
        ),
        # Card styling
        padding="4",
        width="99%",
        height="100%",
        margin="auto",
        bg=styles.BG_PANEL,
        # Hover effects
        _hover={
            "transform": "translateY(-4px)",
            "box_shadow": "0 12px 24px -10px rgba(0, 0, 0, 0.1)",
            "border_color": "var(--accent-8)",
            "cursor": "pointer",
        },
        transition="all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
        # Glassmorphism effect
        style={
            "border": "1px solid var(--gray-4)",
            "border_radius": "16px",
            "overflow": "hidden",
            "min_height": "200px",
        },
    )
