import decimal
from datetime import date, datetime
from typing import Any, Dict, List, Optional, ClassVar

import reflex as rx

from src.aplicacion.servicios.servicio_dashboard import ServicioDashboard
from src.infraestructura.persistencia.database import db_manager
from src.infraestructura.persistencia.repositorio_asesor_postgres import (
    RepositorioAsesorPostgres,
)
from src.infraestructura.persistencia.repositorio_dashboard import RepositorioDashboard
from src.presentacion_reflex.utils.formatters import format_currency, format_number
from src.presentacion_reflex.state.dashboard_base import DashboardBaseState

import plotly.graph_objects as go


import logging

logger = logging.getLogger(__name__)


def _default_fig_layout(height=280, show_legend=False, **kwargs):
    layout = dict(
        margin=dict(l=50, r=20, t=30, b=40),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter, sans-serif", size=11, color="#5e5d59"),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="#1f2937", font_size=12, font_color="white", bordercolor="#374151"
        ),
        xaxis=dict(showgrid=False, tickfont=dict(size=10, color="#87867f")),
        yaxis=dict(
            showgrid=True, gridcolor="#f0eee6", tickfont=dict(size=10, color="#87867f")
        ),
        height=height,
        showlegend=show_legend,
    )
    for k, v in kwargs.items():
        if isinstance(v, dict) and k in layout and isinstance(layout[k], dict):
            layout[k].update(v)
        else:
            layout[k] = v
    return layout


def _serialize_decimals(obj: Any) -> Any:
    """Convierte tipos incompatibles (Decimal, date, datetime) a tipos serializables por Reflex JSON."""
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    elif isinstance(obj, (datetime, date)):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {k: _serialize_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_serialize_decimals(v) for v in obj]
    return obj


class DashboardState(DashboardBaseState):
    """
    Estado del Dashboard.
    Maneja datos de KPIs, gráficos y filtros.

    FASE 1+2: Hydration-safe + Métodos atómicos.
    - _hydration_ready previene carga de datos durante SSR.
    - load_dashboard_data() es ahora una tarea en background (`@rx.event(background=True)`).
    """

    # Flag de hidratación: solo True después de que el componente se montó en cliente
    _hydration_ready: bool = False

    # Filtros — se inicializan en on_load para tomar la fecha real del sistema
    selected_month: int = 0  # 0 = "no inicializado aún"
    selected_year: int = 0  # 0 = "no inicializado aún"
    selected_advisor_id: Optional[int] = None

    # Opciones para filtros
    advisor_options: List[Dict[str, Any]] = []

    # Datos de KPIs
    mora_data: Dict[str, Any] = {"monto_total": 0, "cantidad_contratos": 0}

    flujo_data: Dict[str, Any] = {"recaudado": 0, "esperado": 0, "porcentaje": 0}

    ocupacion_data: Dict[str, Any] = {
        "porcentaje_ocupacion": 0,
        "ocupadas": 0,
        "disponibles": 0,
    }

    propiedades_tipo_data: Dict[str, int] = {}

    kpi_financiero: Dict[str, float] = {
        "ocupacion_financiera": 0,
        "eficiencia_recaudo": 0,
        "potencial_total": 0,
        "recaudo_real": 0,
    }
    top_asesores_data: List[Dict] = []
    tunel_vencimientos_data: List[Dict] = []

    comisiones_data: Dict[str, Any] = {"monto_total": 0, "cantidad_liquidaciones": 0}

    contratos_count: int = 0

    recibos_data: Dict[str, Any] = {"cantidad": 0, "monto_total": 0}

    alertas_pendientes: int = 0

    # Datos de gráficos
    vencimiento_data: Dict[str, Any] = {
        "vence_30_dias": 0,
        "vence_60_dias": 0,
        "vence_90_dias": 0,
    }
    vencimientos_lista: List[Dict[str, Any]] = []

    evolucion_data: Dict[str, Any] = {"etiquetas": [], "valores": []}

    incidentes_data: Dict[str, Any] = {"por_estado": {}}

    incidentes_data: Dict[str, Any] = {"por_estado": {}}

    # ─── Fase 1: Hydration-safe on_load ───────────────────────────────────────

    def on_load(self):
        """
        Se ejecuta al montar la página del dashboard.
        Marca _hydration_ready=True y dispara la carga de datos como evento
        separado para evitar mutación de estado durante SSR/hydration.
        """
        import time

        run_id = int(time.time() * 1000) % 1000000
        self._hydration_ready = True
        logger.debug(
            f"DashboardState.on_load CALLED | run_id={run_id} | hydration_ready=True"
        )

        # Inicializar fecha solo si es la primera vez (valor = 0 indica "no inicializado")
        if self.selected_month == 0 or self.selected_year == 0:
            now = datetime.now()
            self.selected_month = now.month
            self.selected_year = now.year

        self.load_advisor_options()
        logger.debug(f"on_load → yield load_dashboard_data | run_id={run_id}")
        yield DashboardState.load_dashboard_data

    def load_advisor_options(self):
        """Carga la lista de asesores para el dropdown."""
        logger.debug("load_advisor_options START")
        try:
            repo_asesores = RepositorioAsesorPostgres(db_manager)
            asesores = repo_asesores.listar_todos()
            self.advisor_options = [
                {
                    "value": str(a.id_asesor),
                    "label": getattr(a, "nombre_completo", f"Asesor {a.id_asesor}"),
                }
                for a in asesores
            ]
            logger.debug(f"load_advisor_options OK | count={len(self.advisor_options)}")
        except Exception as e:
            logger.error(f"load_advisor_options ERROR: {e}", exc_info=True)
            self.advisor_options = []

    # ─── Fase 2: Métodos atómicos de carga ────────────────────────────────────

    def _get_servicio(self) -> ServicioDashboard:
        """Instancia el servicio de dashboard con sus repositorios."""
        from src.infraestructura.persistencia.repositorio_alerta_postgres import (
            RepositorioAlertaPostgres,
        )

        repo_dashboard = RepositorioDashboard(db_manager)
        repo_alerta = RepositorioAlertaPostgres(db_manager)
        return ServicioDashboard(repo_dashboard=repo_dashboard, repo_alerta=repo_alerta)

    @staticmethod
    def _safe_fetch(
        fetch_fn, default_val, error_list: Optional[List[str]] = None, retries: int = 2
    ):
        """
        Ejecuta una función de fetch con fallback seguro y reintentos (backoff progresivo).
        Registra la duración y éxito para observabilidad.
        """
        import time

        fn_name = getattr(fetch_fn, "__name__", "lambda")
        start_time = time.time()

        for attempt in range(retries + 1):
            try:
                res = fetch_fn()
                duration = time.time() - start_time
                logger.info(
                    f"[DASHBOARD] OK: {fn_name} - {duration:.3f}s (Intento {attempt + 1})"
                )
                return res
            except Exception as e:
                if attempt < retries:
                    sleep_time = 0.2 * (2**attempt)
                    logger.warning(
                        f"[DASHBOARD] RETRY {attempt + 1}/{retries}: {fn_name} falló con {e}. Reintentando en {sleep_time}s..."
                    )
                    time.sleep(sleep_time)
                else:
                    duration = time.time() - start_time
                    logger.error(
                        f"[DASHBOARD] FAIL: {fn_name} falló tras {retries} reintentos en {duration:.3f}s. Error: {e}"
                    )
                    if error_list is not None:
                        error_list.append(f"{fn_name} falló")
                    return default_val

    @rx.event(background=True)
    async def load_dashboard_data(self):
        """
        Carga todos los datos del dashboard en 3 fases atómicas de forma asíncrona no bloqueante.
        """
        async with self:
            if not self._hydration_ready:
                logger.warning("load_dashboard_data ABORTADO: hydration no lista")
                return

            token = self._generate_token()
            self.is_loading = True
            self.error_message = ""
            mes = self.selected_month
            anio = self.selected_year
            id_asesor = self.selected_advisor_id

        import asyncio

        loop = asyncio.get_running_loop()

        def _fetch_all():
            servicio = self._get_servicio()
            errors = []

            # Fase 1: KPIs
            alertas = self._safe_fetch(
                servicio.obtener_conteo_alertas_pendientes, 0, errors
            )
            flujo = self._safe_fetch(
                lambda: servicio.obtener_flujo_caja_mes(
                    mes=mes, anio=anio, id_asesor=id_asesor
                ),
                {"recaudado": 0, "esperado": 0, "porcentaje": 0},
                errors,
            )
            ocup = self._safe_fetch(
                lambda: servicio.obtener_tasa_ocupacion(id_asesor=id_asesor),
                {"porcentaje_ocupacion": 0, "ocupadas": 0, "disponibles": 0},
                errors,
            )
            contratos = self._safe_fetch(
                lambda: servicio.obtener_total_contratos_activos(id_asesor=id_asesor),
                0,
                errors,
            )
            comis = self._safe_fetch(
                lambda: servicio.obtener_comisiones_pendientes(id_asesor=id_asesor),
                {"monto_total": 0, "cantidad_liquidaciones": 0},
                errors,
            )
            mora = self._safe_fetch(
                servicio.obtener_cartera_mora,
                {"monto_total": 0, "cantidad_contratos": 0},
                errors,
            )

            # Fase 2: Gráficas
            evolucion = self._safe_fetch(
                lambda: servicio.obtener_evolucion_recaudo(
                    mes_fin=mes, anio_fin=anio, id_asesor=id_asesor
                ),
                {"etiquetas": [], "valores": []},
                errors,
            )
            recibos = self._safe_fetch(
                servicio.obtener_recibos_vencidos_resumen,
                {"cantidad": 0, "monto_total": 0},
                errors,
            )
            prop_tipo = self._safe_fetch(
                lambda: servicio.obtener_propiedades_por_tipo(id_asesor=id_asesor),
                {},
                errors,
            )
            kpi_fin = self._safe_fetch(
                lambda: servicio.obtener_metricas_expertas(id_asesor=id_asesor),
                {
                    "ocupacion_financiera": 0,
                    "eficiencia_recaudo": 0,
                    "potencial_total": 0,
                    "recaudo_real": 0,
                },
                errors,
            )

            top_asesores = []
            tunel = []
            if not id_asesor:
                top_asesores = self._safe_fetch(
                    servicio.obtener_top_asesores_revenue, [], errors
                )
                tunel = self._safe_fetch(
                    servicio.obtener_tunel_vencimientos, [], errors
                )

            # Fase 3: Tablas y Vencimientos
            venc_data = self._safe_fetch(
                servicio.obtener_contratos_por_vencer,
                {"vence_30_dias": 0, "vence_60_dias": 0, "vence_90_dias": 0},
                errors,
            )
            venc_lista = self._safe_fetch(
                lambda: servicio.obtener_contratos_proximos_vencer(90), [], errors
            )
            incidentes = self._safe_fetch(
                servicio.obtener_metricas_incidentes, {"por_estado": {}}, errors
            )

            return {
                "alertas": alertas,
                "flujo": flujo,
                "ocupacion": ocup,
                "contratos": contratos,
                "comisiones": comis,
                "mora": mora,
                "evolucion": evolucion,
                "recibos": recibos,
                "prop_tipo": prop_tipo,
                "kpi_fin": kpi_fin,
                "top_asesores": top_asesores,
                "tunel": tunel,
                "venc_data": venc_data,
                "venc_lista": venc_lista,
                "incidentes": incidentes,
                "errors": errors,
            }

        try:
            # Ejecutar fetchers en un threadpool para no bloquear el loop asíncrono
            res = await loop.run_in_executor(None, _fetch_all)

            async with self:
                if not self._is_valid_token(token):
                    return

                self.alertas_pendientes = _serialize_decimals(res["alertas"])
                self.flujo_data = _serialize_decimals(res["flujo"])
                self.ocupacion_data = _serialize_decimals(res["ocupacion"])
                self.contratos_count = _serialize_decimals(res["contratos"])
                self.comisiones_data = _serialize_decimals(res["comisiones"])
                self.mora_data = _serialize_decimals(res["mora"])

                self.evolucion_data = _serialize_decimals(res["evolucion"])
                self.recibos_data = _serialize_decimals(res["recibos"])
                self.propiedades_tipo_data = _serialize_decimals(res["prop_tipo"])
                self.kpi_financiero = _serialize_decimals(res["kpi_fin"])
                self.top_asesores_data = _serialize_decimals(res["top_asesores"])
                self.tunel_vencimientos_data = _serialize_decimals(res["tunel"])

                self.vencimiento_data = _serialize_decimals(res["venc_data"])
                self.vencimientos_lista = _serialize_decimals(res["venc_lista"])
                self.incidentes_data = _serialize_decimals(res["incidentes"])

                self.is_loading = False
                self.errores_carga = res["errors"]

                if res["errors"]:
                    yield rx.toast.warning(
                        f"Carga parcial: {len(res['errors'])} métricas fallaron.",
                        position="bottom-right",
                    )

            # Lanzamos la validación de alertas
            from src.presentacion_reflex.state.alertas_state import AlertasState

            yield AlertasState.check_alerts

        except Exception as e:
            logger.error(
                f"load_dashboard_data ERROR: {type(e).__name__}: {e}", exc_info=True
            )
            async with self:
                self.error_message = (
                    f"Error al cargar datos: {type(e).__name__}: {str(e)}"
                )
                self.is_loading = False

    MONTH_MAP: ClassVar[Dict[str, int]] = {
        "Enero": 1,
        "Febrero": 2,
        "Marzo": 3,
        "Abril": 4,
        "Mayo": 5,
        "Junio": 6,
        "Julio": 7,
        "Agosto": 8,
        "Septiembre": 9,
        "Octubre": 10,
        "Noviembre": 11,
        "Diciembre": 12,
    }

    def set_month(self, value: str):
        """Actualiza el mes seleccionado."""
        if value in self.MONTH_MAP:
            self.selected_month = self.MONTH_MAP[value]
        else:
            # Fallback for numeric strings or invalid input
            self.selected_month = (
                int(value) if value and value.isdigit() else datetime.now().month
            )

    @rx.var
    def selected_month_name(self) -> str:
        """Retorna el nombre del mes seleccionado."""
        # Reverse map lookup
        for name, num in self.MONTH_MAP.items():
            if num == self.selected_month:
                return name
        return "Mes"  # Fallback

    def set_year(self, value: str):
        """Actualiza el año seleccionado."""
        self.selected_year = int(value) if value else datetime.now().year

    def set_advisor(self, value: str):
        """Actualiza el asesor seleccionado."""
        if not value or value == "todos_asesores":
            self.selected_advisor_id = None
        else:
            self.selected_advisor_id = int(value)

    @rx.var
    def selected_advisor_value(self) -> str:
        """Valor seguro en string para el select del componente."""
        return (
            str(self.selected_advisor_id)
            if self.selected_advisor_id is not None
            else "todos_asesores"
        )

    def apply_filters(self):
        """Aplica los filtros y recarga los datos."""
        yield DashboardState.load_dashboard_data

    def reset_filters(self):
        """Resetea los filtros a valores por defecto."""
        self.selected_month = datetime.now().month
        self.selected_year = datetime.now().year
        self.selected_advisor_id = None
        yield DashboardState.load_dashboard_data

    # --- Variables Formateadas para UI ---

    @rx.var
    def kpi_ocupacion_financiera_view(self) -> str:
        return format_number(self.kpi_financiero.get("ocupacion_financiera", 0))

    @rx.var
    def kpi_eficiencia_recaudo_view(self) -> str:
        return format_number(self.kpi_financiero.get("eficiencia_recaudo", 0))

    @rx.var
    def kpi_potencial_total_view(self) -> str:
        return format_currency(self.kpi_financiero.get("potencial_total", 0))

    @rx.var
    def kpi_recaudo_real_view(self) -> str:
        return format_currency(self.kpi_financiero.get("recaudo_real", 0))

    @rx.var
    def mora_monto_total_view(self) -> str:
        return format_currency(self.mora_data.get("monto_total", 0))

    @rx.var
    def recaudo_mes_view(self) -> str:
        return format_currency(self.flujo_data.get("recaudado", 0))

    @rx.var
    def comisiones_monto_total_view(self) -> str:
        return format_currency(self.comisiones_data.get("monto_total", 0))

    @rx.var
    def recibos_monto_total_view(self) -> str:
        return format_currency(self.recibos_data.get("monto_total", 0))

    @rx.var
    def recaudo_porcentaje_view(self) -> str:
        return format_number(self.flujo_data.get("porcentaje", 0))

    @rx.var
    def ocupacion_porcentaje_view(self) -> str:
        return format_number(self.ocupacion_data.get("porcentaje_ocupacion", 0))

    @rx.var
    def mora_cantidad_contratos_view(self) -> str:
        return str(self.mora_data.get("cantidad_contratos", 0))

    @rx.var
    def flujo_porcentaje_int_view(self) -> int:
        return int(self.flujo_data.get("porcentaje", 0))

    @rx.var
    def ocupacion_ocupadas_view(self) -> str:
        return str(self.ocupacion_data.get("ocupadas", 0))

    @rx.var
    def ocupacion_disponibles_view(self) -> str:
        return str(self.ocupacion_data.get("disponibles", 0))

    @rx.var
    def comisiones_cantidad_view(self) -> str:
        return str(self.comisiones_data.get("cantidad_liquidaciones", 0))

    @rx.var
    def contratos_count_view(self) -> str:
        return str(self.contratos_count)

    @rx.var
    def recibos_cantidad_view(self) -> str:
        return str(self.recibos_data.get("cantidad", 0))

    @rx.var
    def pulso_tendencias(self) -> Dict[str, Dict[str, Any]]:
        return {
            "mora": {
                "valor": self.mora_monto_total_view,
                "progreso": min(self.flujo_data.get("porcentaje", 0), 100),
            },
            "recaudo": {
                "valor": self.recaudo_mes_view,
                "progreso": self.flujo_data.get("porcentaje", 0),
            },
            "ocupacion": {
                "valor": f"{self.ocupacion_porcentaje_view}%",
                "progreso": self.ocupacion_data.get("porcentaje_ocupacion", 0),
            },
            "comisiones": {"valor": self.comisiones_monto_total_view, "progreso": 0},
            "contratos": {"valor": self.contratos_count_view, "progreso": 0},
            "recibos": {"valor": self.recibos_cantidad_view, "progreso": 0},
            "alertas": {
                "valor": str(self.alertas_pendientes),
                "progreso": min(self.alertas_pendientes * 10, 100),
            },
        }

    @rx.var
    def vencimiento_chart_fig(self) -> go.Figure:
        """Figura de Plotly para el gráfico de barras de vencimientos."""
        labels = ["30 Días", "60 Días", "90 Días"]
        values_30 = self.vencimiento_data.get("vence_30_dias", 0)
        values_60 = self.vencimiento_data.get("vence_60_dias", 0)
        values_90 = self.vencimiento_data.get("vence_90_dias", 0)
        fig = go.Figure()
        fig.add_trace(
            go.Bar(
                name="Próximos 30d",
                x=["Vencimientos"],
                y=[values_30],
                marker_color="#ef4444",
                text=[format_currency(values_30)],
                textposition="inside",
            )
        )
        fig.add_trace(
            go.Bar(
                name="30-60 días",
                x=["Vencimientos"],
                y=[values_60],
                marker_color="#f59e0b",
                text=[format_currency(values_60)],
                textposition="inside",
            )
        )
        fig.add_trace(
            go.Bar(
                name="60-90 días",
                x=["Vencimientos"],
                y=[values_90],
                marker_color="#14b8a6",
                text=[format_currency(values_90)],
                textposition="inside",
            )
        )
        fig.update_layout(
            barmode="stack", **_default_fig_layout(height=320, show_legend=True)
        )
        return fig

    @rx.var
    def evolucion_chart_fig(self) -> go.Figure:
        """Figura de Plotly para el gráfico de área de evolución."""
        etiquetas = self.evolucion_data.get("etiquetas", [])
        valores = self.evolucion_data.get("valores", [])
        targets = [v * 1.1 for v in valores] if valores else []

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=etiquetas,
                y=valores,
                fill="tozeroy",
                mode="lines+markers",
                line=dict(color="#3b82f6", width=3),
                marker=dict(size=8, color="#3b82f6"),
                fillcolor="rgba(59, 130, 246, 0.2)",
                text=[format_currency(v) for v in valores],
                hoverinfo="text+x",
                name="Real",
            )
        )

        # AGREGAR: segunda traza con línea punteada de target
        if targets:
            fig.add_trace(
                go.Scatter(
                    x=etiquetas,
                    y=targets,
                    mode="lines",
                    line=dict(color="#f59e0b", width=2, dash="dash"),
                    name="Target",
                )
            )

        fig.update_layout(**_default_fig_layout(height=320, show_legend=True))
        return fig

    @rx.var
    def ocupacion_chart_fig(self) -> go.Figure:
        """Figura de Plotly para el gráfico circular de ocupación."""
        ocupadas = self.ocupacion_data.get("ocupadas", 0)
        disponibles = self.ocupacion_data.get("disponibles", 0)

        fig = go.Figure(
            data=[
                go.Pie(
                    labels=["Ocupadas", "Disponibles"],
                    values=[ocupadas, disponibles],
                    hole=0.5,
                    marker_colors=["#14b8a6", "#f59e0b"],
                    textinfo="label+percent",
                )
            ]
        )
        fig.update_layout(
            margin=dict(l=20, r=20, t=20, b=20),
            paper_bgcolor="rgba(0,0,0,0)",
            showlegend=True,
            height=250,
        )
        return fig

    @rx.var
    def propiedades_tipo_chart_fig(self) -> go.Figure:
        """Figura Plotly para el gráfico de barras de propiedades por tipo."""
        colors = ["#475569", "#6366f1", "#8b5cf6", "#ec4899", "#14b8a6"]
        tipos = list(self.propiedades_tipo_data.keys())
        cantidades = list(self.propiedades_tipo_data.values())

        fig = go.Figure(
            data=[
                go.Bar(
                    x=tipos,
                    y=cantidades,
                    marker_color=colors[: len(tipos)],
                    text=cantidades,
                    textposition="auto",
                )
            ]
        )
        fig.update_layout(**_default_fig_layout(height=280))
        return fig

    @rx.var
    def top_asesores_chart_fig(self) -> go.Figure:
        """Figura Plotly para el gráfico de top asesores."""
        nombres = [
            row.get("nombre", "N/A").split()[0] for row in self.top_asesores_data
        ]
        revenues = [row.get("revenue", 0) for row in self.top_asesores_data]
        ranking_colors = ["#c96442", "#d97757", "#e8a080"] + ["#d1d5db"] * max(
            0, len(nombres) - 3
        )

        fig = go.Figure(
            data=[
                go.Bar(
                    y=nombres,
                    x=revenues,
                    orientation="h",
                    marker_color=ranking_colors,
                    text=[format_currency(r) for r in revenues],
                    textposition="auto",
                )
            ]
        )
        fig.update_layout(
            **_default_fig_layout(
                height=280, yaxis=dict(showgrid=False, autorange="reversed")
            )
        )
        return fig

    @rx.var
    def tunel_chart_fig(self) -> go.Figure:
        """Figura Plotly para el gráfico de tunel de vencimientos."""
        meses = [row.get("mes", "N/A") for row in self.tunel_vencimientos_data]
        riesgos = [row.get("valor_riesgo", 0) for row in self.tunel_vencimientos_data]
        n = len(riesgos)
        colors = (
            [f"rgba(201, 100, 66, {0.3 + 0.7 * (n - i) / n})" for i in range(n)]
            if n > 0
            else []
        )
        fig = go.Figure(
            data=[
                go.Bar(
                    y=meses,
                    x=riesgos,
                    orientation="h",
                    marker_color=colors,
                    text=[format_currency(v) for v in riesgos],
                    textposition="outside",
                )
            ]
        )
        fig.update_layout(**_default_fig_layout(height=280))
        return fig

    @rx.var
    def incidentes_chart_fig(self) -> go.Figure:
        """Figura Plotly para el gráfico circular de incidentes."""
        por_estado = self.incidentes_data.get("por_estado", {})
        por_estado = dict(sorted(por_estado.items(), key=lambda x: x[1], reverse=True))
        COLORS_MAP = {
            "Reportado": "#FF8042",
            "Cotizado": "#FFBB28",
            "Aprobado": "#0088FE",
            "En Reparación": "#00C49F",
            "Finalizado": "#8884d8",
        }
        fig = go.Figure(
            data=[
                go.Bar(
                    y=list(por_estado.keys()),
                    x=list(por_estado.values()),
                    orientation="h",
                    marker_color=[
                        COLORS_MAP.get(k, "#6b7280") for k in por_estado.keys()
                    ],
                    text=list(por_estado.values()),
                    textposition="outside",
                )
            ]
        )
        fig.update_layout(**_default_fig_layout(height=280))
        return fig
