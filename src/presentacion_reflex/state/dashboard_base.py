import uuid
import reflex as rx

class DashboardBaseState(rx.State):
    """
    Estado base para el dashboard con concurrencia de carga segura.
    Maneja el token de concurrencia y mecanismos de cancelación atómica.
    """
    
    # UI State
    is_loading: bool = False
    error_message: str = ""
    errores_carga: list[str] = []
    
    # Token de concurrencia para evitar race conditions en cargas pesadas
    _concurrency_token: str = ""
    
    def _generate_token(self) -> str:
        """Genera y establece un nuevo token de concurrencia."""
        self._concurrency_token = str(uuid.uuid4())
        return self._concurrency_token
        
    def _is_valid_token(self, token: str) -> bool:
        """Verifica si el token dado sigue siendo el activo."""
        return self._concurrency_token == token
