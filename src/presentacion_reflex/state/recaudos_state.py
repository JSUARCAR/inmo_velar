"""
Estado de Presentación para Gestión de Recaudos.
Delegación completa al Servicio de Aplicación.

Responsabilidades:
- Gestión de UI (modales, filtros, paginación, combobox)
- Delegación de operaciones CRUD al ServicioRecaudo
- Formateo de datos para la vista
"""
from datetime import datetime
from typing import Any, Dict, List, Optional

import reflex as rx

from src.dominio.constantes.recaudo import MetodoPago, EstadoRecaudo
from src.dominio.interfaces.repositorio_recaudo import FiltrosRecaudo
from src.aplicacion.servicios.servicio_recaudo import ServicioRecaudo
from src.infraestructura.persistencia.database import db_manager
from src.infraestructura.persistencia.repositorio_recaudo import RepositorioRecaudo
from src.presentacion_reflex.state.documentos_mixin import DocumentosStateMixin
from src.presentacion_reflex.utils.formatters import format_currency


def _crear_servicio() -> ServicioRecaudo:
    """Factory para inyectar el servicio de recaudos."""
    repo = RepositorioRecaudo(db_manager)
    return ServicioRecaudo(repo, db_manager)


class RecaudosState(DocumentosStateMixin):
    """Estado centralizado para gestión de recaudos (pagos de arrendatarios).
    Toda la lógica de negocio se delega al Servicio de Aplicación.
    """

    # Paginación
    current_page: int = 1
    page_size: int = 25
    total_items: int = 0

    # Datos
    recaudos: List[Dict[str, Any]] = []
    recaudo_actual: Optional[Dict[str, Any]] = None
    is_loading: bool = False
    error_message: str = ""

    # Ordenamiento
    sort_by: str = "fecha_pago"
    sort_order: str = "desc"

    # Filtros
    search_text: str = ""
    filter_estado: str = "Todos"
    filter_contrato: str = ""
    filter_fecha_desde: str = ""
    filter_fecha_hasta: str = ""

    # Opciones de filtros
    estado_options: List[str] = ["Todos"] + EstadoRecaudo.valores()
    contratos_options: List[Dict[str, Any]] = []
    contratos_select_options: List[str] = []

    # Combobox Contrato
    contrato_search: str = ""
    contrato_menu_open: bool = False
    contrato_selected_label: str = ""

    @rx.var
    def filtered_contratos_options(self) -> List[tuple[str, str]]:
        """Opciones filtradas de contratos para el combobox (texto, id_contrato)."""
        search_lower = self.contrato_search.lower()
        if not search_lower:
            return [(c["texto"], c["id"]) for c in self.contratos_options]
        return [
            (c["texto"], c["id"])
            for c in self.contratos_options
            if search_lower in c["texto"].lower()
        ]

    # Modales
    show_form_modal: bool = False
    show_detail_modal: bool = False
    is_editing: bool = False

    # Form data
    form_data: Dict[str, Any] = {}

    # ==================== HELPERS PRIVADOS ====================

    async def _get_usuario_actual(self) -> str:
        """Obtiene el usuario actual (Mock para estabilidad de StateProxy)."""
        # TODO: Integrar con AuthState cuando Reflex garantice get_state seguro en BG tasks
        return "admin"

    def _parse_estado(self, estado: str) -> Optional[EstadoRecaudo]:
        """Convierte string de filtro a Enum, None si es 'Todos'."""
        if estado == "Todos":
            return None
        return EstadoRecaudo(estado)

    # ==================== CICLO DE VIDA ====================

    @rx.event(background=True)
    async def on_load(self):
        """Carga inicial al montar la página."""
        async with self:
            self.is_loading = True

        try:
            yield RecaudosState.load_filter_options()
            yield RecaudosState.load_recaudos()
        finally:
            async with self:
                self.is_loading = False

    @rx.event(background=True)
    async def load_filter_options(self):
        """Carga contratos activos para dropdown de filtros."""
        servicio = _crear_servicio()
        contratos = servicio.obtener_contratos_activos()
        contratos_select = [c["texto"] for c in contratos]

        async with self:
            self.contratos_options = contratos
            self.contratos_select_options = contratos_select

    @rx.event(background=True)
    async def load_recaudos(self):
        """Carga recaudos con filtros y paginación usando el servicio."""
        async with self:
            self.is_loading = True
            self.error_message = ""
            
            # Leer estado dentro del contexto para seguridad de StateProxy
            estado_val = self.filter_estado
            fecha_desde = self.filter_fecha_desde or None
            fecha_hasta = self.filter_fecha_hasta or None
            busqueda = self.search_text or None
            page = self.current_page
            page_size = self.page_size
            sort_by = self.sort_by
            sort_order = self.sort_order

        try:
            servicio = _crear_servicio()

            filtros = FiltrosRecaudo(
                estado=self._parse_estado(estado_val),
                fecha_desde=fecha_desde,
                fecha_hasta=fecha_hasta,
                busqueda=busqueda,
                page=page,
                page_size=page_size,
                sort_by=sort_by,
                sort_order=sort_order,
            )

            resultado = servicio.listar_paginado(filtros)

            # Formatear items para la vista
            formatted_list = []
            for row in resultado.items:
                new_item = dict(row) if not isinstance(row, dict) else row.copy()
                new_item["valor_total_view"] = format_currency(
                    new_item.get("valor_total") or new_item.get("VALOR_TOTAL") or 0
                )
                formatted_list.append(new_item)

            async with self:
                self.recaudos = formatted_list
                self.total_items = resultado.total
                self.is_loading = False

        except Exception as e:
            async with self:
                self.error_message = f"Error al cargar recaudos: {str(e)}"
                self.recaudos = []
                self.total_items = 0
                self.is_loading = False

    def toggle_sort(self, column: str):
        """Cambia el criterio de ordenamiento."""
        if self.sort_by == column:
            self.sort_order = "desc" if self.sort_order == "asc" else "asc"
        else:
            self.sort_by = column
            self.sort_order = "desc"
        
        self.current_page = 1
        return RecaudosState.load_recaudos

    # ==================== PAGINACIÓN ====================

    def next_page(self):
        """Avanza a la siguiente página."""
        if self.current_page * self.page_size < self.total_items:
            self.current_page += 1
            return RecaudosState.load_recaudos

    def prev_page(self):
        """Retrocede a la página anterior."""
        if self.current_page > 1:
            self.current_page -= 1
            return RecaudosState.load_recaudos

    def set_page_size(self, size: str):
        """Cambia el tamaño de página."""
        self.page_size = int(size)
        self.current_page = 1
        return RecaudosState.load_recaudos

    # ==================== BÚSQUEDA Y FILTROS ====================

    def set_search(self, value: str):
        """Actualiza búsqueda."""
        self.search_text = value

    def search_recaudos(self):
        """Ejecuta búsqueda."""
        self.current_page = 1
        return RecaudosState.load_recaudos

    def handle_search_key_down(self, key: str):
        """Maneja Enter en búsqueda."""
        if key == "Enter":
            return self.search_recaudos()

    def set_filter_estado(self, value: str):
        """Cambia filtro de estado."""
        self.filter_estado = value
        self.current_page = 1
        return RecaudosState.load_recaudos

    def set_filter_fecha_desde(self, value: str):
        """Cambia filtro de fecha desde."""
        self.filter_fecha_desde = value
        self.current_page = 1
        return RecaudosState.load_recaudos

    def set_filter_fecha_hasta(self, value: str):
        """Cambia filtro de fecha hasta."""
        self.filter_fecha_hasta = value
        self.current_page = 1
        return RecaudosState.load_recaudos

    # ==================== COMBOBOX CONTRATO ====================

    def set_contrato_search(self, value: str):
        """Actualiza el texto de búsqueda de contrato."""
        self.contrato_search = value

    def toggle_contrato_menu(self, open: bool):
        """Abre o cierra el menú del combobox de contrato."""
        self.contrato_menu_open = open

    def select_contrato(self, value: str, label: str):
        """Selecciona un contrato del combobox."""
        self.contrato_selected_label = label
        self.form_data["id_contrato_a"] = value
        self.contrato_menu_open = False

        # Auto-llenar valor con el canon
        contrato = next(
            (c for c in self.contratos_options if str(c["id"]) == str(value)),
            None,
        )
        if contrato and "canon" in contrato and contrato["canon"]:
            self.form_data["valor_total"] = str(contrato["canon"])

    # ==================== MODAL CRUD ====================

    def open_create_modal(self):
        """Abre modal para crear nuevo recaudo."""
        self.is_editing = False
        self.show_form_modal = True
        self.show_detail_modal = False
        self.form_data = {
            "id_contrato_a": "",
            "fecha_pago": datetime.now().date().isoformat(),
            "valor_total": "",
            "metodo_pago": MetodoPago.TRANSFERENCIA.value,
            "referencia_bancaria": "",
            "observaciones": "",
            "tipo_concepto": "Canon",
            "periodo": datetime.now().strftime("%Y-%m"),
        }

        self.contrato_search = ""
        self.contrato_selected_label = ""
        self.contrato_menu_open = False
        self.error_message = ""

    def set_form_field(self, field: str, value: str):
        """Actualiza un campo del formulario manual."""
        self.form_data[field] = value

    def close_modal(self):
        """Cierra todos los modales."""
        self.show_form_modal = False
        self.show_detail_modal = False
        self.recaudo_actual = None
        self.form_data = {}
        self.error_message = ""

    @rx.event(background=True)
    async def open_edit_modal(self, id_recaudo: int):
        """Abre modal para editar recaudo existente."""
        async with self:
            self.is_loading = True
            self.error_message = ""
            
            # Copiar opciones para procesar fuera del contexto
            opts = self.contratos_options.copy()

        try:
            servicio = _crear_servicio()
            detalle = servicio.obtener_detalle(id_recaudo)

            if not detalle:
                async with self:
                    self.error_message = "Recaudo no encontrado"
                    self.is_loading = False
                return

            recaudo = detalle["recaudo"]

            # Solo permitir editar pendientes
            if not recaudo.estado_recaudo.puede_editarse():
                async with self:
                    self.error_message = "Solo se pueden editar recaudos en estado 'Pendiente'"
                    self.is_loading = False
                return

            # Buscar el label del contrato para el combobox
            selected_label = ""
            for option in opts:
                if str(option["id"]) == str(recaudo.id_contrato_a):
                    selected_label = option["texto"]
                    break

            async with self:
                self.contrato_search = ""
                self.contrato_selected_label = selected_label
                self.contrato_menu_open = False

                self.form_data = {
                    "id_recaudo": str(id_recaudo),
                    "id_contrato_a": str(recaudo.id_contrato_a),
                    "fecha_pago": recaudo.fecha_pago,
                    "valor_total": str(recaudo.valor_total),
                    "metodo_pago": recaudo.metodo_pago.value,
                    "referencia_bancaria": recaudo.referencia_bancaria or "",
                    "observaciones": recaudo.observaciones or "",
                    "tipo_concepto": "Canon",
                    "periodo": recaudo.fecha_pago[:7] if recaudo.fecha_pago else "",
                }
                self.is_editing = True
                self.show_form_modal = True
                self.show_detail_modal = False
                self.is_loading = False
        except Exception as e:
            async with self:
                self.error_message = f"Error al cargar recaudo: {str(e)}"
                self.is_loading = False

    @rx.event(background=True)
    async def open_detail_modal(self, id_recaudo: int):
        """Abre modal de detalle para un recaudo."""
        async with self:
            self.is_loading = True
            self.error_message = ""

            # Contexto Documental
            self.current_entidad_tipo = "RECAUDO"
            self.current_entidad_id = str(id_recaudo)
            self.cargar_documentos()

        try:
            servicio = _crear_servicio()
            detalle = servicio.obtener_detalle(id_recaudo)

            if not detalle:
                async with self:
                    self.error_message = "Recaudo no encontrado"
                    self.is_loading = False
                return

            recaudo = detalle["recaudo"]
            conceptos = detalle["conceptos"]

            # Obtener info del contrato vía servicio
            info_contrato = servicio.obtener_info_contrato(recaudo.id_contrato_a)
            direccion = info_contrato["direccion"]
            matricula = info_contrato["matricula"]
            arrendatario = info_contrato["arrendatario"]

            async with self:
                self.recaudo_actual = {
                    "id_recaudo": recaudo.id_recaudo,
                    "id_contrato": recaudo.id_contrato_a,
                    "direccion": direccion,
                    "matricula": matricula,
                    "arrendatario": arrendatario,
                    "fecha_pago": recaudo.fecha_pago,
                    "valor_total": recaudo.valor_total,
                    "valor_total_view": format_currency(recaudo.valor_total),
                    "metodo_pago": recaudo.metodo_pago.value,
                    "referencia": recaudo.referencia_bancaria or "",
                    "estado": recaudo.estado_recaudo.value,
                    "observaciones": recaudo.observaciones or "Sin observaciones",
                    "created_at": recaudo.created_at or "",
                    "created_by": recaudo.created_by or "",
                    "conceptos": [
                        {
                            "tipo": c.tipo_concepto.value,
                            "periodo": c.periodo,
                            "valor": c.valor,
                            "valor_view": format_currency(c.valor),
                        }
                        for c in conceptos
                    ],
                }
                self.show_detail_modal = True
                self.show_form_modal = False
                self.is_loading = False
        except Exception as e:
            async with self:
                self.error_message = f"Error al cargar detalle: {str(e)}"
                self.is_loading = False

    # ==================== SAVE ====================

    @rx.event(background=True)
    async def save_recaudo(self, form_data: Dict):
        """Guarda recaudo (crear o editar) delegando al servicio."""
        async with self:
            self.is_loading = True
            self.error_message = ""
            
            # Leer datos necesarios del estado dentro del contexto para seguridad de StateProxy
            st_form_data = self.form_data.copy()
            st_contratos_options = self.contratos_options.copy()

        try:
            servicio = _crear_servicio()
            usuario = await self._get_usuario_actual()

            # Validaciones y parsing de ID Contrato
            id_contrato = form_data.get("id_contrato_a") or st_form_data.get("id_contrato_a")

            if not id_contrato:
                async with self:
                    self.error_message = "Debe seleccionar un contrato"
                    self.is_loading = False
                return

            # Si viene el texto descriptivo, extraer el ID
            if isinstance(id_contrato, str) and not id_contrato.isdigit():
                contrato_opt = next(
                    (c for c in st_contratos_options if c["texto"] == id_contrato),
                    None
                )
                if contrato_opt:
                    id_contrato = contrato_opt["id"]
                elif id_contrato.startswith("ID:"):
                    try:
                        id_contrato = id_contrato.split(":")[1].split(" -")[0].strip()
                    except (IndexError, ValueError):
                        pass

            valor_total = int(float(form_data.get("valor_total") or 0))
            if valor_total <= 0:
                async with self:
                    self.error_message = "El valor total debe ser mayor a cero"
                    self.is_loading = False
                return

            metodo_pago = form_data.get("metodo_pago", "")
            if metodo_pago != MetodoPago.EFECTIVO.value and not form_data.get("referencia_bancaria", "").strip():
                async with self:
                    self.error_message = "La referencia bancaria es obligatoria para pagos electrónicos"
                    self.is_loading = False
                return

            if form_data.get("id_recaudo"):
                # Editar: usar repositorio directo (mantiene compatibilidad)
                from src.dominio.entidades.recaudo import Recaudo

                recaudo = Recaudo(
                    id_recaudo=int(form_data.get("id_recaudo")),
                    id_contrato_a=int(id_contrato),
                    fecha_pago=form_data["fecha_pago"],
                    valor_total=valor_total,
                    metodo_pago=MetodoPago(metodo_pago),
                    referencia_bancaria=form_data.get("referencia_bancaria", "").strip() or None,
                    estado_recaudo=EstadoRecaudo.PENDIENTE,
                    observaciones=form_data.get("observaciones", "").strip() or None,
                    created_by=usuario,
                )
                repo = RepositorioRecaudo(db_manager)
                repo.actualizar(recaudo, usuario)
            else:
                # Crear: usar servicio con comando tipado
                from src.aplicacion.esquemas.recaudo import ComandoRegistrarPago
                from datetime import date

                comando = ComandoRegistrarPago(
                    id_contrato_a=int(id_contrato),
                    fecha_pago=date.fromisoformat(form_data["fecha_pago"]),
                    valor_total=valor_total,
                    metodo_pago=MetodoPago(metodo_pago),
                    referencia_bancaria=form_data.get("referencia_bancaria", "").strip() or None,
                    tipo_concepto=form_data.get("tipo_concepto", "Canon"),
                    periodo=form_data.get("periodo", datetime.now().strftime("%Y-%m")),
                    observaciones=form_data.get("observaciones", "").strip() or None,
                )
                servicio.registrar_pago(comando, usuario)

            async with self:
                self.show_form_modal = False
                self.form_data = {}

            yield RecaudosState.load_recaudos()

        except ValueError as e:
            async with self:
                self.error_message = f"Error de validación: {str(e)}"
        except Exception as e:
            async with self:
                self.error_message = f"Error al guardar: {str(e)}"
        finally:
            async with self:
                self.is_loading = False

    # ==================== ACCIONES DE ESTADO ====================

    @rx.event(background=True)
    async def aplicar_pago(self, id_recaudo: int):
        """Aplica un pago pendiente delegando al servicio."""
        async with self:
            self.is_loading = True
            self.error_message = ""

        try:
            servicio = _crear_servicio()
            usuario = await self._get_usuario_actual()
            resultado = servicio.aplicar_pago(
                id_recaudo, usuario
            )

            if resultado.exito:
                yield rx.toast.success(resultado.mensaje)
            else:
                yield rx.toast.error(resultado.mensaje)

            yield RecaudosState.load_recaudos()

        except Exception as e:
            async with self:
                self.error_message = f"Error al aplicar pago: {str(e)}"
        finally:
            async with self:
                self.is_loading = False

    @rx.event(background=True)
    async def reversar_pago(self, id_recaudo: int):
        """Reversa un pago aplicado delegando al servicio."""
        async with self:
            self.is_loading = True
            self.error_message = ""

        try:
            servicio = _crear_servicio()
            usuario = await self._get_usuario_actual()
            resultado = servicio.reversar_pago(
                id_recaudo, usuario
            )

            if resultado.exito:
                yield rx.toast.warning(resultado.mensaje)
            else:
                yield rx.toast.error(resultado.mensaje)

            yield RecaudosState.load_recaudos()

        except Exception as e:
            async with self:
                self.error_message = f"Error al reversar pago: {str(e)}"
        finally:
            async with self:
                self.is_loading = False

    @rx.event(background=True)
    async def eliminar_recaudo(self, id_recaudo: int):
        """Elimina un recaudo pendiente delegando al servicio."""
        async with self:
            self.is_loading = True
            self.error_message = ""

        try:
            servicio = _crear_servicio()
            usuario = await self._get_usuario_actual()
            resultado = servicio.eliminar_pago(
                id_recaudo, usuario
            )

            if not resultado.exito:
                async with self:
                    self.error_message = resultado.mensaje
                    self.is_loading = False
                return

            async with self:
                self.is_loading = False

            yield RecaudosState.load_recaudos()

        except Exception as e:
            async with self:
                self.error_message = f"Error al eliminar: {str(e)}"
                self.is_loading = False

    # ==================== GENERACIÓN MASIVA ====================

    @rx.event(background=True)
    async def generar_pagos_masivos(self):
        """Genera pagos masivos usando el servicio de aplicación."""
        async with self:
            self.is_loading = True
            self.error_message = ""

        try:
            servicio = _crear_servicio()
            usuario = await self._get_usuario_actual()

            resultado = servicio.generar_recaudos_mes_actual(usuario)

            async with self:
                self.is_loading = False

            msg = f"Se generaron {resultado.generados} recaudos exitosamente."
            if resultado.omitidos_por_duplicidad > 0:
                msg += (
                    f" {resultado.omitidos_por_duplicidad} contratos ya tenían "
                    f"recaudo este mes y fueron omitidos."
                )

            yield rx.toast.success(msg)
            yield RecaudosState.load_recaudos()

        except Exception as e:
            async with self:
                self.error_message = f"Error al generar pagos masivos: {str(e)}"
                self.is_loading = False
