from datetime import datetime
from typing import List, Optional

from src.dominio.entidades.auditoria_cambio import AuditoriaCambio
from src.dominio.interfaces.repositorio_auditoria import RepositorioAuditoria
from src.infraestructura.persistencia.database import DatabaseManager


class RepositorioAuditoriaPostgres(RepositorioAuditoria):
    def __init__(self, db: DatabaseManager):
        self.db = db

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
        query = """
            INSERT INTO AUDITORIA_CAMBIOS 
            (TABLA, ID_REGISTRO, TIPO_OPERACION, VALOR_ANTERIOR, VALOR_NUEVO, USUARIO, MOTIVO_CAMBIO, CAMPO_MODIFICADO, FECHA_CAMBIO)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING ID_AUDITORIA
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
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        cursor.execute(query, params)
        row = cursor.fetchone()
        conn.commit()
        if row:
            if isinstance(row, dict): return row.get("ID_AUDITORIA") or row.get("id_auditoria")
            return row[0]
    def buscar_por_tabla(self, tabla: str, limit: int = 50) -> List[AuditoriaCambio]:
        query = "SELECT * FROM AUDITORIA_CAMBIOS WHERE TABLA = %s ORDER BY FECHA_CAMBIO DESC LIMIT %s"
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        cursor.execute(query, (tabla, limit))
        return [self._row_to_entity(row) for row in cursor.fetchall()]

    def obtener_por_registro(
        self, tabla: str, id_registro: int, limit: int = 50
    ) -> List[AuditoriaCambio]:
        query = "SELECT * FROM AUDITORIA_CAMBIOS WHERE TABLA = %s AND ID_REGISTRO = %s ORDER BY FECHA_CAMBIO DESC LIMIT %s"
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        cursor.execute(query, (tabla, id_registro, limit))
        return [self._row_to_entity(row) for row in cursor.fetchall()]

    def listar_todos(self, limit: int = 100, offset: int = 0) -> List[AuditoriaCambio]:
        query = "SELECT * FROM AUDITORIA_CAMBIOS ORDER BY FECHA_CAMBIO DESC LIMIT %s OFFSET %s"
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        cursor.execute(query, (limit, offset))
        return [self._row_to_entity(row) for row in cursor.fetchall()]

    def _row_to_entity(self, row) -> AuditoriaCambio:
        if row is None:
            return None
        row_dict = dict(row)
        return AuditoriaCambio(
            id_auditoria=row_dict.get("ID_AUDITORIA") or row_dict.get("id_auditoria"),
            tabla=row_dict.get("TABLA") or row_dict.get("tabla"),
            id_registro=row_dict.get("ID_REGISTRO") or row_dict.get("id_registro"),
            accion=row_dict.get("TIPO_OPERACION") or row_dict.get("tipo_operacion"),
            campo=row_dict.get("CAMPO_MODIFICADO") or row_dict.get("campo_modificado"),
            valor_anterior=row_dict.get("VALOR_ANTERIOR") or row_dict.get("valor_anterior"),
            valor_nuevo=row_dict.get("VALOR_NUEVO") or row_dict.get("valor_nuevo"),
            usuario=row_dict.get("USUARIO") or row_dict.get("usuario"),
            fecha_cambio=row_dict.get("FECHA_CAMBIO") or row_dict.get("fecha_cambio"),
            motivo_cambio=row_dict.get("MOTIVO_CAMBIO") or row_dict.get("motivo_cambio"),
            ip_origen=row_dict.get("IP_ORIGEN") or row_dict.get("ip_origen"),
        )

