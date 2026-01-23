"""
Tests unitarios para CacheManager.

Verifica funcionamiento de cache multi-nivel, LRU, TTL y métricas.
"""

import pytest
import time
import threading
from src.infraestructura.cache.cache_manager import (
    CacheLevel,
    CacheManager,
    cache_manager
)


class TestCacheLevel:
    """Tests para CacheLevel individual."""
    
    def test_basic_get_set(self):
        """Test get/set básico."""
        cache = CacheLevel(max_size=10, ttl_seconds=60, name="test")
        
        # Set y get
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"
        
        # Key inexistente
        assert cache.get("nonexistent") is None
    
    def test_ttl_expiration(self):
        """Test expiración por TTL."""
        cache = CacheLevel(max_size=10, ttl_seconds=1, name="test")
        
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"
        
        # Esperar expiración
        time.sleep(1.1)
        assert cache.get("key1") is None
    
    def test_lru_eviction(self):
        """Test eviction LRU."""
        cache = CacheLevel(max_size=3, ttl_seconds=60, name="test")
        
        # Llenar cache
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")
        
        # Agregar 4to item - debe evict key1
        cache.set("key4", "value4")
        
        assert cache.get("key1") is None  # Evicted
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"
        assert cache.get("key4") == "value4"
    
    def test_lru_access_updates_order(self):
        """Test que acceder actualiza orden LRU."""
        cache = CacheLevel(max_size=3, ttl_seconds=60, name="test")
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")
        
        # Acceder key1 - la mueve al final
        cache.get("key1")
        
        # Agregar key4 - debe evict key2 (no key1)
        cache.set("key4", "value4")
        
        assert cache.get("key1") == "value1"  # Preservada
        assert cache.get("key2") is None  # Evicted
    
    def test_invalidate_all(self):
        """Test invalidar todo el cache."""
        cache = CacheLevel(max_size=10, ttl_seconds=60, name="test")
        
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        
        count = cache.invalidate()
        
        assert count == 2
        assert cache.get("key1") is None
        assert cache.get("key2") is None
        assert cache.size() == 0
    
    def test_invalidate_pattern(self):
        """Test invalidar por patrón."""
        cache = CacheLevel(max_size=10, ttl_seconds=60, name="test")
        
        cache.set("users:1", "user1")
        cache.set("users:2", "user2")
        cache.set("posts:1", "post1")
        
        count = cache.invalidate("users:*")
        
        assert count == 2
        assert cache.get("users:1") is None
        assert cache.get("users:2") is None
        assert cache.get("posts:1") == "post1"  # Preservado
    
    def test_clear_expired(self):
        """Test limpieza de items expirados."""
        cache = CacheLevel(max_size=10, ttl_seconds=1, name="test")
        
        cache.set("key1", "value1")
        time.sleep(0.5)
        cache.set("key2", "value2")
        
        # Esperar a que key1 expire
        time.sleep(0.6)
        
        count = cache.clear_expired()
        
        assert count == 1
        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"
    
    def test_thread_safety(self):
        """Test operaciones concurrentes."""
        cache = CacheLevel(max_size=100, ttl_seconds=60, name="test")
        errors = []
        
        def worker(thread_id):
            try:
                for i in range(100):
                    cache.set(f"t{thread_id}:k{i}", f"v{i}")
                    cache.get(f"t{thread_id}:k{i}")
            except Exception as e:
                errors.append(e)
        
        threads = [
            threading.Thread(target=worker, args=(i,))
            for i in range(5)
        ]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert len(errors) == 0


class TestCacheManager:
    """Tests para CacheManager."""
    
    def test_cached_decorator_l1(self):
        """Test decorador @cached con nivel 1."""
        manager = CacheManager()
        call_count = 0
        
        @manager.cached('test', level=1)
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2
        
        # Primera llamada - cache miss
        result1 = expensive_function(5)
        assert result1 == 10
        assert call_count == 1
        
        # Segunda llamada - cache hit
        result2 = expensive_function(5)
        assert result2 == 10
        assert call_count == 1  # No se ejecutó de nuevo
        
        # Llamada con arg diferente - cache miss
        result3 = expensive_function(10)
        assert result3 == 20
        assert call_count == 2
    
    def test_cached_decorator_preserves_metadata(self):
        """Test que decorador preserva metadata de función."""
        manager = CacheManager()
        
        @manager.cached('test', level=1)
        def my_function(x):
            """Docstring de prueba."""
            return x
        
        assert my_function.__name__ == "my_function"
        assert "Docstring de prueba" in my_function.__doc__
        assert hasattr(my_function, '_cached')
        assert my_function._cache_namespace == 'test'
    
    def test_invalidate_namespace(self):
        """Test invalidación por namespace."""
        manager = CacheManager()
        
        @manager.cached('users', level=1)
        def get_user(id):
            return f"user_{id}"
        
        @manager.cached('posts', level=1)
        def get_post(id):
            return f"post_{id}"
        
        # Cargar cache
        get_user(1)
        get_user(2)
        get_post(1)
        
        # Invalidar solo 'users'
        count = manager.invalidate('users')
        
        assert count >= 2
        
        # Verificar hits/misses
        old_misses = manager.misses
        
        get_user(1)  # Miss
        get_post(1)  # Hit
        
        assert manager.misses == old_misses + 1
    
    def test_stats(self):
        """Test estadísticas de cache."""
        manager = CacheManager()
        
        @manager.cached('test', level=1)
        def func(x):
            return x
        
        func(1)  # Miss
        func(1)  # Hit
        func(1)  # Hit
        func(2)  # Miss
        
        stats = manager.get_stats()
        
        assert stats['hits'] == 2
        assert stats['misses'] == 2
        assert stats['total_requests'] == 4
        assert '50.00%' in stats['hit_rate']
    
    def test_multi_level_cache(self):
        """Test que diferentes niveles funcionan independientemente."""
        manager = CacheManager()
        
        @manager.cached('test', level=1)
        def func_l1(x):
            return x
        
        @manager.cached('test', level=2)
        def func_l2(x):
            return x
        
        func_l1(1)
        func_l2(1)
        
        stats = manager.get_stats()
        
        # Ambos niveles tienen datos
        assert stats['l1_size'] >= 1
        assert stats['l2_size'] >= 1
    
    def test_clear_all(self):
        """Test limpiar todo el cache."""
        manager = CacheManager()
        
        @manager.cached('test1', level=1)
        def func1(x):
            return x
        
        @manager.cached('test2', level=2)
        def func2(x):
            return x
        
        func1(1)
        func2 (1)
        
        count = manager.clear_all()
        
        assert count >= 2
        
        stats = manager.get_stats()
        assert stats['total_cached_items'] == 0


class TestGlobalCacheManager:
    """Tests para instancia global cache_manager."""
    
    def test_singleton_exists(self):
        """Test que instancia global existe."""
        assert cache_manager is not None
        assert isinstance(cache_manager, CacheManager)
    
    def test_can_use_global_instance(self):
        """Test que se puede usar instancia global."""
        @cache_manager.cached('global_test', level=1)
        def func(x):
            return x * 2
        
        result = func(5)
        assert result == 10


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
