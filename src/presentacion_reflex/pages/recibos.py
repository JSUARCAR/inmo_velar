import reflex as rx

from src.presentacion_reflex.components.layout.dashboard_layout import dashboard_layout
from src.presentacion_reflex.components.recibos import (
    detail_modal,
    modal_form,
    payment_modal,
)
from src.presentacion_reflex.state.auth_state import AuthState
from src.presentacion_reflex.state.recibos_state import RecibosState

from src.presentacion_reflex.components.neuro_elements import (
    neuro_input,
    neuro_button,
    neuro_select_root,
)
from src.presentacion_reflex import styles


def filtros_bar() -> rx.Component:
    return rx.flex(
        neuro_input(
            placeholder="Buscar por propiedad o comprobante...",
            on_change=RecibosState.set_search,
            width=["100%", "300px"],
        ),
        neuro_select_root(
            [
                rx.select.item("Todos", value="Todos"),
                rx.select.item("Agua", value="Agua"),
                rx.select.item("Luz", value="Luz"),
                rx.select.item("Gas", value="Gas"),
                rx.select.item("Internet", value="Internet"),
            ],
            placeholder="Filtrar Servicio",
            value=RecibosState.filter_servicio,
            on_change=lambda val: [
                RecibosState.set_filter_servicio(val),
                RecibosState.load_data(),
            ],
            width=["100%", "200px"],
        ),
        neuro_select_root(
            [
                rx.select.item("Todos", value="Todos"),
                rx.select.item("Pendiente", value="Pendiente"),
                rx.select.item("Pagado", value="Pagado"),
                rx.select.item("Vencido", value="Vencido"),
            ],
            placeholder="Estado",
            value=RecibosState.filter_estado,
            on_change=lambda val: [
                RecibosState.set_filter_estado(val),
                RecibosState.load_data(),
            ],
            width=["100%", "150px"],
        ),
        rx.spacer(),
        rx.cond(
            AuthState.check_action("Recibos Publicos", "CREAR"),
            neuro_button(
                rx.hstack(rx.icon("plus"), rx.text("Nuevo Recibo")),
                on_click=RecibosState.open_create_modal,
                width=["100%", "auto"],
            ),
        ),
        width="100%",
        gap="3",
        align="center",
        wrap="wrap",
        padding="4",
        background=styles.BG_PANEL,
        border_radius="16px",
        style={"box_shadow": styles.NEU_SHADOW},
        flex_direction=["column", "row"],
        margin_bottom="4",
    )


def recibos_table() -> rx.Component:
    return rx.table.root(
        rx.table.header(
            rx.table.row(
                rx.table.column_header_cell("Período"),
                rx.table.column_header_cell("Propiedad"),
                rx.table.column_header_cell("Servicio"),
                rx.table.column_header_cell("Desde"),
                rx.table.column_header_cell("Hasta"),
                rx.table.column_header_cell("Días"),
                rx.table.column_header_cell("Valor"),
                rx.table.column_header_cell("Vencimiento"),
                rx.table.column_header_cell("Estado"),
                rx.table.column_header_cell("Acciones", text_align="right"),
            )
        ),
        rx.table.body(
            rx.foreach(
                RecibosState.recibos,
                lambda recibo: rx.table.row(
                    rx.table.cell(recibo.periodo_recibo),
                    rx.table.cell(recibo.propiedad_nombre),
                    rx.table.cell(rx.badge(recibo.tipo_servicio, variant="soft")),
                    rx.table.cell(recibo.fecha_desde),
                    rx.table.cell(recibo.fecha_hasta),
                    rx.table.cell(recibo.dias_facturados),
                    rx.table.cell(recibo.valor_formato),
                    rx.table.cell(recibo.fecha_vencimiento),
                    rx.table.cell(
                        rx.badge(recibo.estado, color_scheme=recibo.clase_estado)
                    ),
                    rx.table.cell(
                        rx.hstack(
                            rx.cond(
                                (recibo.estado == "Pendiente")
                                & AuthState.check_action("Recibos Publicos", "EDITAR"),
                                rx.tooltip(
                                    rx.icon_button(
                                        rx.icon("dollar_sign", size=16),
                                        size="2",
                                        variant="soft",
                                        color_scheme="green",
                                        on_click=lambda: RecibosState.open_payment_modal(
                                            recibo
                                        ),
                                    ),
                                    content="Registrar pago",
                                ),
                            ),
                            rx.cond(
                                (recibo.estado != "Pagado")
                                & AuthState.check_action("Recibos Publicos", "EDITAR"),
                                rx.tooltip(
                                    rx.icon_button(
                                        rx.icon("pencil", size=16),
                                        size="2",
                                        variant="ghost",
                                        on_click=lambda: RecibosState.open_edit_modal(
                                            recibo
                                        ),
                                    ),
                                    content="Editar recibo",
                                ),
                            ),
                            rx.tooltip(
                                rx.icon_button(
                                    rx.icon("eye", size=16),
                                    size="2",
                                    variant="ghost",
                                    color_scheme="blue",
                                    on_click=lambda: RecibosState.open_detail_modal(
                                        recibo
                                    ),
                                ),
                                content="Ver detalle",
                            ),
                            rx.cond(
                                (recibo.estado != "Pagado")
                                & AuthState.check_action(
                                    "Recibos Publicos", "ELIMINAR"
                                ),
                                rx.tooltip(
                                    rx.icon_button(
                                        rx.icon("trash-2", size=16),
                                        size="2",
                                        variant="ghost",
                                        color_scheme="red",
                                        on_click=lambda: RecibosState.delete_recibo(
                                            recibo.id_recibo_publico
                                        ),
                                    ),
                                    content="Eliminar recibo",
                                ),
                            ),
                            justify="end",
                            spacing="2",
                        ),
                        text_align="right",
                    ),
                ),
            )
        ),
        width="100%",
        variant="surface",
    )


def recibos_content() -> rx.Component:
    return rx.vstack(
        rx.heading("Gestión de Recibos Públicos", size="6"),
        rx.text(
            "Administre los vencimientos y pagos de servicios públicos.", color="gray"
        ),
        rx.divider(),
        filtros_bar(),
        rx.cond(
            RecibosState.is_loading,
            rx.center(rx.spinner()),
            recibos_table(),
        ),
        modal_form(),
        payment_modal(),
        detail_modal(),
        spacing="5",
        padding="6",
        width="100%",
        align="stretch",
    )


@rx.page(
    route="/recibos-publicos",
    title="Recibos Públicos | Inmobiliaria Velar",
    on_load=[AuthState.require_login, RecibosState.on_load],
)
def recibos_publicos_page() -> rx.Component:
    return dashboard_layout(recibos_content())
