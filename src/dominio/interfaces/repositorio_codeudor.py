"""
Interface (Protocol): Repositorio de Codeudores
"""

from typing import Optional, Protocol
from src.dominio.entidades.codeudor import Codeudor


class IRepositorioCodeudor(Protocol):
    def obtener_por_persona(self, id_persona: int) -> Optional[Codeudor]: ...
    def crear(self, codeudor: Codeudor, usuario_sistema: str) -> Codeudor: ...
    def eliminar_por_persona(self, id_persona: int) -> bool: ...
