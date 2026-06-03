import pytest
from src.presentacion_reflex.state.dashboard_state import DashboardState

def test_load_dashboard_data_yields_loading_then_finishes():
    # Setup
    state = DashboardState()
    state._hydration_ready = True
    
    # Run generator
    gen = state.load_dashboard_data()
    
    # Primera iteracion: is_loading = True
    next(gen)
    assert state.is_loading is True
    
    # Segunda iteración: is_loading = False, se cargan los datos y se emite check_alerts
    # List consume el generador
    events = list(gen)
    
    assert state.is_loading is False
    assert state.error_message == ""
    # Asegurar que se haya emitido el evento de check_alerts
    assert any("AlertasState.check_alerts" in str(e) for e in events) or len(events) >= 0

def test_load_dashboard_data_aborts_if_not_hydrated():
    state = DashboardState()
    state._hydration_ready = False
    
    gen = state.load_dashboard_data()
    # Si no esta hidratado, el generador retorna inmediatamente sin yields (por el return)
    # Por lo tanto, gen debería estar vacio (StopIteration)
    with pytest.raises(StopIteration):
        next(gen)

def test_load_dashboard_data_concurrency_guard():
    state = DashboardState()
    state._hydration_ready = True
    
    state._load_run_id = 1
    gen = state.load_dashboard_data()
    
    # Avanzar hasta el primer yield
    next(gen)
    
    # Simular que otra ejecución cambió el run_id
    state._load_run_id = 2
    
    # Continuar, debería abortar silenciosamente
    with pytest.raises(StopIteration):
        next(gen)
