"""
Interfaz de Repositorio: Alertas
==============================
Define las operaciones permitidas para la persistencia de alertas.

Autor: Sistema de Gestión Inmobiliaria
Fecha: 2026-05-10
"""

from typing import List, Optional, Protocol, Dict, Any
from src.dominio.entidades.alerta import Alerta


class IRepositorioAlerta(Protocol):
    def obtener_por_id(self, id_alerta: int) -> Optional[Alerta]: ...

    def obtener_todas(
        self,
        estado: Optional[str] = None,
        prioridad: Optional[str] = None,
        tipo: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Alerta]: ...

    def contar_todas(
        self,
        estado: Optional[str] = None,
        prioridad: Optional[str] = None,
        tipo: Optional[str] = None
    ) -> int: ...

    def obtener_por_entidad_y_tipo(
        self, 
        id_entidad: int, 
        tipo_entidad: str, 
        tipo_alerta: str,
        solo_pendientes: bool = True
    ) -> Optional[Alerta]: ...

    def guardar(self, alerta: Alerta, usuario_sistema: str) -> Alerta: ...

    def actualizar(self, alerta: Alerta, usuario_sistema: str) -> bool: ...

    def marcar_resuelta(
        self, 
        id_alerta: int, 
        usuario_sistema: str, 
        accion: str,
        automatica: bool = False
    ) -> bool: ...

    def eliminar(self, id_alerta: int) -> bool: ...
