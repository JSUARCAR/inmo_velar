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
    _tabla_vencimientos,
)
from src.presentacion_reflex.components.layout.dashboard_layout import dashboard_layout
from src.presentacion_reflex.state.auth_state import AuthState
from src.presentacion_reflex.state.alertas_state import AlertasState
from src.presentacion_reflex.state.dashboard_state import DashboardState
from src.presentacion_reflex.components.neuro_elements import (
    neuro_panel,
    neuro_callout,
    neuro_pulse_card,
)
from src.presentacion_reflex.components.dashboard.skeleton_loaders import (
    kpi_skeleton,
    chart_skeleton,
    table_skeleton
)
from src.presentacion_reflex import styles


def _empty_state_message() -> rx.Component:
    """Mensaje amigable cuando no hay datos disponibles."""
    return rx.center(
        rx.vstack(
            rx.icon("inbox", size=40, color=styles.TEXT_TERTIARY),
            rx.text(
                "No hay datos para mostrar",
                size="4",
                weight="bold",
                color=styles.TEXT_SECONDARY,
            ),
            rx.text(
                "Intenta ajustar los filtros o verifica la conexión con la base de datos.",
                size="2",
                color=styles.TEXT_TERTIARY,
                text_align="center",
            ),
            rx.link(
                rx.button(
                    rx.icon("file-text", size=16),
                    "Ir a Contratos",
                    color_scheme="gray",
                    variant="surface",
                    size="2",
                ),
                href="/contratos",
            ),
            spacing="3",
            align="center",
            padding="12",
        ),
        width="100%",
        min_height="300px",
    )

def dashboard_page() -> rx.Component:
    """
    Dashboard principal completo (Gráficos sustituidos por placeholders seguros).
    """

    return dashboard_layout(
        rx.vstack(
            # HEADER ESTRATÉGICO
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
                    rx.spacer(),
                    rx.button(
                        rx.icon("refresh-cw", size=18),
                        "Actualizar",
                        on_click=DashboardState.load_dashboard_data,
                        color_scheme="gray",
                        variant="surface",
                        cursor="pointer",
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
                # 1. ESTADO DE CARGA (Skeletons - Carga progresiva)
                rx.box(
                    rx.vstack(
                        rx.grid(
                            kpi_skeleton(), kpi_skeleton(), kpi_skeleton(),
                            columns=rx.breakpoints(initial="1", md="3"), gap="4", width="100%"
                        ),
                        rx.grid(
                            chart_skeleton(height="250px"), chart_skeleton(height="250px"), chart_skeleton(height="250px"),
                            chart_skeleton(height="250px"), chart_skeleton(height="250px"), chart_skeleton(height="250px"),
                            columns=rx.breakpoints(initial="1", md="2", lg="3"), spacing="6", width="100%"
                        ),
                        rx.box(table_skeleton(rows=8), width="100%", margin_top="6"),
                        spacing="6", width="100%"
                    ),
                    display=rx.cond(DashboardState.is_loading, "block", "none"),
                    width="100%"
                ),

                # 1.5 ERRORES DE CARGA (Si existen)
                rx.cond(
                    DashboardState.errores_carga.length() > 0,
                    rx.box(
                        neuro_callout(
                            "Ocurrieron errores al cargar algunos componentes. Reintente más tarde.",
                            icon="triangle-alert",
                            color_scheme="red",
                        ),
                        width="100%",
                        padding_bottom="4"
                    )
                ),

                # 2. CONTENIDO PRINCIPAL
                rx.vstack(
                    # 1. KPIs ESTRATÉGICOS (Top Row - Grid)
                    rx.grid(
                        kpi_card(
                            "Ocupación Financiera",
                            f"{DashboardState.kpi_ocupacion_financiera_view}%",
                            "bar-chart-2",
                            styles.BRAND_PRIMARY,
                            "Ingresos vs Potencial",
                            variant="elite",
                            tooltip="Mide los ingresos reales frente a la capacidad de generación total.",
                            tendencia="+2.1% MoM",
                        ),
                        kpi_card(
                            "Eficiencia Recaudo",
                            f"{DashboardState.kpi_eficiencia_recaudo_view}%",
                            "wallet",
                            styles.TEXT_SECONDARY,
                            "Recaudado este mes",
                            variant="elite",
                            tooltip="Porcentaje del monto total esperado que ha sido efectivamente recaudado este mes.",
                            tendencia="+1.5% YoY",
                        ),
                        kpi_card(
                            "Potencial Total",
                            DashboardState.kpi_potencial_total_view,
                            "banknote",
                            styles.TEXT_TERTIARY,
                            "Cartera Total Estimada",
                            variant="elite",
                            tooltip="Valor total estimado de contratos activos sin aplicar descuentos o mora.",
                        ),
                        columns=rx.breakpoints(initial="1", md="3"),
                        gap="4",
                        width="100%",
                    ),

                    # ROW 2: PULSO OPERATIVO (HERO - mucho más ancho)
                    rx.box(
                        neuro_panel(
                            rx.vstack(
                                rx.hstack(
                                    rx.text("PULSO OPERATIVO Y ACCIONES", size="4", weight="bold", color=styles.TEXT_SECONDARY),
                                    rx.spacer(),
                                    rx.badge("Tiempo real", color_scheme="green", variant="soft"),
                                    width="100%"
                                ),
                                rx.grid(
                                    neuro_pulse_card("Cartera Mora", DashboardState.mora_monto_total_view,
                                        "triangle-alert", progreso=DashboardState.pulso_tendencias["mora"]["progreso"],
                                        color_scheme="red",
                                        subtitulo=f"{DashboardState.mora_cantidad_contratos_view} contratos"),
                                    neuro_pulse_card("Recaudo Mes", DashboardState.recaudo_mes_view,
                                        "wallet", progreso=DashboardState.pulso_tendencias["recaudo"]["progreso"],
                                        color_scheme="blue",
                                        subtitulo=f"{DashboardState.recaudo_porcentaje_view}% de meta"),
                                    neuro_pulse_card("Ocupación", f"{DashboardState.ocupacion_porcentaje_view}%",
                                        "home", progreso=DashboardState.pulso_tendencias["ocupacion"]["progreso"],
                                        color_scheme="green",
                                        subtitulo=f"{DashboardState.ocupacion_ocupadas_view}/{DashboardState.ocupacion_disponibles_view} disp"),
                                    neuro_pulse_card("Alertas Activas", DashboardState.alertas_pendientes.to(str),
                                        "bell-ring", progreso=DashboardState.pulso_tendencias["alertas"]["progreso"],
                                        color_scheme="amber", href="/alertas",
                                        subtitulo="Requieren atención"),
                                    columns=rx.breakpoints(initial="1", sm="2", md="4"), gap="4", width="100%"
                                ),
                                rx.grid(
                                    kpi_card("Comisiones", DashboardState.comisiones_monto_total_view,
                                        "credit-card", styles.TEXT_TERTIARY, f"{DashboardState.comisiones_cantidad_view} pend", variant="compact"),
                                    kpi_card("Contratos", DashboardState.contratos_count_view,
                                        "file-text", styles.TEXT_SECONDARY, "Activos", variant="compact"),
                                    kpi_card("Recibos Pend.", DashboardState.recibos_cantidad_view,
                                        "receipt", styles.TEXT_SECONDARY, "En mora/próximos", variant="compact"),
                                    columns=rx.breakpoints(initial="1", md="3"), gap="4", width="100%"
                                ),
                                spacing="4", width="100%"
                            ),
                        ), width="100%",
                    ),

                    # ROW 3: SEGUIMIENTO FINANCIERO Y RIESGO
                    rx.grid(
                        rx.box(evolucion_chart(height="320px"), grid_column=rx.breakpoints(initial="span 1", lg="span 2")),
                        rx.box(vencimientos_chart(height="320px"), grid_column=rx.breakpoints(initial="span 1", lg="span 1")),
                        columns=rx.breakpoints(initial="1", lg="3"), spacing="6", width="100%"
                    ),

                    # ROW 4: DISTRIBUCIÓN OPERATIVA
                    rx.grid(
                        rx.box(propiedades_tipo_chart(height="280px")),
                        rx.box(incidentes_pie_chart(height="280px")),
                        rx.box(top_asesores_chart(height="280px")),
                        columns=rx.breakpoints(initial="1", md="2", lg="3"), spacing="6", width="100%"
                    ),

                    # ROW 5: GESTIÓN DE VENCIMIENTOS
                    rx.grid(
                        rx.box(tunel_vencimientos_chart(height="300px")),
                        rx.box(_tabla_vencimientos("Vencimientos de Mandato (90 Días)", "briefcase", "mandato",
                               DashboardState.contratos_vencer_mandato_view)),
                        rx.box(_tabla_vencimientos("Vencimientos de Arrendamiento (90 Días)", "home", "arrendamiento",
                               DashboardState.contratos_vencer_arrendamiento_view)),
                        columns=rx.breakpoints(initial="1", lg="3"), spacing="6", width="100%", class_name="grid-vencimientos"
                    ),
                    spacing="6",
                    width="100%",
                    display=rx.cond(DashboardState.is_loading, "none", "flex"),
                ),

                # Empty state fallback
                rx.cond(
                    ~DashboardState.is_loading & (DashboardState.vencimientos_lista.length() == 0),
                    _empty_state_message(),
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


# Ruta protegida
@rx.page(
    route="/dashboard",
    title="Panel | Velar",
    on_load=[
        AuthState.require_login,
        DashboardState.on_load,
    ],
)
def dashboard():
    return dashboard_page()
