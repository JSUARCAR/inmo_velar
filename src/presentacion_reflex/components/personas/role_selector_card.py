import reflex as rx

from src.presentacion_reflex.state.personas_state import PersonasState
from src.presentacion_reflex import styles


def role_selector_card(rol: str) -> rx.Component:
    """Card interactiva y estilizada para la selección de roles con soporte para múltiples roles."""
    
    # Match color scheme based on role
    color_scheme = rx.match(
        rol,
        ("Propietario", "blue"),
        ("Arrendatario", "green"),
        ("Asesor", "purple"),
        ("Codeudor", "orange"),
        ("Proveedor", "cyan"),
        "gray",
    )

    # Match description
    description = rx.match(
        rol,
        ("Propietario", "Dueño de propiedades"),
        ("Arrendatario", "Inquilino de propiedades"),
        ("Asesor", "Asesor inmobiliario"),
        ("Codeudor", "Garante de contrato"),
        ("Proveedor", "Proveedor de servicios"),
        "",
    )

    is_selected = PersonasState.selected_roles.contains(rol)

    # Match icon
    icon_name = rx.match(
        rol,
        ("Propietario", "home"),
        ("Arrendatario", "user-check"),
        ("Asesor", "briefcase"),
        ("Codeudor", "shield"),
        ("Proveedor", "wrench"),
        "user",
    )

    return rx.card(
        rx.vstack(
            rx.hstack(
                # Icon con fondo dinámico basado en acento
                rx.box(
                    rx.icon(
                        icon_name,
                        size=24,
                        color=rx.cond(is_selected, "white", styles.ACCENT_COLOR),
                    ),
                    padding="12px",
                    border_radius="12px",
                    style={
                        "background": rx.cond(
                            is_selected,
                            styles.ACCENT_COLOR,
                            styles.ACCENT_BG_SOFT,
                        ),
                        "transition": styles.GLOBAL_TRANSITION,
                    },
                ),
                rx.spacer(),
                # Check indicator (solo visible si está seleccionado)
                rx.cond(
                    is_selected,
                    rx.box(
                        rx.icon("check", size=20, color=styles.ACCENT_COLOR),
                        padding="4px",
                        background=styles.BG_PANEL,
                        border_radius="full",
                        box_shadow=styles.NEU_SHADOW,
                    ),
                    rx.box(width="28px", height="28px"), # Placeholder para mantener alineación
                ),
                width="100%",
                align_items="center",
            ),
            rx.vstack(
                rx.text(
                    rol, 
                    weight="bold", 
                    size="4", 
                    color=rx.cond(is_selected, styles.ACCENT_COLOR, styles.TEXT_PRIMARY),
                ),
                rx.text(description, size="2", color=styles.TEXT_SECONDARY),
                spacing="1",
                align_items="start",
            ),
            width="100%",
            spacing="3",
        ),
        # Acción de selección
        on_click=lambda: PersonasState.toggle_rol(rol),
        cursor="pointer",
        variant="ghost",
        margin="0",
        padding="1.5rem",
        # Pneumatic Selection Style: Inset when selected, Raised when not
        style={
            "background": styles.BG_PANEL,
            "box_shadow": rx.cond(is_selected, styles.NEU_INSET, styles.NEU_SHADOW),
            "border": rx.cond(is_selected, f"1px solid {styles.ACCENT_COLOR}", "none"),
            "transition": "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
            "border_radius": "16px",
            "margin": "0",
        },
        _hover={
            "transform": rx.cond(is_selected, "none", "scale(1.02)"),
            "box_shadow": rx.cond(
                is_selected,
                styles.NEU_INSET,
                styles.NEU_MODAL_SHADOW,
            ),
        },
    )