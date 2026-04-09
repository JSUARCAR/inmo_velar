import reflex as rx

from src.presentacion_reflex.components.incidentes.kanban_board import kanban_board
from src.presentacion_reflex.components.layout.dashboard_layout import dashboard_layout
from src.presentacion_reflex.state.auth_state import AuthState
from src.presentacion_reflex.state.incidentes_state import IncidentesState

from src.presentacion_reflex.components.neuro_elements import (
    neuro_input,
    neuro_button,
    neuro_select_root,
)
from src.presentacion_reflex import styles


def _filter_bar() -> rx.Component:
    return rx.flex(
        neuro_input(
            placeholder="Buscar incidente...",
            on_change=IncidentesState.set_search,
            width=["100%", "250px"],
        ),
        neuro_select_root(
            rx.foreach(
                IncidentesState.prioridad_options,
                lambda opt: rx.select.item(opt, value=opt),
            ),
            value=IncidentesState.filter_prioridad,
            on_change=IncidentesState.set_filter_prioridad,
            placeholder="Prioridad",
            width=["100%", "150px"],
        ),
        neuro_select_root(
            rx.foreach(
                IncidentesState.estado_options,
                lambda opt: rx.select.item(opt, value=opt),
            ),
            value=IncidentesState.filter_estado,
            on_change=IncidentesState.set_filter_estado,
            placeholder="Estado",
            width=["100%", "150px"],
        ),
        rx.spacer(display=["none", "block"]),
        rx.segmented_control.root(
            rx.segmented_control.item("Kanban", value="kanban"),
            rx.segmented_control.item("Lista", value="list"),
            value=IncidentesState.view_mode,
            on_change=lambda val: IncidentesState.toggle_view_mode(),
            width=["100%", "auto"],
            style={"box_shadow": styles.NEU_SHADOW, "border_radius": "8px"},
        ),
        rx.cond(
            AuthState.check_action("Incidentes", "CREAR"),
            rx.tooltip(
                neuro_button(
                    rx.hstack(rx.icon("plus", size=18), rx.text("Reportar")),
                    on_click=IncidentesState.open_create_modal,
                    width=["100%", "auto"],
                ),
                content="Reportar nuevo incidente",
            ),
        ),
        width="100%",
        padding="4",
        background=styles.BG_PANEL,
        border_radius="16px",
        style={"box_shadow": styles.NEU_SHADOW},
        align_items="center",
        flex_wrap="wrap",
        gap="4",
        margin_bottom="4",
    )


def _list_view() -> rx.Component:
    return rx.table.root(
        rx.table.header(
            rx.table.row(
                rx.table.column_header_cell("ID"),
                rx.table.column_header_cell("Descripción"),
                rx.table.column_header_cell("Propiedad"),
                rx.table.column_header_cell("Prioridad"),
                rx.table.column_header_cell("Estado"),
                rx.table.column_header_cell("Fecha"),
            )
        ),
        rx.table.body(
            rx.foreach(
                IncidentesState.incidentes,
                lambda item: rx.table.row(
                    rx.table.cell(item["id"]),
                    rx.table.cell(item["descripcion"]),
                    rx.table.cell(item["id_propiedad"]),
                    rx.table.cell(item["prioridad"]),
                    rx.table.cell(rx.badge(item["estado"], variant="soft")),
                    rx.table.cell(item["fecha"]),
                ),
            )
        ),
        width="100%",
    )


from src.presentacion_reflex.components.incidentes.modal_details import modal_details
from src.presentacion_reflex.components.incidentes.modal_form import modal_form
from src.presentacion_reflex.components.incidentes.modal_edit_incidente import (
    modal_edit_incidente,
)
from src.presentacion_reflex.components.incidentes.modal_cancel_incidente import (
    modal_cancel_incidente,
)


@rx.page(
    route="/incidentes", on_load=[AuthState.require_login, IncidentesState.on_load]
)
def incidentes() -> rx.Component:
    return dashboard_layout(
        rx.vstack(
            rx.heading("Gestión de Incidentes", size="6", margin_bottom="1em"),
            _filter_bar(),
            rx.box(
                rx.cond(
                    IncidentesState.view_mode == "kanban", kanban_board(), _list_view()
                ),
                flex="1",
                width="100%",
                height="100%",
                min_height="0",
            ),
            # Pagination Controls
            rx.flex(
                rx.button(
                    rx.icon("chevron-left"),
                    "Anterior",
                    on_click=IncidentesState.prev_page,
                    disabled=IncidentesState.page == 1,
                    variant="soft",
                    color_scheme="gray",
                ),
                rx.text(
                    rx.text(
                        "Página ",
                        IncidentesState.page,
                        " de ",
                        IncidentesState.total_pages,
                    ),
                    weight="medium",
                    color="gray",
                ),
                rx.button(
                    "Siguiente",
                    rx.icon("chevron-right"),
                    on_click=IncidentesState.next_page,
                    disabled=IncidentesState.page == IncidentesState.total_pages,
                    variant="soft",
                    color_scheme="gray",
                ),
                width="100%",
                justify="center",
                align_items="center",
                flex_wrap="wrap",
                gap="4",
                margin_top="1em",
            ),
            modal_form(),
            modal_details(),
            modal_edit_incidente(),
            modal_cancel_incidente(),
            width="100%",
            flex="1",
            height="100%",
            overflow="hidden",
            spacing="4",
        )
    )
