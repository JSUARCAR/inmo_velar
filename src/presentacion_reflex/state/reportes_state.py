import csv
import io
from datetime import datetime
from typing import Any, Dict, List, Optional

import reflex as rx
from pydantic import BaseModel
from src.presentacion_reflex.state.auth_state import AuthState
from src.aplicacion.servicios.servicio_reportes import ServicioReportes

# Importación diferida de servicios para evitar ciclos y carga innecesaria
# Se realizarán dentro de los métodos


class ReportItem(BaseModel):
    id: str
    name: str
    description: str
    module: str


class ReportCategory(BaseModel):
    name: str
    icon: str
    color: str
    reports: List[ReportItem]


class ReportesState(rx.State):
    """Estado para el módulo avanzado de Reportes."""

    # Configuración de Categorías y Reportes
    categories: Dict[str, Dict[str, Any]] = {
        "GESTIÓN": {
            "icon": "folder-cog",
            "color": "#10b981",
            "reports": [
                {
                    "id": "personas",
                    "name": "Reporte de Personas",
                    "description": "Base de datos completa de usuarios y roles.",
                    "module": "Personas",
                },
                {
                    "id": "reporte_propietarios",
                    "name": "Reporte de Propietarios",
                    "description": "Información detallada de propietarios.",
                    "module": "Personas",
                },
                {
                    "id": "reporte_arrendatarios",
                    "name": "Reporte de Arrendatarios",
                    "description": "Información detallada de arrendatarios.",
                    "module": "Personas",
                },
                {
                    "id": "reporte_codeudores",
                    "name": "Reporte de Codeudores",
                    "description": "Información detallada de codeudores.",
                    "module": "Personas",
                },
                {
                    "id": "reporte_asesores",
                    "name": "Reporte de Asesores",
                    "description": "Información detallada de asesores.",
                    "module": "Personas",
                },
                {
                    "id": "propiedades",
                    "name": "Reporte de Propiedades",
                    "description": "Inventario detallado de inmuebles.",
                    "module": "Propiedades",
                },
                {
                    "id": "contratos_mandato",
                    "name": "Contratos: Mandato",
                    "description": "Gestión de contratos con propietarios.",
                    "module": "Contratos",
                },
                {
                    "id": "contratos_arrendamiento",
                    "name": "Contratos: Arrendamiento",
                    "description": "Gestión de contratos con arrendatarios.",
                    "module": "Contratos",
                },
                {
                    "id": "proveedores",
                    "name": "Reporte de Proveedores",
                    "description": "Directorio de proveedores y servicios.",
                    "module": "Proveedores",
                },
            ],
        },
        "OPERACIONES": {
            "icon": "activity",
            "color": "#f59e0b",
            "reports": [
                {
                    "id": "recaudos",
                    "name": "Reporte de Recaudos",
                    "description": "Control de pagos recibidos de inquilinos.",
                    "module": "Recaudos",
                },
                {
                    "id": "liquidaciones",
                    "name": "Reporte de Liquidaciones",
                    "description": "Histórico de pagos a propietarios.",
                    "module": "Liquidaciones",
                },
                {
                    "id": "liquidacion_asesores",
                    "name": "Liquidación Asesores",
                    "description": "Comisiones y pagos comerciales.",
                    "module": "Liquidación Asesores",
                },
                {
                    "id": "desocupaciones",
                    "name": "Reporte de Desocupaciones",
                    "description": "Procesos de restitución de inmuebles.",
                    "module": "Desocupaciones",
                },
                {
                    "id": "incidentes",
                    "name": "Reporte de Incidentes",
                    "description": "Bitácora de mantenimiento y reparaciones.",
                    "module": "Incidentes",
                },
                {
                    "id": "seguros",
                    "name": "Reporte de Seguros",
                    "description": "Control de pólizas vigentes.",
                    "module": "Seguros",
                },
                {
                    "id": "recibos_publicos",
                    "name": "Recibos Públicos",
                    "description": "Pagos de servicios públicos.",
                    "module": "Recibos Públicos",
                },
                {
                    "id": "saldos_favor",
                    "name": "Saldos a Favor",
                    "description": "Control de saldos acreedores.",
                    "module": "Saldos a Favor",
                },
                {
                    "id": "reporte_consolidado",
                    "name": "Reporte Financiero Consolidado",
                    "description": "Información unificada: propietarios, contratos, liquidaciones y estados financieros.",
                    "module": "Liquidaciones",
                },
            ],
        },
    }

    # Estado de Selección y Filtros
    selected_category: str = "GESTIÓN"
    selected_report_id: str = ""
    search_query: str = ""  # Busqueda global en sidebar

    # Filtros Dinámicos (Valores)
    filter_fecha_inicio: str = ""
    filter_fecha_fin: str = ""
    filter_estado: str = "Todos"
    filter_rol: str = "Todos"
    filter_asesor_id: str = "Todos"
    filter_busqueda_tabla: str = ""

    # Filtros específicos Recaudos
    filter_estado_recaudo: str = "Todos"
    filter_metodo_pago: str = "Todos"
    filter_periodo_inicio: str = ""
    filter_periodo_fin: str = ""

    # Filtros específicos Reporte Consolidado
    filter_fecha_pago_inicio: str = ""
    filter_fecha_pago_fin: str = ""
    filter_estado_contrato: str = "Todos"
    filter_estado_liquidacion: str = "Todos"
    filter_propietario_buscar: str = ""

    # Paginación y Datos
    preview_data: List[Dict[str, Any]] = []
    preview_headers: List[str] = []
    total_records: int = 0
    current_page: int = 1
    page_size: int = 20  # Límite por página en preview

    is_loading: bool = False
    error_message: str = ""

    # Opciones para dropdowns de filtros
    estado_options: List[str] = ["Todos", "Activo", "Inactivo"]
    rol_options: List[str] = [
        "Todos",
        "Propietario",
        "Arrendatario",
        "Codeudor",
        "Asesor",
    ]
    asesor_options: List[str] = ["Todos"]
    estado_recaudo_options: List[str] = ["Todos", "Pendiente", "Aplicado", "Reversado"]
    metodo_pago_options: List[str] = [
        "Todos",
        "Efectivo",
        "Transferencia",
        "PSE",
        "Consignación",
    ]
    estado_contrato_options: List[str] = ["Todos", "Activo", "Finalizado", "Cancelado"]
    estado_liquidacion_options: List[str] = [
        "Todos",
        "Sin Liquidar",
        "En Proceso",
        "Aprobada",
        "Pagada",
        "Cancelada",
    ]

    @rx.var
    def active_report(self) -> Dict[str, Any]:
        """Retorna metadatos del reporte seleccionado."""
        for cat in self.categories.values():
            for report in cat["reports"]:
                if report["id"] == self.selected_report_id:
                    return report
        return {}

    @rx.var
    async def filtered_grouped_reports(self) -> List[ReportCategory]:
        """Filtra y agrupa reportes para el sidebar (Retorna Modelos Tipados)."""
        filtered = []
        q = self.search_query.lower()

        for cat_name, cat_data in self.categories.items():
            reports = []
            for r in cat_data["reports"]:
                # 1. Filtro por texto
                if q and (
                    q not in r["name"].lower() and q not in r["description"].lower()
                ):
                    continue

                # 2. Filtro por Permisos (Backend check)
                if await self._check_access(r["module"]):
                    reports.append(
                        ReportItem(
                            id=r["id"],
                            name=r["name"],
                            description=r["description"],
                            module=r["module"],
                        )
                    )

            if reports:
                # Estructura plana para iteración fácil
                filtered.append(
                    ReportCategory(
                        name=cat_name,
                        icon=cat_data["icon"],
                        color=cat_data["color"],
                        reports=reports,
                    )
                )
        return filtered

    async def _check_access(self, module_name: str) -> bool:
        """Verifica acceso backend (Python puro no Var)."""
        # Acceder al estado real (no Var)
        auth_state = await self.get_state(AuthState)

        if not auth_state.is_authenticated:
            return False

        if auth_state.user_rol == "Administrador":
            return True

        return module_name in auth_state.allowed_modules

    def select_report(self, report_id: str):
        """Acción al seleccionar un reporte del sidebar."""
        self.selected_report_id = report_id
        self.current_page = 1
        self.filter_busqueda_tabla = ""
        self.filter_fecha_inicio = ""
        self.filter_fecha_fin = ""
        self.filter_estado = "Todos"
        self.filter_rol = "Todos"
        self.filter_asesor_id = "Todos"
        self.filter_estado_recaudo = "Todos"
        self.filter_metodo_pago = "Todos"
        self.filter_periodo_inicio = ""
        self.filter_periodo_fin = ""
        self.filter_fecha_pago_inicio = ""
        self.filter_fecha_pago_fin = ""
        self.filter_estado_contrato = "Todos"
        self.filter_estado_liquidacion = "Todos"
        self.filter_propietario_buscar = ""
        self.preview_data = []
        self.preview_headers = []
        return ReportesState.load_preview_data()

    def set_search_query(self, query: str):
        self.search_query = query

    def set_filter_busqueda(self, query: str):
        self.filter_busqueda_tabla = query

    def set_filter_activo(self, estado: str):
        self.filter_estado = estado
        self.current_page = 1
        return ReportesState.load_preview_data()

    def set_filter_rol(self, rol: str):
        self.filter_rol = rol
        self.current_page = 1
        return ReportesState.load_preview_data()

    def set_filter_asesor(self, asesor_id: str):
        self.filter_asesor_id = asesor_id
        self.current_page = 1
        return ReportesState.load_preview_data()

    def set_filter_estado_recaudo(self, estado: str):
        self.filter_estado_recaudo = estado
        self.current_page = 1
        return ReportesState.load_preview_data()

    def set_filter_metodo_pago(self, metodo: str):
        self.filter_metodo_pago = metodo
        self.current_page = 1
        return ReportesState.load_preview_data()

    def set_filter_periodo(self, periodo_inicio: str, periodo_fin: str):
        self.filter_periodo_inicio = periodo_inicio
        self.filter_periodo_fin = periodo_fin
        self.current_page = 1
        return ReportesState.load_preview_data()

    def set_filter_fecha_pago(self, fecha_inicio: str, fecha_fin: str):
        self.filter_fecha_pago_inicio = fecha_inicio
        self.filter_fecha_pago_fin = fecha_fin
        self.current_page = 1
        return ReportesState.load_preview_data()

    def set_filter_estado_contrato(self, estado: str):
        self.filter_estado_contrato = estado
        self.current_page = 1
        return ReportesState.load_preview_data()

    def set_filter_estado_liquidacion(self, estado: str):
        self.filter_estado_liquidacion = estado
        self.current_page = 1
        return ReportesState.load_preview_data()

    def set_filter_propietario(self, texto: str):
        self.filter_propietario_buscar = texto
        self.current_page = 1
        return ReportesState.load_preview_data()

    def next_page(self):
        if self.current_page * self.page_size < self.total_records:
            self.current_page += 1
            return ReportesState.load_preview_data()

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            return ReportesState.load_preview_data()

    @rx.event(background=True)
    async def load_preview_data(self):
        """Carga datos paginados para la tabla de previsualización."""
        # 1. Capturar TODOS los valores de estado de forma atómica
        async with self:
            if not self.selected_report_id:
                return
            self.is_loading = True
            self.error_message = ""

            # Snapshot atómico de estado para uso fuera del lock
            _report_id = self.selected_report_id
            _page = self.current_page
            _page_size = self.page_size
            _necesita_asesores = len(self.asesor_options) <= 1
            _filtros = {
                "busqueda": self.filter_busqueda_tabla,
                "estado": self.filter_estado,
                "rol": self.filter_rol,
                "asesor_id": self.filter_asesor_id,
                "estado_recaudo": self.filter_estado_recaudo,
                "metodo_pago": self.filter_metodo_pago,
                "periodo_inicio": self.filter_periodo_inicio,
                "periodo_fin": self.filter_periodo_fin,
                "fecha_pago_inicio": self.filter_fecha_pago_inicio,
                "fecha_pago_fin": self.filter_fecha_pago_fin,
                "estado_contrato": self.filter_estado_contrato,
                "estado_liquidacion": self.filter_estado_liquidacion,
                "propietario_buscar": self.filter_propietario_buscar,
            }

        # 2. Cargar asesores fuera del lock si es necesario
        if _necesita_asesores:
            options = await self._fetch_asesores_options()
            if options:
                async with self:
                    self.asesor_options = options

        # 3. Ejecutar I/O de datos fuera del lock
        try:
            data, headers, total = await self._fetch_data(
                report_id=_report_id,
                page=_page,
                limit=_page_size,
                filtros=_filtros,
                is_export=False,
            )

            async with self:
                self.preview_data = data
                self.preview_headers = headers
                self.total_records = total

        except Exception as e:
            async with self:
                self.error_message = f"Error cargando reporte: {str(e)}"
                self.preview_data = []
        finally:
            async with self:
                self.is_loading = False

    async def _fetch_asesores_options(self) -> List[str]:
        """Obtiene la lista de asesores para los filtros delegando al servicio sin mutar el estado."""
        try:
            servicio = ServicioReportes()
            return servicio.obtener_asesores_filtro()
        except Exception as e:
            print(f"Error cargando asesores en reportes: {e}")
            return []

    async def download_csv(self):
        """Genera y descarga todo el dataset en CSV UTF-8 con BOM."""
        # 1. Snapshot atómico del estado
        async with self:
            if not self.selected_report_id:
                return rx.window_alert("No hay reporte seleccionado.")
            
            _report_id = self.selected_report_id
            _filtros = {
                "busqueda": self.filter_busqueda_tabla,
                "estado": self.filter_estado,
                "rol": self.filter_rol,
                "asesor_id": self.filter_asesor_id,
                "estado_recaudo": self.filter_estado_recaudo,
                "metodo_pago": self.filter_metodo_pago,
                "periodo_inicio": self.filter_periodo_inicio,
                "periodo_fin": self.filter_periodo_fin,
                "fecha_pago_inicio": self.filter_fecha_pago_inicio,
                "fecha_pago_fin": self.filter_fecha_pago_fin,
                "estado_contrato": self.filter_estado_contrato,
                "estado_liquidacion": self.filter_estado_liquidacion,
                "propietario_buscar": self.filter_propietario_buscar,
            }

        # 2. Obtener TODOS los datos sin paginación (fuera del lock)
        try:
            data, headers, _ = await self._fetch_data(
                report_id=_report_id,
                page=1,
                limit=999999,  # Fetch All
                filtros=_filtros,
                is_export=True,
            )

            if not data:
                return rx.window_alert("No hay datos para exportar.")

            # 2. Escribir CSV
            output = io.StringIO()
            # Escribir BOM para Excel
            output.write("\ufeff")

            writer = csv.DictWriter(output, fieldnames=headers)
            writer.writeheader()
            writer.writerows(data)

            content = output.getvalue()
            filename = f"reporte_{self.selected_report_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

            return rx.download(
                data=content,
                filename=filename,
            )

        except Exception as e:
            return rx.window_alert(f"Error generando CSV: {str(e)}")

    def _sanitize_value(self, value: Any) -> str:
        """Limpia el valor para exportación CSV (elimina saltos de linea)."""
        if value is None:
            return ""
        # Convertir a string y eliminar saltos de línea
        return str(value).replace("\n", " ").replace("\r", "").strip()

    async def _fetch_data(self, report_id: str, page: int, limit: int, filtros: dict, is_export: bool):
        """
        Hub central de lógica de obtención de datos delegando al ServicioReportes.
        Los filtros se reciben por parámetro para evitar race conditions al leer self.* fuera de locks.
        """

        try:
            servicio = ServicioReportes()
            data, headers, total = await servicio.obtener_datos_reporte(
                report_id=report_id,
                filtros=filtros,
                pagina=page,
                limite=limit,
                es_exportacion=is_export,
            )

            # Sanitización final para UI
            clean_data = []
            for row in data:
                clean_row = {k: self._sanitize_value(v) for k, v in row.items()}
                clean_data.append(clean_row)

            return clean_data, headers, total

        except Exception as e:
            print(f"Error en _fetch_data: {e}")
            raise e
