import logging
import sys
from datetime import datetime
from typing import Any, Dict

# Configuración básica de logging
class StructuredLogger:
    """
    Logger estructurado para la aplicación.
    Proporciona métodos para loguear eventos con contexto.
    """
    
    def __init__(self, name: str = "app"):
        self.logger = logging.getLogger(name)
        if not self.logger.handlers:
            self.logger.setLevel(logging.INFO)
            
            # Formateador simple para consola
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            
            # TODO: Agregar FileHandler para auditoría persistente

    def _format_context(self, context: Dict[str, Any]) -> str:
        if not context:
            return ""
        items = [f"{k}={v}" for k, v in context.items()]
        return " | " + " | ".join(items)

    def info(self, message: str, **context):
        self.logger.info(f"{message}{self._format_context(context)}")

    def error(self, message: str, error: Exception = None, **context):
        if error:
            context["error_type"] = type(error).__name__
            context["error_msg"] = str(error)
        self.logger.error(f"{message}{self._format_context(context)}", exc_info=True)

    def warning(self, message: str, **context):
        self.logger.warning(f"{message}{self._format_context(context)}")

    def debug(self, message: str, **context):
        self.logger.debug(f"{message}{self._format_context(context)}")

# Instancia global
logger = StructuredLogger()
