"""
Tests unitarios para Debouncer.

Verifica debouncing, throttling y reducción de llamadas.
"""

import pytest
import time
import threading
from src.presentacion.utils.debouncer import Debouncer, ThrottledDebouncer


class TestDebouncer:
    """Tests para Debouncer básico."""
    
    def test_basic_debounce(self):
        """Test debounce básico."""
        call_count = 0
        
        def callback():
            nonlocal call_count
            call_count += 1
        
        debouncer = Debouncer(delay_ms=100, callback=callback)
        
        # Llamar 5 veces rápidamente
        for _ in range(5):
            debouncer()
            time.sleep(0.02)
        
        # Esperar ejecución
        time.sleep(0.15)
        
        # Solo debe haberse ejecutado 1 vez
        assert call_count == 1
    
    def test_debounce_with_args(self):
        """Test debounce con argumentos."""
        received_args = []
        
        def callback(*args, **kwargs):
            received_args.append((args, kwargs))
        
        debouncer = Debouncer(delay_ms=100, callback=callback)
        
        debouncer(1, 2, key='value')
        
        time.sleep(0.15)
        
        assert len(received_args) == 1
        assert received_args[0] == ((1, 2), {'key': 'value'})
    
    def test_cancel(self):
        """Test cancelación de timer."""
        call_count = 0
        
        def callback():
            nonlocal call_count
            call_count += 1
        
        debouncer = Debouncer(delay_ms=100, callback=callback)
        
        debouncer()
        debouncer.cancel()
        
        time.sleep(0.15)
        
        # No debe haberse ejecutado
        assert call_count == 0
    
    def test_flush(self):
        """Test ejecución inmediata con flush."""
        call_count = 0
        
        def callback():
            nonlocal call_count
            call_count += 1
        
        debouncer = Debouncer(delay_ms=1000, callback=callback)  # Delay largo
        
        debouncer()
        debouncer.flush()
        
        # Debe ejecutarse inmediatamente
        assert call_count == 1
    
    def test_stats(self):
        """Test estadísticas."""
        def callback():
            pass
        
        debouncer = Debouncer(delay_ms=50, callback=callback, name="test_debouncer")
        
        # Llamar varias veces
        for _ in range(10):
            debouncer()
            time.sleep(0.01)
        
        time.sleep(0.1)
        
        stats = debouncer.get_stats()
        
        assert stats['name'] == "test_debouncer"
        assert stats['call_count'] == 10
        assert stats['execute_count'] == 1
        assert '90.0%' in stats['reduction_rate']  # 9 de 10 reducidos
    
    def test_multiple_separate_calls(self):
        """Test llamadas separadas ejecutan múltiples veces."""
        call_count = 0
        
        def callback():
            nonlocal call_count
            call_count += 1
        
        debouncer = Debouncer(delay_ms=50, callback=callback)
        
        debouncer()
        time.sleep(0.1)  # Esperar ejecución
        
        debouncer()
        time.sleep(0.1)  # Esperar ejecución
        
        debouncer()
        time.sleep(0.1)  # Esperar ejecución
        
        assert call_count == 3
    
    def test_error_in_callback_is_logged(self):
        """Test que errores en callback no crashean."""
        def bad_callback():
            raise ValueError("Error de prueba")
        
        debouncer = Debouncer(delay_ms=50, callback=bad_callback)
        
        # No debe lanzar excepción
        debouncer()
        time.sleep(0.1)


class TestThrottledDebouncer:
    """Tests para ThrottledDebouncer."""
    
    def test_throttle_enforces_max_wait(self):
        """Test que throttle fuerza ejecución después de max_wait."""
        call_count = 0
        call_times = []
        
        def callback():
            nonlocal call_count
            call_count += 1
            call_times.append(time.time())
        
        debouncer = ThrottledDebouncer(
            delay_ms=100,
            callback=callback,
            max_wait_ms=200
        )
        
        start = time.time()
        
        # Llamar continuamente por 500ms
        while time.time() - start < 0.5:
            debouncer()
            time.sleep(0.03)
        
        # Esperar última ejecución
        time.sleep(0.15)
        
        # Debe haberse ejecutado al menos 2 veces (cada 200ms)
        assert call_count >= 2
    
    def test_throttle_normal_debounce_when_quiet(self):
        """Test que funciona como debouncer normal cuando hay quietud."""
        call_count = 0
        
        def callback():
            nonlocal call_count
            call_count += 1
        
        debouncer = ThrottledDebouncer(
            delay_ms=100,
            callback=callback,
            max_wait_ms=500
        )
        
        # Llamadas rápidas
        for _ in range(5):
            debouncer()
            time.sleep(0.02)
        
        # Esperar
        time.sleep(0.15)
        
        # Solo 1 ejecución (debounce normal)
        assert call_count == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
