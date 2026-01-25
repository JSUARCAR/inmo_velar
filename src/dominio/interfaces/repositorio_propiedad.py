"""
Interface (Protocol): Repositorio de Propiedades
"""

from typing import List, Optional, Protocol, Dict, Any
from src.dominio.entidades.propiedad import Propiedad

class IRepositorioPropiedad(Protocol):
    def obtener_por_id(self, id_propiedad: int) -> Optional[Propiedad]:
        ...
        
    def obtener_por_matricula(self, matricula: str) -> Optional[Propiedad]:
        ...
        
    def listar_con_filtros(
        self,
        filtro_tipo: Optional[str] = None,
        filtro_disponibilidad: Optional[int] = None,
        filtro_municipio: Optional[int] = None,
        solo_activas: bool = True,
        busqueda: Optional[str] = None,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> List[Propiedad]:
        ...
        
    def contar_con_filtros(
        self,
        filtro_tipo: Optional[str] = None,
        filtro_disponibilidad: Optional[int] = None,
        filtro_municipio: Optional[int] = None,
        solo_activas: bool = True,
        busqueda: Optional[str] = None
    ) -> int:
        ...
        
    def crear(self, propiedad: Propiedad, usuario_sistema: str) -> Propiedad:
        ...
        
    def actualizar(self, propiedad: Propiedad, usuario_sistema: str) -> bool:
        ...
        
    def _row_to_entity(self, row: Any) -> Propiedad:
        ...
