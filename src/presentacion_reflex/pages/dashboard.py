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
from src.presentacion_reflex.state.alertas_state import AlertasState
from src.presentacion_reflex.state.dashboard_state import DashboardState
from src.presentacion_reflex.components.neuro_elements import (
    neuro_panel,
    neuro_progress,
    neuro_spinner,
    neuro_callout,
)
from src.presentacion_reflex import styles


def _error_fallback() -> rx.Component:
    """Componente de fallback cuando el dashboard falla en renderizado."""
    return rx.center(
        rx.vstack(
            rx.icon("alert-triangle", size=48, color=styles.BRAND_PRIMARY),
            rx.heading(
                "Error al cargar métricas",
                size="6",
                color=styles.TEXT_PRIMARY,
                font_family=styles.FONT_DISPLAY,
            ),
            rx.text(
                "Hubo un problema al renderizar el dashboard. Serás redirigido automáticamente.",
                size="3",
                color=styles.TEXT_SECONDARY,
                text_align="center",
                max_width="400px",
            ),
            rx.hstack(
                rx.link(
                    rx.button(
                        rx.icon("file-text", size=18),
                        "Ir a Contratos",
                        color_scheme="gray",
                        variant="surface",
                        size="3",
                    ),
                    href="/contratos",
                ),
                rx.link(
                    rx.button(
                        rx.icon("refresh-cw", size=18),
                        "Reintentar",
                        color_scheme="gray",
                        variant="outline",
                        size="3",
                    ),
                    href="/dashboard",
                ),
                spacing="3",
            ),
            spacing="4",
            align="center",
            padding="8",
        ),
        height="80vh",
        width="100%",
    )


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
                    rx.flex(
                        dashboard_filters(),
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
                        gap="4",
                    ),
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
            # CONTENIDO BENTO GRID (Estabilizado para Hydration React 19)
            rx.vstack(
                # 1. ESTADO DE CARGA (Overlay)
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
                        align="center",
                    ),
                    padding="100px",
                    width="100%",
                    display=rx.cond(DashboardState.is_loading, "flex", "none"),
                ),

                # 2. ESTADO DE ERROR
                rx.cond(
                    DashboardState.error_message != "",
                    neuro_callout(
                        DashboardState.error_message,
                        icon="alert-triangle",
                        color_scheme="red",
                        width="100%",
                    ),
                ),

                # 3. GRID DE CONTENIDO (Siempre presente en DOM para evitar Hydration Error #418)
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

                    # 2. SECCIÓN DE FILTROS (OPCIONAL: Duplicado si se requiere)
                    # rx.box(dashboard_filters(), width="100%", padding_y="2"),

                    # 3. GRÁFICOS PRINCIPALES
                    # GRÁFICOS REACTIVADOS EN BENTO GRID
                    rx.grid(
                        rx.box(evolucion_chart(), width="100%", grid_column=rx.breakpoints(initial="span 1", lg="span 2")),
                        rx.box(vencimientos_chart(), width="100%", grid_column=rx.breakpoints(initial="span 1", lg="span 1")),
                        rx.box(tunel_vencimientos_chart(), width="100%", grid_column=rx.breakpoints(initial="span 1", lg="span 1")),
                        rx.box(propiedades_tipo_chart(), width="100%", grid_column=rx.breakpoints(initial="span 1", lg="span 1")),
                        rx.box(incidentes_pie_chart(), width="100%", grid_column=rx.breakpoints(initial="span 1", lg="span 1")),
                        rx.box(top_asesores_chart(), width="100%", grid_column=rx.breakpoints(initial="span 1", lg="span 1")),
                        rx.box(tablas_vencimientos_detalle(), width="100%", grid_column=rx.breakpoints(initial="span 1", lg="span 2")),
                        columns=rx.breakpoints(initial="1", md="2", lg="3"),
                        spacing="6",
                        width="100%",
                    ),

                    # 4. PULSO OPERATIVO (Bottom Row - Bento Grid)
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
                                    "alert-triangle",
                                    styles.BRAND_PRIMARY,
                                    f"{DashboardState.mora_cantidad_contratos_view} ctros",
                                    variant="compact",
                                    tooltip="Total acumulado en mora actual",
                                ),
                                kpi_card(
                                    "Recaudo Mes",
                                    DashboardState.recaudo_mes_view,
                                    "wallet",
                                    styles.TEXT_SECONDARY,
                                    f"{DashboardState.recaudo_porcentaje_view}%",
                                    variant="compact",
                                    tooltip="Recaudo efectivo del mes vs esperado",
                                ),
                                kpi_card(
                                    "Ocupación",
                                    f"{DashboardState.ocupacion_porcentaje_view}%",
                                    "home",
                                    styles.BRAND_PRIMARY,
                                    f"{DashboardState.ocupacion_ocupadas_view}/{DashboardState.ocupacion_disponibles_view}",
                                    variant="compact",
                                    tooltip="Porcentaje de inmuebles ocupados respecto al total administrable",
                                ),
                                kpi_card(
                                    "Comisiones",
                                    DashboardState.comisiones_monto_total_view,
                                    "credit-card",
                                    styles.TEXT_TERTIARY,
                                    f"{DashboardState.comisiones_cantidad_view} pend",
                                    variant="compact",
                                    tooltip="Comisiones pendientes por cobrar de Asesores",
                                ),
                                kpi_card(
                                    "Contratos",
                                    DashboardState.contratos_count_view,
                                    "file-text",
                                    styles.TEXT_SECONDARY,
                                    "Activos",
                                    variant="compact",
                                    tooltip="Número de contratos activos en la plataforma",
                                ),
                                kpi_card(
                                    "Recibos Pend.",
                                    DashboardState.recibos_cantidad_view,
                                    "receipt",
                                    styles.TEXT_SECONDARY,
                                    f"En mora/proximos",
                                    variant="compact",
                                    tooltip="Facturas o recibos pendientes de pago por parte de arrendatarios",
                                ),
                                kpi_card(
                                    "Alertas Activas",
                                    DashboardState.alertas_pendientes.to(str),
                                    "bell-ring",
                                    styles.BRAND_PRIMARY,
                                    "Requieren atención",
                                    variant="compact",
                                    href="/alertas",
                                    tooltip="Alertas del sistema que requieren acción manual",
                                ),
                                columns=rx.breakpoints(initial="1", sm="2", md="3", lg="4"),
                                gap="4",
                                width="100%",
                            ),
                            style=styles.NEU_PANEL_STYLE,
                            width="100%",
                            spacing="4",
                        ),
                        width="100%",
                    ),
                    spacing="6",
                    width="100%",
                    display=rx.cond(DashboardState.is_loading | (DashboardState.error_message != ""), "none", "flex"),
                ),

                # Fase 5: Mensaje amigable cuando no hay datos en vez de grid vacío
                rx.cond(
                    ~DashboardState.is_loading & (DashboardState.error_message == ""),
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
