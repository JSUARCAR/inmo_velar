"""
Página del Dashboard Principal - Reflex
Tablero de control ejecutivo con métricas clave.
"""

import reflex as rx

from src.presentacion_reflex.components.dashboard import (
    dashboard_filters,
    kpi_card,
    tablas_vencimientos_detalle,
)
from src.presentacion_reflex.components.layout.dashboard_layout import dashboard_layout
from src.presentacion_reflex.state.auth_state import AuthState
from src.presentacion_reflex.state.alertas_state import AlertasState
from src.presentacion_reflex.state.dashboard_state import DashboardState
from src.presentacion_reflex.components.neuro_elements import (
    neuro_panel,
    neuro_spinner,
    neuro_callout,
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
    Dashboard principal con KPIs y Tablas. (Gráficos desactivados temporalmente por estabilidad)
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
            ),
            # CONTENIDO
            rx.vstack(
                # 1. ESTADO DE CARGA
                rx.center(
                    rx.vstack(
                        neuro_spinner(size="3"),
                        rx.text("Procesando métricas..."),
                        spacing="3",
                        align="center",
                    ),
                    padding="100px",
                    width="100%",
                    display=rx.cond(DashboardState.is_loading, "flex", "none"),
                ),

                # 2. CONTENIDO PRINCIPAL
                rx.vstack(
                    # KPIs
                    rx.grid(
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
                        columns=rx.breakpoints(initial="1", md="3"),
                        gap="4",
                        width="100%",
                    ),
                    
                    # Tablas de detalle
                    rx.box(tablas_vencimientos_detalle(), width="100%"),
                    
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
