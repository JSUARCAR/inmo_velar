import reflex as rx
from src.presentacion_reflex.state.personas_state import PersonasState
from src.presentacion_reflex.state.auth_state import AuthState

def person_card(persona: dict) -> rx.Component:
    """Elite card component for persona display in cards view."""
    
    # Get initials for avatar
    initials = persona["nombre"][:2]
    
    return rx.card(
        rx.vstack(
            # Avatar section with gradient background
            rx.hstack(
                rx.avatar(
                    fallback=initials,
                    size="4",
                    radius="full",
                    color_scheme=rx.cond(
                        persona["roles"].length() > 0,
                        rx.match(
                            persona["roles"][0],
                            ("Propietario", "blue"),
                            ("Arrendatario", "green"),
                            ("Asesor", "purple"),
                            ("Codeudor", "orange"),
                            ("Proveedor", "cyan"),
                            "gray"
                        ),
                        "gray"
                    ),
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
                        rx.cond(
                            persona["correo"] != "",
                            persona["correo"],
                            "No especificado"
                        ),
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
                    lambda r: rx.badge(
                        rx.hstack(
                            rx.icon(
                                rx.match(
                                    r,
                                    ("Propietario", "home"),
                                    ("Arrendatario", "user-check"),
                                    ("Asesor", "briefcase"),
                                    ("Codeudor", "shield"),
                                    ("Proveedor", "tool"),
                                    "user"
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
                            ("Asesor", "purple"),
                            ("Codeudor", "orange"),
                            ("Proveedor", "cyan"),
                            "gray"
                        ),
                        variant="soft",
                        margin_right="1",
                        margin_bottom="1",
                        radius="full",
                    )
                ),
                width="100%",
            ),
            
            rx.spacer(),

            # Footer: Status, Date & Actions
            rx.hstack(
                rx.badge(
                    persona["estado"],
                    color_scheme=rx.cond(persona["estado"] == "Activo", "green", "red"),
                    variant="soft",
                    radius="full",
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
                            content="Editar persona"
                        )
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
                            content="Eliminar persona"
                        )
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
        height="98",
        margin="auto",
        variant="ghost",
        
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
            "background": "var(--color-panel-solid)",
            "border": "1px solid var(--gray-4)",
            "border_radius": "16px",
            "overflow": "hidden",
            "min_height": "200px",
        }
    )
