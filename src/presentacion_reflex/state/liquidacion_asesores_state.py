import reflex as rx
from typing import Any, Dict, List, Optional
from datetime import datetime

from src.presentacion_reflex.state.documentos_mixin import DocumentosStateMixin
from src.presentacion_reflex.state.auth_state import AuthState
from .liquidacion_asesores.filtros_state import LiquidacionFiltrosState
from .liquidacion_asesores.grid_state import LiquidacionGridState
from .liquidacion_asesores.form_state import LiquidacionFormState

class LiquidacionAsesoresState(DocumentosStateMixin):
    """
    Estado Agregador para el módulo de Liquidación de Asesores.
    Implementa el estándar de Descomposición Élite para optimizar el performance de Reflex.
    Delega responsabilidades a sub-estados especializados.
    """

    @rx.event(background=True)
    async def on_load(self):
        """Inicialización coordinada del módulo."""
        yield LiquidacionFiltrosState.load_filter_options()
        yield LiquidacionGridState.load_liquidaciones()

    # Delegación de eventos de navegación
    def next_page(self):
        return LiquidacionGridState.next_page()

    def prev_page(self):
        return LiquidacionGridState.prev_page()

    # Delegación de búsqueda y filtros
    def search_liquidaciones(self):
        return LiquidacionGridState.load_liquidaciones()

    # Métodos de compatibilidad para apertura de modales
    def open_create_modal(self):
        return LiquidacionFormState.open_create_modal()

    def close_modal(self):
        return LiquidacionFormState.close_modal()

    @rx.event(background=True)
    async def open_detail_modal(self, id_liquidacion: int):
        """Coordinación de carga de detalles y documentos."""
        async with self:
            self.iniciar_contexto_documental("LIQUIDACION_ASESOR", str(id_liquidacion))
        yield LiquidacionFormState.open_detail_modal(id_liquidacion)

    @rx.event(background=True)
    async def handle_save_form(self, form_data: Dict):
        """Punto de entrada para guardado que refresca la grilla tras éxito."""
        yield LiquidacionFormState.handle_save_form(form_data)
        # El grid debe recargarse tras una operación exitosa
        yield LiquidacionGridState.load_liquidaciones()
