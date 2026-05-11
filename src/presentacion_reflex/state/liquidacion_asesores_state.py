from datetime import datetime
from typing import Any, Dict, List, Optional

import reflex as rx

from src.aplicacion.servicios.servicio_liquidacion_asesores import (
    ServicioLiquidacionAsesores,
)
from src.infraestructura.persistencia.database import db_manager
from src.infraestructura.persistencia.repositorio_asesor_sqlite import (
    RepositorioAsesorSQLite,
)
from src.infraestructura.persistencia.repositorio_contrato_arrendamiento_sqlite import (
    RepositorioContratoArrendamientoSQLite,
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
from src.presentacion_reflex.state.auth_state import AuthState
from src.presentacion_reflex.state.documentos_mixin import DocumentosStateMixin


def format_currency(value: Optional[float]) -> str:
    if value is None:
        return "$0"
    return f"${float(value):,.0f}".replace(",", ".")


class LiquidacionAsesoresState(DocumentosStateMixin):
    """Estado para gestión de liquidaciones de asesores.
    Maneja paginación, filtros, CRUD, state machine y descuentos.
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
    sort_by: str = "periodo"
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
    descuentos_actuales: List[Dict[str, Any]] = []
    bonificaciones_actuales: List[Dict[str, Any]] = []

    # Helper items (temporary) - for create/edit mode
    existing_discounts: List[Dict[str, Any]] = []
    existing_bonuses: List[Dict[str, Any]] = []
    new_discounts: List[Dict[str, Any]] = []
    new_bonuses: List[Dict[str, Any]] = []
    temp_discount: Dict[str, Any] = {"tipo": "Otros", "descripcion": "", "valor": ""}
    temp_bonus: Dict[str, Any] = {"tipo": "Bono", "descripcion": "", "valor": ""}
    advisor_properties: List[Dict[str, Any]] = []

    def set_form_field(self, name: str, value: Any):
        """Actualiza un campo del formulario."""
        self.form_data[name] = value

        # Si cambia el asesor, cargar sus propiedades y su porcentaje de comisión
        if name == "id_asesor" and value:
            try:
                # 1. Buscar el porcentaje de comisión del asesor seleccionado
                id_str = str(value)
                for asesor in self.asesores_options:
                    if asesor["id"] == id_str:
                        # Asignar automáticamente el porcentaje al formulario
                        pct = asesor.get("comision_porcentaje", 5.0)
                        self.form_data["porcentaje_comision"] = str(pct)
                        break

                # 2. Disparamos el evento de carga de propiedades en background
                return LiquidacionAsesoresState.fetch_advisor_properties(int(value))
            except Exception:
                pass

    def set_discount_field(self, name: str, value: Any):
        """Actualiza un campo del formulario de descuento."""
        self.discount_form[name] = value

    def close_discount_modal(self):
        """Cierra el modal de descuento."""
        self.show_discount_modal = False
        self.discount_form = {}
        self.error_message = ""

    @rx.event(background=True)
    async def save_descuento(self, form_data: Dict):
        """Guarda un nuevo descuento para una liquidación existente."""
        async with self:
            self.is_loading = True
            self.error_message = ""
            auth_state = await self.get_state(AuthState)
            usuario = auth_state.user_nombre

        try:
            repo_descuento = RepositorioDescuentoAsesor(db_manager)
            servicio = ServicioLiquidacionAsesores(None, repo_descuento, None)

            tipo = form_data.get("tipo")
            descripcion = form_data.get("descripcion")
            valor = int(form_data.get("valor", 0))

            if not tipo or not descripcion or valor <= 0:
                async with self:
                    self.error_message = "Todos los campos son obligatorios y valor > 0"
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

            yield rx.toast.success("Descuento agregado correctamente")
            yield LiquidacionAsesoresState.open_detail_modal(
                self.selected_liquidacion_id
            )

        except Exception as e:
            async with self:
                self.error_message = f"Error al guardar descuento: {e}"
                self.is_loading = False

    def set_temp_bonus_field(self, name: str, value: Any):
        self.temp_bonus[name] = value

    def add_temp_bonus(self):
        if self.temp_bonus["descripcion"] and self.temp_bonus["valor"]:
            self.new_bonuses.append(
                {
                    "tipo": self.temp_bonus["tipo"],
                    "descripcion": self.temp_bonus["descripcion"],
                    "valor": self.temp_bonus["valor"],
                }
            )
            self.temp_bonus = {"tipo": "Bono", "descripcion": "", "valor": ""}

    def remove_temp_bonus(self, item: Dict):
        self.new_bonuses.remove(item)

    def set_temp_discount_field(self, name: str, value: Any):
        self.temp_discount[name] = value

    def add_temp_discount(self):
        if self.temp_discount["descripcion"] and self.temp_discount["valor"]:
            self.new_discounts.append(
                {
                    "tipo": self.temp_discount["tipo"],
                    "descripcion": self.temp_discount["descripcion"],
                    "valor": self.temp_discount["valor"],
                }
            )
            self.temp_discount = {"tipo": "Otros", "descripcion": "", "valor": ""}

    def remove_temp_discount(self, item: Dict):
        self.new_discounts.remove(item)

    @rx.event(background=True)
    async def eliminar_descuento(self, id_descuento: int):
        """Elimina un descuento guardado en la base de datos."""
        async with self:
            self.is_loading = True
            self.error_message = ""
            auth_state = await self.get_state(AuthState)
            usuario = auth_state.user_nombre

        try:
            repo_liquidacion = RepositorioLiquidacionAsesor(db_manager)
            repo_descuento = RepositorioDescuentoAsesor(db_manager)
            servicio = ServicioLiquidacionAsesores(
                repo_liquidacion=repo_liquidacion,
                repo_descuento=repo_descuento,
                repo_pago=RepositorioPagoAsesor(db_manager),
            )
            
            servicio.eliminar_descuento(id_descuento, usuario)
            
            yield rx.toast.success("Descuento eliminado")
            # Recargar el modal
            yield LiquidacionAsesoresState.open_edit_modal(self.selected_liquidacion_id)
        except Exception as e:
            async with self:
                self.error_message = f"Error al eliminar descuento: {e}"
                self.is_loading = False

    @rx.event(background=True)
    async def eliminar_bonificacion(self, id_bonificacion: int):
        """Elimina una bonificación guardada en la base de datos."""
        async with self:
            self.is_loading = True
            self.error_message = ""
            auth_state = await self.get_state(AuthState)
            usuario = auth_state.user_nombre

        try:
            repo_liquidacion = RepositorioLiquidacionAsesor(db_manager)
            repo_bonificacion = RepositorioBonificacionAsesor(db_manager)
            servicio = ServicioLiquidacionAsesores(
                repo_liquidacion=repo_liquidacion,
                repo_descuento=RepositorioDescuentoAsesor(db_manager),
                repo_pago=RepositorioPagoAsesor(db_manager),
                repo_bonificacion=repo_bonificacion,
            )
            
            servicio.eliminar_bonificacion(id_bonificacion, usuario)
            
            yield rx.toast.success("Bonificación eliminada")
            # Recargar el modal
            yield LiquidacionAsesoresState.open_edit_modal(self.selected_liquidacion_id)
        except Exception as e:
            async with self:
                self.error_message = f"Error al eliminar bonificación: {e}"
                self.is_loading = False

    @rx.event(background=True)
    async def on_load(self):
        """Carga inicial al montar la página."""
        async with self:
            self.is_loading = True

        try:
            yield LiquidacionAsesoresState.load_filter_options()
            yield LiquidacionAsesoresState.load_liquidaciones()
        except Exception:
            pass
        finally:
            async with self:
                self.is_loading = False

    @rx.event(background=True)
    async def load_filter_options(self):
        """Carga opciones para filtros (asesores, períodos)."""
        try:
            repo_asesor = RepositorioAsesorSQLite(db_manager)
            asesores_entidades = repo_asesor.listar_activos()

            asesores = []
            for a in asesores_entidades:
                asesores.append(
                    {
                        "id": str(a.id_asesor),
                        "texto": a.nombre_completo,
                        "comision_porcentaje": a.comision_porcentaje_arriendo
                        if a.comision_porcentaje_arriendo is not None
                        else 5.0,
                    }
                )

            asesores_select = [a["texto"] for a in asesores]

            from datetime import datetime

            from dateutil.relativedelta import relativedelta

            periodos = []
            fecha_actual = datetime.now()
            for i in range(24):
                fecha = fecha_actual - relativedelta(months=i)
                periodos.append(fecha.strftime("%Y-%m"))

            async with self:
                self.asesores_options = asesores
                self.asesores_select_options = asesores_select
                self.periodo_options = periodos
        except Exception as e:
            async with self:
                self.error_message = f"Error al cargar filtros: {str(e)}"

    @rx.event(background=True)
    async def fetch_advisor_properties(self, id_asesor: int):
        """Carga las propiedades/contratos activos para visualización."""
        try:
            repo_liquidacion = RepositorioLiquidacionAsesor(db_manager)
            repo_descuento = RepositorioDescuentoAsesor(db_manager)
            repo_pago = RepositorioPagoAsesor(db_manager)
            repo_contrato = RepositorioContratoArrendamientoSQLite(db_manager)

            servicio = ServicioLiquidacionAsesores(
                repo_liquidacion=repo_liquidacion,
                repo_descuento=repo_descuento,
                repo_pago=repo_pago,
                repo_contrato_arrendamiento=repo_contrato,
            )

            props = servicio.obtener_contratos_activos_asesor(id_asesor)

            props_formatted = []
            for p in props:
                props_formatted.append(
                    {
                        "DIRECCION_PROPIEDAD": p["direccion"],
                        "CANON_ARRENDAMIENTO": p["canon"],
                        "CANON_ARRENDAMIENTO_VIEW": format_currency(p["canon"]),
                        "ID_CONTRATO_A": p["id_contrato"],
                    }
                )

            async with self:
                self.advisor_properties = props_formatted
        except Exception:
            async with self:
                self.advisor_properties = []

    @rx.event(background=True)
    async def load_liquidaciones(self):
        """Carga liquidaciones con filtros y paginación."""
        async with self:
            self.is_loading = True
            self.error_message = ""

        try:
            repo_liquidacion = RepositorioLiquidacionAsesor(db_manager)
            repo_descuento = RepositorioDescuentoAsesor(db_manager)
            repo_pago = RepositorioPagoAsesor(db_manager)

            servicio = ServicioLiquidacionAsesores(
                repo_liquidacion=repo_liquidacion,
                repo_descuento=repo_descuento,
                repo_pago=repo_pago,
            )

            filtros = {}
            if self.filter_estado and self.filter_estado != "Todos":
                filtros["estado"] = self.filter_estado
            if self.filter_periodo:
                filtros["periodo"] = self.filter_periodo
            if self.filter_asesor:
                for asesor in self.asesores_options:
                    if asesor["texto"] == self.filter_asesor:
                        filtros["id_asesor"] = int(asesor["id"])
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

            liquidaciones_list = [
                {
                    "id_liquidacion": liq.id_liquidacion_asesor,
                    "periodo": liq.periodo_liquidacion,
                    "asesor": liq.nombre_asesor
                    if hasattr(liq, "nombre_asesor")
                    else "N/A",
                    "id_asesor": liq.id_asesor,
                    "canon_liquidado": liq.canon_arrendamiento_liquidado,
                    "canon_liquidado_view": format_currency(
                        liq.canon_arrendamiento_liquidado
                    ),
                    "porcentaje": liq.porcentaje_comision / 100.0,
                    "comision_bruta": liq.comision_bruta,
                    "comision_bruta_view": format_currency(liq.comision_bruta),
                    "total_descuentos": liq.total_descuentos,
                    "total_descuentos_view": format_currency(liq.total_descuentos),
                    "total_bonificaciones": getattr(liq, "total_bonificaciones", 0),
                    "total_bonificaciones_view": format_currency(
                        getattr(liq, "total_bonificaciones", 0)
                    ),
                    "valor_neto": liq.valor_neto_asesor,
                    "valor_neto_view": format_currency(liq.valor_neto_asesor),
                    "estado": liq.estado_liquidacion,
                    "fecha_creacion": liq.fecha_creacion,
                    "fecha_aprobacion": liq.fecha_aprobacion,
                    "observaciones": liq.observaciones_liquidacion or "",
                }
                for liq in resultado["items"]
            ]

            async with self:
                self.liquidaciones = liquidaciones_list
                self.total_items = resultado["total"]
                self.is_loading = False
        except Exception as e:
            async with self:
                self.error_message = f"Error al cargar liquidaciones: {str(e)}"
                self.liquidaciones = []
                self.total_items = 0
                self.is_loading = False

    @rx.event(background=True)
    async def limpiar_filtros(self):
        """Limpia todos los filtros y recarga."""
        async with self:
            self.search_text = ""
            self.filter_estado = "Todos"
            self.filter_periodo = ""
            self.filter_asesor = ""
        yield LiquidacionAsesoresState.load_liquidaciones

    def next_page(self):
        if self.current_page * self.page_size < self.total_items:
            self.current_page += 1
            return LiquidacionAsesoresState.load_liquidaciones

    def prev_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            return LiquidacionAsesoresState.load_liquidaciones

    def set_page_size(self, size: str):
        self.page_size = int(size)
        self.current_page = 1
        return LiquidacionAsesoresState.load_liquidaciones

    def set_search(self, value: str):
        self.search_text = value

    def toggle_sort(self, column: str):
        if self.sort_by == column:
            self.sort_order = "asc" if self.sort_order == "desc" else "desc"
        else:
            self.sort_by = column
            self.sort_order = "desc"
        self.current_page = 1
        return LiquidacionAsesoresState.load_liquidaciones

    def search_liquidaciones(self):
        self.current_page = 1
        return LiquidacionAsesoresState.load_liquidaciones

    def handle_search_key_down(self, key: str):
        if key == "Enter":
            return self.search_liquidaciones()

    def set_filter_estado(self, value: str):
        self.filter_estado = value
        self.current_page = 1
        return LiquidacionAsesoresState.load_liquidaciones

    def set_filter_periodo(self, value: str):
        self.filter_periodo = value
        self.current_page = 1
        return LiquidacionAsesoresState.load_liquidaciones

    def set_filter_asesor(self, value: str):
        self.filter_asesor = value
        self.current_page = 1
        return LiquidacionAsesoresState.load_liquidaciones

    def open_create_modal(self):
        """Abre modal para crear nueva liquidación."""
        self.selected_liquidacion_id = 0
        self.show_form_modal = True
        self.show_detail_modal = False
        self.form_data = {
            "id_asesor": "",
            "periodo": datetime.now().strftime("%Y-%m"),
            "contratos": [],
            "porcentaje_comision": "5.0",
            "observaciones": "",
        }
        self.advisor_properties = []
        self.new_discounts = []
        self.new_bonuses = []
        self.temp_discount = {"tipo": "Otros", "descripcion": "", "valor": ""}
        self.temp_bonus = {"tipo": "Bono", "descripcion": "", "valor": ""}
        self.error_message = ""

    @rx.event(background=True)
    async def handle_save_form(self, form_data: Dict):
        """Unified handler for saving form (create or edit)."""
        async with self:
            auth_state = await self.get_state(AuthState)
            usuario_sistema = auth_state.user_nombre

        if self.selected_liquidacion_id > 0:
            async with self:
                self.is_loading = True
                self.error_message = ""

            try:
                repo_liquidacion = RepositorioLiquidacionAsesor(db_manager)
                repo_descuento = RepositorioDescuentoAsesor(db_manager)
                repo_pago = RepositorioPagoAsesor(db_manager)
                repo_bonificacion = RepositorioBonificacionAsesor(db_manager)

                servicio = ServicioLiquidacionAsesores(
                    repo_liquidacion=repo_liquidacion,
                    repo_descuento=repo_descuento,
                    repo_pago=repo_pago,
                    repo_bonificacion=repo_bonificacion,
                )

                datos_actualizar = {}
                porcentaje_str = form_data.get("porcentaje_comision")
                if porcentaje_str:
                    try:
                        porcentaje_decimal = float(porcentaje_str)
                        basis_points = int(porcentaje_decimal * 100)
                        datos_actualizar["porcentaje_comision"] = basis_points
                    except ValueError:
                        pass

                observaciones = form_data.get("observaciones")
                if observaciones is not None:
                    datos_actualizar["observaciones_liquidacion"] = observaciones

                if datos_actualizar:
                    servicio.actualizar_liquidacion(
                        self.selected_liquidacion_id, datos_actualizar, usuario_sistema
                    )

                for descuento in self.new_discounts:
                    try:
                        servicio.agregar_descuento(
                            id_liquidacion=self.selected_liquidacion_id,
                            tipo=descuento["tipo"],
                            descripcion=descuento["descripcion"],
                            valor=int(descuento["valor"]),
                            usuario=usuario_sistema,
                        )
                    except Exception:
                        pass

                for bonificacion in self.new_bonuses:
                    try:
                        servicio.agregar_bonificacion(
                            id_liquidacion=self.selected_liquidacion_id,
                            tipo=bonificacion["tipo"],
                            descripcion=bonificacion["descripcion"],
                            valor=int(bonificacion["valor"]),
                            usuario=usuario_sistema,
                        )
                    except Exception:
                        pass

                async with self:
                    self.show_form_modal = False
                    self.is_loading = False
                    self.form_data = {}
                    self.new_discounts = []
                    self.new_bonuses = []
                    self.selected_liquidacion_id = 0

                yield rx.toast.success("Liquidación actualizada exitosamente")
                yield LiquidacionAsesoresState.load_liquidaciones()

            except Exception as e:
                async with self:
                    self.error_message = f"Error al actualizar liquidación: {str(e)}"
                    self.is_loading = False
                yield rx.toast.error(f"Error al actualizar: {str(e)}")
        else:
            yield LiquidacionAsesoresState.crear_liquidacion(form_data)

    @rx.event(background=True)
    async def crear_liquidacion(self, form_data: Dict):
        """Crea una nueva liquidación."""
        async with self:
            self.is_loading = True
            self.error_message = ""
            auth_state = await self.get_state(AuthState)
            usuario_sistema = auth_state.user_nombre

        try:
            repo_liquidacion = RepositorioLiquidacionAsesor(db_manager)
            repo_descuento = RepositorioDescuentoAsesor(db_manager)
            repo_pago = RepositorioPagoAsesor(db_manager)
            repo_bonificacion = RepositorioBonificacionAsesor(db_manager)
            repo_contrato = RepositorioContratoArrendamientoSQLite(db_manager)

            servicio = ServicioLiquidacionAsesores(
                repo_liquidacion=repo_liquidacion,
                repo_descuento=repo_descuento,
                repo_pago=repo_pago,
                repo_bonificacion=repo_bonificacion,
                repo_contrato_arrendamiento=repo_contrato,
            )

            id_asesor_str = form_data.get("id_asesor")
            if not id_asesor_str:
                async with self:
                    self.error_message = "Debe seleccionar un asesor"
                    self.is_loading = False
                return

            id_asesor = int(id_asesor_str)
            periodo = form_data.get("periodo")
            porcentaje_str = form_data.get("porcentaje_comision", "5.0")
            try:
                porcentaje_decimal = float(porcentaje_str)
            except ValueError:
                porcentaje_decimal = 5.0

            # Desacoplado: usar el servicio para obtener contratos
            contratos_activos = servicio.obtener_contratos_activos_asesor(id_asesor)
            contratos = [
                {"id": c["id_contrato"], "canon": c["canon"]}
                for c in contratos_activos
            ]

            if not contratos:
                async with self:
                    self.error_message = "El asesor seleccionado no tiene contratos activos."
                    self.is_loading = False
                return

            observaciones = form_data.get("observaciones", "")
            pct_basis_points = int(porcentaje_decimal * 100)
            total_bonificaciones = sum(int(b.get("valor", 0)) for b in self.new_bonuses)

            liquidacion = servicio.generar_liquidacion_multi_contrato(
                id_asesor=id_asesor,
                periodo=periodo,
                contratos_lista=contratos,
                porcentaje_comision=pct_basis_points,
                total_bonificaciones=total_bonificaciones,
                datos_adicionales={"observaciones": observaciones},
                usuario=usuario_sistema,
            )

            for descuento in self.new_discounts:
                try:
                    servicio.agregar_descuento(
                        id_liquidacion=liquidacion.id_liquidacion_asesor,
                        tipo=descuento["tipo"],
                        descripcion=descuento["descripcion"],
                        valor=int(descuento["valor"]),
                        usuario=usuario_sistema,
                    )
                except Exception:
                    pass

            for bonificacion in self.new_bonuses:
                try:
                    servicio.agregar_bonificacion(
                        id_liquidacion=liquidacion.id_liquidacion_asesor,
                        tipo=bonificacion["tipo"],
                        descripcion=bonificacion["descripcion"],
                        valor=int(bonificacion["valor"]),
                        usuario=usuario_sistema,
                    )
                except Exception:
                    pass

            async with self:
                self.show_form_modal = False
                self.is_loading = False
                self.form_data = {}
                self.new_discounts = []
                self.new_bonuses = []
                self.advisor_properties = []

            yield rx.toast.success("Liquidación creada exitosamente")
            yield LiquidacionAsesoresState.load_liquidaciones()

        except Exception as e:
            async with self:
                self.error_message = f"Error al crear liquidación: {str(e)}"
                self.is_loading = False
            yield rx.toast.error(f"Error al crear liquidación: {str(e)}")

    @rx.event(background=True)
    async def open_detail_modal(self, id_liquidacion: int):
        """Abre modal de detalles de liquidación."""
        async with self:
            self.is_loading = True
            self.error_message = ""
            self.current_entidad_tipo = "LIQUIDACION_ASESOR"
            self.current_entidad_id = str(id_liquidacion)
            self.cargar_documentos()

        try:
            repo_liquidacion = RepositorioLiquidacionAsesor(db_manager)
            repo_descuento = RepositorioDescuentoAsesor(db_manager)
            repo_pago = RepositorioPagoAsesor(db_manager)

            servicio = ServicioLiquidacionAsesores(
                repo_liquidacion=repo_liquidacion,
                repo_descuento=repo_descuento,
                repo_pago=repo_pago,
            )

            detalles = servicio.obtener_detalle_completo(id_liquidacion)
            if not detalles or "liquidacion" not in detalles:
                async with self:
                    self.error_message = "Liquidación no encontrada"
                    self.is_loading = False
                return

            liq_data = detalles["liquidacion"]
            descuentos = detalles.get("descuentos", [])
            bonificaciones = detalles.get("bonificaciones", [])
            contratos_data = detalles.get("contratos", [])

            async with self:
                self.liquidacion_actual = {
                    "id_liquidacion": liq_data["id_liquidacion_asesor"],
                    "periodo": liq_data["periodo_liquidacion"],
                    "asesor": liq_data.get("nombre_asesor", "N/A"),
                    "canon_liquidado": liq_data["canon_arrendamiento_liquidado"],
                    "canon_liquidado_view": format_currency(
                        liq_data["canon_arrendamiento_liquidado"]
                    ),
                    "porcentaje": liq_data["porcentaje_comision"] / 100.0,
                    "comision_bruta": liq_data["comision_bruta"],
                    "comision_bruta_view": format_currency(liq_data["comision_bruta"]),
                    "total_descuentos": liq_data["total_descuentos"],
                    "total_descuentos_view": format_currency(
                        liq_data["total_descuentos"]
                    ),
                    "total_bonificaciones": liq_data.get("total_bonificaciones", 0),
                    "total_bonificaciones_view": format_currency(
                        liq_data.get("total_bonificaciones", 0)
                    ),
                    "valor_neto": liq_data["valor_neto_asesor"],
                    "valor_neto_view": format_currency(liq_data["valor_neto_asesor"]),
                    "estado": liq_data["estado_liquidacion"],
                    "observaciones": liq_data["observaciones_liquidacion"] or "",
                }
                self.descuentos_actuales = [
                    {
                        "id_descuento": d["id_descuento_asesor"],
                        "tipo": d["tipo_descuento"],
                        "descripcion": d["descripcion_descuento"],
                        "valor": d["valor_descuento"],
                        "valor_view": format_currency(d["valor_descuento"]),
                    }
                    for d in descuentos
                ]
                self.bonificaciones_actuales = [
                    {
                        "id_bonificacion": b["id_bonificacion_asesor"],
                        "tipo": b["tipo_bonificacion"],
                        "descripcion": b["descripcion_bonificacion"],
                        "valor": b["valor_bonificacion"],
                        "valor_view": format_currency(b["valor_bonificacion"]),
                    }
                    for b in bonificaciones
                ]

                self.advisor_properties = [
                    {
                        "DIRECCION_PROPIEDAD": c.get("direccion_propiedad")
                        or c.get("direccion", "N/A"),
                        "CANON_ARRENDAMIENTO": c.get("canon_arrendamiento")
                        or c.get("canon_incluido", 0),
                        "CANON_ARRENDAMIENTO_VIEW": format_currency(
                            c.get("canon_arrendamiento") or c.get("canon_incluido", 0)
                        ),
                        "ID_CONTRATO_A": c.get("id_contrato")
                        or c.get("id_contrato_a"),
                    }
                    for c in contratos_data
                ]

                self.show_detail_modal = True
                self.show_form_modal = False
                self.is_loading = False
        except Exception as e:
            async with self:
                self.error_message = f"Error al cargar detalles: {str(e)}"
                self.is_loading = False

    def close_modal(self):
        self.show_form_modal = False
        self.show_detail_modal = False
        self.show_discount_modal = False
        self.liquidacion_actual = None
        self.form_data = {}
        self.error_message = ""
        self.existing_discounts = []
        self.existing_bonuses = []
        self.new_discounts = []
        self.new_bonuses = []
        self.selected_liquidacion_id = 0

    @rx.event(background=True)
    async def generar_liquidacion_masiva(self, form_data: Dict):
        """Genera liquidaciones para todos los asesores activos."""
        async with self:
            self.is_loading = True
            self.error_message = ""
            auth_state = await self.get_state(AuthState)
            usuario_sistema = auth_state.user_nombre

        try:
            periodo = form_data.get("periodo")
            if not periodo:
                raise ValueError("Debe seleccionar un período")

            # Inicializar repositorios y servicios
            repo_liquidacion = RepositorioLiquidacionAsesor(db_manager)
            repo_descuento = RepositorioDescuentoAsesor(db_manager)
            repo_pago = RepositorioPagoAsesor(db_manager)
            repo_contrato = RepositorioContratoArrendamientoSQLite(db_manager)
            repo_asesor = RepositorioAsesorSQLite(db_manager)

            servicio = ServicioLiquidacionAsesores(
                repo_liquidacion=repo_liquidacion,
                repo_descuento=repo_descuento,
                repo_pago=repo_pago,
                repo_contrato_arrendamiento=repo_contrato,
                repo_asesor=repo_asesor,
            )

            # LLAMADA OPTIMIZADA (Fase 3)
            stats = servicio.generar_liquidaciones_masivas_optimizado(
                periodo=periodo, usuario=usuario_sistema
            )

            async with self:
                self.show_bulk_modal = False
                self.is_loading = False

            yield rx.toast.success(
                f"Proceso completado. Creadas: {stats['creadas']}, Omitidas: {stats['omitidas']}, Errores: {stats['errores']}",
                duration=5000,
            )

            yield LiquidacionAsesoresState.load_liquidaciones()

        except Exception as e:
            async with self:
                self.error_message = f"Error en proceso masivo: {str(e)}"
                self.is_loading = False
            yield rx.toast.error(f"Error crítico: {str(e)}")

    @rx.event(background=True)
    async def open_edit_modal(self, id_liquidacion: int):
        async with self:
            self.is_loading = True
            self.error_message = ""

        try:
            repo_liquidacion = RepositorioLiquidacionAsesor(db_manager)
            repo_descuento = RepositorioDescuentoAsesor(db_manager)
            repo_pago = RepositorioPagoAsesor(db_manager)

            servicio = ServicioLiquidacionAsesores(
                repo_liquidacion=repo_liquidacion,
                repo_descuento=repo_descuento,
                repo_pago=repo_pago,
            )

            detalles = servicio.obtener_detalle_completo(id_liquidacion)
            if not detalles or "liquidacion" not in detalles:
                raise ValueError("No se encontró la liquidación")

            liq = detalles["liquidacion"]
            contratos_data = detalles.get("contratos", [])

            async with self:
                self.advisor_properties = [
                    {
                        "DIRECCION_PROPIEDAD": c.get("direccion_propiedad")
                        or c.get("direccion", "N/A"),
                        "CANON_ARRENDAMIENTO": c.get("canon_arrendamiento")
                        or c.get("canon_incluido", 0),
                        "ID_CONTRATO_A": c.get("id_contrato")
                        or c.get("id_contrato_a"),
                    }
                    for c in contratos_data
                ]
                self.form_data = {
                    "id_asesor": str(liq["id_asesor"]),
                    "periodo": liq["periodo_liquidacion"],
                    "porcentaje_comision": str(liq["porcentaje_comision"]),
                    "observaciones": liq["observaciones_liquidacion"] or "",
                }
                self.existing_discounts = [
                    {
                        "id_descuento": d.get("id_descuento_asesor"),
                        "tipo": d.get("tipo_descuento"),
                        "descripcion": d.get("descripcion_descuento"),
                        "valor": d.get("valor_descuento"),
                        "valor_view": format_currency(d.get("valor_descuento")),
                    }
                    for d in detalles.get("descuentos", [])
                ]
                self.existing_bonuses = [
                    {
                        "id_bonificacion": b.get("id_bonificacion_asesor"),
                        "tipo": b.get("tipo_bonificacion"),
                        "descripcion": b.get("descripcion_bonificacion"),
                        "valor": b.get("valor_bonificacion"),
                        "valor_view": format_currency(b.get("valor_bonificacion")),
                    }
                    for b in detalles.get("bonificaciones", [])
                ]
                self.new_discounts = []
                self.new_bonuses = []
                self.selected_liquidacion_id = id_liquidacion
                self.is_loading = False
                self.show_form_modal = True
        except Exception as e:
            async with self:
                self.error_message = f"Error al cargar liquidación: {str(e)}"
                self.is_loading = False

    @rx.event(background=True)
    async def aprobar_liquidacion(self, id_liquidacion: int):
        async with self:
            self.is_loading = True
            self.error_message = ""
            auth_state = await self.get_state(AuthState)
            usuario_sistema = auth_state.user_nombre

        try:
            repo_liquidacion = RepositorioLiquidacionAsesor(db_manager)
            servicio = ServicioLiquidacionAsesores(repo_liquidacion=repo_liquidacion)
            servicio.aprobar_liquidacion(id_liquidacion, usuario_sistema)

            async with self:
                self.is_loading = False
                self.show_detail_modal = False
            yield rx.toast.success("Liquidación aprobada correctamente")
            yield LiquidacionAsesoresState.load_liquidaciones()
        except Exception as e:
            async with self:
                self.error_message = f"Error al aprobar: {str(e)}"
                self.is_loading = False
            yield rx.toast.error(f"Error: {str(e)}")

    @rx.event(background=True)
    async def marcar_como_pagada(self, id_liquidacion: int):
        async with self:
            self.is_loading = True
            self.error_message = ""
            auth_state = await self.get_state(AuthState)
            usuario_sistema = auth_state.user_nombre

        try:
            repo_liquidacion = RepositorioLiquidacionAsesor(db_manager)
            repo_pago = RepositorioPagoAsesor(db_manager)
            servicio = ServicioLiquidacionAsesores(
                repo_liquidacion=repo_liquidacion, repo_pago=repo_pago
            )
            servicio.registrar_pago(
                id_liquidacion=id_liquidacion,
                metodo_pago="Transferencia",
                referencia_pago=f"PAGO-{id_liquidacion}-{datetime.now().strftime('%Y%m%d')}",
                fecha_pago=datetime.now().strftime("%Y-%m-%d"),
                usuario=usuario_sistema,
            )
            async with self:
                self.is_loading = False
                self.show_detail_modal = False
            yield rx.toast.success("Pago registrado correctamente")
            yield LiquidacionAsesoresState.load_liquidaciones()
        except Exception as e:
            async with self:
                self.error_message = f"Error al registrar pago: {str(e)}"
                self.is_loading = False
            yield rx.toast.error(f"Error: {str(e)}")

    @rx.event(background=True)
    async def anular_liquidacion(self, id_liquidacion: int, motivo: str):
        async with self:
            self.is_loading = True
            self.error_message = ""
            auth_state = await self.get_state(AuthState)
            usuario_sistema = auth_state.user_nombre

        try:
            repo_liquidacion = RepositorioLiquidacionAsesor(db_manager)
            servicio = ServicioLiquidacionAsesores(repo_liquidacion=repo_liquidacion)
            servicio.anular_liquidacion(id_liquidacion, motivo, usuario_sistema)
            async with self:
                self.is_loading = False
                self.show_annul_modal = False
                self.show_detail_modal = False
            yield rx.toast.success("Liquidación anulada correctamente")
            yield LiquidacionAsesoresState.load_liquidaciones()
        except Exception as e:
            async with self:
                self.error_message = f"Error al anular: {str(e)}"
                self.is_loading = False
            yield rx.toast.error(f"Error: {str(e)}")

    def set_show_form_modal(self, value: bool): self.show_form_modal = value
    def set_show_detail_modal(self, value: bool): self.show_detail_modal = value
    def set_show_discount_modal(self, value: bool): self.show_discount_modal = value
    def set_show_bulk_modal(self, value: bool): self.show_bulk_modal = value
    def close_form_modal(self): self.close_modal()
    def open_annul_modal(self, id_liq: int): self.selected_annul_id = id_liq; self.annul_reason = ""; self.show_annul_modal = True
    def close_annul_modal(self): self.show_annul_modal = False; self.annul_reason = ""; self.selected_annul_id = 0
    def set_annul_reason(self, value: str): self.annul_reason = value
    
    def confirm_annulment(self):
        if self.selected_annul_id:
            return LiquidacionAsesoresState.anular_liquidacion(self.selected_annul_id, self.annul_reason)

    def open_bulk_modal(self): self.show_bulk_modal = True; self.form_data["periodo"] = datetime.now().strftime("%Y-%m"); self.error_message = ""
    def close_bulk_modal(self): self.show_bulk_modal = False
