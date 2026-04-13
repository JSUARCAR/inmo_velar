"""
Repositorio PostgreSQL para Propietario.
Implementa mapeo 1:1 estricto con tabla PROPIETARIOS.
"""

from datetime import datetime
from typing import List, Optional
import logging

from src.dominio.entidades.propietario import Propietario
from src.infraestructura.persistencia.database import DatabaseManager

logger = logging.getLogger(__name__)

class RepositorioPropietarioPostgres:
    """Repositorio PostgreSQL para la entidad Propietario."""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def _row_to_entity(self, row) -> Propietario:
        """Convierte una fila SQL a entidad Propietario."""
        if row is None:
            return None

        row_dict = dict(row)

        return Propietario(
            id_propietario=row_dict.get("ID_PROPIETARIO"),
            id_persona=row_dict.get("ID_PERSONA"),
            banco_propietario=row_dict.get("BANCO_PROPIETARIO"),
            numero_cuenta_propietario=row_dict.get("NUMERO_CUENTA_PROPIETARIO"),
            tipo_cuenta=row_dict.get("TIPO_CUENTA"),
            observaciones_propietario=row_dict.get("OBSERVACIONES_PROPIETARIO"),
            estado_propietario=row_dict.get("ESTADO_PROPIETARIO"),
            fecha_ingreso_propietario=row_dict.get("FECHA_INGRESO_PROPIETARIO"),
            consignatario=row_dict.get("CONSIGNATARIO"),
            documento_consignatario=row_dict.get("DOCUMENTO_CONSIGNATARIO"),
            motivo_inactivacion=row_dict.get("MOTIVO_INACTIVACION"),
            created_at=row_dict.get("CREATED_AT"),
            created_by=row_dict.get("CREATED_BY"),
            updated_at=row_dict.get("UPDATED_AT"),
            updated_by=row_dict.get("UPDATED_BY"),
        )

    def obtener_por_id(self, id_propietario: int) -> Optional[Propietario]:
        """Obtiene un propietario por su ID."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)

        cursor.execute(
            "SELECT * FROM PROPIETARIOS WHERE ID_PROPIETARIO = %s", (id_propietario,)
        )

        row = cursor.fetchone()
        return self._row_to_entity(row) if row else None

    def obtener_por_persona(self, id_persona: int) -> Optional[Propietario]:
        """Obtiene un propietario por ID de persona."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)

        cursor.execute(
            "SELECT * FROM PROPIETARIOS WHERE ID_PERSONA = %s", (id_persona,)
        )

        row = cursor.fetchone()
        return self._row_to_entity(row) if row else None

    def listar_activos(self) -> List[Propietario]:
        """Lista todos los propietarios activos."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)

        cursor.execute("SELECT * FROM PROPIETARIOS WHERE ESTADO_PROPIETARIO = TRUE")

        return [self._row_to_entity(row) for row in cursor.fetchall()]

    def crear(self, propietario: Propietario, usuario_sistema: str) -> Propietario:
        """Crea un nuevo propietario con RETURNING id (PostgreSQL)."""
        logger.debug(f"Ejecutando crear propietario (Postgres): id_persona={propietario.id_persona}")
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO PROPIETARIOS (
                ID_PERSONA,
                BANCO_PROPIETARIO,
                NUMERO_CUENTA_PROPIETARIO,
                TIPO_CUENTA,
                OBSERVACIONES_PROPIETARIO,
                ESTADO_PROPIETARIO,
                FECHA_INGRESO_PROPIETARIO,
                CONSIGNATARIO,
                DOCUMENTO_CONSIGNATARIO,
                CREATED_AT,
                CREATED_BY
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING ID_PROPIETARIO
            """,
            (
                propietario.id_persona,
                propietario.banco_propietario,
                propietario.numero_cuenta_propietario,
                propietario.tipo_cuenta,
                propietario.observaciones_propietario,
                bool(propietario.estado_propietario) if propietario.estado_propietario is not None else True,
                propietario.fecha_ingreso_propietario or datetime.now().isoformat(),
                propietario.consignatario,
                propietario.documento_consignatario,
                datetime.now().isoformat(),
                usuario_sistema,
            ),
        )

        row = cursor.fetchone()
        if row:
            if isinstance(row, dict):
                propietario.id_propietario = row["ID_PROPIETARIO"]
            else:
                propietario.id_propietario = row[0]

        conn.commit()
        return propietario

    def actualizar(self, propietario: Propietario, usuario_sistema: str) -> bool:
        """Actualiza un propietario existente en PostgreSQL."""
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()

        cursor.execute(
            """
            UPDATE PROPIETARIOS SET
                BANCO_PROPIETARIO = %s,
                NUMERO_CUENTA_PROPIETARIO = %s,
                TIPO_CUENTA = %s,
                OBSERVACIONES_PROPIETARIO = %s,
                CONSIGNATARIO = %s,
                DOCUMENTO_CONSIGNATARIO = %s,
                ESTADO_PROPIETARIO = %s,
                UPDATED_AT = %s,
                UPDATED_BY = %s
            WHERE ID_PROPIETARIO = %s
            """,
            (
                propietario.banco_propietario,
                propietario.numero_cuenta_propietario,
                propietario.tipo_cuenta,
                propietario.observaciones_propietario,
                propietario.consignatario,
                propietario.documento_consignatario,
                bool(propietario.estado_propietario) if propietario.estado_propietario is not None else True,
                datetime.now().isoformat(),
                usuario_sistema,
                propietario.id_propietario,
            ),
        )

        conn.commit()
        return cursor.rowcount > 0

    def eliminar_por_persona(self, id_persona: int) -> bool:
        """Elimina físicamente el registro de propietario asociado a una persona (Postgres)."""
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM PROPIETARIOS WHERE ID_PERSONA = %s", (id_persona,))
        conn.commit()
        return cursor.rowcount > 0
