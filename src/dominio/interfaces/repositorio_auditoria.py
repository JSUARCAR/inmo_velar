from typing import List, Optional
from src.dominio.entidades.auditoria_cambio import AuditoriaCambio


class RepositorioAuditoria:
    """
    Interface para operaciones de auditoría de cambios del sistema.
    """

    def guardar_cambio(
        self,
        tabla: str,
        id_registro: int,
        tipo_operacion: str,
        valor_anterior: Optional[str],
        valor_nuevo: Optional[str],
        usuario: str,
        motivo_cambio: str,
        campo_modificado: Optional[str] = None,
    ) -> int: ...

    def buscar_por_tabla(self, tabla: str, limit: int = 50) -> List[AuditoriaCambio]: ...

    def obtener_por_registro(
        self, tabla: str, id_registro: int, limit: int = 50
    ) -> List[AuditoriaCambio]: ...

    def listar_todos(self, limit: int = 100, offset: int = 0) -> List[AuditoriaCambio]: ...

