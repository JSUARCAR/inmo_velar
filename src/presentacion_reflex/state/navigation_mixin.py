import time
import uuid
import reflex as rx
import logging

logger = logging.getLogger(__name__)

class NavigationGenerationMixin(rx.State):
    \"\"\"
    Mixin para Estados de Reflex que requieren control de concurrencia en navegacion asincrona.
    Evita la corrupcion de estado por race conditions y descarta payloads de paginas abandonadas.
    \"\"\"
    
    current_generation: str = \"\"
    is_loading: bool = False
    
    def start_navigation_generation(self) -> str:
        \"\"\"Inicia una nueva generacion de navegacion y la retorna.\"\"\"
        self.current_generation = str(uuid.uuid4())
        self.is_loading = True
        return self.current_generation
        
    def end_navigation_generation(self):
        self.is_loading = False

    def validate_generation(self, generation_id: str) -> bool:
        \"\"\"
        Valida si el generation_id de una tarea background corresponde al estado actual.
        Si no coincide, significa que el usuario navego fuera y la tarea debe descartarse.
        \"\"\"
        if not self.current_generation:
            return True
            
        is_valid = self.current_generation == generation_id
        if not is_valid:
            logger.warning(f\"[DROP] Mutación caducada (Generación mismatch). Expected: {self.current_generation}, Got: {generation_id}\")
        return is_valid
        
    def trigger_graceful_rollback(self) -> list[rx.event.EventSpec]:
        \"\"\"
        Retorna la secuencia de eventos para redirigir al dashboard y notificar el timeout.
        \"\"\"
        logger.error(\"Fallback trigger: Graceful Rollback a Dashboard.\")
        self.is_loading = False
        return [
            rx.toast(\"Error de conexión. Redirigiendo al Dashboard\", color=\"yellow\"),
            rx.redirect(\"/\")
        ]
