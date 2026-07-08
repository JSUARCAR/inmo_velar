import reflex as rx

from src.presentacion_reflex.components.incidentes.kanban_board import kanban_board
from src.presentacion_reflex.components.layout.dashboard_layout import dashboard_layout
from src.presentacion_reflex.state.auth_state import AuthState
from src.presentacion_reflex.state.incidentes_state import (
    IncidentesState,
    IncidenteDict,
)

from src.presentacion_reflex.components.neuro_elements import (
    neuro_floating_input,
    neuro_floating_select,
    neuro_button,
)
from src.presentacion_reflex.components.tablas import header_cell_sortable
from src.presentacion_reflex.components.shared.advanced_filter_bar import advanced_filter_bar
from src.presentacion_reflex import styles


def _filter_bar() -> rx.Component:
    return advanced_filter_bar(
        # Prioridad Select
        rx.box(
            rx.text("Prioridad", style=styles.NEU_FILTER_LABEL_STYLE),
            rx.select(
                IncidentesState.prioridad_options,
                value=IncidentesState.filter_prioridad,
                on_change=IncidentesState.set_filter_prioridad,
                placeholder="Prioridad",
                style=styles.NEU_FILTER_SELECT_STYLE,
            ),
            width=["100%", "100%", "150px"]
        ),
        # Estado Select
        rx.box(
            rx.text("Estado", style=styles.NEU_FILTER_LABEL_STYLE),
            rx.select(
                IncidentesState.estado_options,
                value=IncidentesState.filter_estado,
                on_change=IncidentesState.set_filter_estado,
                placeholder="Estado",
                style=styles.NEU_FILTER_SELECT_STYLE,
            ),
            width=["100%", "100%", "150px"]
        ),
        # Estado de Pago Select
        rx.box(
            rx.text("Estado de Pago", style=styles.NEU_FILTER_LABEL_STYLE),
            rx.select(
                IncidentesState.estados_pago_options,
                value=IncidentesState.filter_estado_pago,
                on_change=IncidentesState.set_filter_estado_pago,
                placeholder="Estado de Pago",
                style=styles.NEU_FILTER_SELECT_STYLE,
            ),
            width=["100%", "100%", "180px"]
        ),
        search_placeholder="Buscar incidente...",
        on_search=IncidentesState.set_search,
        search_value=IncidentesState.search_text,
        on_key_down=IncidentesState.handle_search_key_down,
        on_clear=IncidentesState.clear_filters,
        active_filter_count=IncidentesState.active_filter_count,
        action_buttons=[
            # Toggle Vista
            rx.tooltip(
                rx.icon_button(
                    rx.cond(
                        IncidentesState.view_mode == "kanban",
                        rx.icon("list", size=18),
                        rx.icon("layout_grid", size=18),
                    ),
                    color_scheme="gray",
                    style=styles.NEU_FILTER_ICON_BUTTON_STYLE,
                    on_click=lambda: IncidentesState.toggle_view_mode(),
                ),
                content=rx.cond(
                    IncidentesState.view_mode == "kanban",
                    "Cambiar a Vista Lista",
                    "Cambiar a Vista Kanban",
                ),
            ),
            # Botón Reportar
            rx.cond(
                AuthState.check_action("Incidentes", "CREAR"),
                rx.tooltip(
                    rx.icon_button(
                        rx.icon("plus", size=18),
                        color_scheme="green",
                        style=styles.NEU_FILTER_ICON_BUTTON_STYLE,
                        on_click=IncidentesState.open_create_modal,
                    ),
                    content="Reportar Incidente",
                ),
            ),
            # Refresh
            rx.tooltip(
                rx.icon_button(
                    rx.icon("refresh_cw", size=18),
                    style=styles.NEU_FILTER_ICON_BUTTON_STYLE,
                    on_click=IncidentesState.load_incidentes,
                ),
                content="Recargar",
            ),
        ]
    )


def _list_view() -> rx.Component:
    return rx.cond(
        IncidentesState.is_loading,
        rx.center(rx.spinner(size="3"), padding_y="4em"),
        rx.cond(
            IncidentesState.incidentes.length() > 0,
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        header_cell_sortable(
                            "ID",
                            "id",
                            IncidentesState.sort_by,
                            IncidentesState.sort_order,
                            IncidentesState.toggle_sort,
                        ),
                        rx.table.column_header_cell("Descripción"),
                        header_cell_sortable(
                            "Propiedad",
                            "direccion",
                            IncidentesState.sort_by,
                            IncidentesState.sort_order,
                            IncidentesState.toggle_sort,
                        ),
                        header_cell_sortable(
                            "Prioridad",
                            "prioridad",
                            IncidentesState.sort_by,
                            IncidentesState.sort_order,
                            IncidentesState.toggle_sort,
                        ),
                        header_cell_sortable(
                            "Estado",
                            "estado",
                            IncidentesState.sort_by,
                            IncidentesState.sort_order,
                            IncidentesState.toggle_sort,
                        ),
                        header_cell_sortable(
                            "Fecha",
                            "fecha",
                            IncidentesState.sort_by,
                            IncidentesState.sort_order,
                            IncidentesState.toggle_sort,
                        ),
                    )
                ),
                rx.table.body(
                    rx.foreach(
                        IncidentesState.incidentes.to(list[IncidenteDict]),
                        lambda item: rx.table.row(
                            rx.table.cell(item.id),
                            rx.table.cell(item.descripcion),
                            rx.table.cell(item.direccion_propiedad),
                            rx.table.cell(item.prioridad),
                            rx.table.cell(rx.badge(item.estado, variant="soft")),
                            rx.table.cell(item.fecha),
                        ),
                    )
                ),
                width="100%",
            ),
            rx.center(
                rx.vstack(
                    rx.icon("database", size=24, color="var(--gray-9)"),
                    rx.text("No hay incidentes registrados", color="gray"),
                    padding_y="4em",
                ),
            ),
        ),
    )


from src.presentacion_reflex.components.incidentes.modal_details import modal_details
from src.presentacion_reflex.components.incidentes.modal_form import modal_form
from src.presentacion_reflex.components.incidentes.modal_edit_incidente import (
    modal_edit_incidente,
)
from src.presentacion_reflex.components.incidentes.modal_cancel_incidente import (
    modal_cancel_incidente,
)
from src.presentacion_reflex.components.incidentes.modal_plan_pago import (
    modal_plan_pago,
)


@rx.page(
    route="/incidentes", on_load=[AuthState.require_login, IncidentesState.on_load]
)
def incidentes() -> rx.Component:
    return dashboard_layout(
        rx.vstack(
            rx.heading("Gestión de Incidentes", size="6", margin_bottom="1em"),
            rx.cond(
                IncidentesState.error_message != "",
                rx.box(
                    rx.hstack(
                        rx.icon("triangle-alert", color="red"),
                        rx.text(IncidentesState.error_message, color="red", size="2"),
                    ),
                    padding="3",
                    border="1px solid red",
                    border_radius="8px",
                    margin_bottom="4",
                    bg="var(--red-2)",
                ),
            ),
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
                    "Página ",
                    IncidentesState.page,
                    " de ",
                    IncidentesState.total_pages,
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
            modal_plan_pago(),
            width="100%",
            flex="1",
            height="100%",
            overflow="hidden",
            spacing="4",
        )
    )
