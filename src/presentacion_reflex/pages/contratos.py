"""
Página de Contratos - Reflex Simplificada
"""

import reflex as rx
from src.presentacion_reflex import styles

from src.presentacion_reflex.components.layout.dashboard_layout import dashboard_layout
from src.presentacion_reflex.state.contratos_state import ContratosState


def contratos_page() -> rx.Component:
    return dashboard_layout(
        rx.vstack(
            rx.heading("Gestión de Contratos", size="8"),
            rx.text("Total de contratos: ", ContratosState.total_items.to(str)),
            rx.table.root(
                rx.table.header(
                    rx.table.row(
                        rx.table.column_header_cell("ID"),
                        rx.table.column_header_cell("Tipo"),
                    )
                ),
                rx.table.body(
                    rx.foreach(
                        ContratosState.contratos,
                        lambda c: rx.table.row(
                            rx.table.cell(c["id_contrato"].to(str)),
                            rx.table.cell(c["tipo_contrato"]),
                        )
                    )
                ),
                width="100%",
            ),
            spacing="4",
        )
    )


# Ruta protegida
@rx.page(route="/contratos")
def contratos():
    return contratos_page()
