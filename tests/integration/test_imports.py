"""
Test de validación de imports para CI/CD.
Garantiza que la carga de módulos (especialmente con lazy loading) no genere ModuleNotFoundError ni dependencias circulares.
"""

def test_imports_no_ciclicos():
    """Valida que todos los servicios principales se puedan importar sin errores."""
    try:
        from src.aplicacion.servicios import (
            ServicioAutenticacion,
            ServicioConfiguracion,
            ServicioDashboard,
            ServicioPersonas,
            ServicioPropiedades,
            ServicioRecibosPublicos,
            ServicioTerceros,
        )
        
        # Validar que los atributos son accesibles para forzar el lazy loading en __init__
        assert ServicioAutenticacion is not None
        assert ServicioConfiguracion is not None
        assert ServicioDashboard is not None
        assert ServicioPersonas is not None
        assert ServicioPropiedades is not None
        assert ServicioRecibosPublicos is not None
        assert ServicioTerceros is not None
        
    except Exception as e:
        assert False, f"Fallo en importaciones del CI/CD: {e}"
