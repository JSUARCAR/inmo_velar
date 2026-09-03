from typing import Any, Dict, List

import reflex as rx
from src.presentacion_reflex.state.navigation_mixin import NavigationGenerationMixin

from src.aplicacion.servicios.servicio_alertas import ServicioAlertas
from src.infraestructura.persistencia.database import db_manager


import logging

logger = logging.getLogger(__name__)


class AlertasDashboardState(NavigationGenerationMixin):
    """
    Estado para la página dedicada de Gestión de Alertas.
    """

    alertas: List[Dict[str, Any]] = []
    total_alertas: int = 0
    is_loading: bool = False

    # Filtros
    filtro_estado: str = "Pendiente"
    filtro_prioridad: str = "Todas"
    filtro_tipo: str = "Todos"

    # Paginación
    page: int = 1
    page_size: int = 20

    def _get_servicio(self) -> ServicioAlertas:
        from src.infraestructura.persistencia.repositorio_alerta_postgres import (
            RepositorioAlertaPostgres,
        )

        repo = RepositorioAlertaPostgres(db_manager)
        return ServicioAlertas(db_manager, repo)

    def load_alertas(self):
        gen_id = self.start_navigation_generation()
        yield AlertasDashboardState._load_alertas_background(gen_id)

    @rx.event(background=True)
    async def _load_alertas_background(self, gen_id: str):
        async with self:
            if not self.validate_generation(gen_id):
                return
            page = getattr(self, "page", 1)
            page_size = getattr(self, "page_size", 20)
            filtro_estado = getattr(self, "filtro_estado", "Pendiente")
            filtro_prioridad = getattr(self, "filtro_prioridad", "Todas")
            filtro_tipo = getattr(self, "filtro_tipo", "Todos")
            
        try:
            servicio = self._get_servicio()

            estado = filtro_estado if filtro_estado != "Todas" else None
            prioridad = (
                filtro_prioridad if filtro_prioridad != "Todas" else None
            )
            tipo = filtro_tipo if filtro_tipo != "Todos" else None

            offset = max(0, (page - 1) * page_size)

            # Obtener datos persistidos
            alertas = servicio.obtener_alertas(
                estado=estado,
                prioridad=prioridad,
                tipo=tipo,
                limit=page_size,
                offset=offset,
            )

            # Obtener total
            total = servicio.contar_todas(
                estado=estado, prioridad=prioridad, tipo=tipo
            )
            
            async with self:
                if not self.validate_generation(gen_id): return
                self.alertas = alertas
                self.total_alertas = total

        except Exception as e:
            logger.error(f"Error cargando dashboard alertas: {e}", exc_info=True)
            async with self:
                for event in self.trigger_graceful_rollback():
                    yield event
        finally:
            async with self:
                self.end_navigation_generation()

    def set_filtro_estado(self, val: str):
        self.filtro_estado = val
        self.page = 1
        return AlertasDashboardState.load_alertas

    def set_filtro_prioridad(self, val: str):
        self.filtro_prioridad = val
        self.page = 1
        return AlertasDashboardState.load_alertas

    def set_filtro_tipo(self, val: str):
        self.filtro_tipo = val
        self.page = 1
        return AlertasDashboardState.load_alertas

    def set_page(self, page: int):
        self.page = max(1, page)
        return AlertasDashboardState.load_alertas

    def exportar_csv(self):
        """Exporta las alertas actuales a CSV."""
        self.is_loading = True
        yield rx.toast.info("Generando reporte de alertas...", position="bottom-right")
        try:
            servicio = self._get_servicio()

            estado = self.filtro_estado if self.filtro_estado != "Todas" else None
            prioridad = (
                self.filtro_prioridad if self.filtro_prioridad != "Todas" else None
            )
            tipo = self.filtro_tipo if self.filtro_tipo != "Todos" else None

            csv_data = servicio.exportar_alertas_csv(
                estado=estado, prioridad=prioridad, tipo=tipo
            )

            # Codificar con BOM para Excel
            data_bytes = csv_data.encode("utf-8-sig")

            import time

            filename = f"reporte_alertas_{int(time.time())}.csv"

            yield rx.download(data=data_bytes, filename=filename)
            yield rx.toast.success("Descarga iniciada", position="bottom-right")

        except Exception as e:
            logger.error(f"Error exportando alertas: {e}", exc_info=True)
            yield rx.toast.error(f"Error al exportar: {str(e)}")
        finally:
            self.is_loading = False

    def resolver_alerta(self, id_alerta: int):
        """Resuelve alerta desde la tabla."""
        try:
            servicio = self._get_servicio()
            success = servicio.marcar_como_resuelta(
                id_alerta, usuario="admin", accion="Resuelta desde Dashboard"
            )
            if success:
                return AlertasDashboardState.load_alertas
        except Exception as e:
            logger.error(f"Error resolviendo alerta {id_alerta}: {e}", exc_info=True)

    def sincronizar_ahora(self):
        """Dispara el motor de reglas."""
        self.is_loading = True
        yield
        try:
            servicio = self._get_servicio()
            nuevas = servicio.sincronizar_alertas(usuario_sistema="manual_dashboard")
            logger.info(f"Sincronización manual finalizada: {nuevas} nuevas alertas.")
            return AlertasDashboardState.load_alertas
        finally:
            self.is_loading = False
