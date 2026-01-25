import reflex as rx

from src.presentacion_reflex.components.incidentes.kanban_board import kanban_board
from src.presentacion_reflex.components.layout.dashboard_layout import dashboard_layout
from src.presentacion_reflex.state.auth_state import AuthState
from src.presentacion_reflex.state.incidentes_state import IncidentesState

# from src.presentacion_reflex.components.incidentes.modal_form import modal_form # To be implemented


def _filter_bar() -> rx.Component:
    return rx.hstack(
        rx.input(
            placeholder="Buscar incidente...",
            on_change=IncidentesState.set_search,
            width="250px",
            icon="search",
        ),
        rx.select(
            IncidentesState.prioridad_options,
            value=IncidentesState.filter_prioridad,
            on_change=IncidentesState.set_filter_prioridad,
            width="150px",
        ),
        rx.select(
            IncidentesState.estado_options,
            value=IncidentesState.filter_estado,
            on_change=IncidentesState.set_filter_estado,
            width="150px",
        ),
        rx.spacer(),
        rx.segmented_control.root(
            rx.segmented_control.item("Kanban", value="kanban"),
            rx.segmented_control.item("Lista", value="list"),
            value=IncidentesState.view_mode,
            on_change=lambda val: IncidentesState.toggle_view_mode(),
        ),
        rx.cond(
            AuthState.check_action("Incidentes", "CREAR"),
            rx.tooltip(
                rx.button(
                    rx.icon("plus", size=18),
                    "Reportar",
                    on_click=IncidentesState.open_create_modal,
                ),
                content="Reportar nuevo incidente",
            ),
        ),
        width="100%",
        padding_bottom="1em",
        align_items="center",
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


@rx.page(route="/incidentes", on_load=[AuthState.require_login, IncidentesState.on_load])
def incidentes() -> rx.Component:
    return dashboard_layout(
        rx.vstack(
            rx.heading("Gestión de Incidentes", size="6", margin_bottom="1em"),
            _filter_bar(),
            rx.cond(IncidentesState.view_mode == "kanban", kanban_board(), _list_view()),
            # Pagination Controls
            rx.hstack(
                rx.button(
                    rx.icon("chevron-left"),
                    "Anterior",
                    on_click=IncidentesState.prev_page,
                    disabled=IncidentesState.page == 1,
                    variant="soft",
                    color_scheme="gray",
                ),
                rx.text(
                    f"Página {IncidentesState.page} de {IncidentesState.total_pages}",
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
                spacing="4",
                margin_top="1em",
            ),
            modal_form(),
            modal_details(),
            width="100%",
            height="calc(100vh - 100px)",  # Ajuste para que el kanban ocupe espacio vertical
            spacing="4",
        )
    )
