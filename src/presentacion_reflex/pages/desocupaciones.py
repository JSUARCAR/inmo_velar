import reflex as rx
from src.presentacion_reflex.components.layout.dashboard_layout import dashboard_layout
from src.presentacion_reflex.state.desocupaciones_state import DesocupacionesState
from src.presentacion_reflex.state.auth_state import AuthState
from src.presentacion_reflex.components.desocupaciones.modal_form import modal_form

def _filter_bar() -> rx.Component:
    return rx.hstack(
        rx.select(
            DesocupacionesState.estado_options,
            value=DesocupacionesState.filter_estado,
            on_change=DesocupacionesState.set_filter_estado,
            width="200px"
        ),
        rx.cond(
            AuthState.check_action("Desocupaciones", "CREAR"),
            rx.button(
                rx.icon("plus", size=18),
                "Nueva Desocupación",
                on_click=DesocupacionesState.open_create_modal,
            )
        ),
        justify="between",
        width="100%",
        padding_bottom="1em"
    )

def _data_table() -> rx.Component:
    return rx.table.root(
        rx.table.header(
            rx.table.row(
                rx.table.column_header_cell("ID"),
                rx.table.column_header_cell("Dirección"),
                rx.table.column_header_cell("Fecha Programada"),
                rx.table.column_header_cell("Estado"),
                rx.table.column_header_cell("Progreso"),
                rx.table.column_header_cell("Acciones"),
            )
        ),
        rx.table.body(
            rx.foreach(
                DesocupacionesState.desocupaciones,
                lambda item: rx.table.row(
                    rx.table.cell(item["id"]),
                    rx.table.cell(item["direccion"]),
                    rx.table.cell(item["fecha_programada"]),
                    rx.table.cell(
                        rx.badge(item["estado"], variant="soft", color_scheme="blue")
                    ),
                    rx.table.cell(
                        rx.progress(value=item["progreso"], width="100px")
                    ),
                    rx.table.cell(
                        rx.hstack(
                            rx.cond(
                                AuthState.check_action("Desocupaciones", "EDITAR"),
                                rx.tooltip(
                                    rx.icon_button(
                                        rx.icon("clipboard_list", size=18),
                                        on_click=lambda: DesocupacionesState.open_checklist(item["id"]),
                                        variant="ghost",
                                        color_scheme="blue"
                                    ),
                                    content="Ver checklist"
                                )
                            ),
                            rx.cond(
                                AuthState.check_action("Desocupaciones", "EDITAR"),
                                rx.tooltip(
                                    rx.icon_button(
                                        rx.icon("circle_check_big", size=18),
                                        on_click=lambda: DesocupacionesState.open_finalize_modal(item["id"]),
                                        variant="ghost",
                                        color_scheme="green"
                                    ),
                                    content="Finalizar proceso"
                                )
                            )
                        )
                    )
                )
            )
        ),
        width="100%"
    )

from src.presentacion_reflex.components.desocupaciones.checklist_modal import checklist_modal
from src.presentacion_reflex.components.desocupaciones.finalize_modal import finalize_confirm_modal

@rx.page(route="/desocupaciones", on_load=DesocupacionesState.on_load)
def desocupaciones() -> rx.Component:
    return dashboard_layout(
        rx.vstack(
            rx.heading("Gestión de Desocupaciones", size="6", margin_bottom="1em"),
            _filter_bar(),
            _data_table(),
            modal_form(),
            checklist_modal(),
            finalize_confirm_modal(),
            width="100%",
            spacing="4"
        )
    )
