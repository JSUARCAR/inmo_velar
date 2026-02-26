import sys
import time
from typing import Any, Dict, List

import reflex as rx

from src.aplicacion.servicios.servicio_alertas import ServicioAlertas
from src.infraestructura.persistencia.database import db_manager


class AlertasState(rx.State):
    """
    Estado global para notificaciones y alertas.
    Incluye un guard de tiempo para evitar consultas repetidas
    al navegar entre páginas del mismo layout.
    """

    notifications: List[Dict[str, Any]] = []
    unread_count: int = 0
    show_list: bool = False

    # Var privada: NO se serializa al frontend (prefijo _)
    # Guarda el timestamp de la última consulta exitosa
    _last_check_ts: float = 0.0

    def check_alerts(self):
        """
        Consulta nuevas alertas con guard de 60 segundos.
        Evita queries redundantes al navegar entre páginas.
        """
        now = time.time()
        if now - self._last_check_ts < 60:
            # Menos de 1 minuto desde la última consulta — no recargar
            return
        self._last_check_ts = now
        print("[ALERT_DEBUG] check_alerts CALLED", file=sys.stderr, flush=True)
        try:
            servicio = ServicioAlertas(db_manager)
            items = servicio.obtener_alertas()
            self.notifications = items
            self.unread_count = len(items)
            print(f"[ALERT_DEBUG] check_alerts OK | count={len(items)}", file=sys.stderr, flush=True)
        except Exception as e:
            print(f"[ALERT_DEBUG] check_alerts ERROR: {e}", file=sys.stderr, flush=True)

    def force_check_alerts(self):
        """
        Fuerza una recarga de alertas ignorando el guard.
        Usar cuando el usuario pulsa manualmente el ícono de campana.
        """
        self._last_check_ts = 0.0
        self.check_alerts()

    def toggle_list(self):
        self.show_list = not self.show_list

    def close_list(self):
        self.show_list = False
