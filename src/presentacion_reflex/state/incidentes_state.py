from datetime import datetime
from typing import Any, Dict, List

import reflex as rx

from src.aplicacion.servicios.servicio_incidentes import ServicioIncidentes
from src.infraestructura.persistencia.database import db_manager
from src.presentacion_reflex.state.documentos_mixin import DocumentosStateMixin
from src.infraestructura.servicios.pdf_elite.templates.incidente_template_elite import IncidenteTemplateElite
from src.aplicacion.servicios.servicio_configuracion import ServicioConfiguracion
from pathlib import Path


class IncidentesState(DocumentosStateMixin):
    """Estado para gestión de Incidentes."""

    # Datos
    incidentes: List[Dict[str, Any]] = []
    incidentes_kanban: Dict[str, List[Dict[str, Any]]] = {
        "Reportado": [],
        "Cotizado": [],
        "Aprobado": [],
        "En Reparacion": [],
        "Finalizado": [],
    }

    # UI State
    is_loading: bool = False
    error_message: str = ""
    view_mode: str = "kanban"  # "list" or "kanban"

    # Filtros
    filter_estado: str = "Todos"
    filter_prioridad: str = "Todas"
    search_text: str = ""

    # Pagination
    page: int = 1
    total_pages: int = 1
    items_per_page: int = 12

    estado_options: List[str] = [
        "Todos",
        "Reportado",
        "En Revision",
        "Cotizado",
        "Aprobado",
        "En Reparacion",
        "Finalizado",
        "Cancelado",
    ]
    prioridad_options: List[str] = ["Todas", "Alta", "Media", "Baja"]
    propiedades_options: List[Dict[str, Any]] = []

    # Mapeo de estados backend a columnas Kanban
    # Backend states: Reportado, En Revision, Cotizado, Aprobado, En Reparacion, Finalizado, Cancelado
    kanban_columns: Dict[str, List[str]] = {
        "Reportado": [
            "Reportado",
            "En Revision",
        ],  # Agrupamos En Revision aquí o podría tener su propia col
        "Cotizado": ["Cotizado"],
        "Aprobado": ["Aprobado"],
        "En Reparacion": ["En Reparacion"],
        "Finalizado": [
            "Finalizado",
            "Cancelado",
        ],  # Agrupamos Cancelado aquí por ahora o lo ocultamos
    }

    # Modal Create/Edit
    modal_open: bool = False
    form_data: Dict[str, Any] = {
        "id_propiedad": "",
        "descripcion": "",
        "prioridad": "Media",
        "origen_reporte": "Inquilino",
        "fecha_incidente": "",  # Default to today in UI if empty
        "responsable_pago": "Inquilino",  # Pre-assign or leave empty
    }

    origen_reporte_options: List[str] = ["Inquilino", "Propietario", "Inmobiliaria"]
    responsable_pago_options: List[str] = [
        "Inquilino",
        "Propietario",
        "Inmobiliaria",
        "Aseguradora",
    ]

    # --- DETAILS MODAL & QUOTING ---
    details_modal_open: bool = False
    selected_incidente: Dict[str, Any] = {}
    cotizaciones: List[Dict[str, Any]] = []  # Lista de cotizaciones del incidente seleccionado

    show_quote_form: bool = False

    # Estado formulario finalización
    show_finalize_form: bool = False
    finalize_date: str = ""
    finalize_obs: str = ""

    # Lista de proveedores para el select
    proveedores_options: List[Dict[str, Any]] = []

    cotizacion_form: Dict[str, Any] = {
        "id_proveedor": "",
        "materiales": 0,
        "mano_obra": 0,
        "descripcion": "",
        "dias": 1,
    }

    @rx.var
    def incidentes_reportado(self) -> List[Dict[str, Any]]:
        return self.incidentes_kanban.get("Reportado", [])

    @rx.var
    def incidentes_cotizado(self) -> List[Dict[str, Any]]:
        return self.incidentes_kanban.get("Cotizado", [])

    @rx.var
    def incidentes_aprobado(self) -> List[Dict[str, Any]]:
        return self.incidentes_kanban.get("Aprobado", [])

    @rx.var
    def incidentes_en_reparacion(self) -> List[Dict[str, Any]]:
        return self.incidentes_kanban.get("En Reparacion", [])

    @rx.var
    def incidentes_finalizado(self) -> List[Dict[str, Any]]:
        return self.incidentes_kanban.get("Finalizado", [])

    @rx.event(background=True)
    async def on_load(self):
        """Carga inicial."""
        async with self:
            self.is_loading = True

        try:
            yield IncidentesState.load_incidentes()
            yield IncidentesState.load_propiedades()
            yield IncidentesState.load_proveedores()
        finally:
            async with self:
                self.is_loading = False

    @rx.event(background=True)
    async def load_propiedades(self):
        """Carga lista de propiedades para el select."""
        try:
            # TODO: Usar repositorio o servicio adecuado
            # Por simplicidad query directa o servicio propiedades si disponible
            from src.aplicacion.servicios.servicio_propiedades import ServicioPropiedades
            from src.infraestructura.persistencia.repositorio_propiedad_sqlite import (
                RepositorioPropiedadSQLite,
            )

            repo_prop = RepositorioPropiedadSQLite(db_manager)
            servicio = ServicioPropiedades(repo_prop)
            props = servicio.listar_propiedades()  # Limit removed as not supported by service

            options = [
                {"id": str(p.id_propiedad), "texto": f"{p.direccion_propiedad} (#{p.id_propiedad})"}
                for p in props
            ]
            async with self:
                self.propiedades_options = options
        except Exception:
            pass  # print(f"Error cargando propiedades: {e}") [OpSec Removed]

    @rx.event(background=True)
    async def load_incidentes(self):
        """Carga lista de incidentes y actualiza vistas."""
        async with self:
            self.is_loading = True
            self.error_message = ""

        try:
            servicio = ServicioIncidentes(db_manager)

            # Filtros para el servicio
            prioridad = self.filter_prioridad if self.filter_prioridad != "Todas" else None
            estado = self.filter_estado if self.filter_estado != "Todos" else None

            # TODO: El servicio tiene `listar_con_filtros` pero no soporta todos en `listar_incidentes`.
            # Usaremos `listar_con_filtros` que es más completo.
            resultado = servicio.listar_con_filtros(
                busqueda=self.search_text if self.search_text else None,
                prioridad=prioridad,
                page=self.page,
                page_size=self.items_per_page,
                # estado=estado # listar_con_filtros no tiene filtro directo de estado, filtramos en memoria por ahora o actualizamos servicio
            )

            resultado_objs = resultado["items"]
            total_items = resultado["total"]

            # Filtrado manual de estado si el servicio no lo soporta directamente en `listar_con_filtros`
            if estado:
                # NOTA: Al filtrar en memoria DESPUÉS de paginar, la página podría quedar vacía.
                # Lo ideal es mover el filtro de estado al servicio.
                # Por ahora, para mantener la consistencia con el plan, aceptamos esta limitación
                # o el servicio debería tener el filtro de estado.
                # REVISIÓN: listar_con_filtros NO tiene 'estado'. Se añadio en memoria.
                resultado_objs = [i for i in resultado_objs if i.estado == estado]

            # Cargar propiedades para mapeo de direcciones
            from src.aplicacion.servicios.servicio_propiedades import ServicioPropiedades
            from src.infraestructura.persistencia.repositorio_propiedad_sqlite import (
                RepositorioPropiedadSQLite,
            )

            repo_prop = RepositorioPropiedadSQLite(db_manager)
            servicio_props = ServicioPropiedades(repo_prop)
            props = servicio_props.listar_propiedades()
            props_map = {p.id_propiedad: p.direccion_propiedad for p in props}

            # Serializar
            items = []
            kanban_grouped = {k: [] for k in self.kanban_columns.keys()}

            for inc in resultado_objs:
                # Obtener dirección o fallback a ID
                direccion = props_map.get(inc.id_propiedad, f"#{inc.id_propiedad}")
                # Truncar si es muy larga para la tarjeta
                if len(direccion) > 20:
                    direccion = direccion[:17] + "..."

                item = {
                    "id": inc.id_incidente,
                    "descripcion": inc.descripcion_incidente,
                    "estado": inc.estado,
                    "prioridad": inc.prioridad,
                    "fecha": (
                        inc.fecha_incidente.isoformat()
                        if hasattr(inc.fecha_incidente, "isoformat")
                        else str(inc.fecha_incidente)
                    ),
                    "id_propiedad": inc.id_propiedad,
                    "direccion_propiedad": direccion,
                    "id_proveedor": inc.id_proveedor_asignado,
                    "origen": inc.origen_reporte or "Inquilino",
                }
                items.append(item)

                # Agrupar para Kanban
                for col_name, status_list in self.kanban_columns.items():
                    if inc.estado in status_list:
                        kanban_grouped[col_name].append(item)
                        break

            async with self:
                self.incidentes = items
                self.incidentes_kanban = kanban_grouped
                import math

                self.total_pages = math.ceil(total_items / self.items_per_page)
                if self.total_pages < 1:
                    self.total_pages = 1

        except Exception as e:
            async with self:
                self.error_message = f"Error al cargar incidentes: {str(e)}"
        finally:
            async with self:
                self.is_loading = False

    @rx.event(background=True)
    async def load_proveedores(self):
        """Carga lista de proveedores."""
        try:
            # Query directa para obtener proveedores con nombre
            query = """
                SELECT pr.ID_PROVEEDOR, p.NOMBRE_COMPLETO, pr.ESPECIALIDAD 
                FROM PROVEEDORES pr
                JOIN PERSONAS p ON pr.ID_PERSONA = p.ID_PERSONA
                WHERE pr.ESTADO_REGISTRO = TRUE
            """

            conn = db_manager.obtener_conexion()
            cursor = db_manager.get_dict_cursor(conn)
            cursor.execute(query)
            rows = cursor.fetchall()

            options = [
                {
                    "id": str(r["ID_PROVEEDOR"]),
                    "texto": f"{r['NOMBRE_COMPLETO']} ({r['ESPECIALIDAD']})",
                }
                for r in rows
            ]

            async with self:
                self.proveedores_options = options

        except Exception:
            pass  # print(f"Error cargando proveedores: {e}") [OpSec Removed]

    def toggle_view_mode(self):
        """Alterna entre vista lista y kanban."""
        self.view_mode = "list" if self.view_mode == "kanban" else "kanban"

    def set_filter_estado(self, value: str):
        self.filter_estado = value
        return IncidentesState.load_incidentes

    def set_filter_prioridad(self, value: str):
        self.filter_prioridad = value
        return IncidentesState.load_incidentes

    def set_search(self, value: str):
        self.search_text = value

    def search_incidentes(self):
        return IncidentesState.load_incidentes

    # --- CRUD ---
    def open_create_modal(self):
        self.modal_open = True
        from datetime import datetime

        self.form_data = {
            "id_propiedad": "",
            "descripcion": "",
            "prioridad": "Media",
            "origen_reporte": "Inquilino",
            "fecha_incidente": datetime.now().strftime("%Y-%m-%d"),
            "responsable_pago": "Inquilino",
        }

    def close_modal(self):
        self.modal_open = False

    def set_form_data(self, key: str, value: Any):
        self.form_data[key] = value

    def set_id_propiedad(self, value: str):
        self.form_data["id_propiedad"] = value

    def set_descripcion(self, value: str):
        self.form_data["descripcion"] = value

    def set_prioridad(self, value: str):
        self.form_data["prioridad"] = value

    def set_origen_reporte(self, value: str):
        self.form_data["origen_reporte"] = value

    def set_fecha_incidente(self, value: str):
        self.form_data["fecha_incidente"] = value

    def set_responsable_pago(self, value: str):
        self.form_data["responsable_pago"] = value

    def set_modal_open(self, value: bool):
        self.modal_open = value

    def set_details_modal_open(self, value: bool):
        self.details_modal_open = value

    # --- DETAILS & QUOTING ACTIONS ---

    @rx.event(background=True)
    @rx.event(background=True)
    async def select_incidente(self, incidente: Dict[str, Any]):
        """Selecciona un incidente y carga sus detalles completos."""
        async with self:
            # Inicializar con ID mientras carga
            incidente["direccion_propiedad"] = f"#{incidente.get('id_propiedad', '')}..."
            self.selected_incidente = incidente
            self.details_modal_open = True
            self.show_quote_form = False
            self.error_message = ""
            self.is_loading = True

            # Configurar identidad de documentos
            self.current_entidad_tipo = "INCIDENTE"
            self.current_entidad_id = str(incidente["id"])
            self.cargar_documentos()

        try:
            servicio = ServicioIncidentes(db_manager)
            detalle = servicio.obtener_detalle(incidente["id"])

            cotizaciones_data = []
            if detail_cots := detalle.get("cotizaciones"):
                # Serializar cotizaciones
                for cot in detail_cots:
                    # Obtener nombre proveedor si es posible
                    nombre_prov = "Proveedor"
                    if cot.id_proveedor:
                        # Buscamos en opciones cargadas o servicio
                        prov_opt = next(
                            (
                                p
                                for p in self.proveedores_options
                                if p["id"] == str(cot.id_proveedor)
                            ),
                            None,
                        )
                        if prov_opt:
                            nombre_prov = prov_opt["texto"]

                    cotizaciones_data.append(
                        {
                            "id": cot.id_cotizacion,
                            "proveedor": nombre_prov,
                            "valor_total": cot.valor_total,
                            "materiales": cot.valor_materiales,
                            "mano_obra": cot.valor_mano_obra,
                            "dias": cot.dias_estimados,
                            "descripcion": cot.descripcion_trabajo,
                            "estado": cot.estado_cotizacion,
                        }
                    )

            # Obtener historial para buscar observaciones de finalización
            historial = servicio.obtener_historial(incidente["id"])
            observacion_final = ""
            for h in historial:
                if h.estado_nuevo == "Finalizado":
                    observacion_final = h.comentario
                    break

            async with self:
                current_inc = self.selected_incidente.copy()

                # Actualizar datos del incidente completo
                inc_obj = detalle["incidente"]
                current_inc["costo_incidente"] = inc_obj.costo_incidente

                # Manejo robusto de fecha_arreglo (str o datetime)
                fecha_val = inc_obj.fecha_arreglo
                if hasattr(fecha_val, "strftime"):
                    current_inc["fecha_arreglo"] = fecha_val.strftime("%Y-%m-%d")
                elif isinstance(fecha_val, str):
                    # Si viene como string 'YYYY-MM-DD HH:MM:SS', tomar solo fecha
                    current_inc["fecha_arreglo"] = fecha_val.split(" ")[0]
                else:
                    current_inc["fecha_arreglo"] = "N/A"

                current_inc["observaciones_final"] = observacion_final

                # Actualizar dirección si existe propiedad
                if prop := detalle.get("propiedad"):
                    current_inc["direccion_propiedad"] = getattr(
                        prop, "direccion_propiedad", str(prop)
                    )

                # Actualizar nombre proveedor si existe
                current_inc["nombre_proveedor"] = "Proveedor No Asignado"
                if pid := inc_obj.id_proveedor_asignado:  # Usar del objeto real, mas seguro
                    # Buscar en opciones (formato id, texto)
                    prov_opt = next(
                        (p for p in self.proveedores_options if p["id"] == str(pid)), None
                    )
                    if prov_opt:
                        current_inc["nombre_proveedor"] = prov_opt["texto"]

                self.selected_incidente = current_inc
                self.cotizaciones = cotizaciones_data

        except Exception:
            pass  # print(f"Error cargando detalle incidente: {e}") [OpSec Removed]
            # Fallback a datos básicos si falla
            async with self:
                self.cotizaciones = []
        finally:
            async with self:
                self.is_loading = False

    def close_details_modal(self):
        self.details_modal_open = False
        self.selected_incidente = {}

    def toggle_quote_form(self):
        self.show_quote_form = not self.show_quote_form

    def set_cotizacion_field(self, key: str, value: Any):
        self.cotizacion_form[key] = value

    @rx.event(background=True)
    async def save_cotizacion(self):
        async with self:
            self.is_loading = True

        try:
            servicio = ServicioIncidentes(db_manager)
            usuario = "admin"

            # Prepare data
            datos = {
                "id_proveedor": int(self.cotizacion_form["id_proveedor"]),
                "materiales": float(self.cotizacion_form["materiales"]),
                "mano_obra": float(self.cotizacion_form["mano_obra"]),
                "descripcion": self.cotizacion_form["descripcion"],
                "dias": int(self.cotizacion_form["dias"]),
            }

            id_incidente = self.selected_incidente["id"]

            servicio.registrar_cotizacion(id_incidente, datos, usuario)

            yield rx.toast.success("Cotización registrada exitosamente.")

            # Ocultar formulario pero MANTENER modal abierto
            async with self:
                self.show_quote_form = False

            # Recargar lista general
            yield IncidentesState.load_incidentes()

            # Recargar detalles del incidente actual (cotizaciones)
            yield IncidentesState.select_incidente(self.selected_incidente)

        except Exception as e:
            yield rx.toast.error(f"Error al registrar cotización: {str(e)}")
        finally:
            async with self:
                self.is_loading = False

    @rx.event(background=True)
    async def save_incidente(self):
        async with self:
            self.is_loading = True
            self.error_message = ""

        try:
            servicio = ServicioIncidentes(db_manager)
            usuario = "admin"  # TODO Auth

            # Validación básica
            if not self.form_data["id_propiedad"] or not self.form_data["descripcion"]:
                raise ValueError("Propiedad y Descripción son obligatorias")

            datos = {
                "id_propiedad": int(self.form_data["id_propiedad"]),
                "descripcion": self.form_data["descripcion"],
                "prioridad": self.form_data["prioridad"],
                "origen_reporte": self.form_data["origen_reporte"],
                "fecha_incidente": self.form_data["fecha_incidente"],
                "responsable_pago": self.form_data["responsable_pago"],
            }

            servicio.reportar_incidente(datos, usuario)

            async with self:
                self.modal_open = False

            yield IncidentesState.load_incidentes()

        finally:
            async with self:
                self.is_loading = False

    @rx.event(background=True)
    async def aprobar_cotizacion_event(self, id_incidente: int, id_cotizacion: int):
        """Aprueba una cotización y genera Orden de Trabajo."""
        async with self:
            self.is_loading = True

        try:
            servicio = ServicioIncidentes(db_manager)
            usuario = "admin"  # TODO Auth
            # Asumimos 'Propietario' por defecto o requerir input extra
            servicio.aprobar_cotizacion(
                id_incidente, id_cotizacion, usuario, responsable_pago="Propietario"
            )

            yield rx.toast.success("Cotización aprobada y Orden de Trabajo creada.")
            yield IncidentesState.load_incidentes()

        except Exception as e:
            yield rx.toast.error(f"Error al aprobar: {str(e)}")
        finally:
            async with self:
                self.is_loading = False

    @rx.event(background=True)
    async def iniciar_reparacion_event(self, id_incidente: int):
        """Inicia la reparación."""
        async with self:
            self.is_loading = True

        try:
            servicio = ServicioIncidentes(db_manager)
            usuario = "admin"
            servicio.iniciar_reparacion(id_incidente, usuario)

            yield rx.toast.success("Reparación iniciada.")
            yield IncidentesState.load_incidentes()

        except Exception as e:
            yield rx.toast.error(f"Error al iniciar reparación: {str(e)}")
        finally:
            async with self:
                self.is_loading = False

    @rx.event(background=True)
    async def finalizar_incidente_event(self, id_incidente: int):
        """Finaliza el incidente."""
        async with self:
            self.is_loading = True

        try:
            servicio = ServicioIncidentes(db_manager)
            usuario = "admin"
            servicio.finalizar_incidente(id_incidente, usuario)

            yield rx.toast.success("Incidente finalizado exitosamente.")
            yield IncidentesState.load_incidentes()

        except Exception as e:
            yield rx.toast.error(f"Error al finalizar: {str(e)}")
        finally:
            async with self:
                self.is_loading = False

    @rx.event(background=True)
    async def finalizar_carga_cotizaciones(self, id_incidente: int):
        """Finaliza la carga de cotizaciones y pasa a estado Cotizado."""
        async with self:
            self.is_loading = True

        try:
            servicio = ServicioIncidentes(db_manager)
            usuario = "admin"
            servicio.cambiar_estado(id_incidente, "Cotizado", usuario)

            yield rx.toast.success(
                "Cotizaciones finalizadas. Incidente pasa a estado Cotizado para aprobación."
            )
            yield IncidentesState.load_incidentes()

            # Actualizar estado seleccionado localmente para reflejar cambio inmediato en UI
            async with self:
                if self.selected_incidente and self.selected_incidente["id"] == id_incidente:
                    self.selected_incidente["estado"] = "Cotizado"
                    self.details_modal_open = True

        except Exception as e:
            yield rx.toast.error(f"Error al cambiar estado: {str(e)}")
        finally:
            async with self:
                self.is_loading = False

    @rx.event
    def toggle_finalize_form(self):
        """Alterna la visibilidad del formulario de finalización."""
        self.show_finalize_form = not self.show_finalize_form
        if self.show_finalize_form:
            # Prellenar fecha con hoy
            self.finalize_date = datetime.now().strftime("%Y-%m-%d")
            self.finalize_obs = ""

    @rx.event
    def set_finalize_date(self, value: str):
        self.finalize_date = value

    @rx.event
    def set_finalize_obs(self, value: str):
        self.finalize_obs = value

    @rx.event(background=True)
    async def confirmar_finalizacion(self):
        """Confirma la finalización del incidente con fecha y observaciones."""
        async with self:
            self.is_loading = True
            if not self.finalize_date:
                yield rx.toast.error("Debe ingresar una fecha de finalización.")
                self.is_loading = False
                return

        try:
            servicio = ServicioIncidentes(db_manager)
            usuario = "admin"

            # Parsear fecha string a datetime
            fecha_fin = datetime.strptime(self.finalize_date, "%Y-%m-%d")

            # Pasar fecha y observación (comentario)
            servicio.finalizar_incidente(
                self.selected_incidente["id"],
                usuario,
                comentario=self.finalize_obs,
                fecha_arreglo=fecha_fin,
            )

            yield rx.toast.success("Incidente finalizado exitosamente.")
            yield IncidentesState.load_incidentes()

            async with self:
                self.show_finalize_form = False
                self.details_modal_open = False  # Cerrar modal al finalizar

        except Exception as e:
            yield rx.toast.error(f"Error al finalizar: {str(e)}")
        finally:
            async with self:
                self.is_loading = False

    @rx.event
    def prev_page(self):
        if self.page > 1:
            self.page -= 1
            return IncidentesState.load_incidentes

    @rx.event
    def next_page(self):
        if self.page < self.total_pages:
            self.page += 1
            return IncidentesState.load_incidentes

    @rx.event(background=True)
    async def generar_pdf_incidente(self):
        """Genera el PDF del incidente seleccionado."""
        async with self:
            if not self.selected_incidente:
                 yield rx.toast.error("No hay incidente seleccionado.")
                 return
            self.is_loading = True

        try:
            # 1. Obtener datos completos
            datos = self.selected_incidente.copy()
            # Mapear fecha a fecha_reporte para el template
            datos["fecha_reporte"] = datos.get("fecha")
            # Agregar cotizaciones
            datos["cotizaciones"] = self.cotizaciones
            # Agregar dirección legible
            datos["direccion"] = datos.get("direccion_propiedad")

            # 2. Configuración empresa
            servicio_config = ServicioConfiguracion(db_manager)
            config_empresa = servicio_config.obtener_configuracion_empresa()
            if config_empresa:
                datos["empresa"] = {
                     "logo_base64": config_empresa.logo_base64,
                     "nombre": config_empresa.nombre_empresa
                }

            # 3. Generar PDF
            # Usar un directorio temporal o el de documentos generados
            template = IncidenteTemplateElite(output_dir=Path("documentos_generados"))
            pdf_path = template.generate(datos)

            yield rx.toast.success("PDF generado exitosamente.")

            # 4. Descargar
            pdf_filename = Path(pdf_path).name
            download_url = f"http://localhost:8000/api/pdf/download/{pdf_filename}"

            js_download = f"""
            fetch('{download_url}')
              .then(res => res.blob())
              .then(blob => {{
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = '{pdf_filename}';
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                window.URL.revokeObjectURL(url);
              }})
              .catch(err => console.error('Download error:', err));
            """
            yield rx.call_script(js_download)

        except Exception as e:
            yield rx.toast.error(f"Error generando PDF: {str(e)}")
        finally:
             async with self:
                self.is_loading = False
