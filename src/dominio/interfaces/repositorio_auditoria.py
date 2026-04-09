from typing import Optional


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
    ) -> int: ...
