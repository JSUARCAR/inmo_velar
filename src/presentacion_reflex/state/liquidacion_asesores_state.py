from datetime import datetime
from typing import Any, Dict, List, Optional

import reflex as rx

from src.aplicacion.servicios.servicio_liquidacion_asesores import (
    ServicioLiquidacionAsesores,
)
from src.infraestructura.persistencia.database import db_manager
from src.infraestructura.persistencia.repositorio_asesor_postgres import (
    RepositorioAsesorPostgres,
)
from src.infraestructura.persistencia.repositorio_contrato_arrendamiento_postgres import (
    RepositorioContratoArrendamientoPostgres,
)
from src.infraestructura.persistencia.repositorio_persona_postgres import (
    RepositorioPersonaPostgres,
)
from src.infraestructura.persistencia.repositorio_propiedad_postgres import (
    RepositorioPropiedadPostgres,
)
from src.infraestructura.repositorios.repositorio_bonificacion_asesor import (
    RepositorioBonificacionAsesor,
)
from src.infraestructura.repositorios.repositorio_descuento_asesor import (
    RepositorioDescuentoAsesor,
)
from src.infraestructura.repositorios.repositorio_liquidacion_asesor import (
    RepositorioLiquidacionAsesor,
)
from src.infraestructura.repositorios.repositorio_pago_asesor import (
    RepositorioPagoAsesor,
)
from src.infraestructura.servicios.servicio_documentos_pdf import ServicioDocumentosPDF
from src.presentacion_reflex.state.auth_state import AuthState
from src.presentacion_reflex.state.documentos_mixin import DocumentosStateMixin


def format_currency(value: Optional[float]) -> str:
    if value is None:
        return "$0"
    return f"${float(value):,.0f}".replace(",", ".")


class LiquidacionAsesoresState(DocumentosStateMixin):
    """Estado para gestión de liquidaciones de asesores.
    Implementa desacoplamiento de infraestructura según estándares Élite.
    """

    # Paginación
    current_page: int = 1
    page_size: int = 25
    total_items: int = 0

    # Datos
    liquidaciones: List[Dict[str, Any]] = []
    liquidacion_actual: Optional[Dict[str, Any]] = None
    descuentos_actuales: List[Dict[str, Any]] = []
    is_loading: bool = False
    error_message: str = ""

    # Filtros
    search_text: str = ""
    filter_estado: str = "Todos"
    filter_periodo: str = ""
    filter_asesor: str = ""

    # Ordenamiento
    sort_by: str = "periodo_liquidacion"
    sort_order: str = "desc"

    # Opciones de filtros
    estado_options: List[str] = ["Todos", "Pendiente", "Aprobada", "Pagada", "Anulada"]
    periodo_options: List[str] = []
    asesores_options: List[Dict[str, Any]] = []
    asesores_select_options: List[str] = []

    # Modales
    show_form_modal: bool = False
    show_detail_modal: bool = False
    show_discount_modal: bool = False
    show_annul_modal: bool = False
    selected_annul_id: int = 0
    annul_reason: str = ""
    show_edit_modal: bool = False
    show_bulk_modal: bool = False

    # Form data
    selected_liquidacion_id: int = 0
    form_data: Dict[str, Any] = {}
    discount_form: Dict[str, Any] = {}
    edit_form: Dict[str, Any] = {}

    # Detalles actuales para modal
    bonificaciones_actuales: List[Dict[str, Any]] = []

    # Helper items (temporary)
    existing_discounts: List[Dict[str, Any]] = []
    existing_bonuses: List[Dict[str, Any]] = []
    new_discounts: List[Dict[str, Any]] = []
    new_bonuses: List[Dict[str, Any]] = []
    temp_discount: Dict[str, Any] = {"tipo": "Otros", "descripcion": "", "valor": ""}
    temp_bonus: Dict[str, Any] = {"tipo": "Bono", "descripcion": "", "valor": ""}
    advisor_properties: List[Dict[str, Any]] = []

    def _obtener_servicio(self) -> ServicioLiquidacionAsesores:
        """Factoría interna para inyectar dependencias PostgreSQL."""
        return ServicioLiquidacionAsesores(
            repo_liquidacion=RepositorioLiquidacionAsesor(db_manager),
            repo_descuento=RepositorioDescuentoAsesor(db_manager),
            repo_pago=RepositorioPagoAsesor(db_manager),
            repo_bonificacion=RepositorioBonificacionAsesor(db_manager),
            repo_contrato_arrendamiento=RepositorioContratoArrendamientoPostgres(db_manager),
            repo_propiedad=RepositorioPropiedadPostgres(db_manager),
            repo_asesor=RepositorioAsesorPostgres(db_manager),
            repo_persona=RepositorioPersonaPostgres(db_manager),
            servicio_pdf=ServicioDocumentosPDF(),
        )

    def set_form_field(self, name: str, value: Any):
        self.form_data[name] = value
        if name == "id_asesor" and value:
            try:
                id_str = str(value)
                for asesor in self.asesores_options:
                    if asesor["id"] == id_str:
                        pct = asesor.get("comision_porcentaje", 5.0)
                        self.form_data["porcentaje_comision"] = str(pct)
                        break
                return LiquidacionAsesoresState.fetch_advisor_properties(int(value))
            except Exception:
                pass

    def set_discount_field(self, name: str, value: Any):
        self.discount_form[name] = value

    def close_discount_modal(self):
        self.show_discount_modal = False
        self.discount_form = {}
        self.error_message = ""

    @rx.event(background=True)
    async def save_descuento(self, form_data: Dict):
        async with self:
            self.is_loading = True
            self.error_message = ""
            auth_state = await self.get_state(AuthState)
            usuario = auth_state.user_nombre

        try:
            servicio = self._obtener_servicio()
            tipo = form_data.get("tipo")
            descripcion = form_data.get("descripcion")
            valor = int(form_data.get("valor", 0))

            if not tipo or not descripcion or valor <= 0:
                async with self:
                    self.error_message = "Campos obligatorios incompletos"
                    self.is_loading = False
                return

            servicio.agregar_descuento(
                id_liquidacion=self.selected_liquidacion_id,
                tipo=tipo,
                descripcion=descripcion,
                valor=valor,
                usuario=usuario,
            )

            async with self:
                self.show_discount_modal = False
                self.discount_form = {}
                self.is_loading = False

            yield rx.toast.success("Descuento agregado")
            yield LiquidacionAsesoresState.open_detail_modal(self.selected_liquidacion_id)

        except Exception as e:
            async with self:
                self.error_message = f"Error: {e}"
                self.is_loading = False

    def set_temp_bonus_field(self, name: str, value: Any):
        self.temp_bonus[name] = value

    def add_temp_bonus(self):
        if self.temp_bonus["descripcion"] and self.temp_bonus["valor"]:
            self.new_bonuses.append(dict(self.temp_bonus))
            self.temp_bonus = {"tipo": "Bono", "descripcion": "", "valor": ""}

    def remove_temp_bonus(self, item: Dict):
        self.new_bonuses.remove(item)

    def set_temp_discount_field(self, name: str, value: Any):
        self.temp_discount[name] = value

    def add_temp_discount(self):
        if self.temp_discount["descripcion"] and self.temp_discount["valor"]:
            self.new_discounts.append(dict(self.temp_discount))
            self.temp_discount = {"tipo": "Otros", "descripcion": "", "valor": ""}

    def remove_temp_discount(self, item: Dict):
        self.new_discounts.remove(item)

    @rx.event(background=True)
    async def eliminar_descuento(self, id_descuento: int):
        async with self:
            self.is_loading = True
            auth_state = await self.get_state(AuthState)
            usuario = auth_state.user_nombre

        try:
            servicio = self._obtener_servicio()
            servicio.eliminar_descuento(id_descuento, usuario)
            yield rx.toast.success("Descuento eliminado")
            # Refrescar datos según el contexto
            if self.show_detail_modal:
                yield LiquidacionAsesoresState.open_detail_modal(self.selected_liquidacion_id)
            else:
                yield LiquidacionAsesoresState.open_edit_modal(self.selected_liquidacion_id)
        except Exception as e:
            async with self:
                self.error_message = f"Error: {e}"
                self.is_loading = False

    @rx.event(background=True)
    async def eliminar_bonificacion(self, id_bonificacion: int):
        async with self:
            self.is_loading = True
            auth_state = await self.get_state(AuthState)
            usuario = auth_state.user_nombre

        try:
            servicio = self._obtener_servicio()
            servicio.eliminar_bonificacion(id_bonificacion, usuario)
            yield rx.toast.success("Bonificación eliminada")
            # Refrescar datos según el contexto
            if self.show_detail_modal:
                yield LiquidacionAsesoresState.open_detail_modal(self.selected_liquidacion_id)
            else:
                yield LiquidacionAsesoresState.open_edit_modal(self.selected_liquidacion_id)
        except Exception as e:
            async with self:
                self.error_message = f"Error: {e}"
                self.is_loading = False

    @rx.event(background=True)
    async def on_load(self):
        async with self:
            self.is_loading = True
        try:
            yield LiquidacionAsesoresState.load_filter_options()
            yield LiquidacionAsesoresState.load_liquidaciones()
        finally:
            async with self:
                self.is_loading = False

    @rx.event(background=True)
    async def load_filter_options(self):
        try:
            repo_asesor = RepositorioAsesorPostgres(db_manager)
            asesores_entidades = repo_asesor.listar_activos()

            asesores = [{
                "id": str(a.id_asesor),
                "texto": a.nombre_completo,
                "comision_porcentaje": a.comision_porcentaje_arriendo or 5.0,
            } for a in asesores_entidades]

            from dateutil.relativedelta import relativedelta
            periodos = [(datetime.now() - relativedelta(months=i)).strftime("%Y-%m") for i in range(24)]

            async with self:
                self.asesores_options = asesores
                self.asesores_select_options = [a["texto"] for a in asesores]
                self.periodo_options = periodos
        except Exception as e:
            async with self:
                self.error_message = f"Filtros error: {e}"

    @rx.event(background=True)
    async def fetch_advisor_properties(self, id_asesor: int):
        try:
            servicio = self._obtener_servicio()
            props = servicio.obtener_contratos_activos_asesor(id_asesor)
            async with self:
                self.advisor_properties = [{
                    "DIRECCION_PROPIEDAD": p["direccion"],
                    "CANON_ARRENDAMIENTO": p["canon"],
                    "CANON_ARRENDAMIENTO_VIEW": format_currency(p["canon"]),
                    "ID_CONTRATO_A": p["id_contrato"],
                } for p in props]
        except Exception:
            async with self:
                self.advisor_properties = []

    def toggle_sort(self, column: str):
        """Cambia el criterio de ordenamiento."""
        if self.sort_by == column:
            self.sort_order = "desc" if self.sort_order =="asc" else "asc"
        else:
            self.sort_by = column
            self.sort_order = "desc"

        self.current_page = 1
        return LiquidacionAsesoresState.load_liquidaciones

    @rx.event(background=True)
    async def load_liquidaciones(self):
        async with self:
            self.is_loading = True
            self.error_message = ""

        try:
            servicio = self._obtener_servicio()
            filtros = {}
            if self.filter_estado != "Todos":
                filtros["estado"] = self.filter_estado
            if self.filter_periodo:
                filtros["periodo"] = self.filter_periodo
            if self.filter_asesor:
                for a in self.asesores_options:
                    if a["texto"] == self.filter_asesor:
                        filtros["id_asesor"] = int(a["id"])
                        break
            if self.search_text:
                filtros["search"] = self.search_text

            resultado = servicio.listar_liquidaciones_paginado(
                page=self.current_page,
                page_size=self.page_size,
                filtros=filtros,
                sort_by=self.sort_by,
                sort_order=self.sort_order,
            )

            # Mapear y formatear items para la UI
            formatted_items = []
            for item in resultado["items"]:
                formatted_items.append({
                    "id_liquidacion": item["id_liquidacion_asesor"],
                    "asesor": item["nombre_asesor"],
                    "periodo": item["periodo_liquidacion"],
                    "estado": item["estado_liquidacion"],
                    "comision_bruta": item["comision_bruta"],
                    "comision_bruta_view": format_currency(item["comision_bruta"]),
                    "total_descuentos": item["total_descuentos"],
                    "total_descuentos_view": format_currency(item["total_descuentos"]),
                    "total_bonificaciones": item["total_bonificaciones"],
                    "total_bonificaciones_view": format_currency(item["total_bonificaciones"]),
                    "valor_neto": item["valor_neto_asesor"],
                    "valor_neto_view": format_currency(item["valor_neto_asesor"]),
                    "puede_editarse": item.get("puede_editarse", False),
                    "puede_aprobarse": item.get("puede_aprobarse", False),
                    "puede_anularse": item.get("puede_anularse", False),
                })

            async with self:
                self.liquidaciones = formatted_items
                self.total_items = resultado["total"]
                self.is_loading = False
        except Exception as e:
            async with self:
                self.error_message = f"Carga error: {e}"
                self.is_loading = False

    @rx.event(background=True)
    async def handle_save_form(self, form_data: Dict):
        async with self:
            auth_state = await self.get_state(AuthState)
            usuario = auth_state.user_nombre

        if self.selected_liquidacion_id > 0:
            async with self:
                self.is_loading = True
            try:
                servicio = self._obtener_servicio()
                datos_upd = {}
                if "porcentaje_comision" in form_data:
                    datos_upd["porcentaje_comision"] = int(float(form_data["porcentaje_comision"]) * 100)
                if "observaciones" in form_data:
                    datos_upd["observaciones_liquidacion"] = form_data["observaciones"]

                if datos_upd:
                    servicio.actualizar_liquidacion(self.selected_liquidacion_id, datos_upd, usuario)

                for d in self.new_discounts:
                    servicio.agregar_descuento(self.selected_liquidacion_id, d["tipo"], d["descripcion"], int(d["valor"]), usuario)
                for b in self.new_bonuses:
                    servicio.agregar_bonificacion(self.selected_liquidacion_id, b["tipo"], b["descripcion"], int(b["valor"]), usuario)

                async with self:
                    self.show_form_modal = False
                    self.selected_liquidacion_id = 0
                yield rx.toast.success("Actualizado")
                yield LiquidacionAsesoresState.load_liquidaciones()
            except Exception as e:
                async with self:
                    self.error_message = str(e)
                    self.is_loading = False
        else:
            yield LiquidacionAsesoresState.crear_liquidacion(form_data)

    @rx.event(background=True)
    async def crear_liquidacion(self, form_data: Dict):
        async with self:
            self.is_loading = True
            auth_state = await self.get_state(AuthState)
            usuario = auth_state.user_nombre

        try:
            servicio = self._obtener_servicio()
            id_asesor = int(form_data.get("id_asesor"))
            periodo = form_data.get("periodo")
            pct = int(float(form_data.get("porcentaje_comision", "5.0")) * 100)

            contratos_activos = servicio.obtener_contratos_activos_asesor(id_asesor)
            if not contratos_activos:
                async with self:
                    self.error_message = "Asesor sin contratos activos"
                    self.is_loading = False
                return

            liquidacion = servicio.generar_liquidacion_multi_contrato(
                id_asesor=id_asesor,
                periodo=periodo,
                contratos_lista=[{"id": c["id_contrato"], "canon": c["canon"]} for c in contratos_activos],
                porcentaje_comision=pct,
                total_bonificaciones=sum(int(b.get("valor", 0)) for b in self.new_bonuses),
                datos_adicionales={"observaciones": form_data.get("observaciones", "")},
                usuario=usuario,
            )

            for d in self.new_discounts:
                servicio.agregar_descuento(liquidacion.id_liquidacion_asesor, d["tipo"], d["descripcion"], int(d["valor"]), usuario)

            async with self:
                self.show_form_modal = False
                self.is_loading = False
            yield rx.toast.success("Creada")
            yield LiquidacionAsesoresState.load_liquidaciones()

        except Exception as e:
            async with self:
                self.error_message = str(e)
                self.is_loading = False

    @rx.event(background=True)
    async def open_detail_modal(self, id_liquidacion: int):
        async with self:
            self.is_loading = True
            self.current_entidad_tipo = "LIQUIDACION_ASESOR"
            self.current_entidad_id = str(id_liquidacion)
            self.cargar_documentos()

        try:
            servicio = self._obtener_servicio()
            detalles = servicio.obtener_detalle_completo(id_liquidacion)
            async with self:
                liq_raw = detalles["liquidacion"]
                # Normalización centralizada para Detail Modal
                self.liquidacion_actual = {
                    "id_liquidacion": liq_raw["id_liquidacion_asesor"],
                    "id_liquidacion_asesor": liq_raw["id_liquidacion_asesor"],
                    "asesor": liq_raw["nombre_asesor"],
                    "periodo": liq_raw["periodo_liquidacion"],
                    "estado": liq_raw["estado_liquidacion"],
                    "canon_liquidado": liq_raw["canon_arrendamiento_liquidado"],
                    "canon_liquidado_view": format_currency(liq_raw["canon_arrendamiento_liquidado"]),
                    "comision_bruta": liq_raw["comision_bruta"],
                    "comision_bruta_view": format_currency(liq_raw["comision_bruta"]),
                    "total_descuentos": liq_raw["total_descuentos"],
                    "total_descuentos_view": format_currency(liq_raw["total_descuentos"]),
                    "total_bonificaciones": liq_raw["total_bonificaciones"],
                    "total_bonificaciones_view": format_currency(liq_raw["total_bonificaciones"]),
                    "valor_neto": liq_raw["valor_neto_asesor"],
                    "valor_neto_view": format_currency(liq_raw["valor_neto_asesor"]),
                    "observaciones": liq_raw["observaciones_liquidacion"],
                }
                
                # Normalizar descuentos
                descuentos = []
                for d in detalles.get("descuentos", []):
                    descuentos.append({
                        "id_descuento": d["id_descuento_asesor"],
                        "tipo": d["tipo_descuento"],
                        "descripcion": d["descripcion_descuento"],
                        "valor": d["valor_descuento"],
                        "valor_view": format_currency(d["valor_descuento"]),
                    })
                self.descuentos_actuales = descuentos
                
                # Normalizar bonificaciones
                bonificaciones = []
                for b in detalles.get("bonificaciones", []):
                    bonificaciones.append({
                        "id_bonificacion": b["id_bonificacion_asesor"],
                        "tipo": b["tipo_bonificacion"],
                        "descripcion": b["descripcion_bonificacion"],
                        "valor": b["valor_bonificacion"],
                        "valor_view": format_currency(b["valor_bonificacion"]),
                    })
                self.bonificaciones_actuales = bonificaciones
                
                # Normalizar contratos/propiedades
                propiedades = []
                for p in detalles.get("contratos", []):
                    propiedades.append({
                        "DIRECCION_PROPIEDAD": p.get("direccion", p.get("DIRECCION_PROPIEDAD")),
                        "CANON_ARRENDAMIENTO": p.get("canon", p.get("CANON_ARRENDAMIENTO")),
                        "CANON_ARRENDAMIENTO_VIEW": format_currency(p.get("canon", p.get("CANON_ARRENDAMIENTO"))),
                    })
                self.advisor_properties = propiedades
                
                self.show_detail_modal = True
                self.is_loading = False
        except Exception as e:
            async with self:
                self.error_message = f"Error detalle: {e}"
                self.is_loading = False

    @rx.event(background=True)
    async def generar_liquidacion_masiva(self, form_data: Dict):
        async with self:
            self.is_loading = True
            auth_state = await self.get_state(AuthState)
            usuario = auth_state.user_nombre

        try:
            periodo = form_data.get("periodo")
            servicio = self._obtener_servicio()
            stats = servicio.generar_liquidaciones_masivas_optimizado(periodo, usuario)
            async with self:
                self.show_bulk_modal = False
                self.is_loading = False
            yield rx.toast.success(f"Masivo: {stats['creadas']} creadas")
            yield LiquidacionAsesoresState.load_liquidaciones()
        except Exception as e:
            async with self:
                self.error_message = str(e)
                self.is_loading = False

    @rx.event(background=True)
    async def open_edit_modal(self, id_liquidacion: int):
        async with self:
            self.is_loading = True
        try:
            servicio = self._obtener_servicio()
            detalles = servicio.obtener_detalle_completo(id_liquidacion)
            liq = detalles["liquidacion"]
            
            # Normalizar existentes para edición
            existing_discounts = []
            for d in detalles.get("descuentos", []):
                existing_discounts.append({
                    "id_descuento": d["id_descuento_asesor"],
                    "tipo": d["tipo_descuento"],
                    "descripcion": d["descripcion_descuento"],
                    "valor": d["valor_descuento"],
                    "valor_view": format_currency(d["valor_descuento"]),
                })
                
            existing_bonuses = []
            for b in detalles.get("bonificaciones", []):
                existing_bonuses.append({
                    "id_bonificacion": b["id_bonificacion_asesor"],
                    "tipo": b["tipo_bonificacion"],
                    "descripcion": b["descripcion_bonificacion"],
                    "valor": b["valor_bonificacion"],
                    "valor_view": format_currency(b["valor_bonificacion"]),
                })

            async with self:
                self.form_data = {
                    "id_asesor": str(liq["id_asesor"]),
                    "periodo": liq["periodo_liquidacion"],
                    "porcentaje_comision": str(liq["porcentaje_comision"] / 100.0 if liq["porcentaje_comision"] > 1.0 else liq["porcentaje_comision"]),
                    "observaciones": liq["observaciones_liquidacion"] or "",
                }
                self.existing_discounts = existing_discounts
                self.existing_bonuses = existing_bonuses
                self.new_discounts = []
                self.new_bonuses = []
                self.selected_liquidacion_id = id_liquidacion
                self.show_form_modal = True
                self.is_loading = False
        except Exception as e:
            async with self:
                self.error_message = str(e)
                self.is_loading = False

    @rx.event(background=True)
    async def aprobar_liquidacion(self, id_liquidacion: int):
        async with self:
            self.is_loading = True
            auth_state = await self.get_state(AuthState)
            usuario = auth_state.user_nombre
        try:
            servicio = self._obtener_servicio()
            servicio.aprobar_liquidacion(id_liquidacion, usuario)
            async with self:
                self.show_detail_modal = False
            yield rx.toast.success("Aprobada")
            yield LiquidacionAsesoresState.load_liquidaciones()
        except Exception as e:
            async with self:
                self.error_message = str(e)
                self.is_loading = False

    @rx.event(background=True)
    async def anular_liquidacion(self, id_liquidacion: int, motivo: str):
        """Anula una liquidación con motivo."""
        async with self:
            self.is_loading = True
            auth_state = await self.get_state(AuthState)
            usuario = auth_state.user_nombre
        try:
            servicio = self._obtener_servicio()
            servicio.anular_liquidacion(id_liquidacion, motivo, usuario)
            async with self:
                self.show_annul_modal = False
                self.show_detail_modal = False
                self.selected_annul_id = 0
                self.annul_reason = ""
            yield rx.toast.success("Liquidación anulada")
            yield LiquidacionAsesoresState.load_liquidaciones()
        except Exception as e:
            async with self:
                self.error_message = str(e)
                self.is_loading = False

    @rx.event(background=True)
    async def registrar_pago(self, id_liquidacion: int):
        # Implementación simplificada para el refactor
        pass

    def open_create_modal(self):
        self.selected_liquidacion_id = 0
        self.show_form_modal = True
        self.form_data = {
            "id_asesor": "",
            "periodo": datetime.now().strftime("%Y-%m"),
            "porcentaje_comision": "5.0",
            "observaciones": "",
        }
        self.new_discounts = []
        self.new_bonuses = []

    def close_modal(self):
        self.show_form_modal = False
        self.show_detail_modal = False
        self.show_discount_modal = False
        self.liquidacion_actual = None
        self.error_message = ""

    def next_page(self):
        self.current_page += 1
        return LiquidacionAsesoresState.load_liquidaciones()

    def prev_page(self):
        self.current_page -= 1
        return LiquidacionAsesoresState.load_liquidaciones()

    def set_search(self, value: str):
        self.search_text = value

    def search_liquidaciones(self):
        self.current_page = 1
        return LiquidacionAsesoresState.load_liquidaciones()

    def set_filter_estado(self, value: str):
        self.filter_estado = value
        return LiquidacionAsesoresState.load_liquidaciones()

    def set_filter_periodo(self, value: str):
        self.filter_periodo = value
        return LiquidacionAsesoresState.load_liquidaciones()

    def set_filter_asesor(self, value: str):
        self.filter_asesor = value
        return LiquidacionAsesoresState.load_liquidaciones()

    def set_show_form_modal(self, value: bool):
        self.show_form_modal = value

    def set_show_detail_modal(self, value: bool):
        self.show_detail_modal = value

    def set_show_discount_modal(self, value: bool):
        self.show_discount_modal = value

    def set_show_bulk_modal(self, value: bool):
        self.show_bulk_modal = value

    def close_form_modal(self):
        self.close_modal()

    def open_annul_modal(self, id_liq: int):
        self.selected_annul_id = id_liq
        self.annul_reason = ""
        self.show_annul_modal = True

    def close_annul_modal(self):
        self.show_annul_modal = False
        self.annul_reason = ""
        self.selected_annul_id = 0

    def set_annul_reason(self, value: str):
        self.annul_reason = value
    
    def confirm_annulment(self):
        if self.selected_annul_id:
            return LiquidacionAsesoresState.anular_liquidacion(self.selected_annul_id, self.annul_reason)

    def open_bulk_modal(self):
        self.show_bulk_modal = True
        self.form_data["periodo"] = datetime.now().strftime("%Y-%m")
        self.error_message = ""

    def close_bulk_modal(self):
        self.show_bulk_modal = False

    @rx.event(background=True)
    async def marcar_como_pagada(self, id_liquidacion: int):
        """Registra un pago rápido de forma simplificada."""
        async with self:
            self.is_loading = True
            auth_state = await self.get_state(AuthState)
            usuario = auth_state.user_nombre
        try:
            servicio = self._obtener_servicio()
            # Crear un registro de pago automático
            pago = servicio.programar_pago(
                id_liquidacion=id_liquidacion,
                id_asesor=self.liquidacion_actual["id_asesor"] if self.liquidacion_actual else 0,
                valor=self.liquidacion_actual["valor_neto"] if self.liquidacion_actual else 0,
                fecha_programada=datetime.now().strftime("%Y-%m-%d"),
                medio_pago="Transferencia",
                usuario=usuario
            )
            servicio.registrar_pago(
                id_pago=pago.id_pago_asesor,
                fecha_pago=datetime.now().strftime("%Y-%m-%d"),
                comprobante=f"TRF-{id_liquidacion}",
                usuario=usuario
            )
            async with self:
                self.show_detail_modal = False
            yield rx.toast.success("Liquidación marcada como pagada")
            yield LiquidacionAsesoresState.load_liquidaciones()
        except Exception as e:
            async with self:
                self.error_message = str(e)
                self.is_loading = False
