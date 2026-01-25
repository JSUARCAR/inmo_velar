import csv
import io
from datetime import datetime
from typing import Any, Dict, List, Optional

import reflex as rx
from src.infraestructura.persistencia.database import db_manager
from src.presentacion_reflex.state.auth_state import AuthState

# Importación diferida de servicios para evitar ciclos y carga innecesaria
# Se realizarán dentro de los métodos

class ReportItem(rx.Base):
    id: str
    name: str
    description: str
    module: str

class ReportCategory(rx.Base):
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
                {"id": "personas", "name": "Reporte de Personas", "description": "Base de datos completa de usuarios y roles.", "module": "Personas"},
                {"id": "propiedades", "name": "Reporte de Propiedades", "description": "Inventario detallado de inmuebles.", "module": "Propiedades"},
                {"id": "contratos_mandato", "name": "Contratos: Mandato", "description": "Gestión de contratos con propietarios.", "module": "Contratos"},
                {"id": "contratos_arrendamiento", "name": "Contratos: Arrendamiento", "description": "Gestión de contratos con arrendatarios.", "module": "Contratos"},
                {"id": "proveedores", "name": "Reporte de Proveedores", "description": "Directorio de proveedores y servicios.", "module": "Proveedores"},
            ]
        },
        "OPERACIONES": {
            "icon": "activity",
            "color": "#f59e0b",
            "reports": [
                {"id": "liquidaciones", "name": "Reporte de Liquidaciones", "description": "Histórico de pagos a propietarios.", "module": "Liquidaciones"},
                {"id": "liquidacion_asesores", "name": "Liquidación Asesores", "description": "Comisiones y pagos comerciales.", "module": "Liquidación Asesores"},
                {"id": "desocupaciones", "name": "Reporte de Desocupaciones", "description": "Procesos de restitución de inmuebles.", "module": "Desocupaciones"},
                {"id": "incidentes", "name": "Reporte de Incidentes", "description": "Bitácora de mantenimiento y reparaciones.", "module": "Incidentes"},
                {"id": "seguros", "name": "Reporte de Seguros", "description": "Control de pólizas vigentes.", "module": "Seguros"},
                {"id": "recibos_publicos", "name": "Recibos Públicos", "description": "Pagos de servicios públicos.", "module": "Recibos Públicos"},
                {"id": "saldos_favor", "name": "Saldos a Favor", "description": "Control de saldos acreedores.", "module": "Saldos a Favor"},
            ]
        }
    }

    # Estado de Selección y Filtros
    selected_category: str = "GESTIÓN"
    selected_report_id: str = ""
    search_query: str = ""  # Busqueda global en sidebar
    
    # Filtros Dinámicos (Valores)
    filter_fecha_inicio: str = ""
    filter_fecha_fin: str = ""
    filter_estado: str = "Todos"
    filter_busqueda_tabla: str = ""  # Busqueda especifica en tabla

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
                if q and (q not in r["name"].lower() and q not in r["description"].lower()):
                    continue
                
                # 2. Filtro por Permisos (Backend check)
                if await self._check_access(r["module"]):
                    reports.append(
                        ReportItem(
                            id=r["id"],
                            name=r["name"],
                            description=r["description"],
                            module=r["module"]
                        )
                    )
            
            if reports:
                # Estructura plana para iteración fácil
                filtered.append(
                    ReportCategory(
                        name=cat_name,
                        icon=cat_data["icon"],
                        color=cat_data["color"],
                        reports=reports
                    )
                )
        return filtered

    async def _check_access(self, module_name: str) -> bool:
        """Verifica acceso backend (Python puro no Var)."""
        # Acceder al estado real (no Var)
        auth_state = await self.get_state(AuthState)
        user = auth_state.user_info
        
        if not user: return False
        if user.get("rol") == "Administrador": return True
        
        return module_name in auth_state.allowed_modules

    def select_report(self, report_id: str):
        """Acción al seleccionar un reporte del sidebar."""
        self.selected_report_id = report_id
        self.current_page = 1
        self.filter_busqueda_tabla = ""
        self.filter_fecha_inicio = ""
        self.filter_fecha_fin = ""
        self.filter_estado = "Todos"
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
        async with self:
            if not self.selected_report_id:
                return
            self.is_loading = True
            self.error_message = ""

        try:
            # Seleccionar estrategia de carga según ID
            data, headers, total = await self._fetch_data(
                report_id=self.selected_report_id,
                page=self.current_page,
                limit=self.page_size,
                is_export=False
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

    async def download_csv(self):
        """Genera y descarga todo el dataset en CSV UTF-8 con BOM."""
        # 1. Obtener TODOS los datos sin paginación
        try:
            data, headers, _ = await self._fetch_data(
                report_id=self.selected_report_id,
                page=1,
                limit=999999, # Fetch All
                is_export=True
            )
            
            if not data:
                return rx.window_alert("No hay datos para exportar.")

            # 2. Escribir CSV
            output = io.StringIO()
            # Escribir BOM para Excel
            output.write('\ufeff') 
            
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

    async def _fetch_data(self, report_id: str, page: int, limit: int, is_export: bool):
        """
        Hub central de lógica de obtención de datos.
        Retorna: (List[Dict], List[Headers], TotalCount)
        """
        offset = (page - 1) * limit
        
        # --- INSTANCIACIÓN DE SERVICIOS (Lazy) ---
        if report_id == "personas":
            from src.infraestructura.persistencia.repositorio_persona_sqlite import RepositorioPersonaSQLite
            repo = RepositorioPersonaSQLite(db_manager)
            
            # Construir filtros
            solo_activos = True if self.filter_estado == "Activo" else False
            if self.filter_estado == "Todos": solo_activos = False # Logica custom: repo suele pedir booleano
            
            # TODO: Ajustar repo para soportar 'Todos', por ahora asumiremos Activos por defecto si no es export
            # Si es export, y filtro es todos, traer inactivos tambien? 
            # El repo tiene 'solo_activos' bool parameter.
            
            # Obtener datos usando obtener_todos con offset/limit custom si lo soportara,
            # pero el repo usa un metodo estandar. Simularemos paginacion en memoria si repo no soporta
            # O llamaremos al conteo.
            
            # Nota: El servicio tiene listar_personas_paginado, usémoslo o modifiquémoslo.
            # ServicioPersonas ya lo instanciamos? No, directo al repo para raw data si es mas rapido?
            # Mejor usar servicio si tiene logica.
            
            personas = repo.obtener_todos(
                busqueda=self.filter_busqueda_tabla if self.filter_busqueda_tabla else None,
                solo_activos=False if self.filter_estado == "Todos" else (True if self.filter_estado == "Activo" else False)
            )
            
            # Filtrado en memoria si el repo no filtra todo (ej. fechas, o si queremos 'Inactivo' especifico)
            if self.filter_estado == "Inactivo":
                personas = [p for p in personas if not p.estado_registro]
            elif self.filter_estado == "Activo":
                personas = [p for p in personas if p.estado_registro]

            total = len(personas)
            # Paginación en memoria
            paginated = personas[offset : offset + limit]
            
            # Serializar TODAS las columnas
            data = [p.__dict__ for p in paginated] 
            # Limpiar campos internos de SQLAlchemy/DB si los hay (usually _sa_instance_state)
            if data:
                headers = list(data[0].keys())
                # Clean headers
                headers = [h for h in headers if not h.startswith('_')]
                # Rebuild data dicts with clean headers y strings
                clean_data = []
                for item in data:
                    new_item = {k: str(v) if v is not None else "" for k, v in item.items() if k in headers}
                    clean_data.append(new_item)
                return clean_data, headers, total
            else:
                return [], [], 0

        elif report_id == "propiedades":
            from src.infraestructura.persistencia.repositorio_propiedad_sqlite import RepositorioPropiedadSQLite
            repo = RepositorioPropiedadSQLite(db_manager)
            
            # Use listar_con_filtros instead of listar_todos
            props = repo.listar_con_filtros(
                busqueda=self.filter_busqueda_tabla if self.filter_busqueda_tabla else None,
                solo_activas=False if self.filter_estado == "Todos" else (True if self.filter_estado == "Activo" else False)
            )
            
            total = len(props)
            paginated = props[offset : offset + limit]
            
            data = [p.__dict__ for p in paginated]
            if data:
                headers = [h for h in list(data[0].keys()) if not h.startswith('_')]
                clean_data = []
                for item in data:
                    new_item = {k: str(v) for k, v in item.items() if k in headers}
                    clean_data.append(new_item)
                return clean_data, headers, total
            return [], [], 0

        # Mapeo de reportes a tablas para lógica genérica "SELECT *"
        table_map = {
            "contratos_mandato": "CONTRATOS_MANDATOS",
            "contratos_arrendamiento": "CONTRATOS_ARRENDAMIENTOS",
            "proveedores": "PROVEEDORES",
            "liquidaciones": "liquidaciones", # user indicated this is the populated table
            "liquidacion_asesores": "LIQUIDACIONES_ASESORES",
            "desocupaciones": "DESOCUPACIONES",
            "incidentes": "INCIDENTES",
            "seguros": "SEGUROS",
            "recibos_publicos": "RECIBOS_PUBLICOS",
            "saldos_favor": "SALDOS_FAVOR"
        }

        if report_id in table_map:
            table_name = table_map[report_id]
            query = f"SELECT * FROM {table_name}"
            
            with db_manager.obtener_conexion() as conn:
                cursor = db_manager.get_dict_cursor(conn)
                try:
                    cursor.execute(query)
                    rows = cursor.fetchall()
                    
                    # Filtrado básico en memoria (Búsqueda global sencilla)
                    if self.filter_busqueda_tabla:
                        t = self.filter_busqueda_tabla.lower()
                        rows = [r for r in rows if any(t in str(v).lower() for v in r.values())]

                    total = len(rows)
                    paginated = rows[offset : offset + limit]
                    
                    if paginated:
                        headers = list(paginated[0].keys())
                        clean_data = [{k: str(v) if v is not None else "" for k,v in row.items()} for row in paginated]
                        return clean_data, headers, total
                except Exception as ex:
                    print(f"Error querying {table_name}: {ex}")
                    return [], [], 0
            
            return [], [], 0
        
        return [], [], 0
