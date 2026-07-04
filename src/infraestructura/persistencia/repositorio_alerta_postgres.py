"""
Repositorio PostgreSQL para Alertas.
==================================
Implementa la persistencia de alertas en PostgreSQL mapeando a la tabla ALERTAS.

Autor: Sistema de Gestión Inmobiliaria
Fecha: 2026-05-10
"""

import logging
from datetime import datetime
from typing import List, Optional

from src.dominio.entidades.alerta import Alerta
from src.infraestructura.persistencia.database import DatabaseManager

logger = logging.getLogger(__name__)


class RepositorioAlertaPostgres:
    """
    Repositorio PostgreSQL para la entidad Alerta.
    """

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def _row_to_entity(self, row) -> Alerta:
        """Convierte una fila SQL a entidad Alerta."""
        if row is None:
            return None

        row_dict = dict(row)

        def _date_to_str(val):
            if isinstance(val, datetime):
                return val.isoformat()
            elif hasattr(val, "isoformat"):
                return val.isoformat()
            return str(val) if val else None

        return Alerta(
            id_alertas=row_dict.get("ID_ALERTAS"),
            tipo_alerta=row_dict.get("TIPO_ALERTA"),
            descripcion_alerta=row_dict.get("DESCRIPCION_ALERTA"),
            prioridad=row_dict.get("PRIORIDAD", "Media"),
            fecha_generacion_alerta=_date_to_str(
                row_dict.get("FECHA_GENERACION_ALERTA")
            ),
            fecha_vencimiento_alerta=_date_to_str(
                row_dict.get("FECHA_VENCIMIENTO_ALERTA")
            ),
            estado_alerta=row_dict.get("ESTADO_ALERTA", "Pendiente"),
            id_entidad_relacionada=row_dict.get("ID_ENTIDAD_RELACIONADA"),
            tipo_entidad=row_dict.get("TIPO_ENTIDAD"),
            usuario_asignado=row_dict.get("USUARIO_ASIGNADO"),
            accion_tomada=row_dict.get("ACCION_TOMADA"),
            fecha_accion=_date_to_str(row_dict.get("FECHA_ACCION")),
            plantilla_mensaje=row_dict.get("PLANTILLA_MENSAJE"),
            destinatario_nombre=row_dict.get("DESTINATARIO_NOMBRE"),
            destinatario_telefono=row_dict.get("DESTINATARIO_TELEFONO"),
            destinatario_email=row_dict.get("DESTINATARIO_EMAIL"),
            fecha_resolucion=_date_to_str(row_dict.get("FECHA_RESOLUCION")),
            resuelto_automaticamente=bool(
                row_dict.get("RESUELTO_AUTOMATICAMENTE", False)
            ),
            created_at=_date_to_str(row_dict.get("CREATED_AT")),
            created_by=row_dict.get("CREATED_BY"),
        )

    def obtener_por_id(self, id_alerta: int) -> Optional[Alerta]:
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)

        cursor.execute("SELECT * FROM ALERTAS WHERE ID_ALERTAS = %s", (id_alerta,))
        return self._row_to_entity(cursor.fetchone())

    def obtener_todas(
        self,
        estado: Optional[str] = None,
        prioridad: Optional[str] = None,
        tipo: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
    ) -> List[Alerta]:
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)

        query = "SELECT * FROM ALERTAS"
        conditions = []
        params = []

        if estado:
            conditions.append("ESTADO_ALERTA = %s")
            params.append(estado)
        if prioridad:
            conditions.append("PRIORIDAD = %s")
            params.append(prioridad)
        if tipo:
            conditions.append("TIPO_ALERTA = %s")
            params.append(tipo)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        limit_val = max(0, int(limit)) if limit is not None else 50
        offset_val = max(0, int(offset)) if offset is not None else 0

        query += " ORDER BY FECHA_GENERACION_ALERTA DESC LIMIT %s OFFSET %s"
        params.extend([limit_val, offset_val])

        cursor.execute(query, params)
        return [self._row_to_entity(row) for row in cursor.fetchall()]

    def contar_todas(
        self,
        estado: Optional[str] = None,
        prioridad: Optional[str] = None,
        tipo: Optional[str] = None,
    ) -> int:
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)

        query = "SELECT COUNT(*) as total FROM ALERTAS"
        conditions = []
        params = []

        if estado:
            conditions.append("ESTADO_ALERTA = %s")
            params.append(estado)
        if prioridad:
            conditions.append("PRIORIDAD = %s")
            params.append(prioridad)
        if tipo:
            conditions.append("TIPO_ALERTA = %s")
            params.append(tipo)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        cursor.execute(query, params)
        row = cursor.fetchone()
        return row["TOTAL"] if row else 0

    def obtener_por_entidad_y_tipo(
        self,
        id_entidad: Optional[int],
        tipo_entidad: str,
        tipo_alerta: str,
        solo_pendientes: bool = True,
    ) -> Optional[Alerta]:
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)

        query = "SELECT * FROM ALERTAS WHERE TIPO_ENTIDAD = %s AND TIPO_ALERTA = %s"
        params = [tipo_entidad, tipo_alerta]

        if id_entidad is None:
            query += " AND ID_ENTIDAD_RELACIONADA IS NULL"
        else:
            query += " AND ID_ENTIDAD_RELACIONADA = %s"
            params.append(id_entidad)

        if solo_pendientes:
            query += " AND ESTADO_ALERTA IN ('Pendiente', 'En Proceso')"
        else:
            # Si no es solo pendientes, buscamos las más recientes
            query += " ORDER BY FECHA_GENERACION_ALERTA DESC"

        cursor.execute(query, params)
        return self._row_to_entity(cursor.fetchone())

    def guardar(self, alerta: Alerta, usuario_sistema: str) -> Alerta:
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)

        sql = """
            INSERT INTO ALERTAS (
                TIPO_ALERTA, DESCRIPCION_ALERTA, PRIORIDAD, 
                FECHA_GENERACION_ALERTA, FECHA_VENCIMIENTO_ALERTA, ESTADO_ALERTA,
                ID_ENTIDAD_RELACIONADA, TIPO_ENTIDAD, DESTINATARIO_NOMBRE,
                DESTINATARIO_TELEFONO, DESTINATARIO_EMAIL, CREATED_BY
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING ID_ALERTAS
        """
        params = (
            alerta.tipo_alerta,
            alerta.descripcion_alerta,
            alerta.prioridad,
            alerta.fecha_generacion_alerta or datetime.now().isoformat(),
            alerta.fecha_vencimiento_alerta,
            alerta.estado_alerta,
            alerta.id_entidad_relacionada,
            alerta.tipo_entidad,
            alerta.destinatario_nombre,
            alerta.destinatario_telefono,
            alerta.destinatario_email,
            usuario_sistema,
        )

        cursor.execute(sql, params)
        row = cursor.fetchone()
        if row:
            alerta.id_alertas = row.get("ID_ALERTAS")
        conn.commit()
        return alerta

    def actualizar(self, alerta: Alerta, usuario_sistema: str) -> bool:
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)

        sql = """
            UPDATE ALERTAS SET
                ESTADO_ALERTA = %s, ACCION_TOMADA = %s, FECHA_ACCION = %s,
                USUARIO_ASIGNADO = %s, FECHA_RESOLUCION = %s, 
                RESUELTO_AUTOMATICAMENTE = %s
            WHERE ID_ALERTAS = %s
        """
        params = (
            alerta.estado_alerta,
            alerta.accion_tomada,
            alerta.fecha_accion,
            alerta.usuario_asignado,
            alerta.fecha_resolucion,
            bool(alerta.resuelto_automaticamente),
            alerta.id_alertas,
        )

        cursor.execute(sql, params)
        conn.commit()
        return cursor.rowcount > 0

    def marcar_resuelta(
        self,
        id_alerta: int,
        usuario_sistema: str,
        accion: str,
        automatica: bool = False,
    ) -> bool:
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)

        ahora = datetime.now().isoformat()
        sql = """
            UPDATE ALERTAS SET
                ESTADO_ALERTA = 'Resuelta',
                ACCION_TOMADA = %s,
                FECHA_ACCION = %s,
                FECHA_RESOLUCION = %s,
                RESUELTO_AUTOMATICAMENTE = %s
            WHERE ID_ALERTAS = %s
        """
        params = (accion, ahora, ahora, bool(automatica), id_alerta)

        cursor.execute(sql, params)
        conn.commit()
        return cursor.rowcount > 0

    def eliminar(self, id_alerta: int) -> bool:
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        cursor.execute("DELETE FROM ALERTAS WHERE ID_ALERTAS = %s", (id_alerta,))
        conn.commit()
        return cursor.rowcount > 0
