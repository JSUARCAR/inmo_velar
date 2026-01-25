"""
Repositorio SQLite para Auditoría de Cambios.
Implementa mapeo con tabla AUDITORIA_CAMBIOS.
"""

import sqlite3
from typing import List

from src.dominio.entidades.auditoria_cambio import AuditoriaCambio
from src.infraestructura.persistencia.database import DatabaseManager


class RepositorioAuditoriaSQLite:
    """Repositorio SQLite para la entidad AuditoriaCambio."""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def _row_to_entity(self, row: sqlite3.Row) -> AuditoriaCambio:
        """Convierte una fila SQL a entidad AuditoriaCambio."""

        # Manejar tanto sqlite3.Row como dict (PostgreSQL)

        if row is None:

            return None

        # Convertir a dict si es necesario

        if hasattr(row, "keys"):

            row_dict = dict(row)

        else:

            row_dict = row

        return AuditoriaCambio(
            id_auditoria=(row_dict.get("id_auditoria") or row_dict.get("ID_AUDITORIA")),
            tabla=(row_dict.get("tabla") or row_dict.get("TABLA")),
            id_registro=(row_dict.get("id_registro") or row_dict.get("ID_REGISTRO")),
            accion=(row_dict.get("tipo_operacion") or row_dict.get("TIPO_OPERACION")),
            campo=(row_dict.get("campo_modificado") or row_dict.get("CAMPO_MODIFICADO")),
            valor_anterior=(row_dict.get("valor_anterior") or row_dict.get("VALOR_ANTERIOR")),
            valor_nuevo=(row_dict.get("valor_nuevo") or row_dict.get("VALOR_NUEVO")),
            usuario=(row_dict.get("usuario") or row_dict.get("USUARIO")),
            fecha_cambio=(row_dict.get("fecha_cambio") or row_dict.get("FECHA_CAMBIO")),
            motivo_cambio=(row_dict.get("motivo_cambio") or row_dict.get("MOTIVO_CAMBIO")),
            ip_origen=(row_dict.get("ip_origen") or row_dict.get("IP_ORIGEN")),
        )

    def listar_todos(self, limit: int = 100, offset: int = 0) -> List[AuditoriaCambio]:
        """
        Lista los registros de auditoría paginados.
        Ordenados por fecha descendente (lo más reciente primero).
        """
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        placeholder = self.db.get_placeholder()

        cursor.execute(
            f"""
            SELECT * FROM AUDITORIA_CAMBIOS
            ORDER BY ID_AUDITORIA DESC
            LIMIT {placeholder} OFFSET {placeholder}
            """,
            (limit, offset),
        )

        return [self._row_to_entity(row) for row in cursor.fetchall()]

    def buscar_por_tabla(self, tabla: str, limit: int = 100) -> List[AuditoriaCambio]:
        """Busca auditoría por tabla."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        placeholder = self.db.get_placeholder()

        cursor.execute(
            f"""
            SELECT * FROM AUDITORIA_CAMBIOS
            WHERE TABLA LIKE {placeholder}
            ORDER BY ID_AUDITORIA DESC
            LIMIT {placeholder}
            """,
            (f"%{tabla}%", limit),
        )

        return [self._row_to_entity(row) for row in cursor.fetchall()]
