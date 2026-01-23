"""
Utilidades de presentación para InmoVelar Web.

Incluye herramientas de optimización como LazyLoader y Debouncer.
"""

from .lazy_loader import LazyModule, LazyLoaderManager, lazy_loader
from .debouncer import Debouncer

__all__ = [
    'LazyModule',
    'LazyLoaderManager', 
    'lazy_loader',
    'Debouncer'
]
