"""
Componente de Tabla Consolidada de Vencimientos para Dashboard - Reflex
Muestra una lista unificada de contratos próximos a vencer (Mandato + Arrendamiento).
"""

import reflex as rx
from src.presentacion_reflex.state.dashboard_state import DashboardState
from src.presentacion_reflex import styles
from src.presentacion_reflex.components.neuro_elements import (
    neuro_badge,
)


def badge_dias(dias: int) -> rx.Component:
    """Retorna un badge de color según los días restantes."""
    return rx.cond(
        dias <= 30,
        neuro_badge(dias.to(str), " días", color_scheme="red"),
        rx.cond(
            dias <= 60,
            neuro_badge(dias.to(str), " días", color_scheme="orange"),
            neuro_badge(dias.to(str), " días", color_scheme="amber"),
        ),
    )


def tabla_vencimientos_consolidados() -> rx.Component:
    """Tabla consolidada de vencimientos (Mandato + Arrendamiento) con scroll vertical."""
    return rx.card(
        rx.vstack(
            rx.hstack(
                rx.icon("clock", color="var(--brand-primary)", size=20),
                rx.text(
                    "Vencimientos Próximos (90 Días)",
                    size="4",
                    weight="bold",
                    color=styles.TEXT_PRIMARY,
                ),
                rx.spacer(),
                align="center",
                spacing="2",
            ),
            rx.divider(),
            rx.box(
                rx.cond(
                    DashboardState.vencimientos_lista.length() > 0,
                    rx.table.root(
                        rx.table.header(
                            rx.table.row(
                                rx.table.column_header_cell(
                                    "Propiedad",
                                    color=styles.TEXT_SECONDARY,
                                    weight="medium",
                                ),
                                rx.table.column_header_cell(
                                    "Fecha Fin",
                                    color=styles.TEXT_SECONDARY,
                                    weight="medium",
                                    text_align="right",
                                ),
                            ),
                            style={
                                "position": "sticky",
                                "top": 0,
                                "z_index": 1,
                                "background": styles.BG_PANEL,
                            },
                        ),
                        rx.table.body(
                            rx.foreach(
                                DashboardState.vencimientos_lista,
                                lambda item: rx.table.row(
                                    rx.table.cell(
                                        rx.text(
                                            item.get("direccion", "N/A"),
                                            size="2",
                                            color=styles.TEXT_SECONDARY,
                                        )
                                    ),
                                    rx.table.cell(
                                        rx.hstack(
                                            rx.text(
                                                item.get("fecha_fin", "N/A"), size="2"
                                            ),
                                            badge_dias(
                                                item.get("dias_restantes", 0).to(int)
                                            ),
                                            justify="end",
                                            align="center",
                                            spacing="2",
                                        )
                                    ),
                                    align="center",
                                ),
                            )
                        ),
                        variant="ghost",
                        size="1",
                        width="100%",
                    ),
                    rx.center(
                        rx.vstack(
                            rx.icon("inbox", size=32, color=styles.TEXT_TERTIARY),
                            rx.text(
                                "No hay contratos próximos a vencer.",
                                size="2",
                                color=styles.TEXT_SECONDARY,
                            ),
                            spacing="2",
                            align="center",
                        ),
                        padding="6",
                        width="100%",
                    ),
                ),
                max_height="320px",
                overflow_y="auto",
                width="100%",
            ),
            spacing="3",
            width="100%",
        ),
        size="2",
        variant="ghost",
        style=styles.NEU_PANEL_STYLE,
        width="100%",
        height="100%",
    )
