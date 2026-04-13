import reflex as rx

from src.presentacion_reflex.state.personas_state import PersonasState
from src.presentacion_reflex import styles

def tarjeta_selector_rol(rol: str) -> rx.Component:
    """Tarjeta interactiva y estilizada para la selección de roles con estetica Claude."""

    # Mapeo de descripción
    descripcion = rx.match(
        rol,
        ("Propietario", "Dueño de propiedades"),
        ("Arrendatario", "Inquilino de propiedades"),
        ("Asesor", "Asesor inmobiliario"),
        ("Codeudor", "Garante de contrato"),
        ("Proveedor", "Proveedor de servicios"),
        "",
    )

    esta_seleccionado = PersonasState.selected_roles.contains(rol)

    # Mapeo de icono
    nombre_icono = rx.match(
        rol,
        ("Propietario", "home"),
        ("Arrendatario", "user_check"),
        ("Asesor", "briefcase"),
        ("Codeudor", "shield"),
        ("Proveedor", "wrench"),
        "user",
    )

    return rx.card(
        rx.vstack(
            rx.hstack(
                # Icono con fondo dinámico basado en acento terracota
                rx.box(
                    rx.icon(
                        nombre_icono,
                        size=24,
                        color=rx.cond(esta_seleccionado, "white", styles.BRAND_PRIMARY),
                    ),
                    padding="12px",
                    border_radius="12px",
                    style={
                        "background": rx.cond(
                            esta_seleccionado,
                            styles.BRAND_PRIMARY,
                            styles.ACCENT_BG_SOFT,
                        ),
                        "transition": styles.GLOBAL_TRANSITION,
                    },
                ),
                rx.spacer(),
                # Indicador de verificación
                rx.cond(
                    esta_seleccionado,
                    rx.box(
                        rx.icon("check", size=20, color=styles.BRAND_PRIMARY),
                        padding="4px",
                        background="white",
                        border_radius="full",
                        box_shadow=styles.SHADOW_RING,
                    ),
                    rx.box(
                        width="28px", 
                        height="28px",
                        border=f"1px solid {styles.BORDER_DEFAULT}",
                        border_radius="full",
                    ),
                ),
                width="100%",
                align_items="center",
            ),
            rx.vstack(
                rx.text(
                    rol, 
                    weight="bold", 
                    size="4", 
                    color=rx.cond(esta_seleccionado, styles.BRAND_PRIMARY, styles.TEXT_PRIMARY),
                ),
                rx.text(descripcion, size="2", color=styles.TEXT_SECONDARY),
                spacing="1",
                align_items="start",
            ),
            width="100%",
            spacing="3",
        ),
        # Acción de selección
        on_click=lambda: PersonasState.toggle_rol(rol),
        cursor="pointer",
        variant="surface",
        margin="0",
        padding="x-large",
        # Estilo de seleccion Claude: Inset cuando esta seleccionado, Ring cuando no
        style={
            "background": rx.cond(esta_seleccionado, styles.BG_APP, styles.BG_PANEL),
            "box_shadow": rx.cond(esta_seleccionado, styles.SHADOW_INSET, styles.SHADOW_RING),
            "border": rx.cond(esta_seleccionado, f"1px solid {styles.BRAND_PRIMARY}", f"1px solid {styles.BORDER_DEFAULT}"),
            "transition": styles.GLOBAL_TRANSITION,
            "border_radius": "16px",
            "outline": "none",
        },
        _hover={
            "transform": rx.cond(esta_seleccionado, "none", "translateY(-4px)"),
            "box_shadow": rx.cond(
                esta_seleccionado,
                styles.SHADOW_INSET,
                styles.SHADOW_WHISPER,
            ),
            "border_color": styles.BRAND_PRIMARY,
        },
    )