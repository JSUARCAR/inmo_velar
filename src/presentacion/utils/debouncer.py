"""
Debouncer para InmoVelar Web.

Utilidad para reducir llamadas repetitivas en eventos frecuentes
como búsquedas en tiempo real.

Autor: InmoVelar Dev Team
Fecha: 2025-12-29
"""

import threading
from typing import Callable, Any, Optional
import logging

logger = logging.getLogger(__name__)


class Debouncer:
    """
    Debounce de eventos con delay configurable.
    
    Espera N ms después del último evento antes de ejecutar callback.
    Útil para búsquedas, validaciones, etc.
    
    Example:
        # Crear debouncer para búsqueda
        search_debouncer = Debouncer(
            delay_ms=500,
            callback=self.cargar_datos
        )
        
        # En on_change del TextField
        def on_search_change(e):
            search_debouncer()  # Ejecutará después de 500ms
    """
    
    def __init__(
        self, 
        delay_ms: int, 
        callback: Callable,
        name: Optional[str] = None
    ):
        """
        Inicializa el debouncer.
        
        Args:
            delay_ms: Delay en milisegundos
            callback: Función a ejecutar
            name: Nombre descriptivo (para logging)
        """
        if delay_ms < 0:
            raise ValueError("delay_ms debe ser >= 0")
        
        self.delay_ms = delay_ms
        self.callback = callback
        self.name = name or f"Debouncer-{id(self)}"
        
        self._timer: Optional[threading.Timer] = None
        self._lock = threading.Lock()
        self._call_count = 0
        self._execute_count = 0
        
        logger.debug(f"Debouncer '{self.name}' creado (delay={delay_ms}ms)")
    
    def __call__(self, *args, **kwargs) -> None:
        """
        Llama al debouncer con argumentos.
        
        Args:
            *args: Argumentos posicionales para callback
            **kwargs: Argumentos nombrados para callback
        """
        with self._lock:
            self._call_count += 1
            
            # Cancelar timer previo si existe
            if self._timer is not None:
                self._timer.cancel()
                logger.debug(
                    f"Debouncer '{self.name}': Timer cancelado "
                    f"(call #{self._call_count})"
                )
            
            # Crear nuevo timer
            def execute_callback():
                with self._lock:
                    self._execute_count += 1
                    execute_num = self._execute_count
                
                logger.debug(
                    f"Debouncer '{self.name}': Ejecutando callback "
                    f"(execute #{execute_num})"
                )
                
                try:
                    self.callback(*args, **kwargs)
                except Exception as e:
                    logger.error(
                        f"Debouncer '{self.name}': Error en callback: {e}",
                        exc_info=True
                    )
            
            self._timer = threading.Timer(
                interval=self.delay_ms / 1000.0,
                function=execute_callback
            )
            self._timer.daemon = True
            self._timer.start()
    
    def cancel(self) -> None:
        """Cancela timer pendiente si existe."""
        with self._lock:
            if self._timer is not None:
                self._timer.cancel()
                self._timer = None
                logger.debug(f"Debouncer '{self.name}': Timer cancelado manualmente")
    
    def flush(self) -> None:
        """
        Ejecuta el callback inmediatamente si hay un timer pendiente.
        Útil para forzar ejecución antes de cerrar ventana, etc.
        """
        with self._lock:
            if self._timer is not None:
                # Cancelar timer
                self._timer.cancel()
                
                # Ejecutar callback inmediatamente
                logger.debug(
                    f"Debouncer '{self.name}': Flush - ejecutando inmediatamente"
                )
                
                try:
                    self.callback()
                except Exception as e:
                    logger.error(
                        f"Debouncer '{self.name}': Error en flush: {e}",
                        exc_info=True
                    )
                
                self._timer = None
                self._execute_count += 1
    
    def get_stats(self) -> dict:
        """
        Retorna estadísticas del debouncer.
        
        Returns:
            Diccionario con métricas
        """
        with self._lock:
            reduction_rate = 0.0
            if self._call_count > 0:
                reduction_rate = (
                    (self._call_count - self._execute_count) / 
                    self._call_count * 100
                )
            
            return {
                'name': self.name,
                'delay_ms': self.delay_ms,
                'call_count': self._call_count,
                'execute_count': self._execute_count,
                'reduction_rate': f"{reduction_rate:.1f}%",
                'pending': self._timer is not None
            }
    
    def reset_stats(self) -> None:
        """Reinicia contadores de estadísticas."""
        with self._lock:
            self._call_count = 0
            self._execute_count = 0
            logger.debug(f"Debouncer '{self.name}': Estadísticas reiniciadas")
    
    def __repr__(self) -> str:
        """Representación string del debouncer."""
        return (
            f"Debouncer(name='{self.name}', delay_ms={self.delay_ms}, "
            f"calls={self._call_count}, executes={self._execute_count})"
        )


class ThrottledDebouncer(Debouncer):
    """
    Variante de Debouncer que garantiza ejecución periódica.
    
    A diferencia del Debouncer normal que puede postponer indefinidamente,
    este garantiza que el callback se ejecute al menos cada max_wait_ms.
    
    Útil para actualizaciones que deben ocurrir aunque el usuario siga
    interactuando (ej: auto-save).
    """
    
    def __init__(
        self,
        delay_ms: int,
        callback: Callable,
        max_wait_ms: int,
        name: Optional[str] = None
    ):
        """
        Inicializa throttled debouncer.
        
        Args:
            delay_ms: Delay normal de debounce
            callback: Función a ejecutar
            max_wait_ms: Máximo tiempo de espera antes de forzar ejecución
            name: Nombre descriptivo
        """
        super().__init__(delay_ms, callback, name)
        self.max_wait_ms = max_wait_ms
        self._first_call_time: Optional[float] = None
        
        logger.debug(
            f"ThrottledDebouncer '{self.name}' creado "
            f"(delay={delay_ms}ms, max_wait={max_wait_ms}ms)"
        )
    
    def __call__(self, *args, **kwargs) -> None:
        """Llama al debouncer con throttling."""
        import time
        
        with self._lock:
            current_time = time.time()
            
            # Primera llamada en secuencia
            if self._first_call_time is None:
                self._first_call_time = current_time
            
            # Verificar si superamos max_wait
            elapsed_ms = (current_time - self._first_call_time) * 1000
            
            if elapsed_ms >= self.max_wait_ms:
                logger.debug(
                    f"ThrottledDebouncer '{self.name}': Max wait alcanzado, "
                    f"ejecutando inmediatamente"
                )
                
                # Cancelar timer si existe
                if self._timer is not None:
                    self._timer.cancel()
                
                # Ejecutar inmediatamente
                self._execute_count += 1
                self._first_call_time = None
                
                try:
                    self.callback(*args, **kwargs)
                except Exception as e:
                    logger.error(
                        f"ThrottledDebouncer '{self.name}': Error: {e}",
                        exc_info=True
                    )
            else:
                # Comportamiento normal de debounce
                super().__call__(*args, **kwargs)
