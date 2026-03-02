import reflex as rx

from src.presentacion_reflex.components.layout.dashboard_layout import dashboard_layout
from src.presentacion_reflex.state.auth_state import AuthState
from src.presentacion_reflex.state.auditoria_state import AuditoriaState

from src.presentacion_reflex.components.neuro_elements import neuro_input, neuro_button, neuro_select_root
from src.presentacion_reflex import styles

def filters_bar() -> rx.Component:
    return rx.flex(
        neuro_input(
            placeholder="Buscar por usuario o detalle...",
            on_change=lambda val: [AuditoriaState.set_search(val), AuditoriaState.load_logs()],
            width=["100%", "350px"],
        ),
        neuro_select_root(
            [
                rx.select.item("Todas", value="Todas"),
                rx.select.item("PROPIEDADES", value="PROPIEDADES"),
                rx.select.item("CONTRATOS", value="CONTRATOS"),
                rx.select.item("PERSONAS", value="PERSONAS"),
                rx.select.item("USUARIOS", value="USUARIOS"),
                rx.select.item("PAGOS", value="PAGOS"),
            ],
            placeholder="Filtrar por Tabla",
            value=AuditoriaState.filter_tabla,
            on_change=lambda val: [
                AuditoriaState.set_filter_tabla(val),
                AuditoriaState.load_logs(),
            ],
            width=["100%", "200px"],
        ),
        rx.spacer(),
        neuro_button(
            rx.hstack(rx.icon("refresh-cw"), rx.text("Actualizar")),
            on_click=AuditoriaState.load_logs,
            width=["100%", "auto"],
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


def auditoria_table() -> rx.Component:
    return rx.table.root(
        rx.table.header(
            rx.table.row(
                rx.table.column_header_cell("Fecha"),
                rx.table.column_header_cell("Usuario"),
                rx.table.column_header_cell("Tabla/Módulo"),
                rx.table.column_header_cell("Acción"),
                rx.table.column_header_cell("Detalles"),
            )
        ),
        rx.table.body(
            rx.foreach(
                AuditoriaState.logs,
                lambda log: rx.table.row(
                    rx.table.cell(log.fecha_cambio),
                    rx.table.cell(log.usuario),
                    rx.table.cell(rx.badge(log.tabla, variant="soft")),
                    rx.table.cell(
                        rx.badge(
                            log.accion,
                            color_scheme=rx.match(
                                log.accion,
                                ("INSERT", "green"),
                                ("UPDATE", "blue"),
                                ("DELETE", "red"),
                                "gray",
                            ),
                        )
                    ),
                    rx.table.cell(log.detalle),
                ),
            )
        ),
        width="100%",
        variant="surface",
    )


def auditoria_content() -> rx.Component:
    return rx.vstack(
        rx.heading("Registro de Auditoría", size="6"),
        rx.text("Seguimiento de cambios y acciones en el sistema.", color="gray"),
        rx.divider(),
        filters_bar(),
        rx.cond(
            AuditoriaState.is_loading,
            rx.center(rx.spinner()),
            auditoria_table(),
        ),
        spacing="5",
        padding="6",
        width="100%",
        align="stretch",
    )


@rx.page(
    route="/auditoria",
    title="Auditoría | Inmobiliaria Velar",
    on_load=[AuthState.require_login, AuditoriaState.load_logs],
)
def auditoria_page() -> rx.Component:
    return dashboard_layout(auditoria_content())
