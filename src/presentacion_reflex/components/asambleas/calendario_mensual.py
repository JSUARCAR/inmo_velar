"""
Componente de Calendario Mensual para Asambleas.
Diseño Neumorphic Executive - Producción Elite.
"""

import reflex as rx
from typing import List, Dict

from src.presentacion_reflex import styles
from src.presentacion_reflex.components.neuro_elements import neuro_icon_action_button
from src.presentacion_reflex.state.propiedad_horizontal_models import (
    AsistenciaCalendarioModel,
)


def _obtener_días_mes(año: int, mes: int) -> List[int]:
    """Retorna los días del mes."""
    if mes == 12:
        siguiente_mes = 1
        siguiente_año = año + 1
    else:
        siguiente_mes = mes + 1
        siguiente_año = año

    from calendar import monthrange

    _, último_día = monthrange(año, mes)
    return list(range(1, último_día + 1))


def _obtener_nombre_mes(mes: int) -> str:
    """Retorna el nombre del mes."""
    meses = [
        "Enero",
        "Febrero",
        "Marzo",
        "Abril",
        "Mayo",
        "Junio",
        "Julio",
        "Agosto",
        "Septiembre",
        "Octubre",
        "Noviembre",
        "Diciembre",
    ]
    return meses[mes - 1]


def neuro_calendario_header(
    año: int,
    mes: int,
    on_mes_anterior: rx.EventHandler,
    on_mes_siguiente: rx.EventHandler,
) -> rx.Component:
    """Header de navegación del calendario."""
    return rx.hstack(
        neuro_icon_action_button(
            "chevron-left",
            color_scheme="gray",
            size="2",
            tooltip_content="Mes anterior",
            on_click=on_mes_anterior,
        ),
        rx.heading(
            f"{_obtener_nombre_mes(mes)} {año}",
            size="3",
            font_weight="600",
            color=styles.TEXT_PRIMARY,
        ),
        neuro_icon_action_button(
            "chevron-right",
            color_scheme="gray",
            size="2",
            tooltip_content="Mes siguiente",
            on_click=on_mes_siguiente,
        ),
        justify="between",
        width="100%",
        padding="1rem",
    )


def _render_día(
    día: int,
    eventos: List[AsistenciaCalendarioModel],
    es_hoy: bool,
    es_mes_actual: bool,
    on_click,
) -> rx.Component:
    """Renderiza una celda de día."""
    if not eventos:
        return rx.box(
            rx.text(
                str(día),
                font_size="0.875rem",
                color=styles.TEXT_SECONDARY if es_mes_actual else "var(--gray-5)",
            ),
            width="100%",
            height="100%",
            display="flex",
            align_items="center",
            justify_content="center",
            padding="0.25rem",
        )

    primer_evento = eventos[0]
    más_eventos = len(eventos) > 1

    indicadores = rx.hstack(
        rx.box(
            style={
                "width": "6px",
                "height": "6px",
                "border_radius": "50%",
                "background": f"var(--{primer_evento.color_estado}-9)",
            }
        ),
        gap="2px",
    )

    contenido = rx.vstack(
        rx.text(
            str(día),
            font_size="0.875rem",
            font_weight="600" if es_hoy else "400",
            color=styles.TEXT_PRIMARY,
        ),
        indicadores,
        gap="2px",
        align="center",
    )

    if es_hoy:
        contenido = rx.box(
            contenido,
            style={
                "background": f"var(--{primer_evento.color_estado}-3)",
                "border_radius": "8px",
                "border": f"2px solid var(--{primer_evento.color_estado}-6)",
            },
            padding="0.25rem",
        )

    return rx.box(
        rx.cond(
            más_eventos,
            rx.box(
                contenido,
                rx.text(
                    f"+{len(eventos) - 1}",
                    font_size="0.625rem",
                    color=styles.TEXT_SECONDARY,
                ),
                align="center",
            ),
            contenido,
        ),
        on_click=on_click,
        cursor="pointer",
        _hover={
            "background": f"var(--{primer_evento.color_estado}-2)",
            "transform": "scale(1.02)",
        },
        transition="all 150ms ease",
        width="100%",
        height="100%",
        display="flex",
        flex_direction="column",
        align_items="center",
        justify_content="center",
        padding="0.25rem",
    )


def neuro_calendario_grid(
    año: int,
    mes: int,
    eventos_por_día: Dict[int, List[AsistenciaCalendarioModel]],
    on_día_click: rx.EventHandler,
) -> rx.Component:
    """Grid de días del mes."""
    from datetime import date
    from calendar import monthrange

    días = _obtener_días_mes(año, mes)
    primer_día_semana, _ = monthrange(año, mes)

    espacios_previos = primer_día_semana
    espacios_post = (7 - (espacios_previos + len(días) % 7)) % 7

    días_render = [0] * espacios_previos + días + [0] * espacios_post

    celdas = []
    hoy = date.today()

    for i, día in enumerate(días_render):
        if día == 0:
            celdas.append(rx.box())
        else:
            eventos = eventos_por_día.get(día, [])
            es_hoy = año == hoy.year and mes == hoy.month and día == hoy.day
            eventos_model = [
                AsistenciaCalendarioModel(
                    id_asistencia=e.id_asistencia or 0,
                    id_propiedad=e.id_propiedad,
                    fecha_asistencia=e.fecha_asistencia,
                    hora_asistencia=e.hora_asistencia,
                    tipo_reunion=e.tipo_reunion,
                    tipo_asistente=e.tipo_asistente,
                    nombre_asistente=e.nombre_asistente,
                    costo_asistente=e.costo_asistente,
                    direccion_asistencia=e.direccion_asistencia,
                    estado_asistencia=e.estado_asistencia,
                    color_tipo=e.color_tipo,
                )
                for e in eventos
            ]

            celdas.append(
                _render_día(
                    día,
                    eventos_model,
                    es_hoy,
                    True,
                    lambda d=día: on_día_click(d),
                )
            )

    días_semana = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"]
    headers = [
        rx.box(
            rx.text(
                d, font_size="0.75rem", font_weight="600", color=styles.TEXT_SECONDARY
            ),
            width="100%",
            text_align="center",
            padding="0.5rem",
        )
        for d in días_semana
    ]

    return rx.box(
        rx.grid(
            *headers,
            *celdas,
            template_columns="repeat(7, 1fr)",
            gap="4px",
            width="100%",
        ),
        style={
            "background": styles.BG_PANEL,
            "box_shadow": styles.NEU_MODAL_SHADOW,
            "border_radius": "12px",
            "padding": "1rem",
        },
        width="100%",
    )


def neuro_calendario_leyenda() -> rx.Component:
    """Leyenda de estados."""
    return rx.hstack(
        rx.hstack(
            rx.box(
                style={
                    "width": "8px",
                    "height": "8px",
                    "border_radius": "50%",
                    "background": "var(--blue-9)",
                }
            ),
            rx.text("Programada", font_size="0.75rem", color=styles.TEXT_SECONDARY),
            gap="0.25rem",
        ),
        rx.hstack(
            rx.box(
                style={
                    "width": "8px",
                    "height": "8px",
                    "border_radius": "50%",
                    "background": "var(--green-9)",
                }
            ),
            rx.text("Realizada", font_size="0.75rem", color=styles.TEXT_SECONDARY),
            gap="0.25rem",
        ),
        rx.hstack(
            rx.box(
                style={
                    "width": "8px",
                    "height": "8px",
                    "border_radius": "50%",
                    "background": "var(--red-9)",
                }
            ),
            rx.text("Cancelada", font_size="0.75rem", color=styles.TEXT_SECONDARY),
            gap="0.25rem",
        ),
        gap="1.5rem",
        justify="center",
        padding="1rem",
    )
