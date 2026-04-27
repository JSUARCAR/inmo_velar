"""
Repositorio PostgreSQL para la entidad Seguro.
Implementa el acceso a datos de seguros de arrendamiento.
"""

from datetime import datetime
from typing import List, Optional
import logging

from src.dominio.entidades.seguro import Seguro
from src.infraestructura.persistencia.database import DatabaseManager

logger = logging.getLogger(__name__)

class RepositorioSeguroPostgres:
    """
    Repositorio para gestionar seguros en PostgreSQL.
    """

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def crear(self, seguro: Seguro, usuario_sistema: str) -> Seguro:
        """Crea un nuevo seguro con RETURNING id (PostgreSQL)."""
        logger.debug(f"Ejecutando crear seguro (Postgres): nombre={seguro.nombre_seguro}")
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()

        ahora = datetime.now().isoformat()

        cursor.execute(
            """
            INSERT INTO SEGUROS (
                NOMBRE_SEGURO,
                FECHA_INICIO_SEGURO,
                PORCENTAJE_SEGURO,
                ESTADO_SEGURO,
                FECHA_INGRESO_SEGURO,
                CREATED_AT,
                CREATED_BY
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING ID_SEGURO
            """,
            (
                seguro.nombre_seguro,
                seguro.fecha_inicio_seguro,
                seguro.porcentaje_seguro,
                bool(seguro.estado_seguro) if seguro.estado_seguro is not None else True,
                seguro.fecha_ingreso_seguro or datetime.now().date().isoformat(),
                ahora,
                usuario_sistema,
            ),
        )

        row = cursor.fetchone()
        if row:
            if isinstance(row, dict):
                seguro.id_seguro = row["ID_SEGURO"]
            else:
                seguro.id_seguro = row[0]

        seguro.created_at = ahora
        seguro.created_by = usuario_sistema

        conn.commit()
        return seguro

    def obtener_por_id(self, id_seguro: int) -> Optional[Seguro]:
        """Obtiene un seguro por su ID en PostgreSQL."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)

        cursor.execute(
            "SELECT * FROM SEGUROS WHERE ID_SEGURO = %s", (id_seguro,)
        )

        row = cursor.fetchone()
        return self._row_a_seguro(row) if row else None

    def obtener_por_nombre(self, nombre_seguro: str) -> Optional[Seguro]:
        """Obtiene un seguro por su nombre en PostgreSQL."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)

        cursor.execute(
            "SELECT * FROM SEGUROS WHERE NOMBRE_SEGURO = %s", (nombre_seguro,)
        )

        row = cursor.fetchone()
        return self._row_a_seguro(row) if row else None

    def listar_todos(self, solo_activos: Optional[bool] = True) -> List[Seguro]:
        """Lista todos los seguros en PostgreSQL."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)

        query = "SELECT * FROM SEGUROS"
        params = []

        if solo_activos is not None:
            query += " WHERE ESTADO_SEGURO = %s"
            params.append(bool(solo_activos))

        query += " ORDER BY NOMBRE_SEGURO"

        cursor.execute(query, params)
        return [self._row_a_seguro(row) for row in cursor.fetchall()]

    def actualizar(self, seguro: Seguro, usuario_sistema: str) -> Seguro:
        """Actualiza un seguro existente en PostgreSQL."""
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()

        ahora = datetime.now().isoformat()

        cursor.execute(
            """
            UPDATE SEGUROS SET
                NOMBRE_SEGURO = %s,
                FECHA_INICIO_SEGURO = %s,
                PORCENTAJE_SEGURO = %s,
                ESTADO_SEGURO = %s,
                UPDATED_AT = %s,
                UPDATED_BY = %s
            WHERE ID_SEGURO = %s
            """,
            (
                seguro.nombre_seguro,
                seguro.fecha_inicio_seguro,
                seguro.porcentaje_seguro,
                bool(seguro.estado_seguro) if seguro.estado_seguro is not None else True,
                ahora,
                usuario_sistema,
                seguro.id_seguro,
            ),
        )

        seguro.updated_at = ahora
        seguro.updated_by = usuario_sistema

        conn.commit()
        return seguro

    def desactivar(self, id_seguro: int, motivo: str, usuario_sistema: str) -> bool:
        """Desactiva un seguro (soft delete) en PostgreSQL."""
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE SEGUROS SET
                ESTADO_SEGURO = FALSE,
                MOTIVO_INACTIVACION = %s,
                UPDATED_AT = %s,
                UPDATED_BY = %s
            WHERE ID_SEGURO = %s
            """,
            (motivo, datetime.now().isoformat(), usuario_sistema, id_seguro),
        )

        conn.commit()
        return cursor.rowcount > 0

    def _row_a_seguro(self, row) -> Seguro:
        """Convierte una fila de la BD a entidad Seguro."""
        if row is None:
            return None

        data = dict(row)

        return Seguro(
            id_seguro=data.get("ID_SEGURO"),
            nombre_seguro=data.get("NOMBRE_SEGURO"),
            fecha_inicio_seguro=data.get("FECHA_INICIO_SEGURO"),
            porcentaje_seguro=data.get("PORCENTAJE_SEGURO"),
            estado_seguro=data.get("ESTADO_SEGURO"),
            fecha_ingreso_seguro=data.get("FECHA_INGRESO_SEGURO"),
            motivo_inactivacion=data.get("MOTIVO_INACTIVACION"),
            created_at=data.get("CREATED_AT"),
            created_by=data.get("CREATED_BY"),
            updated_at=data.get("UPDATED_AT"),
            updated_by=data.get("UPDATED_BY"),
        )
