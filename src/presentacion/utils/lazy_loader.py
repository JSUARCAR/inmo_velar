"""
Lazy Loading Manager para InmoVelar Web.

Permite cargar módulos bajo demanda en lugar de al inicio,
reduciendo significativamente el tiempo de arranque de la aplicación.

Autor: InmoVelar Dev Team
Fecha: 2025-12-29
"""

from typing import Callable, Optional, Any, Dict, Tuple, List
import threading
import importlib
import time
import logging

logger = logging.getLogger(__name__)


class LazyModule:
    """
    Wrapper para módulo lazy-loaded con soporte para precarga.
    
    Características:
    - Carga diferida (solo cuando se necesita)
    - Precarga async opcional
    - Thread-safe
    - Error handling robusto
    """
    
    def __init__(
        self,
        module_path: str,
        builder_function: str,
        preload_after_seconds: Optional[int] = None
    ):
        """
        Inicializa un módulo lazy.
        
        Args:
            module_path: Ruta del módulo (ej: 'src.presentacion.views.personas_list_view')
            builder_function: Nombre de la función builder
            preload_after_seconds: Si se especifica, precarga después de N segundos
        """
        self.module_path = module_path
        self.builder_function = builder_function
        self.preload_after_seconds = preload_after_seconds
        
        self._module = None
        self._builder = None
        self._loading = False
        self._error = None
        self._load_time = None
        self._lock = threading.RLock()
    
    def load(self) -> Callable:
        """
        Carga el módulo sincronamente si no está cargado.
        
        Returns:
            Función builder del módulo
            
        Raises:
            ImportError: Si el módulo no existe
            AttributeError: Si la función builder no existe
        """
        with self._lock:
            # Ya cargado
            if self._builder is not None:
                return self._builder
            
            # Error previo
            if self._error is not None:
                raise self._error
            
            # Carga en progreso - esperar
            if self._loading:
                # Liberar lock mientras esperamos
                pass
            
            self._loading = True
        
        try:
            start_time = time.time()
            logger.info(f"Cargando módulo lazy: {self.module_path}")
            
            # Import dinámico
            self._module = importlib.import_module(self.module_path)
            
            # Obtener builder function
            if not hasattr(self._module, self.builder_function):
                raise AttributeError(
                    f"Módulo {self.module_path} no tiene función "
                    f"'{self.builder_function}'"
                )
            
            self._builder = getattr(self._module, self.builder_function)
            self._load_time = time.time() - start_time
            
            logger.info(
                f"Módulo {self.module_path} cargado en {self._load_time:.3f}s"
            )
            
            return self._builder
            
        except Exception as e:
            logger.error(f"Error cargando {self.module_path}: {e}")
            self._error = e
            raise
        
        finally:
            with self._lock:
                self._loading = False
    
    def preload_async(self) -> None:
        """Precarga el módulo en background thread."""
        if self._module is None and not self._loading:
            def preload_task():
                try:
                    self.load()
                except Exception as e:
                    logger.warning(f"Precarga falló para {self.module_path}: {e}")
            
            threading.Thread(
                target=preload_task,
                daemon=True,
                name=f"Preload-{self.module_path}"
            ).start()
            
            logger.debug(f"Precarga async iniciada: {self.module_path}")
    
    @property
    def is_loaded(self) -> bool:
        """Indica si el módulo ya está cargado."""
        return self._builder is not None
    
    @property
    def load_time(self) -> Optional[float]:
        """Tiempo que tomó cargar el módulo."""
        return self._load_time


class LazyLoaderManager:
    """
    Gestiona la carga lazy de todos los módulos de la app.
    
    Características:
    - Registro centralizado de módulos
    - Prioridades de carga
    - Precarga inteligente
    - Estadísticas de carga
    """
    
    def __init__(self):
        """Inicializa el manager."""
        self.modules: Dict[str, Dict[str, Any]] = {}
        self.load_order: List[Tuple[str, Dict[str, Any]]] = []
        self._lock = threading.RLock()
        
        logger.info("LazyLoaderManager inicializado")
    
    def register(
        self,
        name: str,
        module_path: str,
        builder_function: str,
        priority: int = 5,  # 1=alta, 10=baja
        preload_after: Optional[int] = None
    ) -> None:
        """
        Registra un módulo para lazy loading.
        
        Args:
            name: Nombre identificador del módulo
            module_path: Ruta del módulo Python
            builder_function: Nombre de la función builder
            priority: Prioridad de carga (1-10, menor=más prioritario)
            preload_after: Segundos para precargar (opcional)
        """
        with self._lock:
            if name in self.modules:
                logger.warning(f"Módulo '{name}' ya registrado, sobrescribiendo")
            
            lazy_mod = LazyModule(module_path, builder_function, preload_after)
            
            self.modules[name] = {
                'loader': lazy_mod,
                'priority': priority,
                'loaded': False,
                'module_path': module_path,
                'builder_function': builder_function,
                'preload_after': preload_after
            }
            
            # Ordenar por prioridad
            self.load_order = sorted(
                self.modules.items(),
                key=lambda x: x[1]['priority']
            )
            
            logger.debug(
                f"Registrado módulo lazy: {name} "
                f"(priority={priority}, path={module_path})"
            )
            
            # Programar precarga si corresponde
            if preload_after is not None:
                self._schedule_preload(name, preload_after)
    
    def _schedule_preload(self, name: str, delay_seconds: int) -> None:
        """Programa precarga de un módulo."""
        def delayed_preload():
            time.sleep(delay_seconds)
            if not self.modules[name]['loaded']:
                logger.info(f"Precargando módulo '{name}' (scheduled)")
                self.modules[name]['loader'].preload_async()
        
        threading.Thread(
            target=delayed_preload,
            daemon=True,
            name=f"DelayedPreload-{name}"
        ).start()
    
    def get_builder(self, name: str) -> Callable:
        """
        Obtiene el builder function, cargándolo si es necesario.
        
        Args:
            name: Nombre del módulo
            
        Returns:
            Función builder
            
        Raises:
            ValueError: Si el módulo no está registrado
        """
        with self._lock:
            if name not in self.modules:
                available = ', '.join(self.modules.keys())
                raise ValueError(
                    f"Módulo no registrado: '{name}'. "
                    f"Disponibles: {available}"
                )
            
            module_info = self.modules[name]
            loader = module_info['loader']
        
        # Cargar (puede tomar tiempo, fuera del lock)
        builder = loader.load()
        
        # Marcar como cargado
        with self._lock:
            module_info['loaded'] = True
        
        return builder
    
    def preload_high_priority(self, threshold: int = 3) -> None:
        """
        Precarga módulos de alta prioridad en background.
        
        Args:
            threshold: Precargar módulos con priority <= threshold
        """
        logger.info(f"Precargando módulos con prioridad <= {threshold}")
        
        preloaded_count = 0
        for name, info in self.load_order:
            if info['priority'] <= threshold and not info['loaded']:
                info['loader'].preload_async()
                preloaded_count += 1
        
        logger.info(f"Iniciada precarga de {preloaded_count} módulos")
    
    def preload_all(self) -> None:
        """Precarga todos los módulos no cargados."""
        logger.info("Precargando TODOS los módulos")
        
        for name, info in self.modules.items():
            if not info['loaded']:
                info['loader'].preload_async()
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Retorna estadísticas de carga.
        
        Returns:
            Diccionario con métricas
        """
        with self._lock:
            total = len(self.modules)
            loaded = sum(1 for m in self.modules.values() if m['loaded'])
            
            modules_detail = {}
            total_load_time = 0.0
            
            for name, info in self.modules.items():
                loader = info['loader']
                status = 'loaded' if info['loaded'] else 'pending'
                load_time = loader.load_time if loader.load_time else 0.0
                
                modules_detail[name] = {
                    'status': status,
                    'priority': info['priority'],
                    'load_time': f"{load_time:.3f}s" if load_time > 0 else "N/A",
                    'module_path': info['module_path']
                }
                
                if load_time > 0:
                    total_load_time += load_time
            
            return {
                'total_modules': total,
                'loaded_modules': loaded,
                'pending_modules': total - loaded,
                'load_percentage': f"{(loaded/total*100):.1f}%" if total > 0 else "0%",
                'total_load_time': f"{total_load_time:.3f}s",
                'modules': modules_detail
            }
    
    def is_loaded(self, name: str) -> bool:
        """
        Verifica si un módulo está cargado.
        
        Args:
            name: Nombre del módulo
            
        Returns:
            True si está cargado
        """
        with self._lock:
            if name not in self.modules:
                return False
            return self.modules[name]['loaded']
    
    def unregister(self, name: str) -> None:
        """
        Desregistra un módulo (útil para testing).
        
        Args:
            name: Nombre del módulo
        """
        with self._lock:
            if name in self.modules:
                del self.modules[name]
                self.load_order = [
                    (n, i) for n, i in self.load_order if n != name
                ]
                logger.debug(f"Módulo '{name}' desregistrado")


# Instancia global singleton
lazy_loader = LazyLoaderManager()


# Helper functions
def register_lazy_module(
    name: str,
    module_path: str,
    builder_function: str,
    priority: int = 5,
    preload_after: Optional[int] = None
) -> None:
    """
    Helper para registrar módulo lazy.
    
    Args:
        name: Nombre del módulo
        module_path: Ruta del módulo
        builder_function: Función builder
        priority: Prioridad (1-10)
        preload_after: Segundos para precargar
    """
    lazy_loader.register(
        name,
        module_path,
        builder_function,
        priority,
        preload_after
    )


def get_lazy_builder(name: str) -> Callable:
    """
    Helper para obtener builder.
    
    Args:
        name: Nombre del módulo
        
    Returns:
        Función builder
    """
    return lazy_loader.get_builder(name)
