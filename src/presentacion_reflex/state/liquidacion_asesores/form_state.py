import reflex as rx
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging

from src.aplicacion.servicios.servicio_liquidacion_asesores import ServicioLiquidacionAsesores
from src.infraestructura.persistencia.database import db_manager
from src.infraestructura.persistencia.repositorio_asesor_postgres import RepositorioAsesorPostgres
from src.infraestructura.persistencia.repositorio_contrato_arrendamiento_postgres import RepositorioContratoArrendamientoPostgres
from src.infraestructura.persistencia.repositorio_persona_postgres import RepositorioPersonaPostgres
from src.infraestructura.persistencia.repositorio_propiedad_postgres import RepositorioPropiedadPostgres
from src.infraestructura.repositorios.repositorio_bonificacion_asesor import RepositorioBonificacionAsesor
from src.infraestructura.repositorios.repositorio_descuento_asesor import RepositorioDescuentoAsesor
from src.infraestructura.repositorios.repositorio_liquidacion_asesor import RepositorioLiquidacionAsesor
from src.infraestructura.repositorios.repositorio_pago_asesor import RepositorioPagoAsesor
from src.infraestructura.servicios.servicio_documentos_pdf import ServicioDocumentosPDF
from src.presentacion_reflex.state.auth_state import AuthState

logger = logging.getLogger(__name__)

def format_currency(value: Optional[float]) -> str:
    if value is None:
        return "$0"
    return f"${float(value):,.0f}".replace(",", ".")

class LiquidacionFormState(rx.State):
    """Maneja los formularios de creación, edición, detalles y modales asociados."""
    
    show_form_modal: bool = False
    show_detail_modal: bool = False
    show_discount_modal: bool = False
    show_annul_modal: bool = False
    show_bulk_modal: bool = False
    
    selected_liquidacion_id: int = 0
    form_data: Dict[str, Any] = {}
    discount_form: Dict[str, Any] = {}
    annul_reason: str = ""
    error_message: str = ""
    
    liquidacion_actual: Optional[Dict[str, Any]] = None
    descuentos_actuales: List[Dict[str, Any]] = []
    bonificaciones_actuales: List[Dict[str, Any]] = []
    advisor_properties: List[Dict[str, Any]] = []
    
    # Previsualización Financiera (LIQ-AUTO-001)
    preview_4x1000: str = "$0"
    preview_seguros_total: str = "$0"
    
    # Datos para edición
    existing_discounts: List[Dict[str, Any]] = []
    existing_bonuses: List[Dict[str, Any]] = []

    # Temporales para creación/edición
    new_discounts: List[Dict[str, Any]] = []
    new_bonuses: List[Dict[str, Any]] = []
    temp_discount: Dict[str, Any] = {"tipo": "Otros", "descripcion": "", "valor": ""}
    temp_bonus: Dict[str, Any] = {"tipo": "Bono", "descripcion": "", "valor": ""}

    def _obtener_servicio(self) -> ServicioLiquidacionAsesores:
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

    # --- Lógica de Campos Temporales ---
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

    # --- Lógica Operativa (Backend) ---
    @rx.event(background=True)
    async def handle_save_form(self, form_data: Dict):
        async with self:
            auth_state = await self.get_state(AuthState)
            usuario = auth_state.user_nombre
            id_liq = self.selected_liquidacion_id

        try:
            servicio = self._obtener_servicio()
            if id_liq > 0:
                # Edición
                datos_upd = {}
                if "porcentaje_comision" in form_data:
                    datos_upd["porcentaje_comision"] = int(float(form_data["porcentaje_comision"]) * 100)
                if "observaciones" in form_data:
                    datos_upd["observaciones_liquidacion"] = form_data["observaciones"]

                if datos_upd:
                    servicio.actualizar_liquidacion(id_liq, datos_upd, usuario)

                async with self:
                    new_d = list(self.new_discounts)
                    new_b = list(self.new_bonuses)

                for d in new_d:
                    servicio.agregar_descuento(id_liq, d["tipo"], d["descripcion"], int(d["valor"]), usuario)
                for b in new_b:
                    servicio.agregar_bonificacion(id_liq, b["tipo"], b["descripcion"], int(b["valor"]), usuario)

                async with self:
                    self.show_form_modal = False
                    self.selected_liquidacion_id = 0
                
                # Sincronización Élite: Recargar grilla para reflejar totales actualizados
                from src.presentacion_reflex.state.liquidacion_asesores.grid_state import LiquidacionGridState
                yield LiquidacionGridState.load_liquidaciones()
                yield rx.toast.success("Liquidación actualizada")
            else:
                # Creación
                id_asesor = int(form_data.get("id_asesor"))
                periodo = form_data.get("periodo")
                
                contratos_activos = servicio.repo_contrato_arrendamiento.obtener_activos_por_asesor(id_asesor)
                if not contratos_activos:
                    async with self:
                        self.error_message = "Asesor sin contratos activos"
                    return

                # Desglose de contratos con su porcentaje respectivo
                contratos_lista = []
                for c in contratos_activos:
                    pct = getattr(c, 'comision_porcentaje_contrato_m', 0) or 0
                    contratos_lista.append({
                        "id": c.id_contrato_a,
                        "canon": c.canon_arrendamiento,
                        "porcentaje_comision": pct,
                        "id_seguro": getattr(c, "id_seguro", None),
                        "porcentaje_seguro": getattr(c, "porcentaje_seguro", 0),
                    })

                async with self:
                    new_d = list(self.new_discounts)
                    new_b = list(self.new_bonuses)

                liquidacion = servicio.generar_liquidacion_multi_contrato(
                    id_asesor=id_asesor,
                    periodo=periodo,
                    contratos_lista=contratos_lista,
                    total_bonificaciones=sum(int(b.get("valor", 0)) for b in new_b),
                    datos_adicionales={"observaciones": form_data.get("observaciones", "")},
                    usuario=usuario,
                )

                for d in new_d:
                    servicio.agregar_descuento(liquidacion.id_liquidacion_asesor, d["tipo"], d["descripcion"], int(d["valor"]), usuario)

                async with self:
                    self.show_form_modal = False
                yield rx.toast.success("Liquidación generada")

        except Exception as e:
            async with self:
                self.error_message = str(e)

    @rx.event(background=True)
    async def eliminar_descuento(self, id_descuento: int):
        async with self:
            auth_state = await self.get_state(AuthState)
            usuario = auth_state.user_nombre
            id_liq = self.selected_liquidacion_id

        try:
            servicio = self._obtener_servicio()
            servicio.eliminar_descuento(id_descuento, usuario)
            yield rx.toast.success("Descuento eliminado")
            if self.show_detail_modal:
                yield LiquidacionFormState.open_detail_modal(id_liq)
        except Exception as e:
            async with self:
                self.error_message = str(e)

    @rx.event(background=True)
    async def eliminar_bonificacion(self, id_bonificacion: int):
        async with self:
            auth_state = await self.get_state(AuthState)
            usuario = auth_state.user_nombre
            id_liq = self.selected_liquidacion_id

        try:
            servicio = self._obtener_servicio()
            servicio.eliminar_bonificacion(id_bonificacion, usuario)
            yield rx.toast.success("Bonificación eliminada")
            if self.show_detail_modal:
                yield LiquidacionFormState.open_detail_modal(id_liq)
        except Exception as e:
            async with self:
                self.error_message = str(e)

    @rx.event(background=True)
    async def aprobar_liquidacion(self, id_liquidacion: int):
        async with self:
            auth_state = await self.get_state(AuthState)
            usuario = auth_state.user_nombre
        try:
            servicio = self._obtener_servicio()
            servicio.aprobar_liquidacion(id_liquidacion, usuario)
            async with self:
                self.show_detail_modal = False
            yield rx.toast.success("Aprobada")
        except Exception as e:
            async with self:
                self.error_message = str(e)

    @rx.event(background=True)
    async def anular_liquidacion(self, id_liquidacion: int, motivo: str):
        async with self:
            auth_state = await self.get_state(AuthState)
            usuario = auth_state.user_nombre
        try:
            servicio = self._obtener_servicio()
            servicio.anular_liquidacion(id_liquidacion, motivo, usuario)
            async with self:
                self.show_annul_modal = False
                self.show_detail_modal = False
                self.annul_reason = ""
            yield rx.toast.success("Anulada")
        except Exception as e:
            async with self:
                self.error_message = str(e)

    @rx.event(background=True)
    async def open_detail_modal(self, id_liquidacion: int):
        async with self:
            self.error_message = ""
        try:
            servicio = self._obtener_servicio()
            detalles = servicio.obtener_detalle_completo(id_liquidacion)
            async with self:
                liq_raw = detalles["liquidacion"]
                self.liquidacion_actual = {
                    "id_liquidacion": liq_raw["id_liquidacion_asesor"],
                    "id_liquidacion_asesor": liq_raw["id_liquidacion_asesor"],
                    "asesor": liq_raw["nombre_asesor"],
                    "periodo": liq_raw["periodo_liquidacion"],
                    "estado": liq_raw["estado_liquidacion"],
                    "canon_liquidado_view": format_currency(liq_raw["canon_arrendamiento_liquidado"]),
                    "comision_bruta_view": format_currency(liq_raw["comision_bruta"]),
                    "total_descuentos_view": format_currency(liq_raw["total_descuentos"]),
                    "total_bonificaciones_view": format_currency(liq_raw["total_bonificaciones"]),
                    "valor_neto_view": format_currency(liq_raw["valor_neto_asesor"]),
                    "observaciones": liq_raw["observaciones_liquidacion"],
                    "puede_aprobarse": liq_raw.get("puede_aprobarse", False),
                    "puede_anularse": liq_raw.get("puede_anularse", False),
                }
                self.descuentos_actuales = [{
                    "id_descuento": d["id_descuento_asesor"],
                    "tipo": d["tipo_descuento"],
                    "descripcion": d["descripcion_descuento"],
                    "valor_view": format_currency(d["valor_descuento"]),
                } for d in detalles.get("descuentos", [])]
                
                self.bonificaciones_actuales = [{
                    "id_bonificacion": b["id_bonificacion_asesor"],
                    "tipo": b["tipo_bonificacion"],
                    "descripcion": b["descripcion_bonificacion"],
                    "valor_view": format_currency(b["valor_bonificacion"]),
                } for b in detalles.get("bonificaciones", [])]
                
                self.advisor_properties = [{
                    "DIRECCION_PROPIEDAD": p.get("direccion") or p.get("DIRECCION_PROPIEDAD"),
                    "CANON_ARRENDAMIENTO_VIEW": format_currency(p.get("canon_incluido") or p.get("CANON_INCLUIDO")),
                    "COMISION_PORCENTAJE_VIEW": f"{(p.get('comision_porcentaje_contrato') or 0) / 100.0:.2f}%",
                    "COMISION_MONTO_VIEW": format_currency(p.get('comision_monto_contrato') or 0),
                } for p in detalles.get("contratos", [])]
                
                self.show_detail_modal = True
        except Exception as e:
            async with self:
                self.error_message = f"Error detalle: {e}"

    def set_form_field(self, name: str, value: Any):
        self.form_data[name] = value
        if name == "id_asesor" and value:
            return LiquidacionFormState.fetch_advisor_properties(int(value))

    @rx.event(background=True)
    async def fetch_advisor_properties(self, id_asesor: int):
        try:
            servicio = self._obtener_servicio()
            props = servicio.repo_contrato_arrendamiento.obtener_activos_por_asesor(id_asesor)
            from src.dominio.entidades.liquidacion_asesor import LiquidacionAsesor
            async with self:
                self.advisor_properties = []
                total_4x1000 = 0
                total_seguros = 0
                
                for p in props:
                    pct = getattr(p, 'comision_porcentaje_contrato_m', 0) or 0
                    monto = LiquidacionAsesor.calcular_comision_bruta(p.canon_arrendamiento, pct)
                    
                    # Previsualización de 4x1000 (Granular por Propiedad - Base Canon)
                    valor_4x1000 = LiquidacionAsesor.calcular_4x1000(p.canon_arrendamiento)
                    total_4x1000 += valor_4x1000
                    
                    # Previsualización de Seguro (LIQ-AUTO-001 - Normalizado)
                    pct_seguro = getattr(p, 'porcentaje_seguro', 0) or 0
                    if pct_seguro > 0 and pct_seguro < 100:
                        pct_seguro *= 100 # Normalizar 2 -> 200 (2.00%)
                        
                    valor_seguro = LiquidacionAsesor.calcular_valor_seguro(p.canon_arrendamiento, pct_seguro)
                    total_seguros += valor_seguro
                    
                    self.advisor_properties.append({
                        "DIRECCION_PROPIEDAD": p.direccion_propiedad if hasattr(p, 'direccion_propiedad') else "N/A",
                        "CANON_ARRENDAMIENTO": p.canon_arrendamiento,
                        "CANON_ARRENDAMIENTO_VIEW": format_currency(p.canon_arrendamiento),
                        "ID_CONTRATO_A": p.id_contrato_a,
                        "COMISION_PORCENTAJE_CONTRATO": pct,
                        "COMISION_PORCENTAJE_VIEW": f"{pct / 100.0:.2f}%",
                        "COMISION_MONTO_CONTRATO": monto,
                        "COMISION_MONTO_VIEW": format_currency(monto),
                    })
                
                # Previsualización global (LIQ-AUTO-001)
                self.preview_4x1000 = format_currency(total_4x1000)
                self.preview_seguros_total = format_currency(total_seguros)
                
        except Exception as e:
            logger.error(f"Error fetch_advisor_properties: {e}")
            async with self:
                self.advisor_properties = []
                self.preview_4x1000 = "$0"
                self.preview_seguros_total = "$0"

    def open_create_modal(self):
        self.selected_liquidacion_id = 0
        self.show_form_modal = True
        self.form_data = {
            "id_asesor": "",
            "periodo": datetime.now().strftime("%Y-%m"),
            "porcentaje_comision": "0.0",
            "observaciones": "",
        }
        self.new_discounts = []
        self.new_bonuses = []
        self.error_message = ""

    def close_modal(self):
        self.show_form_modal = False
        self.show_detail_modal = False
        self.show_discount_modal = False
        self.show_bulk_modal = False
        self.show_annul_modal = False
        self.liquidacion_actual = None
        self.error_message = ""

    @rx.event(background=True)
    async def open_edit_modal(self, id_liquidacion: int):
        """Carga datos de una liquidación para edición."""
        async with self:
            self.error_message = ""
            self.selected_liquidacion_id = id_liquidacion
            
        try:
            servicio = self._obtener_servicio()
            detalles = servicio.obtener_detalle_completo(id_liquidacion)
            
            async with self:
                liq = detalles["liquidacion"]
                self.form_data = {
                    "id_asesor": str(liq["id_asesor"]),
                    "periodo": liq["periodo_liquidacion"],
                    "porcentaje_comision": str(liq["porcentaje_comision"] / 100.0),
                    "observaciones": liq["observaciones_liquidacion"] or "",
                }
                self.existing_discounts = [{
                    "id_descuento": d["id_descuento_asesor"],
                    "tipo": d["tipo_descuento"],
                    "descripcion": d["descripcion_descuento"],
                    "valor_view": format_currency(d["valor_descuento"]),
                } for d in detalles.get("descuentos", [])]
                
                self.existing_bonuses = [{
                    "id_bonificacion": b["id_bonificacion_asesor"],
                    "tipo": b["tipo_bonificacion"],
                    "descripcion": b["descripcion_bonificacion"],
                    "valor_view": format_currency(b["valor_bonificacion"]),
                } for b in detalles.get("bonificaciones", [])]
                
                self.new_discounts = []
                self.new_bonuses = []
                
                # Cargar propiedades históricas asociadas a esta liquidación (con Fallback de Mandato)
                self.advisor_properties = [{
                    "DIRECCION_PROPIEDAD": p.get("direccion") or p.get("DIRECCION_PROPIEDAD") or "N/A",
                    "CANON_ARRENDAMIENTO_VIEW": format_currency(p.get("canon_incluido") or p.get("CANON_INCLUIDO")),
                    "COMISION_PORCENTAJE_VIEW": f"{(p.get('comision_porcentaje_contrato') or 0) / 100.0:.2f}%",
                    "COMISION_MONTO_VIEW": format_currency(p.get('comision_monto_contrato') or 0),
                } for p in detalles.get("contratos", [])]

                self.show_form_modal = True
            
        except Exception as e:
            async with self:
                self.error_message = f"Error cargando edición: {e}"

    @rx.event(background=True)
    async def marcar_como_pagada(self, id_liquidacion: int):
        """Marca una liquidación aprobada como pagada."""
        async with self:
            auth_state = await self.get_state(AuthState)
            usuario = auth_state.user_nombre
        try:
            servicio = self._obtener_servicio()
            servicio.marcar_como_pagada(id_liquidacion, usuario)
            async with self:
                if self.liquidacion_actual and self.liquidacion_actual["id_liquidacion"] == id_liquidacion:
                    self.liquidacion_actual["estado"] = "Pagada"
                self.show_detail_modal = False
            yield rx.toast.success("Liquidación marcada como pagada")
            from src.presentacion_reflex.state.liquidacion_asesores.grid_state import LiquidacionGridState
            yield LiquidacionGridState.load_liquidaciones()
        except Exception as e:
            async with self:
                self.error_message = str(e)

    def set_discount_field(self, name: str, value: Any):
        self.discount_form[name] = value

    @rx.event(background=True)
    async def save_descuento(self, form_data: Dict):
        """Persiste un descuento manual agregado desde el detalle."""
        async with self:
            auth_state = await self.get_state(AuthState)
            usuario = auth_state.user_nombre
            id_liq = self.selected_liquidacion_id

        try:
            servicio = self._obtener_servicio()
            servicio.agregar_descuento(
                id_liq, 
                form_data.get("tipo"), 
                form_data.get("descripcion"), 
                int(form_data.get("valor", 0)), 
                usuario
            )
            async with self:
                self.show_discount_modal = False
            yield rx.toast.success("Descuento agregado")
            yield LiquidacionFormState.open_detail_modal(id_liq)
        except Exception as e:
            async with self:
                self.error_message = str(e)

    def set_show_form_modal(self, value: bool): self.show_form_modal = value
    def set_show_detail_modal(self, value: bool): self.show_detail_modal = value
    def set_show_discount_modal(self, value: bool): self.show_discount_modal = value
    def set_show_annul_modal(self, value: bool): self.show_annul_modal = value
    def set_annul_reason(self, value: str): self.annul_reason = value
    def open_annul_modal(self, id_liq: int):
        self.selected_liquidacion_id = id_liq
        self.annul_reason = ""
        self.show_annul_modal = True

    def set_show_bulk_modal(self, value: bool): 
        self.show_bulk_modal = value

    def open_bulk_modal(self):
        self.show_bulk_modal = True
        self.form_data = {"periodo": datetime.now().strftime("%Y-%m")}
        self.error_message = ""

    @rx.event(background=True)
    async def generar_liquidacion_masiva(self, form_data: Dict):
        """Generación masiva atómica invocando el servicio optimizado."""
        async with self:
            auth_state = await self.get_state(AuthState)
            usuario = auth_state.user_nombre
            periodo = form_data.get("periodo")

        try:
            servicio = self._obtener_servicio()
            stats = servicio.generar_liquidaciones_masivas_optimizado(periodo, usuario)
            
            async with self:
                self.show_bulk_modal = False
            
            yield rx.toast.success(f"Liquidaciones generadas: {stats['creadas']}. Omitidas: {stats['omitidas']}.")
            
            # Recargar la grilla desde el estado correspondiente
            from src.presentacion_reflex.state.liquidacion_asesores.grid_state import LiquidacionGridState
            yield LiquidacionGridState.load_liquidaciones()
            
        except Exception as e:
            async with self:
                self.error_message = f"Error en generación masiva: {e}"
