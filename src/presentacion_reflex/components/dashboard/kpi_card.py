"""
Componente KPI Card para Dashboard - Reflex
Tarjeta reutilizable para mostrar indicadores clave de rendimiento.
"""

import reflex as rx


def kpi_card(
    titulo: str,
    valor: str,
    icono: str,
    color_icono: str = "var(--brand-primary)",
    subtitulo: str = "",
    es_critico: bool = False,
    variant: str = "standard",  # standard, elite, compact
    hover_content: rx.Component = None,
) -> rx.Component:
    """
    Tarjeta KPI reutilizable.
    """

    from src.presentacion_reflex import styles

    # Manejo de colores según criticidad usando paleta cálida
    text_color = "white" if es_critico else styles.TEXT_PRIMARY
    subtitle_color = "red.11" if es_critico else styles.TEXT_SECONDARY

    # Icon colors - use warm palette (Terracotta for brand identity)
    icon_bg = rx.cond(es_critico, styles.BRAND_PRIMARY, styles.BG_HOVER)
    icon_color = rx.cond(es_critico, "white", color_icono)

    # Estilo base de tarjeta Anthropic/Claude
    card_base_style = {
        "background": styles.BG_PANEL,
        "border": f"1px solid {styles.BORDER_DEFAULT}",
        "box_shadow": styles.SHADOW_RING,
        "border_radius": "16px",
        "transition": styles.GLOBAL_TRANSITION,
        "_hover": {
            "box_shadow": styles.SHADOW_WHISPER,
            "transform": "translateY(-4px)",
        },
        "margin": "0",
        "width": "100%",
    }

    if variant == "compact":
        card_component = rx.box(
            rx.hstack(
                rx.center(
                    rx.icon(icono, size=16, color=icon_color),
                    bg=icon_bg,
                    border_radius="8px",
                    padding="6px",
                ),
                rx.vstack(
                    rx.text(
                        titulo,
                        size="1",
                        weight="medium",
                        color=styles.TEXT_TERTIARY,
                        font_family=styles.FONT_SANS,
                    ),
                    rx.text(
                        valor,
                        size="3",
                        weight="bold",
                        color=text_color,
                        font_family=styles.FONT_SANS,
                    ),
                    spacing="0",
                    align="start",
                ),
                rx.spacer(),
                rx.cond(
                    subtitulo != "",
                    rx.text(
                        subtitulo, 
                        size="1", 
                        color=subtitle_color, 
                        font_family=styles.FONT_SANS,
                        white_space="nowrap"
                    ),
                ),
                width="100%",
                align="center",
                gap="3",
            ),
            style={**card_base_style, "padding": "0.75rem"},
        )

    elif variant == "elite":
        card_component = rx.box(
            rx.vstack(
                rx.hstack(
                    rx.vstack(
                        rx.text(
                            titulo,
                            size="1",
                            weight="bold",
                            color=styles.TEXT_TERTIARY,
                            text_transform="uppercase",
                            letter_spacing="0.05em",
                            font_family=styles.FONT_SANS,
                        ),
                        rx.text(
                            valor,
                            size="8",
                            weight="bold",
                            color=text_color,
                            letter_spacing="-0.03em",
                            line_height="1",
                            font_family=styles.FONT_SANS,
                        ),
                        spacing="1",
                        align="start",
                    ),
                    rx.spacer(),
                    rx.center(
                        rx.icon(icono, size=24, color=icon_color),
                        bg=icon_bg,
                        border_radius="12px",
                        padding="10px",
                    ),
                    width="100%",
                    align="start",
                ),
                rx.cond(
                    subtitulo != "",
                    rx.box(
                        rx.text(
                            subtitulo, 
                            size="1", 
                            weight="medium", 
                            color=subtitle_color,
                            font_family=styles.FONT_SANS,
                        ),
                        margin_top="8px",
                        padding_top="8px",
                        border_top=f"1px solid {styles.BORDER_DEFAULT}",
                        width="100%",
                    ),
                ),
                spacing="1",
                width="100%",
            ),
            style={**card_base_style, "padding": "1.5rem"},
        )

    else:
        card_component = rx.card(
            rx.vstack(
                rx.hstack(
                    rx.box(
                        rx.icon(icono, size=20, color=icon_color),
                        bg=icon_bg,
                        border_radius="8px",
                        padding="8px",
                        display="flex",
                        align_items="center",
                        justify_content="center",
                    ),
                    rx.hstack(
                        rx.text(
                            titulo,
                            size="2",
                            weight="medium",
                            color=styles.TEXT_TERTIARY,
                        ),
                        align="center",
                        spacing="1",
                    ),
                    width="100%",
                    align="center",
                    spacing="3",
                ),
                rx.text(
                    valor,
                    size="6",
                    weight="bold",
                    color=text_color,
                    letter_spacing="-0.02em",
                ),
                rx.cond(
                    subtitulo != "",
                    rx.text(
                        subtitulo, size="1", color=subtitle_color, margin_top="2px"
                    ),
                ),
                spacing="3",
                align="start",
                width="100%",
            ),
            size="2",
            variant="ghost",
            width="100%",
            transition="all 0.2s ease",
            _hover={
                "box_shadow": styles.NEU_MODAL_SHADOW,
            },
            style=styles.NEU_PANEL_STYLE,
        )

    if hover_content is not None:
        from src.presentacion_reflex.components.neuro_elements import neuro_tooltip

        return neuro_tooltip(content=hover_content, children=card_component)

    return card_component
