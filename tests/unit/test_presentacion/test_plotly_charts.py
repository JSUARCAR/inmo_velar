import pytest
import plotly.graph_objects as go
from src.presentacion_reflex.state.dashboard_state import DashboardState

def test_dashboard_state_initial_chart_vars():
    """Valida que las vars del state inicialmente devuelvan una figura vacía o skeleton"""
    state = DashboardState()
    # In Reflex, you can evaluate computed vars by calling them or accessing them if initialized properly.
    # Alternatively, we can just call the underlying function.
    fig = DashboardState.evolucion_chart_fig._var_data.fget(state) if hasattr(DashboardState.evolucion_chart_fig, '_var_data') else getattr(DashboardState, 'evolucion_chart_fig').fget(state) if hasattr(getattr(DashboardState, 'evolucion_chart_fig'), 'fget') else type(state).evolucion_chart_fig.fget(state) if hasattr(type(state).evolucion_chart_fig, 'fget') else state.evolucion_chart_fig
    
    assert isinstance(fig, go.Figure)
    
    fig2 = state.vencimiento_chart_fig
    assert isinstance(fig2, go.Figure)

def test_dashboard_state_populated_chart_vars():
    """Valida que la figura se construya correctamente cuando hay datos"""
    state = DashboardState()
    object.__setattr__(state, 'evolucion_data', {"etiquetas": ["Ene", "Feb"], "valores": [1000, 2000]})
    
    fig = state.evolucion_chart_fig
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 1
    assert fig.data[0].x == ("Ene", "Feb")
    
    object.__setattr__(state, 'incidentes_data', {"por_estado": {"Abierto": 5, "Cerrado": 10}})
    fig_pie = state.incidentes_chart_fig
    assert isinstance(fig_pie, go.Figure)
    assert len(fig_pie.data) == 1
