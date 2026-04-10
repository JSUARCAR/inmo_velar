"""
Página de Propiedad Horizontal - Reflex
Gestión de Asambleas y Pagos de Administración.
"""

from typing import Dict

import reflex as rx

from src.presentacion_reflex import styles
from src.presentacion_reflex.components.layout.dashboard_layout import dashboard_layout
from src.presentacion_reflex.state.propiedad_horizontal_state import (
    PropiedadHorizontalState,
)
from src.presentacion_reflex.state.auth_state import AuthState
from src.presentacion_reflex.components.neuro_elements import (
    neuro_table_container,
    neuro_select_root,
    neuro_input,
    neuro_form_label,
    neuro_divider,
    neuro_tooltip,
)


def render_asambleas_tab() -> rx.Component:
    """Renderiza el tab de Asambleas."""
    return rx.vstack(
        rx.hstack(
            rx.heading("Asambleas de Propiedad Horizontal", size="4"),
            rx.hstack(
                rx.button(
                    rx.icon(tag="table"),
                    "Tabla",
                    variant="soft",
                    on_click=lambda: [
                        PropiedadHorizontalState.set_vista_asambleas("tabla"),
                        PropiedadHorizontalState.cargar_asambleas(),
                    ],
                ),
                rx.button(
                    rx.icon(tag="calendar"),
                    "Calendario",
                    variant="soft",
                    on_click=lambda: [
                        PropiedadHorizontalState.set_vista_asambleas("calendario"),
                        PropiedadHorizontalState.cargar_eventos_calendario(),
                    ],
                ),
                spacing="2",
            ),
            rx.button(
                rx.icon(tag="plus"),
                "Nueva Asistencia",
                on_click=PropiedadHorizontalState.open_modal_crear_asistencia,
                bg="var(--primary)",
                color="white",
                ml="auto",
            ),
            spacing="4",
            width="100%",
            justify="between",
        ),
        rx.box(height="4"),
        rx.hstack(
            rx.box("Estado:", as_="span"),
            rx.select(
                ["Todos", "Programada", "Realizada", "Cancelada"],
                value=PropiedadHorizontalState.filtro_estado_asistencia,
                on_change=PropiedadHorizontalState.set_filtro_estado_asistencia,
                width="150px",
            ),
            spacing="2",
        ),
        rx.box(height="4"),
        rx.cond(
            PropiedadHorizontalState.vista_asambleas == "calendario",
            render_calendario_asambleas(),
            rx.cond(
                PropiedadHorizontalState.asambleas.length() > 0,
                neuro_table_container(
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                rx.table.column_header_cell("ID"),
                                rx.table.column_header_cell("Propiedad"),
                                rx.table.column_header_cell("Fecha/Hora"),
                                rx.table.column_header_cell("Tipo"),
                                rx.table.column_header_cell("Asistente"),
                                rx.table.column_header_cell("Costo"),
                                rx.table.column_header_cell("Estado"),
                                rx.table.column_header_cell("Acciones"),
                            ),
                        ),
                        rx.table.body(
                            rx.foreach(
                                PropiedadHorizontalState.asambleas,
                                lambda a: rx.table.row(
                                    rx.table.cell(a.id_asistencia),
                                    rx.table.cell(a.direccion_propiedad),
                                    rx.table.cell(
                                        neuro_tooltip(
                                            rx.box(
                                                a.fecha_asistencia.to_string(),
                                                " ",
                                                rx.badge(
                                                    a.hora_asistencia,
                                                    size="1",
                                                    variant="soft",
                                                ),
                                            ),
                                            content=a.tooltip_asistencia,
                                        )
                                    ),
                                    rx.table.cell(a.tipo_reunion),
                                    rx.table.cell(a.nombre_asistente),
                                    rx.table.cell(
                                        rx.cond(
                                            a.costo_asistente,
                                            "$" + a.costo_asistente.to_string(),
                                            "$0",
                                        )
                                    ),
                                    rx.table.cell(a.estado_asistencia),
                                    rx.table.cell(
                                        rx.cond(
                                            a.estado_asistencia == "Programada",
                                            rx.hstack(
                                                rx.button(
                                                    "✓",
                                                    size="1",
                                                    on_click=lambda: (
                                                        PropiedadHorizontalState.marcar_realizada(
                                                            a.id_asistencia
                                                        )
                                                    ),
                                                    aria_label="Marcar como realizada",
                                                ),
                                                rx.button(
                                                    "X",
                                                    size="1",
                                                    on_click=lambda: (
                                                        PropiedadHorizontalState.eliminar_asistencia(
                                                            a.id_asistencia
                                                        )
                                                    ),
                                                    aria_label="Eliminar asistencia",
                                                ),
                                                spacing="2",
                                            ),
                                        ),
                                    ),
                                ),
                            ),
                        ),
                        width="100%",
                        variant="ghost",
                    ),
                ),
                rx.box(
                    rx.center(
                        rx.vstack(
                            rx.icon(
                                tag="calendar-off", size=48, color="var(--text-muted)"
                            ),
                            rx.box(
                                "No hay asambleas programadas",
                                as_="span",
                                color="var(--text-muted)",
                            ),
                            spacing="3",
                        ),
                        padding="48px",
                    ),
                ),
            ),
        ),
        spacing="4",
        width="100%",
    )


def render_calendario_asambleas() -> rx.Component:
    """Renderiza la vista calendario de asambleas."""
    return rx.vstack(
        rx.hstack(
            rx.icon_button(
                rx.icon(tag="chevron-left"),
                variant="soft",
                on_click=PropiedadHorizontalState.navigate_mes_anterior,
            ),
            rx.box(
                rx.match(
                    PropiedadHorizontalState.mes_seleccionado,
                    (1, "Enero"),
                    (2, "Febrero"),
                    (3, "Marzo"),
                    (4, "Abril"),
                    (5, "Mayo"),
                    (6, "Junio"),
                    (7, "Julio"),
                    (8, "Agosto"),
                    (9, "Septiembre"),
                    (10, "Octubre"),
                    (11, "Noviembre"),
                    (12, "Diciembre"),
                    "",
                ),
                " ",
                PropiedadHorizontalState.año_seleccionado.to_string(),
                as_="span",
                font_weight="600",
                font_size="1.25rem",
            ),
            rx.icon_button(
                rx.icon(tag="chevron-right"),
                variant="soft",
                on_click=PropiedadHorizontalState.navigate_mes_siguiente,
            ),
            spacing="4",
            justify="center",
            width="100%",
        ),
        rx.box(height="4"),
        _render_calendario_dias(),
        rx.box(height="4"),
        _render_leyenda(),
        spacing="4",
        width="100%",
    )


def _render_calendario_dias() -> rx.Component:
    """Renderiza los dias del mes en un grid 7x6."""
    return rx.box(
        rx.grid(
            rx.foreach(
                ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"],
                lambda d: _header_dia(d),
            ),
            rx.foreach(
                PropiedadHorizontalState.dias_mes_calendario,
                lambda dia: _celda_dia(dia),
            ),
            columns="7",
            gap="4px",
            width="100%",
        ),
        width="100%",
        style={
            "background": "var(--bg-panel)",
            "box_shadow": "var(--modal-shadow)",
            "border_radius": "12px",
            "padding": "1rem",
            "min_height": "300px",
        },
    )


def _header_dia(nombre: str) -> rx.Component:
    return rx.box(
        nombre,
        as_="span",
        font_size="0.75rem",
        font_weight="600",
        color="var(--text-secondary)",
        width="100%",
        text_align="center",
        padding="0.5rem",
    )


def _celda_vacia() -> rx.Component:
    return rx.box(
        min_height="50px",
        style={
            "background": "var(--bg-subtle)",
            "border_radius": "8px",
        },
    )


def _celda_dia(dia: rx.Var) -> rx.Component:
    """Renderiza una celda de día de forma reactiva."""
    return rx.cond(
        (dia.es_vacio) | (dia.dia == 0),
        rx.box(
            min_height="50px",
            style={
                "background": "var(--bg-subtle)",
                "border_radius": "8px",
                "opacity": "0.3",
            },
        ),
        rx.box(
            rx.vstack(
                rx.box(
                    dia.dia.to_string(),
                    as_="span",
                    font_size="0.875rem",
                    font_weight="500",
                    color="var(--text-primary)",
                ),
                rx.cond(
                    dia.tiene_eventos,
                    rx.hstack(
                        rx.foreach(
                            dia.eventos,
                            lambda evento: rx.tooltip(
                                rx.box(
                                    width="8px",
                                    height="8px",
                                    border_radius="50%",
                                    bg=evento.color_tipo,
                                ),
                                content=evento.direccion_propiedad + " | " + evento.nombre_asistente + " · " + evento.tipo_reunion + " - " + evento.hora_asistencia,
                            ),
                        ),
                        spacing="1",
                        wrap="wrap",
                        justify="center",
                    ),
                ),
                spacing="1",
                align="center",
            ),
            min_height="50px",
            padding="4px",
            on_click=rx.cond(
                dia.tiene_eventos,
                PropiedadHorizontalState.open_modal_dia_calendario(dia.dia),
                None,
            ),
            style={
                "background": "var(--bg-subtle)",
                "border_radius": "8px",
                "cursor": rx.cond(dia.tiene_eventos, "pointer", "default"),
                "transition": "all 0.2s cubic-bezier(0.4, 0, 0.2, 1)",
                "_hover": {
                    "background": "var(--bg-hover)",
                    "box_shadow": "var(--shadow-flat-elite)",
                    "transform": "translateY(-1px)",
                },
            },
        ),
    )


def _render_leyenda() -> rx.Component:
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
            rx.box(
                "Programada",
                font_size="0.75rem",
                color="var(--text-secondary)",
                as_="span",
            ),
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
            rx.box(
                "Realizada",
                font_size="0.75rem",
                color="var(--text-secondary)",
                as_="span",
            ),
            gap="0.25rem",
        ),
        rx.hstack(
            rx.box(
                style={
                    "width": "8px",
                    "height": "8px",
                    "border_radius": "50%",
                    "background": "var(--orange-9)",
                }
            ),
            rx.box(
                "Cancelada",
                font_size="0.75rem",
                color="var(--text-secondary)",
                as_="span",
            ),
            gap="0.25rem",
        ),
        gap="1.5rem",
        justify="center",
    )


def render_pagos_tab() -> rx.Component:
    """Renderiza el tab de Pagos de Administración."""
    return rx.vstack(
        rx.hstack(
            rx.heading("Pagos de Administración", size="4"),
            rx.button(
                rx.icon(tag="wallet"),
                "Generar Pagos",
                on_click=PropiedadHorizontalState.open_modal_generar_pagos,
                bg="var(--primary)",
                color="white",
                ml="auto",
            ),
            spacing="4",
            width="100%",
            justify="between",
        ),
        rx.box(height="4"),
        rx.hstack(
            rx.box("Propietario:", as_="span"),
            rx.input(
                placeholder="Buscar por nombre...",
                value=PropiedadHorizontalState.busqueda_pago_propietario,
                on_change=PropiedadHorizontalState.set_busqueda_pago_propietario,
                width="250px",
            ),
            rx.box("Período:", as_="span"),
            rx.input(
                type="month",
                value=PropiedadHorizontalState.filtro_periodo,
                on_change=PropiedadHorizontalState.set_filtro_periodo,
                width="150px",
            ),
            rx.box("Estado:", as_="span"),
            rx.select(
                ["Todos", "Pendiente", "Pagado", "Vencido"],
                value=PropiedadHorizontalState.filtro_estado_pago,
                on_change=PropiedadHorizontalState.set_filtro_estado_pago,
                width="150px",
            ),
            spacing="4",
        ),
        rx.box(height="4"),
        rx.cond(
            PropiedadHorizontalState.pagos_filtrados.length() > 0,
            neuro_table_container(
                rx.table.root(
                    rx.table.header(
                        rx.table.row(
                            rx.table.column_header_cell("ID"),
                            rx.table.column_header_cell("Propietario"),
                            rx.table.column_header_cell("Propiedad"),
                            rx.table.column_header_cell("Valor"),
                            rx.table.column_header_cell("Día"),
                            rx.table.column_header_cell("Período"),
                            rx.table.column_header_cell("Estado"),
                            rx.table.column_header_cell("Link"),
                            rx.table.column_header_cell("Acciones"),
                        ),
                    ),
                    rx.table.body(
                        rx.foreach(
                            PropiedadHorizontalState.pagos_filtrados,
                            lambda p: rx.table.row(
                                rx.table.cell(p.id_pago_admin),
                                rx.table.cell(p.nombre_propietario),
                                rx.table.cell(p.direccion_propiedad),
                                rx.table.cell(
                                    neuro_tooltip(
                                        rx.box(p.valor_formateado),
                                        content=p.tooltip_pago,
                                    )
                                ),
                                rx.table.cell("Día " + p.fecha_pago.to_string()),
                                rx.table.cell(
                                    neuro_tooltip(
                                        rx.box(p.periodo_pago),
                                        content=p.tooltip_pago,
                                    )
                                ),
                                rx.table.cell(p.estado_pago),
                                rx.table.cell(
                                    rx.cond(
                                        p.link_pago,
                                        rx.link(
                                            "Pagar",
                                            href=p.link_pago,
                                            target="_blank",
                                        ),
                                        rx.cond(
                                            p.estado_pago != "Pagado",
                                            rx.button(
                                                "✓",
                                                size="1",
                                                on_click=lambda: (
                                                    PropiedadHorizontalState.marcar_pagado(
                                                        p.id_pago_admin
                                                    )
                                                ),
                                                aria_label="Marcar pago como pagado",
                                            ),
                                        ),
                                    ),
                                ),
                            ),
                        ),
                    ),
                    width="100%",
                    variant="ghost",
                ),
            ),
            rx.box(
                rx.center(
                    rx.vstack(
                        rx.icon(tag="wallet", size=48, color="var(--text-muted)"),
                        rx.box(
                            "No hay pagos de administración",
                            as_="span",
                            color="var(--text-muted)",
                        ),
                        spacing="3",
                    ),
                    padding="48px",
                ),
            ),
        ),
        spacing="4",
        width="100%",
    )


def modal_crear_asistencia() -> rx.Component:
    """Modal para crear asistencia."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.box(
                rx.hstack(
                    rx.dialog.title(
                        "Nueva Asistencia a Asamblea",
                        font_size="1.25rem",
                        font_weight="600",
                    ),
                    rx.dialog.close(
                        rx.icon_button(
                            rx.icon(tag="x"),
                            variant="ghost",
                            color_scheme="gray",
                            size="1",
                            on_click=PropiedadHorizontalState.close_modal_crear_asistencia,
                        ),
                    ),
                    justify="between",
                    align="center",
                    width="100%",
                    margin_bottom="1rem",
                ),
                rx.dialog.description(
                    "Formulario para registrar una nueva asistencia a asamblea de copropietarios.",
                    size="1",
                    color_scheme="gray",
                    opacity="0",
                    height="0",
                    padding="0",
                    margin="0",
                ),
                rx.box(
                    "Seleccione la propiedad y configure los datos de la asamblea",
                    as_="span",
                    color="var(--text-secondary)",
                    font_size="0.875rem",
                    margin_bottom="1.5rem",
                ),
                rx.vstack(
                    rx.box(
                        neuro_form_label("Propiedad", required=True),
                        rx.input(
                            placeholder="Escriba para buscar propiedad...",
                            value=PropiedadHorizontalState.busqueda_propiedad,
                            on_change=PropiedadHorizontalState.on_propiedad_search_change,
                            list="propiedades-list",
                            width="100%",
                            style=styles.NEU_INPUT_STYLE,
                        ),
                        rx.el.datalist(
                            rx.foreach(
                                PropiedadHorizontalState.propiedades_filtradas,
                                lambda o: rx.el.option(o["label"], value=o["value"]),
                            ),
                            id="propiedades-list",
                        ),
                        width="100%",
                    ),
                    rx.grid(
                        rx.box(
                            neuro_form_label("Fecha", required=True),
                            neuro_input(
                                type="date",
                                placeholder="Seleccionar fecha",
                                on_change=lambda val: (
                                    PropiedadHorizontalState.set_form_field(
                                        "fecha_asistencia", val
                                    )
                                ),
                                width="100%",
                            ),
                        ),
                        rx.box(
                            neuro_form_label("Hora", required=True),
                            neuro_input(
                                type="time",
                                placeholder="Seleccionar hora",
                                on_change=lambda val: (
                                    PropiedadHorizontalState.set_form_field(
                                        "hora_asistencia", val
                                    )
                                ),
                                width="100%",
                            ),
                        ),
                        columns="2",
                        gap="1rem",
                        width="100%",
                    ),
                    rx.grid(
                        rx.box(
                            neuro_form_label("Tipo de Reunión", required=True),
                            neuro_select_root(
                                rx.select.item("Ordinaria", value="Ordinaria"),
                                rx.select.item(
                                    "Extraordinaria", value="Extraordinaria"
                                ),
                                rx.select.item(
                                    "Segunda Convocatoria", value="SegundaConvocatoria"
                                ),
                                placeholder="Seleccionar tipo",
                                on_change=lambda val: (
                                    PropiedadHorizontalState.set_form_field(
                                        "tipo_reunion", val
                                    )
                                ),
                                width="100%",
                            ),
                        ),
                        rx.box(
                            neuro_form_label("Quién Asiste", required=True),
                            neuro_select_root(
                                rx.select.item("Propietario", value="Propietario"),
                                rx.select.item("Inmobiliaria", value="Inmobiliaria"),
                                value=PropiedadHorizontalState.form_data.get(
                                    "tipo_asistente", "Propietario"
                                ),
                                placeholder="Seleccionar...",
                                on_change=lambda val: (
                                    PropiedadHorizontalState.set_form_field(
                                        "tipo_asistente", val
                                    )
                                ),
                                width="100%",
                            ),
                        ),
                        columns="2",
                        gap="1rem",
                        width="100%",
                    ),
                    rx.cond(
                        PropiedadHorizontalState.es_asistente_inmobiliaria,
                        rx.box(
                            neuro_form_label(
                                "Asesor de la Inmobiliaria", required=True
                            ),
                            neuro_select_root(
                                rx.foreach(
                                    PropiedadHorizontalState.asesores_activos,
                                    lambda a: rx.select.item(
                                        a.nombre_completo, value=a.id_asesor.to_string()
                                    ),
                                ),
                                value=PropiedadHorizontalState.form_data.get(
                                    "id_asesor_seleccionado", ""
                                ),
                                placeholder="Seleccionar asesor...",
                                on_change=lambda val: (
                                    PropiedadHorizontalState.set_form_field(
                                        "id_asesor_seleccionado", val
                                    )
                                ),
                                width="100%",
                            ),
                            width="100%",
                        ),
                        rx.box(
                            neuro_form_label("Nombre del Propietario", required=False),
                            neuro_input(
                                value=PropiedadHorizontalState.form_data.get(
                                    "nombre_propietario_display",
                                    "Seleccione una propiedad...",
                                ),
                                disabled=True,
                                width="100%",
                            ),
                            width="100%",
                        ),
                    ),
                    rx.box(
                        neuro_form_label("Dirección de la Asamblea", required=True),
                        neuro_input(
                            placeholder="Ingrese la dirección del lugar de la asamblea",
                            on_change=lambda val: (
                                PropiedadHorizontalState.set_form_field(
                                    "direccion_asistencia", val
                                )
                            ),
                            width="100%",
                        ),
                    ),
                    rx.box(
                        neuro_divider(),
                        margin_y="1rem",
                    ),
                    rx.hstack(
                        rx.box(
                            "Costo del Asistente:",
                            as_="span",
                            font_size="0.875rem",
                            font_weight="500",
                            color="var(--text-primary)",
                        ),
                        rx.cond(
                            PropiedadHorizontalState.form_data.get("tipo_asistente")
                            == "Propietario",
                            rx.badge(
                                "$0 (Sin costo)",
                                color_scheme="green",
                                variant="soft",
                            ),
                            rx.badge(
                                "$50.000",
                                color_scheme="blue",
                                variant="soft",
                            ),
                        ),
                        align="center",
                        justify="between",
                        width="100%",
                    ),
                    gap="1rem",
                    width="100%",
                ),
                rx.flex(
                    rx.dialog.close(
                        rx.button(
                            "Cancelar",
                            variant="soft",
                            color_scheme="gray",
                            on_click=PropiedadHorizontalState.close_modal_crear_asistencia,
                        ),
                    ),
                    rx.button(
                        "Guardar Asistencia",
                        bg="var(--primary)",
                        color="white",
                        on_click=PropiedadHorizontalState.guardar_asistencia,
                    ),
                    spacing="3",
                    justify="end",
                    margin_top="1.5rem",
                    width="100%",
                ),
                style={
                    "max_width": "550px",
                    "width": "100%",
                    "padding": "1.5rem",
                },
            ),
            style={
                "background": "var(--bg-panel)",
                "border_radius": "16px",
                "box_shadow": "0.25rem 0.25rem 0.5rem var(--shadow-dark), -0.25rem -0.25rem 0.5rem var(--shadow-light)",
            },
        ),
        open=PropiedadHorizontalState.show_modal_crear_asistencia,
        on_open_change=lambda _: (
            PropiedadHorizontalState.close_modal_crear_asistencia()
        ),
    )


def modal_generar_pagos() -> rx.Component:
    """Modal para generar pagos."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.dialog.title("Generar Pagos de Administración"),
            rx.dialog.description(
                rx.box(
                    "Se generarán pagos para el período: ",
                    PropiedadHorizontalState.filtro_periodo,
                    ". Se creará un registro por cada propiedad con contrato de mandato activo.",
                    as_="span",
                    size="2",
                ),
            ),
            rx.flex(
                rx.dialog.close(
                    rx.button(
                        "Cancelar",
                        variant="soft",
                        color_scheme="gray",
                        on_click=PropiedadHorizontalState.close_modal_generar_pagos,
                    ),
                ),
                rx.button(
                    "Generar",
                    on_click=PropiedadHorizontalState.generar_pagos_mes,
                    color_scheme="indigo",
                ),
                spacing="3",
                justify="end",
                margin_top="4",
            ),
        ),
        open=PropiedadHorizontalState.show_modal_generar_pagos,
        on_open_change=lambda _: PropiedadHorizontalState.close_modal_generar_pagos(),
    )


def modal_dia_calendario() -> rx.Component:
    """Modal para mostrar eventos de un día específico."""
    return rx.dialog.root(
        rx.dialog.content(
            rx.box(
                rx.hstack(
                    rx.dialog.title(
                        "Eventos del ", PropiedadHorizontalState.dia_seleccionado,
                    ),
                    rx.dialog.close(
                        rx.icon_button(
                            rx.icon(tag="x"),
                            variant="ghost",
                            on_click=PropiedadHorizontalState.close_modal_dia_calendario,
                        ),
                    ),
                    justify="between",
                    width="100%",
                    margin_bottom="1rem",
                ),
                rx.dialog.description(
                    "Detalle de eventos del día seleccionado",
                    class_name="sr-only",
                ),
                rx.cond(
                    PropiedadHorizontalState.eventos_dia_seleccionado.length() > 0,
                    rx.vstack(
                        rx.foreach(
                            PropiedadHorizontalState.eventos_dia_seleccionado,
                            lambda e: rx.box(
                                rx.hstack(
                                    rx.box(
                                        width="10px",
                                        height="10px",
                                        border_radius="50%",
                                        bg=e.color_tipo,
                                    ),
                                    rx.vstack(
                                        rx.box(
                                            e.tipo_reunion,
                                            as_="span",
                                            font_weight="600",
                                        ),
                                        rx.box(
                                            e.hora_asistencia
                                            + " - "
                                            + e.direccion_asistencia,
                                            as_="span",
                                            font_size="0.875rem",
                                            color="var(--text-secondary)",
                                        ),
                                        spacing="0",
                                    ),
                                    spacing="2",
                                    align="center",
                                ),
                                padding="0.75rem",
                                margin_bottom="0.5rem",
                                style={
                                    "background": "var(--bg-subtle)",
                                    "border_radius": "8px",
                                },
                            ),
                        ),
                        spacing="2",
                        width="100%",
                    ),
                    rx.box(
                        "No hay eventos en este día",
                        as_="span",
                        color="var(--text-muted)",
                    ),
                ),
            ),
            style={
                "max_width": "400px",
                "width": "100%",
                "padding": "1.5rem",
                "background": "var(--bg-panel)",
                "border_radius": "12px",
            },
        ),
        open=PropiedadHorizontalState.dia_seleccionado != None,
        on_open_change=PropiedadHorizontalState.handle_dia_modal_open_change,
    )


@rx.page(
    route="/propiedad-horizontal",
    title="Propiedad Horizontal - Inmobiliaria Velar",
    on_load=[AuthState.require_login, PropiedadHorizontalState.load_initial_data],
)
def propiedad_horizontal_page() -> rx.Component:
    """Página principal de Propiedad Horizontal."""
    return dashboard_layout(
        rx.vstack(
            rx.cond(
                PropiedadHorizontalState.is_loading,
                rx.center(
                    rx.spinner(size="3"),
                    width="100%",
                    min_height="400px",
                ),
                rx.vstack(
                    rx.cond(
                        PropiedadHorizontalState.error_message != "",
                        rx.box(
                            rx.box(
                                PropiedadHorizontalState.error_message,
                                color="red",
                                font_weight="bold",
                                as_="span",
                            ),
                            bg="red-100",
                            padding="3",
                            border_radius="md",
                            width="100%",
                        ),
                    ),
                    rx.cond(
                        PropiedadHorizontalState.success_message != "",
                        rx.box(
                            rx.box(
                                PropiedadHorizontalState.success_message,
                                color="green",
                                font_weight="bold",
                                as_="span",
                            ),
                            bg="green-100",
                            padding="3",
                            border_radius="md",
                            width="100%",
                        ),
                    ),
                    rx.tabs.root(
                        rx.tabs.list(
                            rx.tabs.trigger("Asambleas", value="asambleas"),
                            rx.tabs.trigger("Pagos de Administración", value="pagos"),
                        ),
                        rx.tabs.content(
                            render_asambleas_tab(),
                            value="asambleas",
                            width="100%",
                        ),
                        rx.tabs.content(
                            render_pagos_tab(),
                            value="pagos",
                            width="100%",
                        ),
                        value=PropiedadHorizontalState.current_tab,
                        on_change=PropiedadHorizontalState.set_tab,
                        default_value="asambleas",
                    ),
                    modal_crear_asistencia(),
                    modal_generar_pagos(),
                    modal_dia_calendario(),
                    spacing="4",
                    width="100%",
                ),
            ),
            spacing="4",
            width="100%",
            padding="4",
        )
    )
