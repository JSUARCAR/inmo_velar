import sys
import decimal
from datetime import date, datetime
from typing import Any, Dict, List, Optional, ClassVar

import reflex as rx

from src.aplicacion.servicios.servicio_dashboard import ServicioDashboard
from src.infraestructura.persistencia.database import db_manager
from src.infraestructura.persistencia.repositorio_asesor_postgres import RepositorioAsesorPostgres
from src.infraestructura.persistencia.repositorio_dashboard import RepositorioDashboard
from src.presentacion_reflex.utils.formatters import format_currency, format_number


import logging
logger = logging.getLogger(__name__)

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

    FASE 1+2: Hydration-safe + Métodos atómicos.
    - _hydration_ready previene carga de datos durante SSR.
    - load_dashboard_data() NO es generador (sin yields intermedios).
    - Datos se cargan en 3 métodos atómicos con try/except individual.
    """

    # Estado de carga
    is_loading: bool = False
    error_message: str = ""

    # Flag de hidratación: solo True después de que el componente se montó en cliente
    _hydration_ready: bool = False

    # Filtros — se inicializan en on_load para tomar la fecha real del sistema
    selected_month: int = 0  # 0 = "no inicializado aún"
    selected_year: int = 0   # 0 = "no inicializado aún"
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

    alertas_pendientes: int = 0

    # Datos de gráficos
    vencimiento_data: Dict[str, Any] = {"vence_30_dias": 0, "vence_60_dias": 0, "vence_90_dias": 0}
    vencimientos_lista: List[Dict[str, Any]] = []

    evolucion_data: Dict[str, Any] = {"etiquetas": [], "valores": []}

    incidentes_data: Dict[str, Any] = {"por_estado": {}}

    # Guard: ID único del run activo (para detectar concurrencia entre sesiones)
    _load_run_id: int = 0

    # ─── Fase 1: Hydration-safe on_load ───────────────────────────────────────

    def on_load(self):
        """
        Se ejecuta al montar la página del dashboard.
        Marca _hydration_ready=True y dispara la carga de datos como evento
        separado para evitar mutación de estado durante SSR/hydration.
        """
        import time
        run_id = int(time.time() * 1000) % 1000000
        self._load_run_id = run_id
        self._hydration_ready = True
        logger.debug(f"DashboardState.on_load CALLED | run_id={run_id} | hydration_ready=True")

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
        from src.infraestructura.persistencia.repositorio_alerta_postgres import RepositorioAlertaPostgres
        repo_dashboard = RepositorioDashboard(db_manager)
        repo_alerta = RepositorioAlertaPostgres(db_manager)
        return ServicioDashboard(repo_dashboard=repo_dashboard, repo_alerta=repo_alerta)

    @staticmethod
    def _safe_fetch(fetch_fn, default_val, error_list: Optional[List[str]] = None):
        """Ejecuta una función de fetch con fallback seguro."""
        try:
            return fetch_fn()
        except Exception as e:
            msg = f"{getattr(fetch_fn, '__name__', 'lambda')} falló."
            logger.error(f"Error fetch KPI {getattr(fetch_fn, '__name__', 'lambda')}: {e}")
            if error_list is not None:
                error_list.append(msg)
            return default_val

    def _load_kpis_rapidos(self, servicio: ServicioDashboard, errors: List[str]) -> None:
        """
        Carga KPIs primarios: alertas, flujo de caja, ocupación, contratos, comisiones, mora.
        Estos datos se muestran inmediato en las tarjetas principales.
        """
        mes = self.selected_month
        anio = self.selected_year
        id_asesor = self.selected_advisor_id

        try:
            # Alertas
            conteo_alertas = self._safe_fetch(servicio.obtener_conteo_alertas_pendientes, 0, errors)
            self.alertas_pendientes = _serialize_decimals(conteo_alertas)

            # Flujo de caja
            datos_flujo = self._safe_fetch(
                lambda: servicio.obtener_flujo_caja_mes(mes=mes, anio=anio, id_asesor=id_asesor),
                {"recaudado": 0, "esperado": 0, "porcentaje": 0},
                errors
            )
            self.flujo_data = _serialize_decimals(datos_flujo)

            # Ocupación
            datos_ocupacion = self._safe_fetch(
                lambda: servicio.obtener_tasa_ocupacion(id_asesor=id_asesor),
                {"porcentaje_ocupacion": 0, "ocupadas": 0, "disponibles": 0},
                errors
            )
            self.ocupacion_data = _serialize_decimals(datos_ocupacion)

            # Contratos activos
            contratos_activos = self._safe_fetch(
                lambda: servicio.obtener_total_contratos_activos(id_asesor=id_asesor), 0, errors
            )
            self.contratos_count = _serialize_decimals(contratos_activos)

            # Comisiones
            datos_comisiones = self._safe_fetch(
                lambda: servicio.obtener_comisiones_pendientes(id_asesor=id_asesor),
                {"monto_total": 0, "cantidad_liquidaciones": 0},
                errors
            )
            self.comisiones_data = _serialize_decimals(datos_comisiones)

            # Mora
            datos_mora = self._safe_fetch(
                servicio.obtener_cartera_mora,
                {"monto_total": 0, "cantidad_contratos": 0},
                errors
            )
            self.mora_data = _serialize_decimals(datos_mora)

            logger.debug("_load_kpis_rapidos OK")
        except Exception as e:
            logger.error(f"_load_kpis_rapidos ERROR: {e}", exc_info=True)
            errors.append("_load_kpis_rapidos_fatal")

    def _load_graficas(self, servicio: ServicioDashboard, errors: List[str]) -> None:
        """
        Carga datos de gráficas: evolución recaudo, recibos, propiedades,
        KPI financiero, top asesores y túnel de vencimientos.
        """
        mes = self.selected_month
        anio = self.selected_year
        id_asesor = self.selected_advisor_id

        try:
            # Evolución recaudo
            datos_evolucion = self._safe_fetch(
                lambda: servicio.obtener_evolucion_recaudo(mes_fin=mes, anio_fin=anio),
                {"etiquetas": [], "valores": []},
                errors
            )
            self.evolucion_data = _serialize_decimals(datos_evolucion)

            # Recibos vencidos
            datos_recibos = self._safe_fetch(
                servicio.obtener_recibos_vencidos_resumen,
                {"cantidad": 0, "monto_total": 0},
                errors
            )
            self.recibos_data = _serialize_decimals(datos_recibos)

            # Propiedades por tipo
            datos_propiedades_tipo = self._safe_fetch(
                lambda: servicio.obtener_propiedades_por_tipo(id_asesor=id_asesor), {}, errors
            )
            self.propiedades_tipo_data = _serialize_decimals(datos_propiedades_tipo)

            # KPI Financiero experto
            datos_kpi_financiero = self._safe_fetch(
                lambda: servicio.obtener_metricas_expertas(id_asesor=id_asesor),
                {"ocupacion_financiera": 0, "eficiencia_recaudo": 0, "potencial_total": 0, "recaudo_real": 0},
                errors
            )
            self.kpi_financiero = _serialize_decimals(datos_kpi_financiero)

            # Top asesores y túnel (solo sin filtro de asesor)
            if not id_asesor:
                datos_top_asesores = self._safe_fetch(servicio.obtener_top_asesores_revenue, [], errors)
                self.top_asesores_data = _serialize_decimals(datos_top_asesores)

                datos_tunel = self._safe_fetch(servicio.obtener_tunel_vencimientos, [], errors)
                self.tunel_vencimientos_data = _serialize_decimals(datos_tunel)
            else:
                self.top_asesores_data = []
                self.tunel_vencimientos_data = []

            logger.debug("_load_graficas OK")
        except Exception as e:
            logger.error(f"_load_graficas ERROR: {e}", exc_info=True)
            errors.append("_load_graficas_fatal")

    def _load_tablas_vencimiento(self, servicio: ServicioDashboard, errors: List[str]) -> None:
        """
        Carga datos de tablas de vencimiento e incidentes.
        Esta es la operación más pesada.
        """
        try:
            # Vencimientos agrupados
            datos_vencimiento = self._safe_fetch(
                servicio.obtener_contratos_por_vencer,
                {"vence_30_dias": 0, "vence_60_dias": 0, "vence_90_dias": 0},
                errors
            )
            self.vencimiento_data = _serialize_decimals(datos_vencimiento)

            # Lista detallada de vencimientos
            datos_vencimiento_lista = self._safe_fetch(
                lambda: servicio.obtener_contratos_proximos_vencer(90), [], errors
            )
            self.vencimientos_lista = _serialize_decimals(datos_vencimiento_lista)

            # Incidentes
            datos_incidentes = self._safe_fetch(
                servicio.obtener_metricas_incidentes,
                {"por_estado": {}},
                errors
            )
            self.incidentes_data = _serialize_decimals(datos_incidentes)

            logger.debug("_load_tablas_vencimiento OK")
        except Exception as e:
            logger.error(f"_load_tablas_vencimiento ERROR: {e}", exc_info=True)
            errors.append("_load_tablas_fatal")

    def load_dashboard_data(self):
        """
        Carga todos los datos del dashboard en 3 fases atómicas.
        
        FASE 2: Refactorizado de generador con 5 yields a método determinista.
        Solo se hace un yield inicial para mostrar el spinner y un yield final
        para entregar todos los datos de golpe. Sin yields intermedios.
        
        FASE 1: Solo ejecuta si _hydration_ready es True (post-mount en cliente).
        """
        if not self._hydration_ready:
            logger.warning("load_dashboard_data ABORTADO: hydration no lista")
            return

        current_run_id = self._load_run_id
        logger.debug(f"load_dashboard_data START | run_id={current_run_id}")

        self.is_loading = True
        self.error_message = ""
        yield  # ← Entrega is_loading=True → spinner visible

        # Concurrency Guard
        if self._load_run_id != current_run_id:
            logger.warning(f"load_dashboard_data CANCELADO: run_id obsoleto. {self._load_run_id} != {current_run_id}")
            return

        try:
            servicio = self._get_servicio()
            logger.debug("Servicio Dashboard instanciado OK")
            
            fetch_errors: List[str] = []

            # Fase atómica 1: KPIs rápidos
            self._load_kpis_rapidos(servicio, fetch_errors)

            # Fase atómica 2: Gráficas
            self._load_graficas(servicio, fetch_errors)

            # Fase atómica 3: Tablas de vencimiento
            self._load_tablas_vencimiento(servicio, fetch_errors)

            self.is_loading = False
            logger.info("load_dashboard_data COMPLETO OK")

            if fetch_errors:
                yield rx.toast.warning(
                    f"Carga parcial: {len(fetch_errors)} métricas fallaron. Algunos datos pueden estar en 0.", 
                    position="bottom-right"
                )
            
            # Post-carga: sincronizar alertas de manera segura post-SSR
            from src.presentacion_reflex.state.alertas_state import AlertasState
            yield AlertasState.check_alerts

        except Exception as e:
            logger.error(f"load_dashboard_data ERROR: {type(e).__name__}: {e}", exc_info=True)
            self.error_message = f"Error al cargar datos: {type(e).__name__}: {str(e)}"
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

    @rx.var
    def selected_advisor_value(self) -> str:
        """Valor seguro en string para el select del componente."""
        return str(self.selected_advisor_id) if self.selected_advisor_id is not None else "todos_asesores"

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
    def contratos_vencer_mandato_view(self) -> List[Dict[str, Any]]:
        return [c for c in self.vencimientos_lista if str(c.get("tipo_contrato", "")).strip().lower() == "mandato"]

    @rx.var
    def contratos_vencer_arrendamiento_view(self) -> List[Dict[str, Any]]:
        return [c for c in self.vencimientos_lista if str(c.get("tipo_contrato", "")).strip().lower() == "arrendamiento"]

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
                "name": row.get("nombre", "N/A").split()[0],  # Primer nombre para ahorrar espacio
                "revenue": row.get("revenue", 0),
                "revenue_view": format_currency(row.get("revenue", 0)),
                "contratos": row.get("contratos", 0),
            }
            for row in self.top_asesores_data
        ]

    @rx.var
    def tunel_chart_data(self) -> List[Dict[str, Any]]:
        """Transforma datos de tunel de vencimientos."""
        return [
            {
                "name": row.get("mes", "N/A"), 
                "riesgo": row.get("valor_riesgo", 0),
                "riesgo_view": format_currency(row.get("valor_riesgo", 0))
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
