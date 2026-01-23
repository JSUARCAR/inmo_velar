"""
Módulo de Cache Multi-Nivel para InmoVelar Web.

Proporciona un sistema de cache inteligente con 3 niveles:
- L1: Memory Cache (datos calientes, TTL 5 min)
- L2: Query Result Cache (consultas complejas, TTL 15 min)
- L3: Static Data Cache (datos maestros, 24 hrs)
"""

from .cache_manager import CacheManager, cache_manager

__all__ = ['CacheManager', 'cache_manager']
