
import reflex as rx
from typing import List, Dict, Any
from src.aplicacion.servicios.servicio_alertas import ServicioAlertas
from src.infraestructura.persistencia.database import db_manager

class AlertasState(rx.State):
    """
    Estado global para notificaciones y alertas.
    """
    
    notifications: List[Dict[str, Any]] = []
    unread_count: int = 0
    show_list: bool = False
    
    @rx.event(background=True)
    async def check_alerts(self):
        """Consulta nuevas alertas."""
        try:
            servicio = ServicioAlertas(db_manager)
            items = servicio.obtener_alertas()
            
            async with self:
                self.notifications = items
                self.unread_count = len(items)
        except Exception as e:
            pass  # print(f"Error checking alerts: {e}") [OpSec Removed]

    def toggle_list(self):
        self.show_list = not self.show_list

    def close_list(self):
        self.show_list = False
