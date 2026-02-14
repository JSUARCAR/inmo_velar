"""
Página del Dashboard Principal - Reflex
Tablero de control ejecutivo con métricas clave.
"""

import reflex as rx

from src.presentacion_reflex.components.dashboard import (
    dashboard_filters,
    evolucion_chart,
    incidentes_pie_chart,
    kpi_card,
    propiedades_tipo_chart,
    top_asesores_chart,
    tunel_vencimientos_chart,
    vencimientos_chart,
)
from src.presentacion_reflex.components.layout.dashboard_layout import dashboard_layout
from src.presentacion_reflex.state.auth_state import AuthState
from src.presentacion_reflex.state.dashboard_state import DashboardState
from src.presentacion_reflex import styles


def dashboard_page() -> rx.Component:
    """
    Dashboard principal con KPIs y gráficos.
    Diseño Expert Elite: Jerarquía visual optimizada y distribución eficiente.
    """

    return dashboard_layout(
        rx.vstack(
            # Título y Header
            rx.flex(
                rx.heading(
                    "Dashboard Ejecutivo",
                    size="8",
                    font_size=["1.75em", "2em", "2.5em", "3em"],
                    weight="bold",
                    color="gray.12",
                ),
                rx.spacer(),
                dashboard_filters(),
                align="center",
                width="100%",
                padding_bottom="4",
                flex_direction=["column", "column", "row", "row"],
                spacing="4",
            ),
            # Loading Spinner
            rx.cond(
                DashboardState.is_loading,
                rx.center(
                    rx.vstack(
                        rx.spinner(size="3", color="indigo"),
                        rx.text("Procesando métricas en tiempo real...", color="gray.11", size="2"),
                        spacing="3",
                    ),
                    padding="100px",
                    width="100%",
                ),
            ),
            # Error Message
            rx.cond(
                DashboardState.error_message != "",
                rx.callout(
                    DashboardState.error_message,
                    icon="circle_alert",
                    color_scheme="red",
                    role="alert",
                    width="100%",
                ),
            ),
            # Contenido Principal
            rx.cond(
                ~DashboardState.is_loading & (DashboardState.error_message == ""),
                rx.vstack(
                    # 1. NIVEL ESTRATÉGICO (Elite KPIs)
                    rx.vstack(
                        rx.text(
                            "VISIÓN ESTRATÉGICA",
                            size="2",
                            weight="bold",
                            color="gray.9",
                            letter_spacing="0.1em",
                        ),
                        rx.grid(
                            kpi_card(
                                "Ocupación Financiera",
                                rx.text(DashboardState.kpi_ocupacion_financiera_view, "%"),
                                "bar-chart-2",
                                "blue",
                                "Ingresos vs Potencial",
                                variant="elite",
                                hover_content=rx.vstack(
                                    rx.text("Eficiencia de Ingresos", weight="bold", size="3"),
                                    rx.separator(),
                                    rx.text(
                                        "Mide qué porcentaje del valor potencial total de la cartera se está recaudando efectivamente.",
                                        size="2",
                                        color="gray.11",
                                    ),
                                    rx.hstack(
                                        rx.text("Recaudo Real:", weight="medium", size="2"),
                                        rx.text(
                                            DashboardState.kpi_recaudo_real_view,
                                            weight="bold",
                                            color="blue.9",
                                        ),
                                        justify="between",
                                        width="100%",
                                    ),
                                    rx.hstack(
                                        rx.text("Potencial Total:", weight="medium", size="2"),
                                        rx.text(
                                            DashboardState.kpi_potencial_total_view,
                                            weight="bold",
                                            color="gray.9",
                                        ),
                                        justify="between",
                                        width="100%",
                                    ),
                                    spacing="2",
                                    width="100%",
                                ),
                            ),
                             kpi_card(
                                "Eficiencia Recaudo",
                                rx.text(DashboardState.kpi_eficiencia_recaudo_view, "%"),
                                "wallet",
                                "green",
                                "Recaudado este mes",
                                variant="elite",
                                hover_content=rx.vstack(
                                    rx.text("Recaudo Mensual", weight="bold", size="2"),
                                    rx.separator(),
                                    rx.text(
                                        f"Total recaudado en el mes actual: {DashboardState.recaudo_mes_view}",
                                        size="1",
                                    ),
                                    rx.text(
                                        f"Meta de recaudo: {DashboardState.kpi_potencial_total_view}",
                                        size="1",
                                    ),
                                    spacing="1",
                                ),
                            ),
                            kpi_card(
                                "Potencial Total",
                                DashboardState.kpi_potencial_total_view,
                                "banknote",
                                "indigo",
                                "Cartera Total Estimada",
                                variant="elite",
                                hover_content=rx.vstack(
                                    spacing="2",
                                    width="100%",
                                ),
                            ),
                            # columns=["1", "2", "3", "3"],
                            grid_template_columns=[
                                "repeat(1, 1fr)",
                                "repeat(2, 1fr)",
                                "repeat(3, 1fr)",
                                "repeat(3, 1fr)",
                            ],
                            spacing="5",
                            width="100%",
                        ),
                        spacing="3",
                        width="100%",
                        margin_bottom="6",
                    ),
                    # 2. GRID PRINCIPAL (Análisis + Operativo)
                    rx.grid(
                        # COLUMNA IZQUIERDA (Análisis Profundo - Span 2)
                        rx.vstack(
                            # A. Evolución (Tendencia Clave)
                            rx.box(
                                evolucion_chart(),
                                width="100%",
                                box_shadow="0 4px 6px -1px rgba(0, 0, 0, 0.1)",
                                border_radius="12px",
                                overflow="hidden",
                            ),
                            rx.spacer(),
                            # B. Gráficos de Detalle (2x2 Grid interno)
                            rx.grid(
                                # Fila 1
                                top_asesores_chart(),
                                tunel_vencimientos_chart(),
                                # Fila 2
                                propiedades_tipo_chart(),
                                incidentes_pie_chart(),
                                # columns=["1", "1", "2", "2"],
                                grid_template_columns=[
                                    "repeat(1, 1fr)",
                                    "repeat(1, 1fr)",
                                    "repeat(2, 1fr)",
                                    "repeat(2, 1fr)",
                                ],
                                spacing="4",
                                width="100%",
                            ),
                            spacing="5",
                            width="100%",
                            grid_column=["span 1", "span 1", "span 2", "span 2"],
                        ),
                        # COLUMNA DERECHA (Pulso Operativo - Span 1)
                        rx.vstack(
                            rx.text(
                                "PULSO OPERATIVO",
                                size="2",
                                weight="bold",
                                color="gray.9",
                                letter_spacing="0.1em",
                            ),
                            # KPIs Compactos
                            rx.grid(
                                kpi_card(
                                    "Cartera Mora",
                                    DashboardState.mora_monto_total_view,
                                    "circle_alert",
                                    "red",
                                    rx.text(
                                        DashboardState.mora_data["cantidad_contratos"].to(str),
                                        " ctros",
                                    ),
                                    variant="compact",
                                    hover_content=rx.vstack(
                                        rx.text("Cartera Vencida", weight="bold", size="2"),
                                        rx.text(
                                            "Total pendiente de cobro fuera de fecha límite.",
                                            size="1",
                                            color="gray.11",
                                        ),
                                        rx.hstack(
                                            rx.text("Contratos:", size="1"),
                                            rx.text(
                                                DashboardState.mora_data["cantidad_contratos"].to(
                                                    str
                                                ),
                                                weight="bold",
                                                size="1",
                                            ),
                                            justify="between",
                                            width="100%",
                                        ),
                                        width="100%",
                                    ),
                                ),
                                kpi_card(
                                    "Recaudo Mes",
                                    DashboardState.recaudo_mes_view,
                                    "wallet",
                                    "green",
                                    rx.text(DashboardState.recaudo_porcentaje_view, "%"),
                                    variant="compact",
                                    hover_content=rx.vstack(
                                        rx.text("Recaudo Mensual", weight="bold", size="2"),
                                        rx.text(
                                            "Ingresos procesados en el mes corriente.",
                                            size="1",
                                            color="gray.11",
                                        ),
                                        rx.progress(
                                            value=DashboardState.flujo_data["porcentaje"].to(int),
                                            color_scheme="green",
                                            height="6px",
                                            width="100%",
                                        ),
                                        width="100%",
                                    ),
                                ),
                                kpi_card(
                                    "Ocupación",
                                    rx.text(
                                        DashboardState.ocupacion_porcentaje_view,
                                        "%",
                                    ),
                                    "home",
                                    "blue",
                                    rx.text(
                                        DashboardState.ocupacion_data["ocupadas"].to(str),
                                        "/",
                                        DashboardState.ocupacion_data["disponibles"].to(str),
                                    ),
                                    variant="compact",
                                    hover_content=rx.text(
                                        "Relación entre propiedades alquiladas y total disponible.",
                                        size="1",
                                    ),
                                ),
                                kpi_card(
                                    "Comisiones",
                                    DashboardState.comisiones_monto_total_view,
                                    "credit-card",
                                    "amber",
                                    rx.text(
                                        DashboardState.comisiones_data["cantidad_liquidaciones"].to(
                                            str
                                        ),
                                        " pend",
                                    ),
                                    variant="compact",
                                    hover_content=rx.text(
                                        "Valor acumulado de comisiones pendientes de liquidar a asesores.",
                                        size="1",
                                    ),
                                ),
                                kpi_card(
                                    "Contratos",
                                    DashboardState.contratos_count.to(str),
                                    "file-text",
                                    "indigo",
                                    "Activos",
                                    variant="compact",
                                    hover_content=rx.text(
                                        "Total de contratos de arrendamiento vigentes.", size="1"
                                    ),
                                ),
                                kpi_card(
                                    "Recibos Pend.",
                                    DashboardState.recibos_monto_total_view,
                                    "receipt",
                                    "rose",
                                    rx.text(
                                        DashboardState.recibos_data["cantidad"].to(str), " unds"
                                    ),
                                    variant="compact",
                                    hover_content=rx.text(
                                        "Recibos de servicios públicos o administración pendientes de pago.",
                                        size="1",
                                    ),
                                ),
                                # columns=["1", "2", "2", "2"],
                                grid_template_columns=[
                                    "repeat(1, 1fr)",
                                    "repeat(2, 1fr)",
                                    "repeat(2, 1fr)",
                                    "repeat(2, 1fr)",
                                ],
                                spacing="3",
                                width="100%",
                            ),
                            rx.divider(margin_y="4"),
                            # Acción Requerida (Vencimientos Próximos)
                            rx.box(
                                rx.text(
                                    "ACCIÓN REQUERIDA",
                                    size="2",
                                    weight="bold",
                                    color="orange.10",
                                    letter_spacing="0.1em",
                                    margin_bottom="2",
                                ),
                                vencimientos_chart(),  # Muestra "Contratos por Vencer"
                                width="100%",
                            ),
                            padding="5",
                            bg=styles.BG_PANEL,
                            border="1px solid var(--gray-4)",
                            border_radius="16px",
                            height="fit-content",
                            width="100%",
                            grid_column="span 1",
                        ),
                        # columns=["1", "1", "2", "3"],
                        grid_template_columns=[
                            "repeat(1, 1fr)",
                            "repeat(1, 1fr)",
                            "repeat(2, 1fr)",
                            "repeat(3, 1fr)",
                        ],
                        spacing="6",
                        width="100%",
                        align_items="start",
                    ),
                    spacing="6",
                    width="100%",
                ),
            ),
            spacing="4",
            width="100%",
            padding=["4", "6", "8", "32px"],
            # background removed to use default theme background
            min_height="100vh",
        ),
    )


# Ruta protegida
@rx.page(route="/dashboard", on_load=[AuthState.require_login, DashboardState.on_load])
def dashboard():
    return dashboard_page()
