import reflex as rx

from src.presentacion_reflex.state.personas_state import PersonasState


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
                        color=rx.cond(is_selected, "white", "var(--accent-9)"),
                    ),
                    padding="12px",
                    border_radius="12px",
                    style={
                        "background": rx.cond(
                            is_selected,
                            "var(--accent-9)",
                            "var(--accent-3)",
                        ),
                        "transition": "all 0.3s ease",
                    },
                ),
                rx.spacer(),
                # Check indicator (solo visible si está seleccionado)
                rx.cond(
                    is_selected,
                    rx.box(
                        rx.icon("check", size=20, color="var(--accent-9)"),
                        padding="4px",
                        background="var(--accent-3)",
                        border_radius="full",
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
                    color=rx.cond(is_selected, "var(--accent-11)", "var(--gray-12)"),
                ),
                rx.text(description, size="2", color="var(--gray-10)"),
                spacing="1",
                align_items="start",
            ),
            width="100%",
            spacing="3",
        ),
        # Acción de selección (usamos una función lambda que envuelve el evento)
        on_click=lambda: PersonasState.toggle_rol(rol),
        cursor="pointer",
        # Aplicamos el color scheme directamente a la tarjeta para habilitar las variables nativas
        color_scheme=color_scheme,
        # Border highlighting when selected
        style={
            "border_width": rx.cond(is_selected, "2px", "1px"),
            "border_style": "solid",
            "border_color": rx.cond(is_selected, "var(--accent-8)", "var(--gray-6)"),
            "transition": "all 0.2s ease",
        },
        _hover={
            "transform": "scale(1.02)",
            "box_shadow": rx.cond(
                is_selected,
                "0 4px 12px var(--accent-4)",
                "0 2px 8px var(--gray-4)",
            ),
        },
    )