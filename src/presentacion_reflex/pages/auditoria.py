import reflex as rx

from src.presentacion_reflex.components.layout.dashboard_layout import dashboard_layout
from src.presentacion_reflex.state.auditoria_state import AuditoriaState


def filters_bar() -> rx.Component:
    return rx.flex(
        rx.input(
            placeholder="Buscar por usuario o detalle...",
            on_change=lambda val: [AuditoriaState.set_search(val), AuditoriaState.load_logs()],
            icon="search",
            width="350px",
        ),
        rx.select.root(
            rx.select.trigger(placeholder="Filtrar por Tabla"),
            rx.select.content(
                rx.select.group(
                    rx.select.item("Todas", value="Todas"),
                    rx.select.item("PROPIEDADES", value="PROPIEDADES"),
                    rx.select.item("CONTRATOS", value="CONTRATOS"),
                    rx.select.item("PERSONAS", value="PERSONAS"),
                    rx.select.item("USUARIOS", value="USUARIOS"),
                    rx.select.item("PAGOS", value="PAGOS"),
                )
            ),
            value=AuditoriaState.filter_tabla,
            on_change=lambda val: [
                AuditoriaState.set_filter_tabla(val),
                AuditoriaState.load_logs(),
            ],
        ),
        rx.spacer(),
        rx.tooltip(
            rx.button(
                rx.icon("refresh-cw"),
                "Actualizar",
                variant="soft",
                on_click=AuditoriaState.load_logs,
            ),
            content="Actualizar registros de auditoría",
        ),
        width="100%",
        gap="3",
        align="center",
        padding_bottom="4",
    )


def audit_table() -> rx.Component:
    return rx.table.root(
        rx.table.header(
            rx.table.row(
                rx.table.column_header_cell("Fecha"),
                rx.table.column_header_cell("Usuario"),
                rx.table.column_header_cell("Entidad"),
                rx.table.column_header_cell("Acción"),
                rx.table.column_header_cell("Detalle del Cambio"),
            )
        ),
        rx.table.body(
            rx.foreach(
                AuditoriaState.logs,
                lambda log: rx.table.row(
                    rx.table.cell(log.fecha_cambio, white_space="nowrap"),
                    rx.table.cell(rx.text(log.usuario, weight="medium")),
                    rx.table.cell(rx.badge(log.tabla, variant="outline")),
                    rx.table.cell(
                        rx.badge(log.accion, color_scheme=log.color_scheme, variant="soft")
                    ),
                    rx.table.cell(
                        rx.text(
                            log.detalle,
                            size="1",
                            color="gray",
                            overflow="hidden",
                            text_overflow="ellipsis",
                            white_space="nowrap",
                            max_width="400px",
                        ),
                        title=log.detalle,  # Tooltip nativo
                    ),
                ),
            )
        ),
        variant="surface",
        width="100%",
    )


def auditoria_content() -> rx.Component:
    return rx.vstack(
        rx.heading("Auditoría de Cambios", size="6"),
        rx.text("Historial de operaciones críticas y modificaciones del sistema.", color="gray"),
        rx.divider(),
        filters_bar(),
        rx.cond(AuditoriaState.is_loading, rx.center(rx.spinner()), audit_table()),
        spacing="5",
        padding="6",
        width="100%",
        on_mount=AuditoriaState.load_logs,
    )


from src.presentacion_reflex.state.auth_state import AuthState


@rx.page(
    route="/auditoria",
    title="Auditoría | Inmobiliaria Velar",
    on_load=[AuthState.require_login, AuditoriaState.load_logs],
)
def auditoria_page() -> rx.Component:
    return dashboard_layout(auditoria_content())
