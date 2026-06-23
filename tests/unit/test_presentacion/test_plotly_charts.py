import pytest
import plotly.graph_objects as go
from src.presentacion_reflex.state.dashboard_state import DashboardState

def test_dashboard_state_initial_chart_vars():
    """Valida que las vars del state inicialmente devuelvan una figura vacía o skeleton"""
    state = DashboardState()
    
    # In Reflex, you can call the function directly
    # from the state dict bypassing the proxy
    fig = DashboardState.evolucion_chart_fig.fn(state) if hasattr(DashboardState.evolucion_chart_fig, 'fn') else DashboardState.__dict__["evolucion_chart_fig"].fget(state)
    
    assert isinstance(fig, go.Figure)
    
    fig2 = DashboardState.vencimiento_chart_fig.fn(state) if hasattr(DashboardState.vencimiento_chart_fig, 'fn') else DashboardState.__dict__["vencimiento_chart_fig"].fget(state)
    assert isinstance(fig2, go.Figure)

def test_dashboard_state_populated_chart_vars():
    """Valida que la figura se construya correctamente cuando hay datos"""
    state = DashboardState()
    object.__setattr__(state, 'evolucion_data', {"etiquetas": ["Ene", "Feb"], "valores": [1000, 2000]})
    
    fig = DashboardState.evolucion_chart_fig.fn(state) if hasattr(DashboardState.evolucion_chart_fig, 'fn') else DashboardState.__dict__["evolucion_chart_fig"].fget(state)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) in (1, 2)  # Actualizado porque ahora se agrega línea Target
    assert fig.data[0].x == ("Ene", "Feb")
    
    object.__setattr__(state, 'incidentes_data', {"por_estado": {"Abierto": 5, "Cerrado": 10}})
    fig_pie = DashboardState.incidentes_chart_fig.fn(state) if hasattr(DashboardState.incidentes_chart_fig, 'fn') else DashboardState.__dict__["incidentes_chart_fig"].fget(state)
    assert isinstance(fig_pie, go.Figure)
    assert len(fig_pie.data) == 1
