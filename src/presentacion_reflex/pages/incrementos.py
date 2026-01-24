
import reflex as rx
from src.presentacion_reflex.components.layout.dashboard_layout import dashboard_layout
from src.presentacion_reflex.state.ipc_state import IPCState
from src.presentacion_reflex.state.auth_state import AuthState

def ipc_modal() -> rx.Component:
    return rx.dialog.root(
        rx.dialog.content(
             rx.dialog.title(rx.cond(IPCState.is_editing, "Editar IPC", "Registrar IPC")),
             rx.dialog.description("Ingrese los datos del índice para el año correspondiente."),
             
             rx.vstack(
                 rx.cond(
                     IPCState.error_message != "",
                     rx.callout(IPCState.error_message, icon="triangle_alert", color_scheme="red", width="100%")
                 ),
                 
                 rx.text("Año", size="2", weight="bold"),
                 rx.input(
                     value=IPCState.form_anio,
                     on_change=IPCState.set_anio,
                     type="number",
                     disabled=IPCState.is_editing, # No editar año una vez creado
                     placeholder="Ej: 2025"
                 ),
                 
                 rx.text("Valor (%)", size="2", weight="bold"),
                 rx.input(
                     value=IPCState.form_valor,
                     on_change=IPCState.set_valor,
                     type="number",
                     placeholder="Ej: 5.5"
                 ),
                 rx.text("Ingrese el valor porcentual (Ej: escriba 13.12 para 13.12%).", size="1", color="gray"),
                 
                 spacing="4",
                 margin_y="4"
             ),
             
             rx.flex(
                 rx.dialog.close(
                     rx.button("Cancelar", variant="soft", color_scheme="gray", on_click=IPCState.close_modal)
                 ),
                 rx.button("Guardar", on_click=IPCState.save_ipc, loading=IPCState.is_loading),
                 spacing="3",
                 justify="end",
             ),
        ),
        open=IPCState.show_modal,
        on_open_change=IPCState.set_show_modal,
    )

def ipc_table() -> rx.Component:
    return rx.table.root(
        rx.table.header(
            rx.table.row(
                rx.table.column_header_cell("Año"),
                rx.table.column_header_cell("Valor IPC"),
                rx.table.column_header_cell("Fecha Publicación"),
                rx.table.column_header_cell("Acciones"),
            )
        ),
        rx.table.body(
            rx.foreach(
                IPCState.ipcs,
                lambda ipc: rx.table.row(
                    rx.table.cell(rx.badge(ipc.anio, variant="outline")),
                    rx.table.cell(rx.text(f"{ipc.valor_ipc}%", weight="bold")),
                    rx.table.cell(ipc.fecha_publicacion),
                    rx.table.cell(
                        rx.cond(
                            AuthState.check_action("Incrementos", "EDITAR"),
                            rx.tooltip(
                                rx.button(
                                    rx.icon("pencil", size=16),
                                    size="1",
                                    variant="ghost",
                                    on_click=lambda: IPCState.open_edit_modal(ipc)
                                ),
                                content="Editar IPC"
                            )
                        )
                    )
                )
            )
        ),
        variant="surface"
    )

def incrementos_content() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.heading("Gestión de IPC / Incrementos", size="6"),
            rx.spacer(),
            rx.cond(
                AuthState.check_action("Incrementos", "CREAR"),
                rx.button(
                    rx.icon("plus", size=18),
                    "Nuevo Año",
                    on_click=IPCState.open_create_modal
                )
            ),
            width="100%",
            align="center"
        ),
        rx.text("Configure los valores del IPC anual para el cálculo automático de incrementos en cánones.", color="gray"),
        rx.divider(),
        
        rx.cond(
            IPCState.is_loading & ~IPCState.show_modal, # Show spinner if loading and modal not open (initial load)
            rx.center(rx.spinner()),
            ipc_table()
        ),
        
        ipc_modal(),

        spacing="5",
        padding="6",
        width="100%",
        on_mount=IPCState.load_ipcs
    )

@rx.page(route="/incrementos", title="IPC e Incrementos | Inmobiliaria Velar", on_load=[AuthState.require_login, IPCState.load_ipcs])
def incrementos_page() -> rx.Component:
    return dashboard_layout(incrementos_content())
