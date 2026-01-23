"""
Tests unitarios para LazyLoader.

Verifica carga diferida, precarga y gestión de módulos.
"""

import pytest
import time
from unittest.mock import Mock, patch
from src.presentacion.utils.lazy_loader import (
    LazyModule,
    LazyLoaderManager,
    lazy_loader
)


class TestLazyModule:
    """Tests para LazyModule."""
    
    def test_module_loads_on_demand(self):
        """Test que módulo se carga solo cuando se pide."""
        lazy_mod = LazyModule(
            'json',  # Módulo estándar
            'dumps',
            preload_after_seconds=None
        )
        
        assert not lazy_mod.is_loaded
        
        # Cargar
        builder = lazy_mod.load()
        
        assert lazy_mod.is_loaded
        assert callable(builder)
        assert builder.__name__ == 'dumps'
    
    def test_load_is_idempotent(self):
        """Test que llamar load() varias veces no recarga."""
        lazy_mod = LazyModule('json', 'dumps')
        
        builder1 = lazy_mod.load()
        builder2 = lazy_mod.load()
        
        assert builder1 is builder2
    
    def test_invalid_module_raises_error(self):
        """Test que módulo inválido lanza error."""
        lazy_mod = LazyModule('nonexistent_module_xyz', 'func')
        
        with pytest.raises(ModuleNotFoundError):
            lazy_mod.load()
    
    def test_invalid_function_raises_error(self):
        """Test que función inválida lanza error."""
        lazy_mod = LazyModule('json', 'nonexistent_function')
        
        with pytest.raises(AttributeError):
            lazy_mod.load()
    
    def test_preload_async(self):
        """Test precarga asíncrona."""
        lazy_mod = LazyModule('json', 'dumps')
        
        lazy_mod.preload_async()
        
        # Esperar un poco
        time.sleep(0.1)
        
        # Debería estar cargado
        assert lazy_mod.is_loaded
    
    def test_load_time_is_tracked(self):
        """Test que se guarda tiempo de carga."""
        lazy_mod = LazyModule('json', 'dumps')
        
        assert lazy_mod.load_time is None
        
        lazy_mod.load()
        
        assert lazy_mod.load_time is not None
        assert lazy_mod.load_time > 0


class TestLazyLoaderManager:
    """Tests para LazyLoaderManager."""
    
    def test_register_and_get_builder(self):
        """Test registro y obtención de builder."""
        manager = LazyLoaderManager()
        
        manager.register(
            'json_dumps',
            'json',
            'dumps',
            priority=5
        )
        
        builder = manager.get_builder('json_dumps')
        
        assert callable(builder)
        assert builder.__name__ == 'dumps'
    
    def test_get_nonexistent_raises_error(self):
        """Test que módulo no registrado lanza error."""
        manager = LazyLoaderManager()
        
        with pytest.raises(ValueError, match="no registrado"):
            manager.get_builder('nonexistent')
    
    def test_priority_sorting(self):
        """Test que módulos se ordenan por prioridad."""
        manager = LazyLoaderManager()
        
        manager.register('low', 'json', 'dumps', priority=10)
        manager.register('high', 'json', 'loads', priority=1)
        manager.register('med', 'json', 'dump', priority=5)
        
        # Orden debe ser high, med, low
        names = [name for name, _ in manager.load_order]
        
        assert names == ['high', 'med', 'low']
    
    def test_preload_high_priority(self):
        """Test precarga de alta prioridad."""
        manager = LazyLoaderManager()
        
        manager.register('p1', 'json', 'dumps', priority=1)
        manager.register('p5', 'json', 'loads', priority=5)
        manager.register('p10', 'json', 'dump', priority=10)
        
        manager.preload_high_priority(threshold=3)
        
        # Esperar precarga
        time.sleep(0.2)
        
        # Solo p1 debería estar cargado
        assert manager.is_loaded('p1')
        assert not manager.is_loaded('p5')
        assert not manager.is_loaded('p10')
    
    def test_stats(self):
        """Test estadísticas."""
        manager = LazyLoaderManager()
        
        manager.register('m1', 'json', 'dumps', priority=1)
        manager.register('m2', 'json', 'loads', priority=2)
        
        stats = manager.get_stats()
        
        assert stats['total_modules'] == 2
        assert stats['loaded_modules'] == 0
        assert stats['pending_modules'] == 2
        
        # Cargar uno
        manager.get_builder('m1')
        
        stats = manager.get_stats()
        assert stats['loaded_modules'] == 1
        assert stats['pending_modules'] == 1
    
    def test_is_loaded(self):
        """Test verificación de carga."""
        manager = LazyLoaderManager()
        
        manager.register('test', 'json', 'dumps')
        
        assert not manager.is_loaded('test')
        
        manager.get_builder('test')
        
        assert manager.is_loaded('test')
    
    def test_scheduled_preload(self):
        """Test precarga programada."""
        manager = LazyLoaderManager()
        
        manager.register(
            'delayed',
            'json',
            'dumps',
            priority=5,
            preload_after=1  # 1 segundo
        )
        
        assert not manager.is_loaded('delayed')
        
        # Esperar precarga
        time.sleep(1.2)
        
        assert manager.is_loaded('delayed')


class TestGlobalLazyLoader:
    """Tests para instancia global lazy_loader."""
    
    def test_singleton_exists(self):
        """Test que instancia global existe."""
        assert lazy_loader is not None
        assert isinstance(lazy_loader, LazyLoaderManager)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
