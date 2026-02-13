"""
Repositorio SQLite para Propietario.
Implementa mapeo 1:1 estricto con tabla PROPIETARIOS.
"""

import sqlite3
from datetime import datetime
from typing import List, Optional

from src.dominio.entidades.propietario import Propietario
from src.infraestructura.persistencia.database import DatabaseManager


class RepositorioPropietarioSQLite:
    """Repositorio SQLite para la entidad Propietario."""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def _row_to_entity(self, row: sqlite3.Row) -> Propietario:
        """Convierte una fila SQL a entidad Propietario."""

        # Manejar tanto sqlite3.Row como dict (PostgreSQL)

        if row is None:

            return None

        # Convertir a dict si es necesario

        if hasattr(row, "keys"):

            row_dict = dict(row)

        else:

            row_dict = row

        return Propietario(
            id_propietario=(row_dict.get("id_propietario") or row_dict.get("ID_PROPIETARIO")),
            id_persona=(row_dict.get("id_persona") or row_dict.get("ID_PERSONA")),
            banco_propietario=(
                row_dict.get("banco_propietario") or row_dict.get("BANCO_PROPIETARIO")
            ),
            numero_cuenta_propietario=(
                row_dict.get("numero_cuenta_propietario")
                or row_dict.get("NUMERO_CUENTA_PROPIETARIO")
            ),
            tipo_cuenta=(row_dict.get("tipo_cuenta") or row_dict.get("TIPO_CUENTA")),
            observaciones_propietario=(
                row_dict.get("observaciones_propietario")
                or row_dict.get("OBSERVACIONES_PROPIETARIO")
            ),
            estado_propietario=(
                row_dict.get("estado_propietario") or row_dict.get("ESTADO_PROPIETARIO")
            ),
            fecha_ingreso_propietario=(
                row_dict.get("fecha_ingreso_propietario")
                or row_dict.get("FECHA_INGRESO_PROPIETARIO")
            ),
            consignatario=(
                row_dict.get("consignatario") or row_dict.get("CONSIGNATARIO")
            ),
            documento_consignatario=(
                row_dict.get("documento_consignatario")
                or row_dict.get("DOCUMENTO_CONSIGNATARIO")
            ),
            motivo_inactivacion=(
                row_dict.get("motivo_inactivacion") or row_dict.get("MOTIVO_INACTIVACION")
            ),
            created_at=(row_dict.get("created_at") or row_dict.get("CREATED_AT")),
            created_by=(row_dict.get("created_by") or row_dict.get("CREATED_BY")),
            updated_at=(row_dict.get("updated_at") or row_dict.get("UPDATED_AT")),
            updated_by=(row_dict.get("updated_by") or row_dict.get("UPDATED_BY")),
        )

    def obtener_por_id(self, id_propietario: int) -> Optional[Propietario]:
        """Obtiene un propietario por su ID."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        placeholder = self.db.get_placeholder()

        cursor.execute(
            f"SELECT * FROM PROPIETARIOS WHERE ID_PROPIETARIO = {placeholder}", (id_propietario,)
        )

        row = cursor.fetchone()
        return self._row_to_entity(row) if row else None

    def obtener_por_persona(self, id_persona: int) -> Optional[Propietario]:
        """Obtiene un propietario por ID de persona."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        placeholder = self.db.get_placeholder()

        cursor.execute(
            f"SELECT * FROM PROPIETARIOS WHERE ID_PERSONA = {placeholder}", (id_persona,)
        )

        row = cursor.fetchone()
        return self._row_to_entity(row) if row else None

    def listar_activos(self) -> List[Propietario]:
        """Lista todos los propietarios activos."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        self.db.get_placeholder()

        cursor.execute("SELECT * FROM PROPIETARIOS WHERE ESTADO_PROPIETARIO = 1")

        return [self._row_to_entity(row) for row in cursor.fetchall()]

    def crear(self, propietario: Propietario, usuario_sistema: str) -> Propietario:
        """Crea un nuevo propietario."""
        with self.db.obtener_conexion() as conn:
            cursor = conn.cursor()
            placeholder = self.db.get_placeholder()

            cursor.execute(
                f"""
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
                ) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
                """,
                (
                    propietario.id_persona,
                    propietario.banco_propietario,
                    propietario.numero_cuenta_propietario,
                    propietario.tipo_cuenta,
                    propietario.observaciones_propietario,
                    (
                        bool(propietario.estado_propietario)
                        if propietario.estado_propietario is not None
                        else True
                    ),
                    propietario.fecha_ingreso_propietario or datetime.now().isoformat(),
                    propietario.consignatario,
                    propietario.documento_consignatario,
                    datetime.now().isoformat(),
                    usuario_sistema,
                ),
            )

            conn.commit()
            propietario.id_propietario = self.db.get_last_insert_id(
                cursor, "PROPIETARIOS", "ID_PROPIETARIO"
            )

            return propietario

    def actualizar(self, propietario: Propietario, usuario_sistema: str) -> bool:
        """Actualiza un propietario existente."""
        with self.db.obtener_conexion() as conn:
            cursor = conn.cursor()
            placeholder = self.db.get_placeholder()

            cursor.execute(
                f"""
                UPDATE PROPIETARIOS SET
                    BANCO_PROPIETARIO = {placeholder},
                    NUMERO_CUENTA_PROPIETARIO = {placeholder},
                    TIPO_CUENTA = {placeholder},
                    OBSERVACIONES_PROPIETARIO = {placeholder},
                    CONSIGNATARIO = {placeholder},
                    DOCUMENTO_CONSIGNATARIO = {placeholder},
                    ESTADO_PROPIETARIO = {placeholder},
                    UPDATED_AT = {placeholder},
                    UPDATED_BY = {placeholder}
                WHERE ID_PROPIETARIO = {placeholder}
                """,
                (
                    propietario.banco_propietario,
                    propietario.numero_cuenta_propietario,
                    propietario.tipo_cuenta,
                    propietario.observaciones_propietario,
                    propietario.consignatario,
                    propietario.documento_consignatario,
                    (
                        bool(propietario.estado_propietario)
                        if propietario.estado_propietario is not None
                        else True
                    ),
                    datetime.now().isoformat(),
                    usuario_sistema,
                    propietario.id_propietario,
                ),
            )

            conn.commit()
            return cursor.rowcount > 0

    def eliminar_por_persona(self, id_persona: int) -> bool:
        """Elimina físicamente el registro de propietario asociado a una persona."""
        with self.db.obtener_conexion() as conn:
            cursor = conn.cursor()
            placeholder = self.db.get_placeholder()

            cursor.execute(f"DELETE FROM PROPIETARIOS WHERE ID_PERSONA = {placeholder}", (id_persona,))
            conn.commit()
            return cursor.rowcount > 0
