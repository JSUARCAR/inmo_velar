from datetime import datetime
from typing import Any, Dict, List, Optional

import reflex as rx

from src.aplicacion.servicios.servicio_dashboard import ServicioDashboard
from src.infraestructura.persistencia.database import db_manager
from src.infraestructura.persistencia.repositorio_asesor_sqlite import RepositorioAsesorSQLite
from src.infraestructura.persistencia.repositorio_dashboard_sqlite import RepositorioDashboardSQLite
from src.presentacion_reflex.utils.formatters import format_currency, format_number


class DashboardState(rx.State):
    """
    Estado del Dashboard.
    Maneja datos de KPIs, gráficos y filtros.
    """

    # Estado de carga
    is_loading: bool = False
    error_message: str = ""

    # Filtros
    selected_month: int = datetime.now().month
    selected_year: int = datetime.now().year
    selected_advisor_id: Optional[int] = None

    # Opciones para filtros
    advisor_options: List[Dict[str, Any]] = []

    # Datos de KPIs
    mora_data: Dict[str, Any] = {"monto_total": 0, "cantidad_contratos": 0}

    flujo_data: Dict[str, Any] = {"recaudado": 0, "esperado": 0, "porcentaje": 0}

    ocupacion_data: Dict[str, Any] = {"porcentaje_ocupacion": 0, "ocupadas": 0, "disponibles": 0}

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

    # Datos de gráficos
    vencimiento_data: Dict[str, Any] = {"vence_30_dias": 0, "vence_60_dias": 0, "vence_90_dias": 0}

    evolucion_data: Dict[str, Any] = {"etiquetas": [], "valores": []}

    incidentes_data: Dict[str, Any] = {"por_estado": {}}

    def on_load(self):
        """Se ejecuta al montar la página del dashboard."""
        # Cargar opciones de asesores para filtro
        self.load_advisor_options()
        # Cargar datos iniciales - yield background event
        yield DashboardState.load_dashboard_data

    def load_advisor_options(self):
        """Carga la lista de asesores para el dropdown."""
        try:
            repo_asesores = RepositorioAsesorSQLite(db_manager)
            asesores = repo_asesores.listar_todos()

            self.advisor_options = [
                {
                    "value": str(a.id_asesor),
                    "label": getattr(a, "nombre_completo", f"Asesor {a.id_asesor}"),
                }
                for a in asesores
            ]
        except Exception:
            pass  # print(f"Error cargando asesores: {e}") [OpSec Removed]
            self.advisor_options = []

    @rx.event(background=True)
    async def load_dashboard_data(self):
        """
        Carga todos los datos del dashboard en background.
        Usa @rx.event(background=True) para no bloquear la UI.
        """
        async with self:
            self.is_loading = True
            self.error_message = ""

        try:
            # Obtener filtros actuales
            mes = self.selected_month
            anio = self.selected_year
            id_asesor = self.selected_advisor_id

            # Inicializar servicio
            repo_dashboard = RepositorioDashboardSQLite(db_manager)
            servicio = ServicioDashboard(repo_dashboard=repo_dashboard)

            # Fetch all data (estas llamadas son síncronas, pero estamos en background thread)
            datos_flujo = servicio.obtener_flujo_caja_mes(mes=mes, anio=anio, id_asesor=id_asesor)
            datos_ocupacion = servicio.obtener_tasa_ocupacion(id_asesor=id_asesor)
            contratos_activos = servicio.obtener_total_contratos_activos(id_asesor=id_asesor)
            datos_comisiones = servicio.obtener_comisiones_pendientes(id_asesor=id_asesor)
            datos_mora = servicio.obtener_cartera_mora()
            datos_vencimiento = servicio.obtener_contratos_por_vencer()
            datos_incidentes = servicio.obtener_metricas_incidentes()
            datos_evolucion = servicio.obtener_evolucion_recaudo(mes_fin=mes, anio_fin=anio)
            datos_recibos = servicio.obtener_recibos_vencidos_resumen()

            # Actualizar estado con datos
            async with self:
                self.mora_data = datos_mora
                self.flujo_data = datos_flujo
                self.ocupacion_data = datos_ocupacion
                self.comisiones_data = datos_comisiones
                self.contratos_count = contratos_activos
                self.recibos_data = datos_recibos
                self.vencimiento_data = datos_vencimiento
                self.evolucion_data = datos_evolucion
                self.incidentes_data = datos_incidentes
                self.propiedades_tipo_data = servicio.obtener_propiedades_por_tipo(
                    id_asesor=id_asesor
                )

                # Cargar métricas expertas
                self.kpi_financiero = servicio.obtener_metricas_expertas(id_asesor=id_asesor)
                # Solo cargar charts globales si no hay filtro de asesor (o adaptar si se requiere)
                if not id_asesor:
                    self.top_asesores_data = servicio.obtener_top_asesores_revenue()
                    self.tunel_vencimientos_data = servicio.obtener_tunel_vencimientos()
                else:
                    self.top_asesores_data = []  # No mostrar ranking global si filtra por uno
                    # El tunel podria filtrarse pero por ahora lo dejamos global o vacio
                    self.tunel_vencimientos_data = []

                self.is_loading = False

        except Exception as e:
            pass  # print(f"Error cargando dashboard: {e}") [OpSec Removed]
            import traceback

            traceback.print_exc()
            async with self:
                self.error_message = f"Error al cargar datos: {str(e)}"
                self.is_loading = False

    MONTH_MAP = {
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
            self.selected_month = int(value) if value and value.isdigit() else datetime.now().month

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
    def vencimiento_chart_data(self) -> List[Dict[str, Any]]:
        """Transforma datos de vencimiento para el gráfico de barras."""
        return [
            {
                "name": "30 Días",
                "value": self.vencimiento_data.get("vence_30_dias", 0),
                "fill": "#8884d8",
            },
            {
                "name": "60 Días",
                "value": self.vencimiento_data.get("vence_60_dias", 0),
                "fill": "#82ca9d",
            },
            {
                "name": "90 Días",
                "value": self.vencimiento_data.get("vence_90_dias", 0),
                "fill": "#ffc658",
            },
        ]

    @rx.var
    def evolucion_chart_data(self) -> List[Dict[str, Any]]:
        """Transforma datos de evolución para el gráfico de área."""
        etiquetas = self.evolucion_data.get("etiquetas", [])
        valores = self.evolucion_data.get("valores", [])

        data = []
        for i in range(len(etiquetas)):
            data.append({
                "name": etiquetas[i], 
                "recaudo": valores[i],
                "recaudo_view": format_currency(valores[i])
            })
        return data

    @rx.var
    def ocupacion_chart_data(self) -> List[Dict[str, Any]]:
        """Transforma datos de ocupación para el gráfico circular."""
        ocupadas = self.ocupacion_data.get("ocupadas", 0)
        disponibles = self.ocupacion_data.get("disponibles", 0)
        return [
            {"name": "Ocupadas", "value": ocupadas, "fill": "#00C49F"},
            {"name": "Disponibles", "value": disponibles, "fill": "#FFBB28"},
        ]

    @rx.var
    def propiedades_tipo_chart_data(self) -> List[Dict[str, Any]]:
        """Transforma datos de propiedades por tipo para el gráfico de barras."""
        data = []
        # Colores "élite" para la gráfica
        colors = ["#475569", "#6366f1", "#8b5cf6", "#ec4899", "#14b8a6"]

        i = 0
        for tipo, cantidad in self.propiedades_tipo_data.items():
            color = colors[i % len(colors)]
            data.append({"name": tipo, "value": cantidad, "fill": color})
            i += 1
        return data

    @rx.var
    def top_asesores_chart_data(self) -> List[Dict[str, Any]]:
        """Transforma datos de top asesores para gráfico."""
        return [
            {
                "name": row["nombre"].split()[0],  # Primer nombre para ahorrar espacio
                "revenue": row["revenue"],
                "revenue_view": format_currency(row["revenue"]),
                "contratos": row["contratos"],
            }
            for row in self.top_asesores_data
        ]

    @rx.var
    def tunel_chart_data(self) -> List[Dict[str, Any]]:
        """Transforma datos de tunel de vencimientos."""
        return [
            {
                "name": row["mes"], 
                "riesgo": row["valor_riesgo"],
                "riesgo_view": format_currency(row["valor_riesgo"])
            }
            for row in self.tunel_vencimientos_data
        ]

    @rx.var
    def incidentes_chart_data(self) -> List[Dict[str, Any]]:
        """Transforma datos de incidentes para el gráfico circular."""
        por_estado = self.incidentes_data.get("por_estado", {})

        # Mapa de colores para estados
        colors = {
            "Reportado": "#FF8042",
            "Cotizado": "#FFBB28",
            "Aprobado": "#0088FE",
            "En Reparación": "#00C49F",
            "Finalizado": "#8884d8",
        }

        data = []
        for estado, cantidad in por_estado.items():
            data.append({"name": estado, "value": cantidad, "fill": colors.get(estado, "#8884d8")})
        return data
