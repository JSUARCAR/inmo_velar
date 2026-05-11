import sys
import time
from typing import Any, Dict, List

import reflex as rx

from src.aplicacion.servicios.servicio_alertas import ServicioAlertas
from src.infraestructura.persistencia.database import db_manager


import logging
logger = logging.getLogger(__name__)

class AlertasState(rx.State):
    """
    Estado global para notificaciones y alertas.
    Maneja la campana de notificaciones y la sincronización proactiva.
    """

    notifications: List[Dict[str, Any]] = []
    unread_count: int = 0
    show_list: bool = False
    is_syncing: bool = False

    # Var privada para evitar consultas repetidas
    _last_check_ts: float = 0.0

    def _get_servicio(self) -> ServicioAlertas:
        """Instancia el servicio con el repositorio adecuado."""
        if db_manager.use_postgresql:
            from src.infraestructura.persistencia.repositorio_alerta_postgres import (
                RepositorioAlertaPostgres,
            )

            repo = RepositorioAlertaPostgres(db_manager)
        else:
            from src.infraestructura.persistencia.repositorio_alerta_sqlite import (
                RepositorioAlertaSQLite,
            )

            repo = RepositorioAlertaSQLite(db_manager)

        return ServicioAlertas(db_manager, repo)

    def check_alerts(self):
        """
        Consulta alertas persistidas con guard de 60 segundos.
        Sincroniza proactivamente si es necesario.
        """
        now = time.time()
        if now - self._last_check_ts < 60:
            return

        self._last_check_ts = now
        try:
            servicio = self._get_servicio()

            # 1. Sincronizar (detectar nuevos eventos)
            # Solo sincronizamos si ha pasado mucho tiempo (ej: 1 hora) 
            # para no saturar el servidor en cada navegación
            # Por ahora lo dejamos simplificado
            servicio.sincronizar_alertas(usuario_sistema="sistema")

            # 2. Obtener alertas persistidas pendientes
            items = servicio.obtener_alertas(estado="Pendiente", formato_notificacion=True)
            self.notifications = items
            self.unread_count = len(items)
            logger.info(f"Alertas sincronizadas exitosamente: {len(items)}")
        except Exception as e:
            logger.error(f"Error en check_alerts: {e}", exc_info=True)

    def force_sync(self):
        """Fuerza la sincronización completa."""
        self.is_syncing = True
        yield
        try:
            servicio = self._get_servicio()
            servicio.sincronizar_alertas(usuario_sistema="manual")
            self._last_check_ts = 0.0
            self.check_alerts()
        finally:
            self.is_syncing = False

    def resolver_alerta(self, id_alerta: str):
        """Marca una alerta como resuelta desde la campana."""
        try:
            servicio = self._get_servicio()
            # Asumimos que AuthState tiene el usuario, pero usamos 'sistema' por ahora
            success = servicio.marcar_como_resuelta(
                int(id_alerta), usuario="usuario_ui", accion="Resuelta desde notificaciones"
            )
            if success:
                # Recargar localmente
                self.notifications = [n for n in self.notifications if n["id"] != id_alerta]
                self.unread_count = len(self.notifications)
        except Exception as e:
            logger.error(f"Error resolviendo alerta: {e}", exc_info=True)

    def toggle_list(self):
        self.show_list = not self.show_list

    def close_list(self):
        self.show_list = False

