import csv
import io
from datetime import datetime
from typing import Any, Dict, List, Optional

import reflex as rx
from pydantic import BaseModel
from src.infraestructura.persistencia.database import db_manager
from src.presentacion_reflex.state.auth_state import AuthState

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
                {"id": "personas", "name": "Reporte de Personas", "description": "Base de datos completa de usuarios y roles.", "module": "Personas"},
                {"id": "reporte_propietarios", "name": "Reporte de Propietarios", "description": "Información detallada de propietarios.", "module": "Personas"},
                {"id": "reporte_arrendatarios", "name": "Reporte de Arrendatarios", "description": "Información detallada de arrendatarios.", "module": "Personas"},
                {"id": "reporte_codeudores", "name": "Reporte de Codeudores", "description": "Información detallada de codeudores.", "module": "Personas"},
                {"id": "reporte_asesores", "name": "Reporte de Asesores", "description": "Información detallada de asesores.", "module": "Personas"},
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
    filter_rol: str = "Todos"
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
    rol_options: List[str] = ["Todos", "Propietario", "Arrendatario", "Codeudor", "Asesor"]

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
        self.filter_rol = "Todos"
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

    def _sanitize_value(self, value: Any) -> str:
        """Limpia el valor para exportación CSV (elimina saltos de linea)."""
        if value is None:
            return ""
        # Convertir a string y eliminar saltos de línea
        return str(value).replace('\n', ' ').replace('\r', '').strip()

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
                solo_activos=False if self.filter_estado == "Todos" else (True if self.filter_estado == "Activo" else False),
                filtro_rol=self.filter_rol if self.filter_rol != "Todos" else None
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
                    new_item = {k: self._sanitize_value(v) for k, v in item.items() if k in headers}
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
                    new_item = {k: self._sanitize_value(v) for k, v in item.items() if k in headers}
                    clean_data.append(new_item)
                return clean_data, headers, total
            return [], [], 0

        # Lógica para reportes de Roles Específicos (JOINs)
        elif report_id in ["reporte_propietarios", "reporte_arrendatarios", "reporte_codeudores", "reporte_asesores"]:
            table_map_roles = {
                "reporte_propietarios": "PROPIETARIOS",
                "reporte_arrendatarios": "ARRENDATARIOS",
                "reporte_codeudores": "CODEUDORES",
                "reporte_asesores": "ASESORES"
            }
            
            role_table = table_map_roles[report_id]
            
            # Query con JOIN para traer datos de Persona + Datos del Rol
            # Usamos alias para evitar conflictos de ID_PERSONA, aunque en dict cursor se sobreescriben si no cuidamos los nombres
            # Preferimos seleccionar columnas explicitas o dejar que el driver maneje duplicados (normalmente el ultimo gana)
            # Para mas seguridad, p.* y r.*
            
            query = f"""
                SELECT p.TIPO_DOCUMENTO, p.NUMERO_DOCUMENTO, p.NOMBRE_COMPLETO, 
                       p.TELEFONO_PRINCIPAL, p.CORREO_ELECTRONICO, p.DIRECCION_PRINCIPAL,
                       r.* 
                FROM PERSONAS p
                INNER JOIN {role_table} r ON p.ID_PERSONA = r.ID_PERSONA
            """
            
            conditions = []
            params = []
            
            if self.filter_busqueda_tabla:
                # Busqueda simple en nombre o documento
                conditions.append(f"(p.NOMBRE_COMPLETO LIKE ? OR p.NUMERO_DOCUMENTO LIKE ?)")
                params.extend([f"%{self.filter_busqueda_tabla}%", f"%{self.filter_busqueda_tabla}%"])
            
            if self.filter_estado != "Todos":
                # Asumimos que la tabla del rol tiene alguna columna de estado o usamos la de persona
                # Para simplificar, usamos la de PERSONA (ESTADO_REGISTRO) o la del ROL si es estandar
                # Propietarios: ESTADO_PROPIETARIO (int 1/0), Arrendatarios: ESTADO_ARRENDATARIO (bool?)
                # Codeudores: ESTADO_REGISTRO (bool), Asesores: ESTADO (int 1/0)
                
                # Normalización de estados es compleja dinamicamente, usaremos ESTADO_REGISTRO de Persona como base fiable
                # Si el usuario quiere estado del rol especifico, lo agregamos.
                # Por ahora: Filtramos por el estado de la PERSONA para consistencia
                
                is_active = 1 if self.filter_estado == "Activo" else 0
                conditions.append(f"p.ESTADO_REGISTRO = ?")
                params.append(is_active)

            if conditions:
                query += " WHERE " + " AND ".join(conditions)
                
            # Ejecucion
            with db_manager.obtener_conexion() as conn:
                cursor = db_manager.get_dict_cursor(conn) # Importante: devuelve dict
                # SQLite placeholder es ?
                # Adapt params to generic placeholder of db_manager if needed, usually its ? for sqlite
                # Pero db_manager.get_placeholder() devuelve ? o %s.
                placeholder = db_manager.get_placeholder()
                
                # Reconstruir query con placeholders correctos (hack simple replace ?)
                query = query.replace("?", placeholder)
                
                try:
                    cursor.execute(query, tuple(params))
                    rows = cursor.fetchall()
                    
                    total = len(rows)
                    
                    # Paginación en memoria (simple)
                    paginated = rows[offset : offset + limit]
                    
                    if paginated:
                        # Convertir a dict serializable y limpiar headers
                        clean_data = []
                        # Obtener headers del primer row
                        # Nota: Si hay columnas duplicadas en JOIN (ej ID_PERSONA), 
                        # sqlite3.Row / dict cursor puede que solo muestre una.
                        
                        # Definir orden de headers para que sea bonito: Datos Persona primero
                        priority_headers = ["tipo_documento", "numero_documento", "nombre_completo", "telefono_principal", "correo_electronico"]
                        
                        all_keys = list(paginated[0].keys())
                        # Keys devuelve nombres en minuscula o mayuscula dependinedo de config.
                        # Normalizamos a lowercase para chequeo
                        
                        other_keys = [k for k in all_keys if k.lower() not in priority_headers and not k.startswith('_')]
                        
                        # Combine headers
                        # Note: we use actual keys from row to avoid case mismatches
                        final_headers_keys = []
                        
                        # Find actual key names for priority
                        for pk in priority_headers:
                            found = next((k for k in all_keys if k.lower() == pk), None)
                            if found: final_headers_keys.append(found)
                            
                        # Add others
                        for ok in other_keys:
                            if ok not in final_headers_keys:
                                final_headers_keys.append(ok)
                        
                        for row in paginated:
                            item = {k: self._sanitize_value(row[k]) for k in final_headers_keys}
                            clean_data.append(item)
                            
                        return clean_data, final_headers_keys, total
                    return [], [], 0
                    
                except Exception as ex:
                    print(f"Error executing report role query: {ex}")
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
                        clean_data = [{k: self._sanitize_value(v) for k,v in row.items()} for row in paginated]
                        return clean_data, headers, total
                except Exception as ex:
                    print(f"Error querying {table_name}: {ex}")
                    return [], [], 0
            
            return [], [], 0
        
        return [], [], 0
