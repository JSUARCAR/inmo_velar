import reflex as rx
from typing import List, Dict, Any, Optional
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
from .filtros_state import LiquidacionFiltrosState

def format_currency(value: Optional[float]) -> str:
    if value is None:
        return "$0"
    return f"${float(value):,.0f}".replace(",", ".")

class LiquidacionGridState(rx.State):
    """Maneja la grilla de datos, paginación y ordenamiento."""
    
    current_page: int = 1
    page_size: int = 25
    total_items: int = 0
    
    liquidaciones: List[Dict[str, Any]] = []
    is_loading: bool = False
    error_message: str = ""
    
    sort_by: str = "periodo_liquidacion"
    sort_order: str = "desc"

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

    @rx.event(background=True)
    async def load_liquidaciones(self):
        async with self:
            self.is_loading = True
            self.error_message = ""
            filtros_state = await self.get_state(LiquidacionFiltrosState)
            
            filtros = {}
            if filtros_state.filter_estado != "Todos":
                filtros["estado"] = filtros_state.filter_estado
            if filtros_state.filter_periodo:
                filtros["periodo"] = filtros_state.filter_periodo
            if filtros_state.filter_asesor:
                for a in filtros_state.asesores_options:
                    if a["texto"] == filtros_state.filter_asesor:
                        filtros["id_asesor"] = int(a["id"])
                        break
            if filtros_state.search_text:
                filtros["search"] = filtros_state.search_text

        try:
            servicio = self._obtener_servicio()
            resultado = servicio.listar_liquidaciones_paginado(
                page=self.current_page,
                page_size=self.page_size,
                filtros=filtros,
                sort_by=self.sort_by,
                sort_order=self.sort_order,
            )

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

    def toggle_sort(self, column: str):
        if self.sort_by == column:
            self.sort_order = "desc" if self.sort_order == "asc" else "asc"
        else:
            self.sort_by = column
            self.sort_order = "desc"
        self.current_page = 1
        return LiquidacionGridState.load_liquidaciones

    def next_page(self):
        self.current_page += 1
        return LiquidacionGridState.load_liquidaciones()

    def prev_page(self):
        self.current_page -= 1
        return LiquidacionGridState.load_liquidaciones()
