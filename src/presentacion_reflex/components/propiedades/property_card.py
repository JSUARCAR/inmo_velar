import reflex as rx

from src.presentacion_reflex import styles
from src.presentacion_reflex.state.auth_state import AuthState


def property_card(
    id_propiedad: int,
    matricula: str,
    direccion: str,
    tipo: str,
    municipio: str,
    disponibilidad: int,
    valor_canon: float,
    area_metros: float,
    habitaciones: int,
    banos: int,
    parqueadero: int,
    valor_venta: float,
    comision_venta: float,
    codigo_energia: str,
    codigo_agua: str,
    codigo_gas: str,
    imagen_id: int,
    estado_registro: int,
    valor_canon_view: str = "$0",
    valor_venta_view: str = "$0",
    comision_venta_valor_view: str = "$0",
    area_metros_view: str = "0m²",
    on_edit: callable = None,
    on_toggle_disponibilidad: callable = None,
    on_toggle_activa: callable = None,
) -> rx.Component:
    """
    Elite Property Card Component.
    Displays property details with high-end UI, glassmorphism, and interactive elements.
    """

    return rx.card(
        rx.vstack(
            # Header Area (Icon + Status)
            rx.hstack(
                rx.hover_card.root(
                    rx.hover_card.trigger(
                        rx.center(
                            rx.icon(
                                rx.match(
                                    tipo.to(str),
                                    ("Apartamento", "building"),
                                    ("Casa", "home"),
                                    ("Bodega", "warehouse"),
                                    ("Local", "store"),
                                    ("Lote", "map"),
                                    "home",
                                ),
                                size=24,
                                color="white",
                            ),
                            width="40px",
                            height="40px",
                            border_radius="12px",
                            background="linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                            box_shadow="0 4px 10px rgba(102, 126, 234, 0.3)",
                            cursor="pointer",
                        ),
                    ),
                    rx.hover_card.content(
                        rx.cond(
                            imagen_id,
                            rx.box(
                                rx.image(
                                    src="/api/storage/placeholder/download",
                                    width="100%",
                                    height="100%",
                                    border_radius="8px",
                                    object_fit="cover",
                                    alt="Vista previa propiedad",
                                ),
                                padding="4px",
                                width="288px",
                                height="208px",
                                border_radius="12px",
                                background=styles.BG_PANEL,
                                box_shadow=styles.NEU_INSET_LIGHT,
                            ),
                            rx.box(
                                rx.text("Sin imagen", size="1", color=styles.TEXT_TERTIARY),
                                padding="2",
                            ),
                        ),
                        side="top",
                        align="start",
                    ),
                ),
                rx.vstack(
                    rx.text(
                        tipo.to(str),
                        size="1",
                        weight="bold",
                        color=styles.ACCENT_COLOR,
                        text_transform="uppercase",
                        letter_spacing="0.5px",
                    ),
                    rx.text(
                        municipio.to(str),
                        size="1",
                        color=styles.TEXT_TERTIARY,
                    ),
                    spacing="0",
                    align="start",
                ),
                rx.spacer(),
                rx.cond(
                    disponibilidad,
                    rx.badge("Disponible", color_scheme="green", variant="soft", radius="full"),
                    rx.badge("Ocupada", color_scheme="gray", variant="soft", radius="full"),
                ),
                width="100%",
                align="center",
                spacing="3",
            ),
            rx.divider(margin_y="3", color=styles.BORDER_DEFAULT), # Aumentado de 2 a 3
            # Main Info
            rx.vstack(
                rx.text(
                    direccion.to(str),
                    size="3",
                    weight="bold",
                    color=styles.TEXT_PRIMARY,
                    no_of_lines=1,
                ),
                rx.text(
                    "Mat: ",
                    matricula,
                    size="1",
                    color=styles.TEXT_TERTIARY,
                ),
                spacing="2", # Aumentado de 1 a 2
                align="start",
                width="100%",
            ),
            # Stats Grid (Compact)
            rx.grid(
                rx.hstack(
                    rx.icon("scan", size=14, color=styles.TEXT_TERTIARY),
                    rx.text(area_metros_view, size="1", color=styles.TEXT_SECONDARY),
                    spacing="2", # Aumentado de 1 a 2
                    align="center",
                ),
                rx.cond(
                    habitaciones.to(int) > 0,
                    rx.hstack(
                        rx.icon("bed", size=14, color=styles.TEXT_TERTIARY),
                        rx.text(
                            habitaciones.to(str),
                            " Hab",
                            size="1",
                            color=styles.TEXT_SECONDARY,
                        ),
                        spacing="2", # Aumentado de 1 a 2
                        align="center",
                    ),
                    rx.fragment(),
                ),
                rx.cond(
                    banos.to(int) > 0,
                    rx.hstack(
                        rx.icon("bath", size=14, color=styles.TEXT_TERTIARY),
                        rx.text(
                            banos.to(str),
                            " Baños",
                            size="1",
                            color=styles.TEXT_SECONDARY,
                        ),
                        spacing="2", # Aumentado de 1 a 2
                        align="center",
                    ),
                    rx.fragment(),
                ),
                columns="3",
                gap="4", # Aumentado de 2 a 4 para más aire entre columnas
                width="100%",
                padding_y="3", # Aumentado de 2 a 3
            ),
            # Utility Codes (Compact Row)
            rx.cond(
                (codigo_energia.to(str) != "")
                | (codigo_agua.to(str) != "")
                | (codigo_gas.to(str) != ""),
                rx.hstack(
                    rx.cond(
                        codigo_energia.to(str) != "",
                        rx.tooltip(
                            rx.hstack(
                                rx.icon("zap", size=14, color="var(--yellow-9)"),
                                rx.text(codigo_energia, size="1", color=styles.TEXT_SECONDARY),
                                spacing="2", # Aumentado de 1 a 2
                                align="center",
                            ),
                            content="Energía",
                        ),
                    ),
                    rx.cond(
                        codigo_agua.to(str) != "",
                        rx.tooltip(
                            rx.hstack(
                                rx.icon("droplet", size=14, color="var(--blue-9)"),
                                rx.text(codigo_agua, size="1", color=styles.TEXT_SECONDARY),
                                spacing="2", # Aumentado de 1 a 2
                                align="center",
                            ),
                            content="Acueducto",
                        ),
                    ),
                    rx.cond(
                        codigo_gas.to(str) != "",
                        rx.tooltip(
                            rx.hstack(
                                rx.icon("flame", size=14, color="var(--orange-9)"),
                                rx.text(codigo_gas, size="1", color=styles.TEXT_SECONDARY),
                                spacing="2", # Aumentado de 1 a 2
                                align="center",
                            ),
                            content="Gas",
                        ),
                    ),
                    spacing="4", # Aumentado de 3 a 4
                    width="100%",
                    padding_y="2", # Aumentado de 1 a 2
                    justify="start",
                    border_top=f"1px solid {styles.BORDER_DEFAULT}",
                    margin_top="2", # Aumentado de 1 a 2
                ),
            ),
            # Footer: Price & Actions
            rx.hstack(
                rx.vstack(
                    rx.text("Canon", size="1", color=styles.TEXT_TERTIARY),
                    rx.text(
                        valor_canon_view,
                        size="4",
                        weight="bold",
                        color=styles.ACCENT_COLOR,
                        style={"font_variant_numeric": "tabular-nums"},
                    ),
                    spacing="0",
                ),
                rx.cond(
                    valor_venta.to(float) > 0,
                    rx.vstack(
                        rx.text("Venta / Comisión", size="1", color=styles.TEXT_TERTIARY),
                        rx.hstack(
                            rx.text(
                                valor_venta_view,
                                size="3",
                                weight="bold",
                                color="var(--green-9)",
                            ),
                            rx.text(
                                "(",
                                comision_venta_valor_view,
                                ")",
                                size="2",
                                color="var(--red-8)",
                            ),
                            spacing="2", # Aumentado de 1 a 2
                            align="baseline",
                        ),
                        spacing="0",
                    ),
                    rx.fragment(),
                ),
                rx.spacer(),
                rx.hstack(
                    rx.cond(
                        AuthState.check_action("Propiedades", "EDITAR"),
                        rx.hstack(
                            rx.tooltip(
                                rx.icon_button(
                                    rx.icon("refresh-ccw", size=16),
                                    on_click=lambda: on_toggle_disponibilidad(
                                        id_propiedad, rx.cond(disponibilidad == 1, 0, 1)
                                    ),
                                    variant="ghost",
                                    size="2",
                                    color_scheme="blue",
                                    _hover={
                                        "background": "var(--blue-3)",
                                        "color": "var(--blue-9)",
                                    },
                                ),
                                content="Cambiar Estado",
                            ),
                            rx.tooltip(
                                rx.icon_button(
                                    rx.icon("pencil", size=16),
                                    on_click=lambda: on_edit(id_propiedad),
                                    variant="ghost",
                                    size="2",
                                    color_scheme="gray",
                                    _hover={
                                        "background": "var(--gray-3)",
                                        "color": styles.ACCENT_COLOR,
                                    },
                                ),
                                content="Editar",
                            ),
                            rx.tooltip(
                                rx.cond(
                                    estado_registro,
                                    rx.icon_button(
                                        rx.icon("power-off", size=16),
                                        on_click=lambda: on_toggle_activa(id_propiedad, 1),
                                        variant="ghost",
                                        size="2",
                                        color_scheme="red",
                                        _hover={"background": "var(--red-3)", "color": "var(--red-9)"},
                                    ),
                                    rx.icon_button(
                                        rx.icon("power", size=16),
                                        on_click=lambda: on_toggle_activa(id_propiedad, 0),
                                        variant="ghost",
                                        size="3",
                                        color_scheme="green",
                                        _hover={"background": "var(--green-3)", "color": "var(--green-9)"},
                                    ),
                                ),
                                content=rx.cond(estado_registro, "Desactivar", "Activar"),
                            ),
                            spacing="3",
                        ),
                    ),
                    spacing="3",
                ),
                width="100%",
                align="center",
                margin_top="4", 
            ),
            spacing="5", 
            padding="6", 
            width="100%",
        ),
        # Elite Card Styling - Neumorphic Raised
        variant="ghost",
        width="100%",
        height="100%",
        margin="auto",
        style={
            **styles.NEU_PANEL_STYLE,
            "padding": "0",
            "transition": "all 0.4s cubic-bezier(0.2, 0.8, 0.2, 1)",
            "overflow": "hidden",
            "border": "none",
        },
        _hover={
            "transform": "translateY(-8px)",
            "box_shadow": styles.NEU_MODAL_SHADOW,
        },
    )
