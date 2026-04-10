"""
Interface (Protocol): Repositorio de Pagos de Administración
"""

from typing import List, Optional, Protocol, Dict, Any
from src.dominio.entidades.pagos_administracion import PagosAdministracion


class IRepositorioPagosAdmin(Protocol):
    def crear(
        self, pago: PagosAdministracion, usuario_sistema: str
    ) -> PagosAdministracion: ...

    def obtener_por_id(self, id_pago: int) -> Optional[PagosAdministracion]: ...

    def obtener_por_periodo(self, periodo: str) -> List[PagosAdministracion]: ...

    def obtener_por_propiedad_y_periodo(
        self, id_propiedad: int, periodo: str
    ) -> Optional[PagosAdministracion]: ...

    def listar(
        self,
        filtro_periodo: Optional[str] = None,
        filtro_estado: Optional[str] = None,
        filtro_propiedad: Optional[int] = None,
        filtro_nombre: Optional[str] = None,
    ) -> List[PagosAdministracion]: ...

    def marcar_pagado(self, id_pago: int, usuario_sistema: str) -> bool: ...

    def marcar_vencido(self, id_pago: int) -> bool: ...

    def actualizar(self, pago: PagosAdministracion, usuario_sistema: str) -> bool: ...

    def obtener_elegibles(self) -> List[Dict[str, Any]]:
        """Retorna propiedades con contrato mandato activo y valor_admin."""
        ...
