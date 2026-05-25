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
    Diseño Bento Grid: Alta densidad de datos y jerarquía visual optimizada.
    """

    return dashboard_layout(
        rx.vstack(
            # HEADER ESTRATÉGICO (Parchment Background, Whisper Shadow)
            rx.box(
                rx.flex(
                    rx.vstack(
                        rx.heading(
                            "Dashboard Ejecutivo",
                            size="8",
                            font_family=styles.FONT_DISPLAY,
                            weight="bold",
                            color=styles.TEXT_PRIMARY,
                        ),
                        rx.text(
                            "Análisis de rendimiento y control de activos",
                            size="2",
                            color=styles.TEXT_SECONDARY,
                            font_family=styles.FONT_SANS,
                        ),
                        spacing="1",
                        align="start",
                    ),
                    align="center",
                    width="100%",
                ),
                rx.box(
                    dashboard_filters(),
                    width="100%",
                    padding_top="4",
                ),
                width="100%",
                padding_x=["4", "6", "8", "10"],
                padding_y="6",
                background=styles.BG_PANEL,
                border_bottom=f"1px solid {styles.BORDER_DEFAULT}",
                box_shadow=styles.SHADOW_WHISPER,
                position="sticky",
                top="0",
                z_index="100",
            ),
            # CONTENIDO BENTO GRID
            rx.vstack(
                # Loading / Error states
                rx.cond(
                    DashboardState.is_loading,
                    rx.center(
                        rx.vstack(
                            neuro_spinner(size="3"),
                            rx.text(
                                "Procesando métricas INMOBILIARIA...",
                                color=styles.TEXT_SECONDARY,
                                size="2",
                                font_family=styles.FONT_SANS,
                            ),
                            spacing="3",
                        ),
                        padding="100px",
                        width="100%",
                    ),
                ),
                rx.cond(
                    DashboardState.error_message != "",
                    neuro_callout(
                        DashboardState.error_message,
                        icon="circle_alert",
                        color_scheme="red",
                        width="100%",
                    ),
                ),
                # Dashboard Grid
                rx.cond(
                    ~DashboardState.is_loading & (DashboardState.error_message == ""),
                    rx.grid(
                        # 1. KPIs ESTRATÉGICOS (Top Row - Direct in Grid)
                        kpi_card(
                            "Ocupación Financiera",
                            f"{DashboardState.kpi_ocupacion_financiera_view}%",
                            "bar-chart-2",
                            styles.BRAND_PRIMARY,
                            "Ingresos vs Potencial",
                            variant="elite",
                        ),
                        kpi_card(
                            "Eficiencia Recaudo",
                            f"{DashboardState.kpi_eficiencia_recaudo_view}%",
                            "wallet",
                            styles.TEXT_SECONDARY,
                            "Recaudado este mes",
                            variant="elite",
                        ),
                        kpi_card(
                            "Potencial Total",
                            DashboardState.kpi_potencial_total_view,
                            "banknote",
                            styles.TEXT_TERTIARY,
                            "Cartera Total Estimada",
                            variant="elite",
                        ),

                        # 2. ANÁLISIS DE EVOLUCIÓN (Middle Row - Left 2/3)
                        # rx.box(
                        #     evolucion_chart(),
                        #     style={"grid_column": rx.breakpoints(initial="span 1", lg="span 2")},
                        #     width="100%",
                        # ),
                        
                        # 3. TÚNEL DE VENCIMIENTOS (Middle Row - Right 1/3)
                        # rx.box(
                        #     tunel_vencimientos_chart(),
                        #     style={"grid_column": rx.breakpoints(initial="span 1", lg="span 1")},
                        #     width="100%",
                        # ),

                        # 4. PULSO OPERATIVO (Bottom Row - Full Width Actions)
                        rx.box(
                            rx.vstack(
                                rx.text(
                                    "PULSO OPERATIVO Y ACCIONES",
                                    size="2",
                                    weight="bold",
                                    color=styles.TEXT_SECONDARY,
                                    letter_spacing="0.1em",
                                    font_family=styles.FONT_SANS,
                                ),
                                rx.grid(
                                    kpi_card(
                                        "Cartera Mora",
                                        DashboardState.mora_monto_total_view,
                                        "circle_alert",
                                        styles.BRAND_PRIMARY,
                                        f"{DashboardState.mora_cantidad_contratos_view} ctros",
                                        variant="compact",
                                    ),
                                    kpi_card(
                                        "Recaudo Mes",
                                        DashboardState.recaudo_mes_view,
                                        "wallet",
                                        styles.TEXT_SECONDARY,
                                        f"{DashboardState.recaudo_porcentaje_view}%",
                                        variant="compact",
                                    ),
                                    kpi_card(
                                        "Ocupación",
                                        f"{DashboardState.ocupacion_porcentaje_view}%",
                                        "home",
                                        styles.BRAND_PRIMARY,
                                        f"{DashboardState.ocupacion_ocupadas_view}/{DashboardState.ocupacion_disponibles_view}",
                                        variant="compact",
                                    ),
                                    kpi_card(
                                        "Comisiones",
                                        DashboardState.comisiones_monto_total_view,
                                        "credit-card",
                                        styles.TEXT_TERTIARY,
                                        f"{DashboardState.comisiones_cantidad_view} pend",
                                        variant="compact",
                                    ),
                                    kpi_card(
                                        "Contratos",
                                        DashboardState.contratos_count_view,
                                        "file-text",
                                        styles.TEXT_SECONDARY,
                                        "Activos",
                                        variant="compact",
                                    ),
                                    kpi_card(
                                        "Recibos Pend.",
                                        DashboardState.recibos_cantidad_view,
                                        "receipt",
                                        styles.TEXT_SECONDARY,
                                        f"En mora/proximos",
                                        variant="compact",
                                    ),
                                    kpi_card(
                                        "Alertas Activas",
                                        DashboardState.alertas_pendientes.to(str),
                                        "bell-ring",
                                        styles.BRAND_PRIMARY,
                                        "Requieren atención",
                                        variant="compact",
                                        href="/alertas"
                                    ),
                                    grid_template_columns=rx.breakpoints(
                                        initial="1fr",
                                        md="repeat(2, 1fr)",
                                        lg="repeat(3, 1fr)",
                                        xl="repeat(4, 1fr)",
                                    ),
                                    gap="4",
                                    width="100%",
                                ),
                                style=styles.NEU_PANEL_STYLE,
                                width="100%",
                                spacing="4",
                            ),
                            style={"grid_column": rx.breakpoints(initial="span 1", lg="span 3")},
                            width="100%",
                        ),

                        # 5. COMPOSICIÓN, INCIDENTES Y TOP ASESORES (3 columnas)
                        # rx.box(
                        #     propiedades_tipo_chart(),
                        #     style={"grid_column": rx.breakpoints(initial="span 1", lg="span 1")},
                        #     width="100%",
                        # ),
                        # rx.box(
                        #     incidentes_pie_chart(),
                        #     style={"grid_column": rx.breakpoints(initial="span 1", lg="span 1")},
                        #     width="100%",
                        # ),
                        # rx.box(
                        #     top_asesores_chart(),
                        #     style={"grid_column": rx.breakpoints(initial="span 1", lg="span 1")},
                        #     width="100%",
                        # ),

                        # 6. DETALLE DE VENCIMIENTOS (Extra Row)
                        rx.box(
                            tablas_vencimientos_detalle(),
                            style={"grid_column": rx.breakpoints(initial="span 1", lg="span 3")},
                            width="100%",
                        ),
                        grid_template_columns=rx.breakpoints(
                            initial="1fr",
                            lg="repeat(3, 1fr)"
                        ),
                        gap="6",
                        width="100%",
                    ),
                ),
                width="100%",
                padding_x=["4", "6", "8", "10"],
                padding_y="8",
            ),
            spacing="0",
            width="100%",
            background=styles.BG_APP,
            min_height="100vh",
        )
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
