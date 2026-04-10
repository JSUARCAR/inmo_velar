"""
Interface (Protocol): Repositorio de Asistencias a Asambleas
"""

from typing import Dict, List, Optional, Protocol
from src.dominio.entidades.asistencia_asambleas import AsistenciaAsambleas


class IRepositorioAsistencia(Protocol):
    def crear(
        self, asistencia: AsistenciaAsambleas, usuario_sistema: str
    ) -> AsistenciaAsambleas: ...

    def obtener_por_id(self, id_asistencia: int) -> Optional[AsistenciaAsambleas]: ...

    def listar_por_propiedad(self, id_propiedad: int) -> List[AsistenciaAsambleas]: ...

    def listar_todas(
        self,
        filtro_estado: Optional[str] = None,
        filtro_fecha_desde: Optional[str] = None,
        filtro_fecha_hasta: Optional[str] = None,
    ) -> List[AsistenciaAsambleas]: ...

    def listar_todas_enriquecidas(
        self,
        filtro_estado: Optional[str] = None,
    ) -> List[dict]: ...

    def listar_por_mes_enriquecidas(
        self,
        año: int,
        mes: int,
    ) -> List[dict]: ...

    def actualizar_estado(
        self, id_asistencia: int, nuevo_estado: str, usuario_sistema: str
    ) -> bool: ...

    def actualizar(
        self, asistencia: AsistenciaAsambleas, usuario_sistema: str
    ) -> bool: ...

    def eliminar(self, id_asistencia: int) -> bool: ...

