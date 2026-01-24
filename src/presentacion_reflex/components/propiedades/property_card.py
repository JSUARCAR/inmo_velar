import reflex as rx
from src.presentacion_reflex.state.propiedades_state import PropiedadesState
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
    on_edit: callable,
    on_toggle_disponibilidad: callable,
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
                                    "home"
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
                            rx.image(
                                src="http://localhost:8000/api/storage/" + imagen_id.to(str) + "/download",
                                width="280px",
                                height="200px",
                                border_radius="8px",
                                object_fit="cover",
                                alt="Vista previa propiedad"
                            ),
                            rx.box(
                                rx.text("Sin imagen", size="1", color="var(--gray-11)"),
                                padding="2",
                            )
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
                        color="var(--accent-9)",
                        text_transform="uppercase",
                        letter_spacing="0.5px",
                    ),
                    rx.text(
                        municipio.to(str),
                        size="1",
                        color="var(--gray-10)",
                    ),
                    spacing="0",
                    align="start",
                ),
                rx.spacer(),
                rx.badge(
                    rx.cond(disponibilidad.to(int) == 1, "Disponible", "Ocupada"),
                    color_scheme=rx.cond(disponibilidad.to(int) == 1, "green", "gray"),
                    variant="soft",
                    radius="full",
                ),
                width="100%",
                align="center",
                spacing="3",
            ),
            
            rx.divider(margin_y="2", color="var(--gray-4)"),
            
            # Main Info
            rx.vstack(
                rx.text(
                    direccion.to(str),
                    size="3",
                    weight="bold",
                    color="var(--gray-12)",
                    no_of_lines=1,
                ),
                rx.text(
                    f"Mat: {matricula}",
                    size="1",
                    color="var(--gray-10)",
                ),
                spacing="1",
                align="start",
                width="100%",
            ),

            # Stats Grid (Compact)
            rx.grid(
                rx.hstack(
                    rx.icon("scan", size=14, color="var(--gray-9)"),
                    rx.text(f"{area_metros.to(float):.0f}m²", size="1", color="var(--gray-11)"),
                    spacing="1", align="center",
                ),
                rx.cond(
                    habitaciones.to(int) > 0,
                    rx.hstack(
                        rx.icon("bed", size=14, color="var(--gray-9)"),
                        rx.text(f"{habitaciones.to(int)} Hab", size="1", color="var(--gray-11)"),
                        spacing="1", align="center",
                    ),
                    rx.fragment(),
                ),
                rx.cond(
                    banos.to(int) > 0,
                    rx.hstack(
                        rx.icon("bath", size=14, color="var(--gray-9)"),
                        rx.text(f"{banos.to(int)} Baños", size="1", color="var(--gray-11)"),
                        spacing="1", align="center",
                    ),
                    rx.fragment(),
                ),
                columns="3",
                gap="2",
                width="100%",
                padding_y="2",
            ),
            
            # Utility Codes (Compact Row)
            rx.cond(
                (codigo_energia.to(str) != "") | (codigo_agua.to(str) != "") | (codigo_gas.to(str) != ""),
                rx.hstack(
                    rx.cond(
                        codigo_energia.to(str) != "",
                        rx.tooltip(
                            rx.hstack(
                                rx.icon("zap", size=14, color="var(--yellow-9)"),
                                rx.text(codigo_energia, size="1", color="var(--gray-11)"),
                                spacing="1", align="center",
                            ),
                            content="Energía"
                        ),
                    ),
                    rx.cond(
                        codigo_agua.to(str) != "",
                        rx.tooltip(
                            rx.hstack(
                                rx.icon("droplet", size=14, color="var(--blue-9)"),
                                rx.text(codigo_agua, size="1", color="var(--gray-11)"),
                                spacing="1", align="center",
                            ),
                            content="Acueducto"
                        ),
                    ),
                    rx.cond(
                        codigo_gas.to(str) != "",
                        rx.tooltip(
                            rx.hstack(
                                rx.icon("flame", size=14, color="var(--orange-9)"),
                                rx.text(codigo_gas, size="1", color="var(--gray-11)"),
                                spacing="1", align="center",
                            ),
                            content="Gas"
                        ),
                    ),
                    spacing="3",
                    width="100%",
                    padding_y="1",
                    justify="start",
                    border_top="1px solid var(--gray-3)",
                    margin_top="1",
                ),
            ),
            
            # Footer: Price & Actions
            rx.hstack(
                rx.vstack(
                    rx.text("Canon", size="1", color="var(--gray-9)"),
                    rx.text(
                        f"${valor_canon.to(float):,.0f}",
                        size="4",
                        weight="bold",
                        color="var(--accent-9)",
                        style={"font_variant_numeric": "tabular-nums"},
                    ),
                    spacing="0",
                ),
                rx.cond(
                    valor_venta.to(float) > 0,
                    rx.vstack(
                        rx.text("Venta / Comisión", size="1", color="var(--gray-9)"),
                        rx.hstack(
                             rx.text(
                                f"${valor_venta.to(float):,.0f}",
                                size="3",
                                weight="bold",
                                color="var(--green-9)",
                            ),
                             rx.text(
                                f"(${valor_venta.to(float) * comision_venta.to(float) / 100:,.0f})",
                                size="2",
                                color="var(--red-8)",
                            ),
                            spacing="1",
                            align="baseline",
                        ),
                        spacing="0",
                    ),
                    rx.fragment()
                ),
                rx.spacer(),
                rx.hstack(
                    rx.cond(
                        AuthState.check_action("Propiedades", "EDITAR"),
                        rx.hstack(
                             rx.tooltip(
                                rx.icon_button(
                                    rx.icon("refresh-ccw", size=16),
                                    on_click=lambda: on_toggle_disponibilidad(id_propiedad, rx.cond(disponibilidad == 1, 0, 1)),
                                    variant="ghost",
                                    size="2",
                                    color_scheme="blue",
                                    _hover={"background": "var(--blue-3)", "color": "var(--blue-9)"},
                                ),
                                content="Cambiar Estado"
                            ),
                            rx.tooltip(
                                rx.icon_button(
                                    rx.icon("pencil", size=16),
                                    on_click=lambda: on_edit(id_propiedad),
                                    variant="ghost",
                                    size="2",
                                    color_scheme="gray",
                                    _hover={"background": "var(--gray-3)", "color": "var(--accent-9)"},
                                ),
                                content="Editar"
                            ),
                            spacing="1",
                        )
                    ),

                    spacing="1",
                ),
                width="100%",
                align="center",
                margin_top="1",
            ),
            
            spacing="3",
            padding="4",
            width="100%",
        ),
        
        # Elite Card Styling - White & Clean
        variant="ghost",
        width="99%",
        height="98%",
        margin="auto",
        style={
            "background": "var(--color-panel-solid)",
            "border": "1px solid var(--gray-4)",
            "border_radius": "16px",
            "transition": "all 0.3s cubic-bezier(0.4, 0, 0.2, 1)",
            "overflow": "hidden",
        },
        _hover={
            "transform": "translateY(-4px)",
            "box_shadow": "0 12px 24px -10px rgba(0, 0, 0, 0.1)",
            "border_color": "var(--accent-8)",
        }
    )
