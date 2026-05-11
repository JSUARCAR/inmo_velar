from datetime import datetime
import sqlite3
from typing import List, Optional

from src.dominio.entidades.auditoria_cambio import AuditoriaCambio
from src.dominio.interfaces.repositorio_auditoria import RepositorioAuditoria
from src.infraestructura.persistencia.database import DatabaseManager


class RepositorioAuditoriaSQLite(RepositorioAuditoria):
    """Repositorio SQLite para la entidad AuditoriaCambio."""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def _row_to_entity(self, row: sqlite3.Row) -> AuditoriaCambio:
        """Convierte una fila SQL a entidad AuditoriaCambio."""
        if row is None:
            return None

        row_dict = dict(row) if hasattr(row, "keys") else row

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
    ) -> int:
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        p = self.db.get_placeholder()

        sql = f"""
            INSERT INTO AUDITORIA_CAMBIOS 
            (TABLA, ID_REGISTRO, TIPO_OPERACION, VALOR_ANTERIOR, VALOR_NUEVO, USUARIO, MOTIVO_CAMBIO, CAMPO_MODIFICADO, FECHA_CAMBIO)
            VALUES ({p}, {p}, {p}, {p}, {p}, {p}, {p}, {p}, {p})
        """
        params = (
            tabla,
            id_registro,
            tipo_operacion,
            valor_anterior,
            valor_nuevo,
            usuario,
            motivo_cambio,
            campo_modificado,
            datetime.now().isoformat(),
        )
        
        cursor.execute(sql, params)
        id_gen = cursor.lastrowid
        conn.commit()
        return id_gen

    def buscar_por_tabla(self, tabla: str, limit: int = 50) -> List[AuditoriaCambio]:
        """Busca auditoría por tabla."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        p = self.db.get_placeholder()
        
        query = f"SELECT * FROM AUDITORIA_CAMBIOS WHERE TABLA = {p} ORDER BY FECHA_CAMBIO DESC LIMIT {p}"
        cursor.execute(query, (tabla, limit))
        return [self._row_to_entity(row) for row in cursor.fetchall()]

    def obtener_por_registro(
        self, tabla: str, id_registro: int, limit: int = 50
    ) -> List[AuditoriaCambio]:
        """Busca auditoría por tabla y registro específico."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        p = self.db.get_placeholder()
        
        query = f"SELECT * FROM AUDITORIA_CAMBIOS WHERE TABLA = {p} AND ID_REGISTRO = {p} ORDER BY FECHA_CAMBIO DESC LIMIT {p}"
        cursor.execute(query, (tabla, id_registro, limit))
        return [self._row_to_entity(row) for row in cursor.fetchall()]

    def listar_todos(self, limit: int = 100, offset: int = 0) -> List[AuditoriaCambio]:
        """Lista registros de auditoría paginados."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        p = self.db.get_placeholder()
        
        query = f"SELECT * FROM AUDITORIA_CAMBIOS ORDER BY FECHA_CAMBIO DESC LIMIT {p} OFFSET {p}"
        cursor.execute(query, (limit, offset))
        return [self._row_to_entity(row) for row in cursor.fetchall()]

