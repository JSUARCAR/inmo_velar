"""
Utilidades de presentación para InmoVelar Web.

Incluye herramientas de optimización como LazyLoader y Debouncer.
"""

from .debouncer import Debouncer
from .lazy_loader import LazyLoaderManager, LazyModule, lazy_loader

__all__ = ["LazyModule", "LazyLoaderManager", "lazy_loader", "Debouncer"]
