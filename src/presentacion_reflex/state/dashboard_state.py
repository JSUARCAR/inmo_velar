import sys
import decimal
from datetime import date, datetime
from typing import Any, Dict, List, Optional

import reflex as rx

from src.aplicacion.servicios.servicio_dashboard import ServicioDashboard
from src.infraestructura.persistencia.database import db_manager
from src.infraestructura.persistencia.repositorio_asesor_sqlite import RepositorioAsesorSQLite
from src.infraestructura.persistencia.repositorio_dashboard_sqlite import RepositorioDashboardSQLite
from src.presentacion_reflex.utils.formatters import format_currency, format_number


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

    # Guard: ID único del run activo (para detectar concurrencia entre sesiones)
    _load_run_id: int = 0

    def on_load(self):
        """Se ejecuta al montar la página del dashboard."""
        import time
        run_id = int(time.time() * 1000) % 1000000  # ms timestamp mod 1M
        self._load_run_id = run_id
        print(f"[DASH_DEBUG] DashboardState.on_load CALLED | run_id={run_id}", file=sys.stderr, flush=True)
        self.load_advisor_options()
        print(f"[DASH_DEBUG] on_load → yield load_dashboard_data | run_id={run_id}", file=sys.stderr, flush=True)
        yield DashboardState.load_dashboard_data

    def load_advisor_options(self):
        """Carga la lista de asesores para el dropdown."""
        print("[DASH_DEBUG] load_advisor_options START", file=sys.stderr, flush=True)
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
            print(f"[DASH_DEBUG] load_advisor_options OK | count={len(self.advisor_options)}", file=sys.stderr, flush=True)
        except Exception as e:
            import traceback
            print(f"[DASH_DEBUG] load_advisor_options ERROR: {e}", file=sys.stderr, flush=True)
            traceback.print_exc(file=sys.stderr)
            self.advisor_options = []

    def load_dashboard_data(self):
        """
        Carga todos los datos del dashboard.
        NOTA: Usa generador síncrono con yield (no background task) para garantizar
        que el estado se entrega siempre al WebSocket activo del cliente actual.
        Esto elimina el 'Warning: disconnected client' de los background tasks en F5.
        """
        import traceback
        print(f"[DASH_DEBUG] load_dashboard_data START (sync) | run_id={self._load_run_id}", file=sys.stderr, flush=True)

        self.is_loading = True
        self.error_message = ""
        yield  # ← Entrega is_loading=True al WebSocket activo → spinner visible

        try:
            mes = self.selected_month
            anio = self.selected_year
            id_asesor = self.selected_advisor_id
            print(f"[DASH_DEBUG] filtros | mes={mes} anio={anio} asesor={id_asesor}", file=sys.stderr, flush=True)

            repo_dashboard = RepositorioDashboardSQLite(db_manager)
            servicio = ServicioDashboard(repo_dashboard=repo_dashboard)
            print("[DASH_DEBUG] servicio instanciado OK", file=sys.stderr, flush=True)

            print("[DASH_DEBUG] obteniendo flujo_caja_mes...", file=sys.stderr, flush=True)
            datos_flujo = servicio.obtener_flujo_caja_mes(mes=mes, anio=anio, id_asesor=id_asesor)
            print(f"[DASH_DEBUG] flujo_caja_mes OK | {datos_flujo}", file=sys.stderr, flush=True)

            print("[DASH_DEBUG] obteniendo tasa_ocupacion...", file=sys.stderr, flush=True)
            datos_ocupacion = servicio.obtener_tasa_ocupacion(id_asesor=id_asesor)
            print(f"[DASH_DEBUG] tasa_ocupacion OK | {datos_ocupacion}", file=sys.stderr, flush=True)

            print("[DASH_DEBUG] obteniendo contratos_activos...", file=sys.stderr, flush=True)
            contratos_activos = servicio.obtener_total_contratos_activos(id_asesor=id_asesor)
            print(f"[DASH_DEBUG] contratos_activos OK | {contratos_activos}", file=sys.stderr, flush=True)

            print("[DASH_DEBUG] obteniendo comisiones_pendientes...", file=sys.stderr, flush=True)
            datos_comisiones = servicio.obtener_comisiones_pendientes(id_asesor=id_asesor)
            print("[DASH_DEBUG] comisiones OK", file=sys.stderr, flush=True)

            print("[DASH_DEBUG] obteniendo cartera_mora...", file=sys.stderr, flush=True)
            datos_mora = servicio.obtener_cartera_mora()
            print("[DASH_DEBUG] mora OK", file=sys.stderr, flush=True)

            print("[DASH_DEBUG] obteniendo contratos_por_vencer...", file=sys.stderr, flush=True)
            datos_vencimiento = servicio.obtener_contratos_por_vencer()
            print("[DASH_DEBUG] vencimientos OK", file=sys.stderr, flush=True)

            print("[DASH_DEBUG] obteniendo metricas_incidentes...", file=sys.stderr, flush=True)
            datos_incidentes = servicio.obtener_metricas_incidentes()
            print("[DASH_DEBUG] incidentes OK", file=sys.stderr, flush=True)

            print("[DASH_DEBUG] obteniendo evolucion_recaudo...", file=sys.stderr, flush=True)
            datos_evolucion = servicio.obtener_evolucion_recaudo(mes_fin=mes, anio_fin=anio)
            print("[DASH_DEBUG] evolucion OK", file=sys.stderr, flush=True)

            print("[DASH_DEBUG] obteniendo recibos_vencidos...", file=sys.stderr, flush=True)
            datos_recibos = servicio.obtener_recibos_vencidos_resumen()
            print("[DASH_DEBUG] recibos OK", file=sys.stderr, flush=True)

            print("[DASH_DEBUG] obteniendo propiedades_tipo...", file=sys.stderr, flush=True)
            datos_propiedades_tipo = servicio.obtener_propiedades_por_tipo(id_asesor=id_asesor)
            print("[DASH_DEBUG] propiedades_tipo OK", file=sys.stderr, flush=True)

            print("[DASH_DEBUG] obteniendo metricas_expertas...", file=sys.stderr, flush=True)
            datos_kpi_financiero = servicio.obtener_metricas_expertas(id_asesor=id_asesor)
            print("[DASH_DEBUG] metricas_expertas OK", file=sys.stderr, flush=True)

            if not id_asesor:
                print("[DASH_DEBUG] obteniendo top_asesores y tunel...", file=sys.stderr, flush=True)
                datos_top_asesores = servicio.obtener_top_asesores_revenue()
                datos_tunel = servicio.obtener_tunel_vencimientos()
                print("[DASH_DEBUG] top_asesores y tunel OK", file=sys.stderr, flush=True)
            else:
                datos_top_asesores = []
                datos_tunel = []

            print("[DASH_DEBUG] todos los datos obtenidos, actualizando estado...", file=sys.stderr, flush=True)

            # Actualizar estado sanitizando tipos para evitar crash en Reflex JSON serializer
            self.mora_data = _serialize_decimals(datos_mora)
            self.flujo_data = _serialize_decimals(datos_flujo)
            self.ocupacion_data = _serialize_decimals(datos_ocupacion)
            self.comisiones_data = _serialize_decimals(datos_comisiones)
            self.contratos_count = _serialize_decimals(contratos_activos)
            self.recibos_data = _serialize_decimals(datos_recibos)
            self.vencimiento_data = _serialize_decimals(datos_vencimiento)
            self.evolucion_data = _serialize_decimals(datos_evolucion)
            self.incidentes_data = _serialize_decimals(datos_incidentes)
            self.propiedades_tipo_data = _serialize_decimals(datos_propiedades_tipo)
            self.kpi_financiero = _serialize_decimals(datos_kpi_financiero)
            self.top_asesores_data = _serialize_decimals(datos_top_asesores)
            self.tunel_vencimientos_data = _serialize_decimals(datos_tunel)
            self.is_loading = False

            print("[DASH_DEBUG] load_dashboard_data COMPLETO OK (sync generator)", file=sys.stderr, flush=True)

        except Exception as e:
            print(f"[DASH_DEBUG] load_dashboard_data ERROR: {type(e).__name__}: {e}", file=sys.stderr, flush=True)
            traceback.print_exc(file=sys.stderr)
            self.error_message = f"Error al cargar datos: {type(e).__name__}: {str(e)}"
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
