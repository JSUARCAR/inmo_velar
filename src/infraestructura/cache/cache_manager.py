"""
Sistema de Cache Multi-Nivel Inteligente para InmoVelar Web.

Implementa un cache híbrido con 3 niveles (L1, L2, L3) usando
política LRU (Least Recently Used) con TTL (Time To Live).

Autor: InmoVelar Dev Team
Fecha: 2025-12-29
"""

from typing import Any, Optional, Callable, Dict, Tuple
from functools import wraps
from collections import OrderedDict
import threading
import time
import hashlib
import json
import logging

logger = logging.getLogger(__name__)


class CacheLevel:
    """
    Nivel individual de cache con política LRU y TTL.
    
    Thread-safe mediante RLock para soportar operaciones concurrentes.
    """
    
    def __init__(self, max_size: int, ttl_seconds: int, name: str = "cache"):
        """
        Inicializa un nivel de cache.
        
        Args:
            max_size: Número máximo de items en cache
            ttl_seconds: Tiempo de vida en segundos
            name: Nombre descriptivo del nivel
        """
        self.max_size = max_size
        self.ttl = ttl_seconds
        self.name = name
        self._cache: OrderedDict[str, Any] = OrderedDict()
        self._timestamps: Dict[str, float] = {}
        self._lock = threading.RLock()
        
        logger.info(
            f"Inicializado {name} - max_size={max_size}, ttl={ttl_seconds}s"
        )
    
    def get(self, key: str) -> Optional[Any]:
        """
        Obtiene un valor del cache.
        
        Args:
            key: Clave del cache
            
        Returns:
            Valor cacheado o None si no existe o expiró
        """
        with self._lock:
            if key not in self._cache:
                return None
            
            # Verificar TTL
            if time.time() - self._timestamps[key] > self.ttl:
                logger.debug(f"{self.name}: TTL expirado para key={key}")
                del self._cache[key]
                del self._timestamps[key]
                return None
            
            # Mover al final (marcar como usado recientemente)
            self._cache.move_to_end(key)
            logger.debug(f"{self.name}: Cache HIT para key={key}")
            return self._cache[key]
    
    def set(self, key: str, value: Any) -> None:
        """
        Almacena un valor en cache.
        
        Args:
            key: Clave del cache
            value: Valor a almacenar
        """
        with self._lock:
            # Evict si está lleno y no es actualización
            if len(self._cache) >= self.max_size and key not in self._cache:
                oldest_key = next(iter(self._cache))
                logger.debug(
                    f"{self.name}: Evicting oldest key={oldest_key} (LRU)"
                )
                del self._cache[oldest_key]
                del self._timestamps[oldest_key]
            
            self._cache[key] = value
            self._cache.move_to_end(key)
            self._timestamps[key] = time.time()
            
            logger.debug(f"{self.name}: Almacenado key={key}")
    
    def invalidate(self, pattern: Optional[str] = None) -> int:
        """
        Invalida entradas del cache.
        
        Args:
            pattern: Patrón para invalidar (ej: 'personas:*'). 
                    Si es None, invalida todo
                    
        Returns:
            Número de entradas invalidadas
        """
        with self._lock:
            if pattern is None:
                count = len(self._cache)
                self._cache.clear()
                self._timestamps.clear()
                logger.info(f"{self.name}: Invalidado completamente ({count} items)")
                return count
            
            # Invalidar por patrón
            prefix = pattern.replace('*', '')
            keys_to_delete = [
                k for k in self._cache.keys() 
                if k.startswith(prefix)
            ]
            
            for k in keys_to_delete:
                del self._cache[k]
                del self._timestamps[k]
            
            logger.info(
                f"{self.name}: Invalidado patrón '{pattern}' ({len(keys_to_delete)} items)"
            )
            return len(keys_to_delete)
    
    def size(self) -> int:
        """Retorna tamaño actual del cache."""
        with self._lock:
            return len(self._cache)
    
    def clear_expired(self) -> int:
        """
        Limpia entradas expiradas.
        
        Returns:
            Número de entradas eliminadas
        """
        with self._lock:
            current_time = time.time()
            expired_keys = [
                k for k, ts in self._timestamps.items()
                if current_time - ts > self.ttl
            ]
            
            for k in expired_keys:
                del self._cache[k]
                del self._timestamps[k]
            
            if expired_keys:
                logger.debug(
                    f"{self.name}: Limpiados {len(expired_keys)} items expirados"
                )
            
            return len(expired_keys)


class CacheManager:
    """
    Gestor de cache multi-nivel con decoradores y métricas.
    
    Proporciona 3 niveles de cache:
    - L1: Datos calientes (100 items, 5 min TTL)
    - L2: Query results (50 items, 15 min TTL)
    - L3: Datos estáticos (20 items, 24 hrs TTL)
    """
    
    def __init__(self):
        """Inicializa el sistema de cache multi-nivel."""
        self.l1 = CacheLevel(max_size=100, ttl_seconds=300, name="L1-Hot")
        self.l2 = CacheLevel(max_size=50, ttl_seconds=900, name="L2-Queries")
        self.l3 = CacheLevel(max_size=20, ttl_seconds=3600*24, name="L3-Static")
        
        # Métricas
        self.hits = 0
        self.misses = 0
        self._metrics_lock = threading.Lock()
        
        # Background cleanup cada 5 minutos
        self._start_cleanup_thread()
        
        logger.info("CacheManager inicializado correctamente")
    
    def _start_cleanup_thread(self):
        """Inicia thread de limpieza automática."""
        def cleanup_loop():
            while True:
                time.sleep(300)  # 5 minutos
                expired_l1 = self.l1.clear_expired()
                expired_l2 = self.l2.clear_expired()
                expired_l3 = self.l3.clear_expired()
                
                total = expired_l1 + expired_l2 + expired_l3
                if total > 0:
                    logger.info(f"Cleanup: {total} items expirados eliminados")
        
        cleanup_thread = threading.Thread(
            target=cleanup_loop,
            daemon=True,
            name="CacheCleanup"
        )
        cleanup_thread.start()
    
    def _generate_key(self, namespace: str, *args, **kwargs) -> str:
        """
        Genera clave hash única de argumentos.
        
        Args:
            namespace: Namespace del cache (ej: 'personas')
            *args: Argumentos posicionales
            **kwargs: Argumentos nombrados
            
        Returns:
            Clave única en formato 'namespace:hash'
        """
        key_data = {
            'args': args,
            'kwargs': sorted(kwargs.items())
        }
        
        # Serializar y hashear
        try:
            serialized = json.dumps(key_data, sort_keys=True, default=str)
            key_hash = hashlib.md5(serialized.encode()).hexdigest()[:16]
        except Exception as e:
            logger.warning(f"Error generando cache key: {e}")
            # Fallback a hash simple
            key_hash = str(hash(str(key_data)))[:16]
        
        return f"{namespace}:{key_hash}"
    
    def cached(
        self, 
        namespace: str, 
        level: int = 1, 
        ttl: Optional[int] = None
    ):
        """
        Decorador para cachear resultados de función.
        
        Args:
            namespace: Namespace del cache
            level: Nivel de cache (1, 2, o 3)
            ttl: TTL customizado (opcional)
            
        Example:
            @cache_manager.cached('personas', level=1)
            def listar_personas(...):
                return ...
        """
        if level not in [1, 2, 3]:
            raise ValueError("level debe ser 1, 2, o 3")
        
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Generar cache key
                cache_key = self._generate_key(namespace, *args, **kwargs)
                
                # Seleccionar nivel de cache
                cache_level = [self.l1, self.l2, self.l3][level - 1]
                
                # Buscar en cache
                cached_value = cache_level.get(cache_key)
                
                if cached_value is not None:
                    with self._metrics_lock:
                        self.hits += 1
                    logger.debug(
                        f"Cache HIT: {func.__name__} (namespace={namespace})"
                    )
                    return cached_value
                
                # Cache miss - ejecutar función
                with self._metrics_lock:
                    self.misses += 1
                
                logger.debug(
                    f"Cache MISS: {func.__name__} (namespace={namespace})"
                )
                
                result = func(*args, **kwargs)
                
                # Guardar en cache
                cache_level.set(cache_key, result)
                
                return result
            
            # Añadir metadata
            wrapper._cached = True
            wrapper._cache_namespace = namespace
            wrapper._cache_level = level
            
            return wrapper
        
        return decorator
    
    def invalidates(
        self,
        namespace: str,
        level: Optional[int] = None
    ):
        """
        Decorador para invalidar cache DESPUÉS de ejecutar la función.
        
        Args:
            namespace: Namespace a invalidar
            level: Nivel específico (opcional)
        """
        def decorator(func: Callable):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # 1. Ejecutar función original
                result = func(*args, **kwargs)
                
                # 2. Invalidar cache si todo salió bien
                try:
                    count = self.invalidate(namespace, level)
                    logger.debug(
                        f"Cache invalidado por {func.__name__}: "
                        f"{namespace} ({count} items)"
                    )
                except Exception as e:
                    logger.error(f"Error invalidando cache en {func.__name__}: {e}")
                    
                return result
            return wrapper
        return decorator
    
    def invalidate(self, namespace: str, level: Optional[int] = None) -> int:
        """
        Invalida entradas de cache por namespace.
        
        Args:
            namespace: Namespace a invalidar
            level: Si se especifica, solo invalida ese nivel
            
        Returns:
            Número total de entradas invalidadas
        """
        pattern = f"{namespace}:*"
        total = 0
        
        if level is None:
            # Invalidar en todos los niveles
            total += self.l1.invalidate(pattern)
            total += self.l2.invalidate(pattern)
            total += self.l3.invalidate(pattern)
        else:
            cache_level = [self.l1, self.l2, self.l3][level - 1]
            total = cache_level.invalidate(pattern)
        
        logger.info(
            f"Invalidado namespace '{namespace}' "
            f"(level={'all' if level is None else level}, {total} items)"
        )
        
        return total
    
    def clear_all(self) -> int:
        """
        Limpia todo el cache.
        
        Returns:
            Número total de entradas eliminadas
        """
        total = 0
        total += self.l1.invalidate()
        total += self.l2.invalidate()
        total += self.l3.invalidate()
        
        logger.warning(f"Cache completamente limpiado ({total} items)")
        return total
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Retorna estadísticas del cache.
        
        Returns:
            Diccionario con métricas del cache
        """
        with self._metrics_lock:
            total_requests = self.hits + self.misses
            hit_rate = (self.hits / total_requests * 100) if total_requests > 0 else 0
            
            return {
                'hits': self.hits,
                'misses': self.misses,
                'total_requests': total_requests,
                'hit_rate': f"{hit_rate:.2f}%",
                'hit_rate_value': hit_rate,
                'l1_size': self.l1.size(),
                'l1_max': self.l1.max_size,
                'l2_size': self.l2.size(),
                'l2_max': self.l2.max_size,
                'l3_size': self.l3.size(),
                'l3_max': self.l3.max_size,
                'total_cached_items': (
                    self.l1.size() + self.l2.size() + self.l3.size()
                )
            }
    
    def reset_stats(self):
        """Reinicia contadores de métricas."""
        with self._metrics_lock:
            self.hits = 0
            self.misses = 0
        logger.info("Estadísticas de cache reiniciadas")


# Instancia global singleton
cache_manager = CacheManager()


# Helper functions para uso directo
def invalidate_cache(namespace: str, level: Optional[int] = None) -> int:
    """
    Helper para invalidar cache.
    
    Args:
        namespace: Namespace a invalidar
        level: Nivel específico (opcional)
        
    Returns:
        Número de entradas invalidadas
    """
    return cache_manager.invalidate(namespace, level)


def get_cache_stats() -> Dict[str, Any]:
    """
    Helper para obtener estadísticas.
    
    Returns:
        Diccionario con estadísticas
    """
    return cache_manager.get_stats()
