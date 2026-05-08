import uuid
import hashlib
import json
import logging
from typing import Dict, Any, Optional
import reflex as rx

logger = logging.getLogger(__name__)

class IdempotencyStateMixin:
    """
    Mixin para Estados de Reflex que requieren garantías de idempotencia en el frontend.
    Proporciona generación de llaves y tracking básico de peticiones en vuelo.
    """
    
    # Llave de la petición actual para evitar doble envío accidental en la UI
    current_request_key: str = ""
    is_processing_idempotent: bool = False

    def generate_idempotency_key(self, prefix: str, data: Optional[Dict] = None) -> str:
        """
        Genera una clave de idempotencia determinista o aleatoria.
        
        Args:
            prefix: Prefijo descriptivo para la operación.
            data: Datos de la operación para generar un hash determinista.
                 Si es None, se genera un UUID v4.
        """
        if data:
            # Elite: Serialización determinista (sort_keys=True) para evitar 
            # duplicados por orden de llaves en el JSON.
            serialized = json.dumps(data, sort_keys=True, default=str)
            hash_val = hashlib.sha256(serialized.encode()).hexdigest()
            return f"{prefix}:{hash_val[:32]}"
        
        return f"{prefix}:{str(uuid.uuid4())}"

    def start_idempotent_request(self, key: str):
        """Marca el inicio de una petición idempotente."""
        self.current_request_key = key
        self.is_processing_idempotent = True

    def end_idempotent_request(self):
        """Limpia el estado tras finalizar la petición."""
        self.current_request_key = ""
        self.is_processing_idempotent = False
