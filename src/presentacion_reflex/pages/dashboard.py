import reflex as rx
from src.presentacion_reflex.components.layout.dashboard_layout import dashboard_layout
from src.presentacion_reflex.components.dashboard import kpi_card
from src.presentacion_reflex.state.dashboard_state import DashboardState
from src.presentacion_reflex import styles

def dashboard_page() -> rx.Component:
    return dashboard_layout(
        rx.vstack(
            rx.heading("Dashboard con KPIs"),
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
            spacing="6",
            width="100%",
        )
    )

@rx.page(
    route="/dashboard",
    title="Panel | Velar",
    on_load=[DashboardState.on_load],
)
def dashboard():
    return dashboard_page()
