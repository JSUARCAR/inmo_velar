import reflex as rx

from src.presentacion_reflex.state.auth_state import AuthState
from src.presentacion_reflex.state.personas_state import PersonasState


def person_card(persona: dict) -> rx.Component:
    """Elite card component for persona display in cards view."""

    # Get initials for avatar
    initials = persona["nombre"][:2]

    from src.presentacion_reflex import styles
    from src.presentacion_reflex.components.neuro_elements import neuro_badge, neuro_button

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
                        color=styles.TEXT_PRIMARY,
                    ),
                    rx.text(
                        persona["documento"],
                        size="1",
                        color=styles.TEXT_TERTIARY,
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
                    rx.icon("mail", size=14, color=styles.TEXT_TERTIARY),
                    rx.text(
                        rx.cond(persona["correo"] != "", persona["correo"], "No especificado"),
                        size="1",
                        color=styles.TEXT_SECONDARY,
                    ),
                    spacing="2",
                    width="100%",
                ),
                rx.hstack(
                    rx.icon("phone", size=14, color=styles.TEXT_TERTIARY),
                    rx.text(
                        persona["contacto"],
                        size="1",
                        color=styles.TEXT_SECONDARY,
                    ),
                    spacing="2",
                    width="100%",
                ),
                spacing="2",
                width="100%",
                padding_y="2",
            ),
            # Roles badges (neuro_badge neumórfico)
            rx.box(
                rx.foreach(
                    persona["roles"],
                    lambda r: neuro_badge(
                        rx.hstack(
                            rx.icon(
                                rx.match(
                                    r,
                                    ("Propietario", "home"),
                                    ("Arrendatario", "user-check"),
                                    ("Asesor", "briefcase"),
                                    ("Codeudor", "shield"),
                                    ("Proveedor", "wrench"),
                                    "user",
                                ),
                                size=12,
                            ),
                            rx.text(r, size="1"),
                            spacing="1",
                            align="center",
                        ),
                        color_scheme=rx.match(
                            r,
                            ("Propietario", "blue"),
                            ("Arrendatario", "green"),
                            ("Asesor", "violet"),
                            ("Codeudor", "orange"),
                            ("Proveedor", "cyan"),
                            "gray",
                        ),
                        style={"margin_right": "4px", "margin_bottom": "4px"},
                    ),
                ),
                width="100%",
            ),
            rx.spacer(),
            # Footer: Status, Date & Actions
            rx.hstack(
                rx.cond(
                    persona["estado"] == "Activo",
                    neuro_badge("Activo", color_scheme="green"),
                    neuro_badge("Inactivo", color_scheme="red"),
                ),
                rx.spacer(),
                rx.hstack(
                    rx.text(
                        persona["fecha_creacion"],
                        size="1",
                        color=styles.TEXT_TERTIARY,
                        margin_right="2",
                    ),
                    rx.tooltip(
                        neuro_button(
                            rx.icon("eye", size=16),
                            on_click=lambda: PersonasState.open_details_modal(persona),
                            size="1",
                            style={"min_width": "32px", "height": "32px", "padding": "0"},
                        ),
                        content="Ver detalles completos",
                    ),
                    rx.cond(
                        AuthState.check_action("Personas", "EDITAR"),
                        rx.tooltip(
                            neuro_button(
                                rx.icon("pencil", size=16),
                                on_click=lambda: PersonasState.open_edit_modal(persona),
                                size="1",
                                style={"min_width": "32px", "height": "32px", "padding": "0"},
                            ),
                            content="Editar persona",
                        ),
                    ),
                    rx.cond(
                        AuthState.check_action("Personas", "ELIMINAR"),
                        rx.tooltip(
                            neuro_button(
                                rx.icon("trash-2", size=16),
                                size="1",
                                style={
                                    "min_width": "32px", "height": "32px",
                                    "padding": "0", "color": "var(--red-9)",
                                },
                            ),
                            content="Eliminar persona",
                        ),
                    ),
                    spacing="3",
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
        # Card styling with Neumorphism
        width="100%",
        height="100%",
        margin="auto",
        variant="ghost",
        # Hover effects
        _hover={
            "transform": "translateY(-4px)",
            "box_shadow": styles.NEU_MODAL_SHADOW,
            "cursor": "pointer",
        },
        transition="all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
        style={
            **styles.NEU_PANEL_STYLE,
            "overflow": "hidden",
            "min_height": "220px",
        },
    )
