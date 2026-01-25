"""
Vista Principal Dashboard - Inmobiliaria Velar
Tablero de control ejecutivo con metricas clave.
Refactorizado para Arquitectura Shell y Carga Asíncrona (Optimizaciones 17.2 y 17.3)
Adaptado a Flet moderno (sin UserControl).
"""

import threading

import flet as ft
import plotly.graph_objects as go

from src.aplicacion.servicios import ServicioDashboard
from src.infraestructura.persistencia.database import DatabaseManager
from src.presentacion.components.dashboard_filters import DashboardFilters
from src.presentacion.components.widgets.chart_widget import ChartWidget
from src.presentacion.components.widgets.kpi_card import KpiCard
from src.presentacion.theme import colors


class DashboardView(ft.Container):
    def __init__(self, page: ft.Page, usuario, on_navigate=None):
        super().__init__()
        self.page_ref = page
        self.usuario = usuario
        self.on_navigate = on_navigate if on_navigate else lambda x: None

        # Propiedades del Container (reemplaza lo que retornaba build)
        self.expand = True
        self.padding = 30
        self.bgcolor = colors.BACKGROUND

        try:
            self.db_manager = DatabaseManager()
            self.servicio_dashboard = ServicioDashboard(self.db_manager)
        except Exception as e:
            pass  # print(f"ERROR Servicios Dashboard: {e}") [OpSec Removed]
            raise e

        # Estado
        self.cargando = True

        # Contenedores UI
        self.contenedor_kpis = ft.ResponsiveRow(
            run_spacing=20, spacing=20, alignment=ft.MainAxisAlignment.CENTER
        )
        self.contenedor_graficos_1 = ft.ResponsiveRow(run_spacing=20, spacing=20)
        self.contenedor_graficos_2 = ft.ResponsiveRow(run_spacing=20, spacing=20)

        # Loader
        self.loader = ft.Container(
            content=ft.Column(
                [
                    ft.ProgressRing(color=colors.PRIMARY),
                    ft.Text("Calculando métricas...", color=colors.TEXT_SECONDARY),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            alignment=ft.alignment.center,
            padding=50,
            visible=False,
        )

        self.main_content = ft.Column(
            [self.contenedor_kpis, self.contenedor_graficos_1, self.contenedor_graficos_2],
            spacing=20,
            scroll=ft.ScrollMode.AUTO,
            visible=True,
        )

        # Construcción del layout (antes en build)
        self.filtros = DashboardFilters(
            db_manager=self.db_manager, on_filter_apply=self.actualizar_dashboard_con_filtros
        )

        # Contenido del Container principal
        self.content = ft.Column(
            [self.filtros, self.loader, self.main_content], spacing=20, scroll=ft.ScrollMode.AUTO
        )

    def did_mount(self):
        # Carga inicial sin filtros (o defaults)
        self.actualizar_dashboard()

    def actualizar_dashboard_con_filtros(self, mes=None, anio=None, id_asesor=None):
        self.actualizar_dashboard(mes, anio, id_asesor)

    def actualizar_dashboard(self, mes: int = None, anio: int = None, id_asesor: int = None):
        self.cargando = True
        self.loader.visible = True
        self.main_content.visible = False
        self.update()

        threading.Thread(
            target=self._fetch_data_thread, args=(mes, anio, id_asesor), daemon=True
        ).start()

    def _fetch_data_thread(self, mes, anio, id_asesor):
        try:
            # --- OBTENCIÓN DE DATOS (Pesado) ---
            pass  # print(f"DEBUG DASHBOARD: Fetching data (mes={mes}, anio={anio}, asesor={id_asesor})") [OpSec Removed]

            # 1. KPIs Financieros y Operativos
            datos_flujo = self.servicio_dashboard.obtener_flujo_caja_mes(
                mes=mes, anio=anio, id_asesor=id_asesor
            )
            datos_ocupacion = self.servicio_dashboard.obtener_tasa_ocupacion(id_asesor=id_asesor)
            contratos_activos = self.servicio_dashboard.obtener_total_contratos_activos(
                id_asesor=id_asesor
            )
            datos_comisiones = self.servicio_dashboard.obtener_comisiones_pendientes(
                id_asesor=id_asesor
            )

            # 2. Métricas Globales/Anlíticas
            datos_mora = self.servicio_dashboard.obtener_cartera_mora()
            datos_vencimiento = self.servicio_dashboard.obtener_contratos_por_vencer()
            datos_incidentes = self.servicio_dashboard.obtener_metricas_incidentes()
            datos_evolucion = self.servicio_dashboard.obtener_evolucion_recaudo(
                mes_fin=mes, anio_fin=anio
            )
            datos_recibos_vencidos = self.servicio_dashboard.obtener_recibos_vencidos_resumen()

            # Empaquetamos todo para updatear UI
            data_package = {
                "flujo": datos_flujo,
                "ocupacion": datos_ocupacion,
                "contratos": contratos_activos,
                "comisiones": datos_comisiones,
                "mora": datos_mora,
                "vencimiento": datos_vencimiento,
                "incidentes": datos_incidentes,
                "evolucion": datos_evolucion,
                "recibos": datos_recibos_vencidos,
            }

            self._schedule_ui_update(data_package)

        except Exception as e:
            pass  # print(f"Error fetching dashboard data: {e}") [OpSec Removed]
            import traceback

            traceback.print_exc()
            self._schedule_ui_update(None, error=str(e))

    def _schedule_ui_update(self, data, error=None):
        # En Flet Python standard, modificar controles y llamar update() desde thread secundario
        # suele funcionar si los controles ya están montados.
        self._render_ui(data, error)

    def _render_ui(self, data, error):
        if error:
            self.loader.visible = False
            self.page_ref.snack_bar = ft.SnackBar(
                ft.Text(f"Error cargando dashboard: {error}"), bgcolor=colors.ERROR
            )
            self.page_ref.snack_bar.open = True
            self.page_ref.update()
            return

        # Limpiar
        self.contenedor_kpis.controls.clear()
        self.contenedor_graficos_1.controls.clear()
        self.contenedor_graficos_2.controls.clear()

        kpi_cols = {"xs": 12, "sm": 6, "lg": 4, "xl": 2}

        # --- KPIS ---
        self.contenedor_kpis.controls.extend(
            [
                KpiCard(
                    titulo="Cartera en Mora",
                    valor=f"${data['mora']['monto_total']:,.0f}",
                    icono=ft.Icons.WARNING_ROUNDED,
                    es_critico=data["mora"]["cantidad_contratos"] > 0,
                    subtitulo=f"{data['mora']['cantidad_contratos']} contratos afectados",
                    col=kpi_cols,
                ),
                KpiCard(
                    titulo="Recaudo Mes Actual",
                    valor=f"${data['flujo']['recaudado']:,.0f}",
                    icono=ft.Icons.ACCOUNT_BALANCE_WALLET,
                    color_icono=colors.SUCCESS,
                    subtitulo=f"Meta: ${data['flujo']['esperado']:,.0f} ({data['flujo']['porcentaje']}%)",
                    col=kpi_cols,
                ),
                KpiCard(
                    titulo="Tasa de Ocupación",
                    valor=f"{data['ocupacion']['porcentaje_ocupacion']}%",
                    icono=ft.Icons.HOME,
                    color_icono=colors.INFO,
                    subtitulo=f"{data['ocupacion']['ocupadas']} Ocupadas / {data['ocupacion']['disponibles']} Disponibles",
                    col=kpi_cols,
                ),
                KpiCard(
                    titulo="Comisiones Pendientes",
                    valor=f"${data['comisiones']['monto_total']:,.0f}",
                    icono=ft.Icons.PAYMENTS_OUTLINED,
                    color_icono=colors.WARNING,
                    subtitulo=f"{data['comisiones']['cantidad_liquidaciones']} por aprobar",
                    col=kpi_cols,
                ),
                KpiCard(
                    titulo="Contratos Activos",
                    valor=str(data["contratos"]),
                    icono=ft.Icons.DESCRIPTION,
                    color_icono=colors.PRIMARY,
                    subtitulo="Arrendamientos vigentes",
                    col=kpi_cols,
                ),
                KpiCard(
                    titulo="Recibos Vencidos",
                    valor=f"${data['recibos']['monto_total']:,.0f}",
                    icono=ft.Icons.RECEIPT_LONG,
                    color_icono=colors.ERROR if data["recibos"]["cantidad"] > 0 else colors.SUCCESS,
                    es_critico=data["recibos"]["cantidad"] > 0,
                    subtitulo=f"{data['recibos']['cantidad']} recibos pendientes",
                    on_click=lambda _: self.on_navigate("recibos_publicos"),
                    col=kpi_cols,
                ),
            ]
        )

        # --- GRÁFICOS ---
        chart_cols = {"xs": 12, "md": 6}

        # Vencimientos
        fig_vencimientos = go.Figure(
            data=[
                go.Bar(
                    name="30 días",
                    x=["Vencimientos"],
                    y=[data["vencimiento"]["vence_30_dias"]],
                    marker_color="#EF4444",
                ),
                go.Bar(
                    name="60 días",
                    x=["Vencimientos"],
                    y=[data["vencimiento"]["vence_60_dias"]],
                    marker_color="#F59E0B",
                ),
                go.Bar(
                    name="90 días",
                    x=["Vencimientos"],
                    y=[data["vencimiento"]["vence_90_dias"]],
                    marker_color="#3B82F6",
                ),
            ]
        )
        fig_vencimientos.update_layout(
            barmode="stack", height=250, showlegend=True, margin=dict(l=20, r=20, t=20, b=20)
        )
        self.contenedor_graficos_1.controls.append(
            ft.Container(
                content=ChartWidget(
                    "Contratos por Vencer", fig_vencimientos, "Proyección a 90 días"
                ),
                col=chart_cols,
            )
        )

        # Evolución
        fig_evolucion = go.Figure(
            [
                go.Bar(
                    x=data["evolucion"]["etiquetas"],
                    y=data["evolucion"]["valores"],
                    marker_color=colors.PRIMARY,
                )
            ]
        )
        fig_evolucion.update_layout(height=250, margin=dict(l=20, r=20, t=20, b=20))
        self.contenedor_graficos_1.controls.append(
            ft.Container(
                content=ChartWidget("Evolución de Recaudos (6 Meses)", fig_evolucion),
                col=chart_cols,
            )
        )

        # Ocupación Pie
        fig_ocupacion = go.Figure(
            data=[
                go.Pie(
                    labels=["Ocupado", "Disponible"],
                    values=[data["ocupacion"]["ocupadas"], data["ocupacion"]["disponibles"]],
                    hole=0.6,
                    marker=dict(colors=[colors.SUCCESS, colors.BORDER_DEFAULT]),
                )
            ]
        )
        fig_ocupacion.update_layout(
            height=250, showlegend=True, margin=dict(l=20, r=20, t=20, b=20)
        )
        self.contenedor_graficos_2.controls.append(
            ft.Container(content=ChartWidget("Estado de Inventario", fig_ocupacion), col=chart_cols)
        )

        # Incidentes Pie
        fig_incidentes = go.Figure(
            data=[
                go.Pie(
                    labels=list(data["incidentes"]["por_estado"].keys()),
                    values=list(data["incidentes"]["por_estado"].values()),
                    hole=0.6,
                )
            ]
        )
        fig_incidentes.update_layout(
            height=250, showlegend=True, margin=dict(l=20, r=20, t=20, b=20)
        )
        self.contenedor_graficos_2.controls.append(
            ft.Container(
                content=ChartWidget("Incidentes por Estado", fig_incidentes), col=chart_cols
            )
        )

        # Toggle visibilidad
        self.loader.visible = False
        self.main_content.visible = True
        self.update()


# Wrapper
def crear_dashboard_view(page, usuario, on_logout, on_navigate=None):
    return DashboardView(page, usuario, on_navigate)
