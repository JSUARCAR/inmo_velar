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
    tablas_vencimientos_detalle,
)
from src.presentacion_reflex.components.layout.dashboard_layout import dashboard_layout
from src.presentacion_reflex.state.auth_state import AuthState
from src.presentacion_reflex.state.dashboard_state import DashboardState
from src.presentacion_reflex.components.neuro_elements import (
    neuro_panel,
    neuro_progress,
    neuro_spinner,
    neuro_callout,
)
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
                    color=styles.TEXT_PRIMARY,
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
                        neuro_spinner(size="3"),
                        rx.text(
                            "Procesando métricas en tiempo real...",
                            color=styles.TEXT_SECONDARY,
                            size="2",
                        ),
                        spacing="3",
                    ),
                    padding="100px",
                    width="100%",
                ),
            ),
            # Error Message
            rx.cond(
                DashboardState.error_message != "",
                neuro_callout(
                    DashboardState.error_message,
                    icon="circle_alert",
                    color_scheme="red",
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
                            weight="medium",
                            color=styles.TEXT_SECONDARY,
                            letter_spacing="0.1em",
                        ),
                        rx.box(
                            kpi_card(
                                "Ocupación Financiera",
                                rx.text(
                                    DashboardState.kpi_ocupacion_financiera_view, "%"
                                ),
                                "bar-chart-2",
                                styles.BRAND_PRIMARY,
                                "Ingresos vs Potencial",
                                variant="elite",
                                hover_content=rx.vstack(
                                    rx.text(
                                        "Eficiencia de Ingresos",
                                        weight="bold",
                                        size="3",
                                    ),
                                    rx.separator(),
                                    rx.text(
                                        "Mide qué porcentaje del valor potencial total de la cartera se está recaudando efectivamente.",
                                        size="2",
                                        color=styles.TEXT_SECONDARY,
                                    ),
                                    rx.hstack(
                                        rx.text(
                                            "Recaudo Real:", weight="medium", size="2"
                                        ),
                                        rx.text(
                                            DashboardState.kpi_recaudo_real_view,
                                            weight="bold",
                                            color=styles.ACCENT_COLOR,
                                        ),
                                        justify="between",
                                        width="100%",
                                    ),
                                    rx.hstack(
                                        rx.text(
                                            "Potencial Total:",
                                            weight="medium",
                                            size="2",
                                        ),
                                        rx.text(
                                            DashboardState.kpi_potencial_total_view,
                                            weight="bold",
                                            color=styles.TEXT_TERTIARY,
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
                                rx.text(
                                    DashboardState.kpi_eficiencia_recaudo_view, "%"
                                ),
                                "wallet",
                                styles.TEXT_SECONDARY,
                                "Recaudado este mes",
                                variant="elite",
                                hover_content=rx.vstack(
                                    rx.text("Recaudo Mensual", weight="bold", size="2"),
                                    rx.separator(),
                                    rx.text(
                                        "Total recaudado en el mes actual: ",
                                        DashboardState.recaudo_mes_view,
                                        size="1",
                                    ),
                                    rx.text(
                                        "Meta de recaudo: ",
                                        DashboardState.kpi_potencial_total_view,
                                        size="1",
                                    ),
                                    spacing="1",
                                ),
                            ),
                            kpi_card(
                                "Potencial Total",
                                DashboardState.kpi_potencial_total_view,
                                "banknote",
                                styles.TEXT_TERTIARY,
                                "Cartera Total Estimada",
                                variant="elite",
                                hover_content=rx.vstack(
                                    rx.text(
                                        "Proyección de Cartera", weight="bold", size="2"
                                    ),
                                    rx.text(
                                        "Es la suma total del canon esperado de todos los contratos activos.",
                                        size="1",
                                        color=styles.TEXT_SECONDARY,
                                    ),
                                    spacing="1",
                                    width="100%",
                                ),
                            ),
                            class_name="grid-elite",
                        ),
                        spacing="5",
                        width="100%",
                        margin_bottom="8",
                    ),
                    tablas_vencimientos_detalle(),
                    rx.divider(margin_y="4"),
                    # 2. GRID PRINCIPAL (Análisis + Operativo)
                    rx.box(
                        # COLUMNA IZQUIERDA (Análisis Profundo - Span 2)
                        rx.vstack(
                            # A. Evolución (Tendencia Clave)
                            neuro_panel(
                                evolucion_chart(),
                                width="100%",
                                overflow="hidden",
                            ),
                            rx.spacer(),
                            # B. Gráficos de Detalle (2x2 Grid interno)
                            rx.box(
                                # Fila 1
                                top_asesores_chart(),
                                tunel_vencimientos_chart(),
                                # Fila 2
                                propiedades_tipo_chart(),
                                incidentes_pie_chart(),
                                class_name="grid-compact",
                                width="100%",
                            ),
                            spacing="5",
                            width="100%",
                            class_name="grid-main-left",
                        ),
                        # COLUMNA DERECHA (Pulso Operativo - Span 1)
                        rx.vstack(
                            rx.text(
                                "PULSO OPERATIVO",
                                size="2",
                                weight="medium",
                                color=styles.TEXT_SECONDARY,
                                letter_spacing="0.1em",
                            ),
                            # KPIs Compactos
                            rx.box(
                                kpi_card(
                                    "Cartera Mora",
                                    DashboardState.mora_monto_total_view,
                                    "circle_alert",
                                    styles.BRAND_PRIMARY,
                                    rx.text(
                                        DashboardState.mora_cantidad_contratos_view,
                                        " ctros",
                                    ),
                                    variant="compact",
                                    hover_content=rx.vstack(
                                        rx.text(
                                            "Cartera Vencida", weight="bold", size="2"
                                        ),
                                        rx.text(
                                            "Total pendiente de cobro fuera de fecha límite.",
                                            size="1",
                                            color=styles.TEXT_SECONDARY,
                                        ),
                                        rx.hstack(
                                            rx.text("Contratos:", size="1"),
                                            rx.text(
                                                DashboardState.mora_cantidad_contratos_view,
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
                                    styles.TEXT_SECONDARY,
                                    rx.text(
                                        DashboardState.recaudo_porcentaje_view, "%"
                                    ),
                                    variant="compact",
                                    hover_content=rx.vstack(
                                        rx.text(
                                            "Recaudo Mensual", weight="bold", size="2"
                                        ),
                                        rx.text(
                                            "Ingresos procesados en el mes corriente.",
                                            size="1",
                                            color=styles.TEXT_SECONDARY,
                                        ),
                                        neuro_progress(
                                            value=DashboardState.flujo_porcentaje_int_view,
                                            color_scheme="orange",
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
                                    styles.BRAND_PRIMARY,
                                    rx.text(
                                        DashboardState.ocupacion_ocupadas_view,
                                        "/",
                                        DashboardState.ocupacion_disponibles_view,
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
                                    styles.TEXT_TERTIARY,
                                    rx.text(
                                        DashboardState.comisiones_cantidad_view,
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
                                    DashboardState.contratos_count_view,
                                    "file-text",
                                    styles.TEXT_SECONDARY,
                                    "Activos",
                                    variant="compact",
                                    hover_content=rx.text(
                                        "Total de contratos de arrendamiento vigentes.",
                                        size="1",
                                    ),
                                ),
                                kpi_card(
                                    "Recibos Pend.",
                                    DashboardState.recibos_monto_total_view,
                                    "receipt",
                                    styles.TEXT_SECONDARY,
                                    rx.text(
                                        DashboardState.recibos_cantidad_view, " unds"
                                    ),
                                    variant="compact",
                                    hover_content=rx.text(
                                        "Recibos de servicios públicos o administración pendientes de pago.",
                                        size="1",
                                    ),
                                ),
                                class_name="grid-compact",
                                width="100%",
                            ),
                            rx.divider(margin_y="4"),
                            # Acción Requerida (Vencimientos Próximos)
                            rx.box(
                                rx.text(
                                    "ACCIÓN REQUERIDA",
                                    size="2",
                                    weight="medium",
                                    color="orange.10",
                                    letter_spacing="0.1em",
                                    margin_bottom="2",
                                ),
                                vencimientos_chart(),  # Muestra "Contratos por Vencer"
                                width="100%",
                            ),
                            padding="5",
                            style=styles.NEU_PANEL_STYLE,
                            height="fit-content",
                            width="100%",
                            class_name="grid-main-right",
                        ),
                        class_name="grid-main",
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
            min_height="100vh",
        ),
    )


from src.presentacion_reflex.state.alertas_state import AlertasState


# Ruta protegida
@rx.page(
    route="/dashboard",
    on_load=[
        AuthState.require_login,
        DashboardState.on_load,
        AlertasState.check_alerts,
    ],
)
def dashboard():
    return dashboard_page()
