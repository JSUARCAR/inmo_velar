"""
Componente KPI Card para Dashboard - Reflex
Tarjeta reutilizable para mostrar indicadores clave de rendimiento.
"""

import reflex as rx


def kpi_card(
    titulo: str,
    valor: str,
    icono: str,
    color_icono: str = "blue",
    subtitulo: str = "",
    es_critico: bool = False,
    variant: str = "standard",  # standard, elite, compact
    hover_content: rx.Component = None,
) -> rx.Component:
    """
    Tarjeta KPI reutilizable.

    Args:
        titulo: Título del KPI (ej: "Cartera en Mora")
        valor: Valor principal a mostrar (ej: "$1,500,000")
        icono: Nombre del icono de Lucide (ej: "circle-alert")
        color_icono: Color del icono (blue, green, red, amber, etc.)
        subtitulo: Texto descriptivo adicional
        es_critico: Si es True, muestra fondo rojo de alerta
        variant: Variante de visualización ("standard", "elite", "compact")
        hover_content: Contenido opcional para mostrar en hover card

    Returns:
        rx.Component: Card con el KPI formateado
    """

    # Manejo de colores según criticidad
    from src.presentacion_reflex import styles

    # Manejo de colores según criticidad
    bg_color = "red.9" if es_critico else styles.BG_PANEL  # Semantic background
    if variant == "elite":
        # Gradientes sutiles para elite (removed hardcoded light gradient)
        bg_color = styles.BG_PANEL

    text_color = "white" if es_critico else styles.TEXT_PRIMARY
    subtitle_color = "red.11" if es_critico else styles.TEXT_SECONDARY

    # Ajuste de colores de icono
    icon_bg = "red.10" if es_critico else f"{color_icono}.3"
    icon_color = "white" if es_critico else f"{color_icono}.9"

    # --- RENDERIZADO SEGÚN VARIANTE ---

    card_component = None

    # 1. COMPACT (Para listados laterales)
    if variant == "compact":
        card_component = rx.card(
            rx.hstack(
                # Icono más pequeño
                rx.box(
                    rx.icon(icono, size=16, color=icon_color),
                    bg=icon_bg,
                    border_radius="6px",
                    padding="6px",
                    display="flex",
                    align_items="center",
                    justify_content="center",
                ),
                rx.vstack(
                    rx.text(
                        titulo,
                        size="1",
                        font_size=["10px", "10px", "12px"],
                        weight="medium",
                        color="gray.10",
                    ),
                    rx.text(
                        valor, size="3", font_size=["14px", "16px"], weight="bold", color=text_color
                    ),
                    spacing="0",
                    align="start",
                ),
                # Subtítulo alineado a la derecha o debajo si es necesario
                rx.spacer(),
                rx.cond(
                    subtitulo != "",
                    rx.text(subtitulo, size="1", color=subtitle_color, white_space="nowrap"),
                ),
                width="100%",
                align="center",
            ),
            size="1",  # Card size 1 is smaller
            bg=bg_color,
            width="100%",
            style={"box_shadow": "0 1px 3px rgba(0,0,0,0.05)"},
        )

    # 2. ELITE (Más prominente, para cabecera)
    elif variant == "elite":
        card_component = rx.card(
            rx.vstack(
                rx.hstack(
                    rx.vstack(
                        rx.text(
                            titulo,
                            size="1",
                            weight="bold",
                            color="gray.9",
                            text_transform="uppercase",
                            letter_spacing="0.05em",
                            max_width="100%",  # Prevent overflow
                            white_space="normal",  # Allow wrapping
                        ),
                        rx.text(
                            valor,
                            size="8",
                            font_size=rx.breakpoints(
                                initial="1.5em", sm="2em", lg="2.5em", xl="3em"
                            ),
                            weight="bold",
                            color=text_color,
                            letter_spacing="-0.03em",
                            line_height="1",
                            white_space="nowrap",  # Keep number on one line if possible
                            overflow="hidden",  # Truncate if too long (better than breaking layout)
                            text_overflow="ellipsis",
                        ),
                        spacing="1",
                        align="start",
                        width="100%",
                        overflow="hidden",
                    ),
                    rx.spacer(),
                    rx.box(
                        rx.icon(icono, size=24, color=icon_color),
                        bg=icon_bg,
                        border_radius="12px",
                        padding="8px",
                        display=rx.breakpoints(initial="none", sm="flex"),  # Hide icon on very small screens if needed
                        align_items="center",
                        justify_content="center",
                    ),
                    width="100%",
                    align="start",
                ),
                rx.cond(
                    subtitulo != "",
                    rx.box(
                        rx.text(subtitulo, size="1", weight="medium", color=subtitle_color),
                        margin_top="8px",
                        padding_top="8px",
                        border_top="1px solid var(--gray-4)",
                        width="100%",
                    ),
                ),
                spacing="1",
                width="100%",
            ),
            size="3",
            bg=bg_color,
            width="100%",
            style={
                "box_shadow": "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)",
                "border": "1px solid rgba(0,0,0,0.03)",
            },
        )

    # 3. STANDARD (Diseño limpio por defecto)
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
                    rx.text(titulo, size="2", weight="medium", color="gray.10"),
                    width="100%",
                    align="center",
                    spacing="3",
                ),
                rx.text(
                    valor,
                    size="6",
                    font_size=["1.25em", "1.5em"],
                    weight="bold",
                    color=text_color,
                    letter_spacing="-0.02em",
                ),
                rx.cond(
                    subtitulo != "",
                    rx.text(subtitulo, size="1", color=subtitle_color, margin_top="2px"),
                ),
                spacing="3",
                align="start",
                width="100%",
            ),
            size="2",
            bg=bg_color,
            width="100%",
            style={
                "box_shadow": "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
                "border": "1px solid rgba(0,0,0,0.03)",
            },
        )

    # Si hay contenido hover, envolver en HoverCard
    if hover_content is not None:
        return rx.hover_card.root(
            rx.hover_card.trigger(card_component),
            rx.hover_card.content(
                hover_content,
                side="top",
                align="center",
                side_offset=5,
                background_color=styles.BG_PANEL,
                border="1px solid var(--gray-4)",
                box_shadow="0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)",
                border_radius="12px",
                padding="16px",
                max_width="300px",
            ),
        )

    return card_component
