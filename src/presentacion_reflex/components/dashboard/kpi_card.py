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
    """

    from src.presentacion_reflex import styles

    # Manejo de colores según criticidad
    bg_color = "red.9" if es_critico else styles.BG_PANEL  # Semantic background
    if variant == "elite":
        bg_color = styles.BG_PANEL

    text_color = "white" if es_critico else styles.TEXT_PRIMARY
    subtitle_color = "red.11" if es_critico else styles.TEXT_SECONDARY

    # Ajuste de colores de icono (Soporte para Var/cond)
    icon_bg = rx.cond(
        es_critico,
        "red.10",
        rx.cond(
            rx.Var.create(color_icono).to(str) == "green",
            "var(--green-3)",
            rx.cond(
                rx.Var.create(color_icono).to(str) == "blue",
                "var(--blue-3)",
                rx.cond(
                    rx.Var.create(color_icono).to(str) == "red",
                    "var(--red-3)",
                    rx.cond(
                        rx.Var.create(color_icono).to(str) == "amber",
                        "var(--amber-3)",
                        "var(--indigo-3)"
                    )
                )
            )
        )
    )
    
    icon_color = rx.cond(
        es_critico,
        "white",
        rx.cond(
            rx.Var.create(color_icono).to(str) == "green",
            "var(--green-9)",
            rx.cond(
                rx.Var.create(color_icono).to(str) == "blue",
                "var(--blue-9)",
                rx.cond(
                    rx.Var.create(color_icono).to(str) == "red",
                    "var(--red-9)",
                    rx.cond(
                        rx.Var.create(color_icono).to(str) == "amber",
                        "var(--amber-9)",
                        "var(--indigo-9)"
                    )
                )
            )
        )
    )

    card_component = None

    if variant == "compact":
        card_component = rx.card(
            rx.hstack(
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
                    rx.hstack(
                        rx.text(
                            titulo,
                            size="1",
                            font_size=["10px", "10px", "12px"],
                            weight="medium",
                            color="gray.10",
                        ),
                        align="center",
                        spacing="1",
                    ),
                    rx.text(
                        valor, size="3", font_size=["14px", "16px"], weight="bold", color=text_color
                    ),
                    spacing="0",
                    align="start",
                ),
                rx.spacer(),
                rx.cond(
                    subtitulo != "",
                    rx.text(subtitulo, size="1", color=subtitle_color, white_space="nowrap"),
                ),
                width="100%",
                align="center",
            ),
            size="1",
            bg=bg_color,
            width="100%",
            style={"box_shadow": "0 1px 3px rgba(0,0,0,0.05)"},
            color_scheme=color_icono,
        )

    elif variant == "elite":
        card_component = rx.card(
            rx.vstack(
                rx.hstack(
                    rx.vstack(
                        rx.hstack(
                            rx.text(
                                titulo,
                                size="1",
                                weight="bold",
                                color="gray.9",
                                text_transform="uppercase",
                                letter_spacing="0.05em",
                                max_width="100%",
                                white_space="normal",
                            ),
                            align="center",
                            spacing="1",
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
                            white_space="nowrap",
                            overflow="hidden",
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
                        display=rx.breakpoints(initial="none", sm="flex"),
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
            transition="all 0.3s ease",
            _hover={
                "transform": "translateY(-4px)",
                "box_shadow": "0 20px 25px -5px var(--accent-4), 0 8px 10px -6px var(--accent-3)",
                "border_color": "var(--accent-6)",
            },
            style={
                "box_shadow": "0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.03)",
                "border": "1px solid var(--gray-4)",
                "border_top_width": "3px",
                "border_top_style": "solid",
                "border_top_color": "var(--accent-9)",
                "border_radius": "16px",
            },
            color_scheme=color_icono,
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
                        rx.text(titulo, size="2", weight="medium", color="gray.10"),
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
            transition="all 0.2s ease",
            _hover={
                "box_shadow": "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)",
                "border_color": "var(--gray-6)",
            },
            style={
                "box_shadow": "0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03)",
                "border": "1px solid var(--gray-4)",
                "border_radius": "12px",
            },
            color_scheme=color_icono,
        )

    return card_component
