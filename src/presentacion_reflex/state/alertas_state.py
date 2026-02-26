import sys
from typing import Any, Dict, List

import reflex as rx

from src.aplicacion.servicios.servicio_alertas import ServicioAlertas
from src.infraestructura.persistencia.database import db_manager


class AlertasState(rx.State):
    """
    Estado global para notificaciones y alertas.
    """

    notifications: List[Dict[str, Any]] = []
    unread_count: int = 0
    show_list: bool = False

    def check_alerts(self):
        """Consulta nuevas alertas (síncrono, sin background task)."""
        print("[ALERT_DEBUG] check_alerts CALLED", file=sys.stderr, flush=True)
        try:
            servicio = ServicioAlertas(db_manager)
            items = servicio.obtener_alertas()
            self.notifications = items
            self.unread_count = len(items)
            print(f"[ALERT_DEBUG] check_alerts OK | count={len(items)}", file=sys.stderr, flush=True)
        except Exception as e:
            print(f"[ALERT_DEBUG] check_alerts ERROR: {e}", file=sys.stderr, flush=True)

    def toggle_list(self):
        self.show_list = not self.show_list

    def close_list(self):
        self.show_list = False
