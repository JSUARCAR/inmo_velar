from typing import Any, Dict, List

import reflex as rx

from src.aplicacion.servicios.servicio_propiedades import ServicioPropiedades
from src.infraestructura.persistencia.database import db_manager
from src.presentacion_reflex.state.documentos_mixin import DocumentosStateMixin


class PropiedadesState(DocumentosStateMixin):
    """
    Estado para gestión de propiedades.
    Maneja paginación, filtros avanzados y CRUD operations.
    """

    # Paginación
    current_page: int = 1
    page_size: int = 25
    total_items: int = 0

    # Filtros
    search_text: str = ""
    filter_tipo: str = "Todos"
    filter_disponibilidad: str = "Todos"  # "Todos", "1" (Disponible), "0" (Ocupada)
    filter_municipio: str = "0"  # ID municipio, "0" = Todos
    solo_activas: bool = True

    # Vista
    vista_tipo: str = "cards"  # "cards" o "table"

    # Estado de carga
    is_loading: bool = False
    error_message: str = ""

    # Datos
    propiedades: List[Dict[str, Any]] = []

    # Opciones para dropdowns
    municipios_options: List[Dict[str, str]] = []
    tipos_options: List[str] = []

    # Modal state
    show_modal: bool = False
    is_editing: bool = False
    form_data: Dict[str, Any] = {}

    # Wizard state
    modal_step: int = 1
    total_steps: int = 4
    form_validation_errors: Dict[str, str] = {}

    # Documentos
    current_entidad_tipo: str = "PROPIEDAD"

    def on_load(self):
        """Carga inicial al montar la página."""
        self.load_filter_options()
        yield PropiedadesState.load_propiedades

    # --- Wizard Logic ---
    def next_modal_step(self):
        """Avanza al siguiente paso del wizard."""
        if self.modal_step < self.total_steps:
            # Aquí se podría añadir validación por paso
            self.modal_step += 1

    def prev_modal_step(self):
        """Retrocede al paso anterior del wizard."""
        if self.modal_step > 1:
            self.modal_step -= 1

    def set_modal_step(self, step: int):
        """Establece un paso específico."""
        if 1 <= step <= self.total_steps:
            self.modal_step = step

    def reset_wizard(self):
        """Reinicia el wizard al paso 1."""
        self.modal_step = 1
        self.form_validation_errors = {}

    def set_id_municipio(self, value: str):
        """Actualiza el municipio en el formulario."""
        self.form_data["id_municipio"] = value

    def set_form_field(self, key: str, value: Any):
        """Actualiza un campo específico del formulario."""
        self.form_data[key] = value

    def load_filter_options(self):
        """Carga opciones para dropdowns de filtros."""
        try:
            servicio = ServicioPropiedades(db_manager)

            # Cargar municipios
            municipios = servicio.obtener_municipios_disponibles()
            self.municipios_options = [{"value": "0", "label": "Todos"}] + [
                {"value": str(m["id"]), "label": m["nombre"]} for m in municipios
            ]

            # Cargar tipos de propiedad
            tipos = servicio.obtener_tipos_propiedad()
            self.tipos_options = ["Todos"] + tipos

        except Exception:
            pass  # print(f"Error cargando opciones: {e}") [OpSec Removed]
            self.municipios_options = [{"value": "0", "label": "Todos"}]
            self.tipos_options = ["Todos"]

    @rx.event(background=True)
    async def load_propiedades(self):
        """Carga propiedades con filtros y paginación."""
        async with self:
            self.is_loading = True
            self.error_message = ""

        try:
            # Obtener valores de filtros (Reflex maneja el contexto async automáticamente)
            page = self.current_page
            page_size = self.page_size
            search = self.search_text
            tipo = self.filter_tipo
            disponibilidad = self.filter_disponibilidad
            municipio = self.filter_municipio
            solo_activas = self.solo_activas

            # Preparar filtros
            filtro_tipo = None if tipo == "Todos" else tipo
            filtro_disp = None if disponibilidad == "Todos" else int(disponibilidad)
            filtro_mun = None if municipio == "0" else int(municipio)
            busqueda = search.strip() if search else None

            # Servicio
            servicio = ServicioPropiedades(db_manager)
            result = servicio.listar_propiedades_paginado(
                page=page,
                page_size=page_size,
                filtro_tipo=filtro_tipo,
                filtro_disponibilidad=filtro_disp,
                filtro_municipio=filtro_mun,
                solo_activas=solo_activas,
                busqueda=busqueda,
            )
            pass  # print(f"Propiedades Loaded from Service: {len(result.items)} items") [OpSec Removed]
            if len(result.items) > 0:
                pass  # print(f"First Item Availability: {result.items[0].disponibilidad_propiedad}") [OpSec Removed]

            # Crear mapa de municipios para lookup rápido
            municipios_map = {m["value"]: m["label"] for m in self.municipios_options}

            # Convertir a dict
            propiedades_data = [
                {
                    "id_propiedad": p.id_propiedad,
                    "matricula_inmobiliaria": p.matricula_inmobiliaria,
                    "direccion_propiedad": p.direccion_propiedad,
                    "tipo_propiedad": p.tipo_propiedad,
                    "municipio_nombre": municipios_map.get(str(p.id_municipio), "N/A"),
                    "disponibilidad": 1 if p.disponibilidad_propiedad else 0,
                    "valor_canon": getattr(p, "canon_arrendamiento_estimado", 0),
                    "area_metros": getattr(p, "area_m2", 0),
                    "habitaciones": getattr(p, "habitaciones", 0),
                    "banos": getattr(p, "bano", 0),
                    "parqueadero": getattr(p, "parqueadero", 0),
                    "valor_venta": getattr(p, "valor_venta_propiedad", 0),
                    "comision_venta": getattr(p, "comision_venta_propiedad", 0),
                    "codigo_energia": getattr(p, "codigo_energia", ""),
                    "codigo_agua": getattr(p, "codigo_agua", ""),
                    "codigo_gas": getattr(p, "codigo_gas", ""),
                    "imagen_id": getattr(p, "imagen_principal_id", None),
                }
                for p in result.items
            ]

            async with self:
                self.propiedades = propiedades_data
                self.total_items = result.total
                self.is_loading = False

        except Exception as e:
            pass  # print(f"Error cargando propiedades: {e}") [OpSec Removed]
            import traceback

            traceback.print_exc()
            async with self:
                self.error_message = f"Error al cargar propiedades: {str(e)}"
                self.is_loading = False

    # Paginación
    def next_page(self):
        """Avanza a la siguiente página."""
        if self.current_page * self.page_size < self.total_items:
            self.current_page += 1
            yield PropiedadesState.load_propiedades

    def prev_page(self):
        """Retrocede a la página anterior."""
        if self.current_page > 1:
            self.current_page -= 1
            yield PropiedadesState.load_propiedades

    def set_page_size(self, size: str):
        """Cambia el tamaño de página."""
        self.page_size = int(size)
        self.current_page = 1
        yield PropiedadesState.load_propiedades

    # Filtros
    def set_search(self, value: str):
        """Actualiza búsqueda."""
        self.search_text = value

    def search_propiedades(self):
        """Ejecuta búsqueda."""
        self.current_page = 1
        yield PropiedadesState.load_propiedades

    def set_filter_tipo(self, value: str):
        """Cambia filtro de tipo."""
        self.filter_tipo = value
        self.current_page = 1
        yield PropiedadesState.load_propiedades

    def set_filter_disponibilidad(self, value: str):
        """Cambia filtro de disponibilidad."""
        self.filter_disponibilidad = value
        self.current_page = 1
        yield PropiedadesState.load_propiedades

    def set_filter_municipio(self, value: str):
        """Cambia filtro de municipio."""
        self.filter_municipio = value
        self.current_page = 1
        yield PropiedadesState.load_propiedades

    def toggle_solo_activas(self, checked: bool):
        """Toggle solo activas."""
        self.solo_activas = checked
        self.current_page = 1
        yield PropiedadesState.load_propiedades

    # Toggle Vista
    def toggle_vista(self):
        """Cambia entre vista de cards y tabla."""
        self.vista_tipo = "table" if self.vista_tipo == "cards" else "cards"

    # Modal CRUD
    def open_create_modal(self):
        """Abre modal para crear nueva propiedad."""
        self.is_editing = False
        self.form_data = {
            "id_propiedad": "",
            # Básico
            "matricula_inmobiliaria": "",
            "direccion_propiedad": "",
            "tipo_propiedad": "Casa",
            "id_municipio": "1",
            "area_metros": "0",
            "valor_canon": "0",
            "disponibilidad": "1",
            "observaciones": "",
            # Detalles Físicos
            "habitaciones": "0",
            "bano": "0",
            "parqueadero": "0",
            "estrato": "1",
            # Financiero / Venta
            "valor_administracion": "0",
            "valor_venta_propiedad": "0",
            "comision_venta_propiedad": "0",
            # Servicios Públicos
            "codigo_energia": "",
            "codigo_agua": "",
            "codigo_gas": "",
            # Administración
            "telefono_administracion": "",
            "tipo_cuenta_administracion": "Ahorros",
            "numero_cuenta_administracion": "",
        }
        self.show_modal = True
        self.error_message = ""
        self.reset_wizard()
        # Reset documentos config
        self.current_entidad_id = ""
        self.current_entidad_tipo = "PROPIEDAD"
        self.documentos = []
        self.upload_progress = 0

    def open_edit_modal(self, id_propiedad: int):
        """Abre modal para editar propiedad existente."""
        try:
            servicio = ServicioPropiedades(db_manager)
            propiedad = servicio.obtener_propiedad(id_propiedad)

            if propiedad:
                self.is_editing = True
                self.form_data = {
                    "id_propiedad": propiedad.id_propiedad,
                    "matricula_inmobiliaria": propiedad.matricula_inmobiliaria or "",
                    "direccion_propiedad": propiedad.direccion_propiedad or "",
                    "tipo_propiedad": propiedad.tipo_propiedad or "Casa",
                    "id_municipio": str(propiedad.id_municipio) if propiedad.id_municipio else "1",
                    "area_metros": str(propiedad.area_m2) if propiedad.area_m2 else "0",
                    "valor_canon": (
                        str(propiedad.canon_arrendamiento_estimado)
                        if propiedad.canon_arrendamiento_estimado
                        else "0"
                    ),
                    "disponibilidad": (
                        str(propiedad.disponibilidad_propiedad)
                        if propiedad.disponibilidad_propiedad is not None
                        else "1"
                    ),
                    "observaciones": propiedad.observaciones_propiedad or "",
                    # Detalles Físicos
                    "habitaciones": (
                        str(propiedad.habitaciones) if propiedad.habitaciones is not None else "0"
                    ),
                    "bano": str(propiedad.bano) if propiedad.bano is not None else "0",
                    "parqueadero": (
                        str(propiedad.parqueadero) if propiedad.parqueadero is not None else "0"
                    ),
                    "estrato": str(propiedad.estrato) if propiedad.estrato is not None else "1",
                    # Financiero / Venta
                    "valor_administracion": (
                        str(propiedad.valor_administracion)
                        if propiedad.valor_administracion is not None
                        else "0"
                    ),
                    "valor_venta_propiedad": (
                        str(propiedad.valor_venta_propiedad)
                        if propiedad.valor_venta_propiedad is not None
                        else "0"
                    ),
                    "comision_venta_propiedad": (
                        str(propiedad.comision_venta_propiedad)
                        if propiedad.comision_venta_propiedad is not None
                        else "0"
                    ),
                    # Servicios Públicos
                    "codigo_energia": propiedad.codigo_energia or "",
                    "codigo_agua": propiedad.codigo_agua or "",
                    "codigo_gas": propiedad.codigo_gas or "",
                    # Administración
                    "telefono_administracion": propiedad.telefono_administracion or "",
                    "tipo_cuenta_administracion": propiedad.tipo_cuenta_administracion or "Ahorros",
                    "numero_cuenta_administracion": propiedad.numero_cuenta_administracion or "",
                }
                self.show_modal = True
                self.error_message = ""
                self.reset_wizard()

                # Cargar documentos
                self.current_entidad_id = str(propiedad.id_propiedad)
                self.current_entidad_tipo = "PROPIEDAD"
                self.cargar_documentos()

        except Exception as e:
            pass  # print(f"Error cargando propiedad: {e}") [OpSec Removed]
            self.error_message = f"Error al cargar propiedad: {str(e)}"

    def close_modal(self):
        """Cierra el modal."""
        self.show_modal = False
        self.error_message = ""
        self.form_data = {}
        self.reset_wizard()

    def handle_open_change(self, open: bool):
        """Maneja el cambio de estado del modal (cierre externo)."""
        if not open:
            self.close_modal()

    def save_propiedad(self, form_data: Dict):
        """Guarda propiedad (crear o editar)."""
        pass  # print("\n🔍 === SAVE_PROPIEDAD INICIADO ===") [OpSec Removed]
        pass  # print(f"📝 Form Data Recibido: {form_data}") [OpSec Removed]

        self.is_loading = True
        self.error_message = ""

        try:
            servicio = ServicioPropiedades(db_manager)

            # Validaciones básicas
            if not form_data.get("matricula_inmobiliaria"):
                self.error_message = "La matrícula inmobiliaria es requerida"
                self.is_loading = False
                yield rx.toast.error("La matrícula es obligatoria")
                return

            if not form_data.get("direccion_propiedad"):
                self.error_message = "La dirección es requerida"
                self.is_loading = False
                yield rx.toast.error("La dirección es obligatoria")
                return

            # Helper para convertir a float/int seguro
            def safe_float(key, default=0.0):
                val = form_data.get(key)
                if not val:
                    return default
                try:
                    return float(val)
                except:
                    pass  # print(f"⚠️ Error convirtiendo float para {key}: {val}") [OpSec Removed]
                    return default

            def safe_int(key, default=0):
                val = form_data.get(key)
                if not val:
                    return default
                if key == "disponibilidad":
                    if val == "Disponible":
                        return 1
                    if val == "Ocupada":
                        return 0
                    if str(val) == "1":
                        return 1
                    if str(val) == "0":
                        return 0
                try:
                    return int(val)
                except:
                    pass  # print(f"⚠️ Error convirtiendo int para {key}: {val}") [OpSec Removed]
                    return default

            datos = {
                # Básicos
                "matricula_inmobiliaria": form_data["matricula_inmobiliaria"],
                "direccion_propiedad": form_data["direccion_propiedad"],
                "tipo_propiedad": form_data.get("tipo_propiedad", "Casa"),
                "id_municipio": safe_int("id_municipio", 1),
                "area_m2": safe_float("area_metros", 0.0),
                "canon_arrendamiento_estimado": safe_int("valor_canon", 0),
                "disponibilidad_propiedad": safe_int("disponibilidad", 1),
                "observaciones_propiedad": form_data.get("observaciones", ""),
                # Detalles Físicos
                "habitaciones": safe_int("habitaciones", 0),
                "bano": safe_int("bano", 0),
                "parqueadero": safe_int("parqueadero", 0),
                "estrato": safe_int("estrato", 0),
                # Financiero / Venta
                "valor_administracion": safe_int("valor_administracion", 0),
                "valor_venta_propiedad": safe_int("valor_venta_propiedad", 0),
                "comision_venta_propiedad": safe_int("comision_venta_propiedad", 0),
                # Servicios Públicos
                "codigo_energia": form_data.get("codigo_energia", ""),
                "codigo_agua": form_data.get("codigo_agua", ""),
                "codigo_gas": form_data.get("codigo_gas", ""),
                # Administración
                "telefono_administracion": form_data.get("telefono_administracion", ""),
                "tipo_cuenta_administracion": form_data.get("tipo_cuenta_administracion", ""),
                "numero_cuenta_administracion": form_data.get("numero_cuenta_administracion", ""),
            }

            pass  # print(f"📦 Datos Procesados para Servicio: {datos}") [OpSec Removed]

            if self.is_editing:
                # Actualizar
                id_prop = form_data.get("id_propiedad")
                if not id_prop:
                    pass  # print("❌ Error: ID de propiedad no encontrado en form_data durante edición") [OpSec Removed]
                    raise ValueError("ID de propiedad no encontrado")

                pass  # print(f"🔄 Actualizando propiedad ID: {id_prop}") [OpSec Removed]
                servicio.actualizar_propiedad(int(id_prop), datos, usuario_sistema="admin")
                msg = "Propiedad actualizada correctamente"
            else:
                # Crear nueva
                pass  # print("✨ Creando nueva propiedad") [OpSec Removed]
                servicio.crear_propiedad(datos, usuario_sistema="admin")
                msg = "Propiedad creada correctamente"

            # Cerrar modal y recargar
            self.close_modal()
            self.is_loading = False

            yield rx.toast.success(msg, position="bottom-right")
            yield PropiedadesState.load_propiedades

        except Exception as e:
            pass  # print(f"❌ Error guardando propiedad: {e}") [OpSec Removed]
            import traceback

            traceback.print_exc()
            self.error_message = f"Error: {str(e)}"
            self.is_loading = False
            yield rx.toast.error(f"Error al guardar: {str(e)}", position="bottom-right")

    def toggle_disponibilidad(self, id_propiedad: int, nueva_disponibilidad: int):
        """Cambia disponibilidad de una propiedad."""
        try:
            servicio = ServicioPropiedades(db_manager)
            servicio.cambiar_disponibilidad(
                id_propiedad, nueva_disponibilidad, usuario_sistema="admin"
            )
            est_str = "Disponible" if nueva_disponibilidad == 1 else "Ocupada"
            yield rx.toast.success(f"Estado actualizado a {est_str}", position="bottom-right")
            yield PropiedadesState.load_propiedades
        except Exception as e:
            pass  # print(f"Error cambiando disponibilidad: {e}") [OpSec Removed]
            self.error_message = f"Error al cambiar disponibilidad: {str(e)}"
            yield rx.toast.error(f"Error: {e}", position="bottom-right")

    def exportar_csv(self):
        """Exporta los datos filtrados a CSV y descarga el archivo."""
        try:
            yield rx.toast.info("Generando archivo...", position="bottom-right")

            servicio = ServicioPropiedades(db_manager)

            # Preparar filtros
            filtro_disp = None
            if self.filter_disponibilidad and self.filter_disponibilidad != "Todos":
                filtro_disp = int(self.filter_disponibilidad)

            filtro_mun = None
            if self.filter_municipio and self.filter_municipio != "0":
                filtro_mun = int(self.filter_municipio)

            csv_data = servicio.exportar_propiedades_csv(
                filtro_tipo=self.filter_tipo,
                filtro_disponibilidad=filtro_disp,
                filtro_municipio=filtro_mun,
                solo_activas=self.solo_activas,
                busqueda=self.search_text if self.search_text else None,
            )

            # Encode to bytes with BOM for Excel compatibility
            if isinstance(csv_data, str):
                data_bytes = csv_data.encode("utf-8-sig")
            else:
                data_bytes = csv_data

            import time

            timestamp = int(time.time())
            filename = f"propiedades_export_{timestamp}.csv"

            yield rx.download(data=data_bytes, filename=filename)

            yield rx.toast.success("Descarga iniciada", position="bottom-right")

        except Exception as e:
            pass  # print(f"Error al exportar: {e}") [OpSec Removed]
            yield rx.toast.error(f"Error al exportar: {str(e)}", position="bottom-right")
