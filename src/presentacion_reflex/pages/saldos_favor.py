
import reflex as rx
from src.presentacion_reflex.components.layout.dashboard_layout import dashboard_layout
from src.presentacion_reflex.state.saldos_state import SaldosState
from src.presentacion_reflex.state.auth_state import AuthState

def create_saldo_modal() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
             rx.dialog.title("Registrar Saldo a Favor"),
             rx.dialog.description("Registre un dinero a favor de un propietario o asesor."),
             
             rx.vstack(
                 rx.cond(
                     SaldosState.error_message != "",
                     rx.callout(SaldosState.error_message, icon="triangle_alert", color_scheme="red", width="100%")
                 ),
                 
                 rx.text("Tipo Beneficiario", size="2", weight="bold"),
                 rx.select(
                     ["Propietario", "Asesor"],
                     value=SaldosState.form_tipo_beneficiario,
                     on_change=SaldosState.set_form_tipo_beneficiario
                 ),
                 
                 rx.text("ID Beneficiario (Documento/ID)", size="2", weight="bold"),
                 rx.input(
                     value=SaldosState.form_id_beneficiario,
                     on_change=SaldosState.set_form_id_beneficiario_safe,
                     type="number",
                     placeholder="ID del Propietario o Asesor"
                 ),
                 
                 rx.text("Valor ($)", size="2", weight="bold"),
                 rx.input(
                     value=SaldosState.form_valor,
                     on_change=SaldosState.set_form_valor_safe,
                     type="number",
                     placeholder="Monto en pesos"
                 ),
                 
                 rx.text("Motivo", size="2", weight="bold"),
                 rx.input(
                     value=SaldosState.form_motivo,
                     on_change=SaldosState.set_form_motivo,
                     placeholder="Ej: Pago doble de administración"
                 ),
                 
                 rx.text("Observaciones", size="2", weight="bold"),
                 rx.text_area(
                     value=SaldosState.form_observaciones,
                     on_change=SaldosState.set_form_observaciones,
                     placeholder="Detalles adicionales..."
                 ),
                 
                 spacing="3",
                 margin_y="4"
             ),
             
             rx.flex(
                 rx.dialog.close(
                     rx.button("Cancelar", variant="soft", color_scheme="gray", on_click=SaldosState.close_create_modal)
                 ),
                 rx.button("Guardar", on_click=SaldosState.create_saldo, loading=SaldosState.is_loading),
                 spacing="3",
                 justify="end",
             ),
        ),
        open=SaldosState.show_create_modal,
        on_open_change=SaldosState.set_show_create_modal,
    )

def saldos_table() -> rx.Component:
    return rx.table.root(
        rx.table.header(
            rx.table.row(
                rx.table.column_header_cell("Fecha"),
                rx.table.column_header_cell("Tipo"),
                rx.table.column_header_cell("Beneficiario ID"),
                rx.table.column_header_cell("Motivo"),
                rx.table.column_header_cell("Valor"),
                rx.table.column_header_cell("Estado"),
                rx.table.column_header_cell("Acciones"),
            )
        ),
        rx.table.body(
             rx.foreach(
                SaldosState.saldos,
                lambda saldo: rx.table.row(
                    rx.table.cell(saldo.fecha_generacion),
                    rx.table.cell(rx.badge(saldo.tipo_beneficiario, color_scheme="blue", variant="soft")),
                    rx.table.cell(rx.cond(saldo.tipo_beneficiario == "Propietario", str(saldo.id_propietario), str(saldo.id_asesor))),
                    rx.table.cell(saldo.motivo),
                    rx.table.cell(rx.text(f"${saldo.valor_saldo:,.0f}", weight="bold")),
                    rx.table.cell(
                        rx.badge(
                            saldo.estado, 
                            color_scheme=rx.cond(saldo.estado == "Pendiente", "amber", "green"),
                            variant="solid"
                        )
                    ),
                    rx.table.cell(
                        rx.cond(
                            saldo.estado == "Pendiente",
                            rx.hstack(
                                rx.cond(
                                    AuthState.check_action("Saldos Favor", "EDITAR"),
                                    rx.tooltip(
                                        rx.button(rx.icon("circle_check", size=16), size="1", color_scheme="green", variant="ghost", on_click=lambda: SaldosState.action_saldo(saldo.id_saldo, "aplicar")),
                                        content="Marcar como Aplicado"
                                    )
                                ),
                                rx.cond(
                                    AuthState.check_action("Saldos Favor", "EDITAR"),
                                    rx.tooltip(
                                        rx.button(rx.icon("undo-2", size=16), size="1", color_scheme="blue", variant="ghost", on_click=lambda: SaldosState.action_saldo(saldo.id_saldo, "devolver")),
                                        content="Marcar como Devuelto"
                                    )
                                ),
                                rx.cond(
                                    AuthState.check_action("Saldos Favor", "ELIMINAR"),
                                    rx.tooltip(
                                        rx.button(rx.icon("trash-2", size=16), size="1", color_scheme="red", variant="ghost", on_click=lambda: SaldosState.action_saldo(saldo.id_saldo, "eliminar")),
                                        content="Eliminar"
                                    )
                                ),
                                spacing="2"
                            ),
                            rx.text("-", color="gray")
                        )
                    )
                )
            )
        ),
        variant="surface"
    )

def saldos_content() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.heading("Saldos a Favor", size="6"),
            rx.spacer(),
            rx.cond(
                AuthState.check_action("Saldos Favor", "CREAR"),
                rx.button(
                    rx.icon("plus", size=18),
                    "Nuevo Saldo",
                    on_click=SaldosState.open_create_modal
                )
            ),
            width="100%",
            align="center"
        ),
        rx.text("Gestione dineros pendientes por aplicar o devolver a propietarios y asesores.", color="gray"),
        rx.divider(),
        
        rx.hstack(
            rx.select(
                ["Todos", "Propietario", "Asesor"],
                value=SaldosState.filter_tipo,
                on_change=lambda val: [SaldosState.set_filter_tipo(val), SaldosState.load_saldos()]
            ),
            rx.select(
                ["Pendiente", "Historial"],
                value=SaldosState.filter_estado,
                on_change=lambda val: [SaldosState.set_filter_estado(val), SaldosState.load_saldos()]
            ),
            rx.spacer(),
            rx.button(rx.icon("refresh-cw", size=16), variant="ghost", on_click=SaldosState.load_saldos),
            width="100%"
        ),
        
        rx.cond(
            SaldosState.is_loading,
            rx.center(rx.spinner()),
            saldos_table()
        ),
        
        create_saldo_modal(),

        spacing="5",
        padding="6",
        width="100%",
        on_mount=SaldosState.load_saldos
    )

@rx.page(route="/saldos-favor", title="Saldos a Favor | Inmobiliaria Velar", on_load=[AuthState.require_login, SaldosState.load_saldos])
def saldos_page() -> rx.Component:
    return dashboard_layout(saldos_content())
