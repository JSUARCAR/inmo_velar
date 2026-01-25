"""
Repositorio SQLite para Codeudor.
Implementa mapeo 1:1 estricto con tabla CODEUDORES.
"""

import sqlite3
from datetime import datetime
from typing import List, Optional

from src.dominio.entidades.codeudor import Codeudor
from src.infraestructura.persistencia.database import DatabaseManager


class RepositorioCodeudorSQLite:
    """Repositorio SQLite para la entidad Codeudor."""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def _row_to_entity(self, row: sqlite3.Row) -> Codeudor:
        """Convierte una fila SQL a entidad Codeudor."""

        # Manejar tanto sqlite3.Row como dict (PostgreSQL)

        if row is None:

            return None

        # Convertir a dict si es necesario

        if hasattr(row, "keys"):

            row_dict = dict(row)

        else:

            row_dict = row

        return Codeudor(
            id_codeudor=(row_dict.get("id_codeudor") or row_dict.get("ID_CODEUDOR")),
            id_persona=(row_dict.get("id_persona") or row_dict.get("ID_PERSONA")),
            fecha_ingreso_codeudor=(
                row_dict.get("fecha_ingreso_codeudor") or row_dict.get("FECHA_INGRESO_CODEUDOR")
            ),
            estado_registro=(row_dict.get("estado_registro") or row_dict.get("ESTADO_REGISTRO")),
            motivo_inactivacion=(
                row_dict.get("motivo_inactivacion") or row_dict.get("MOTIVO_INACTIVACION")
            ),
            created_at=(row_dict.get("created_at") or row_dict.get("CREATED_AT")),
            created_by=(row_dict.get("created_by") or row_dict.get("CREATED_BY")),
        )

    def obtener_por_id(self, id_codeudor: int) -> Optional[Codeudor]:
        """Obtiene un codeudor por su ID."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        placeholder = self.db.get_placeholder()

        cursor.execute(
            f"SELECT * FROM CODEUDORES WHERE ID_CODEUDOR = {placeholder}", (id_codeudor,)
        )

        row = cursor.fetchone()
        return self._row_to_entity(row) if row else None

    def obtener_por_persona(self, id_persona: int) -> Optional[Codeudor]:
        """Obtiene un codeudor por ID de persona."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        placeholder = self.db.get_placeholder()

        cursor.execute(f"SELECT * FROM CODEUDORES WHERE ID_PERSONA = {placeholder}", (id_persona,))

        row = cursor.fetchone()
        return self._row_to_entity(row) if row else None

    def listar_activos(self) -> List[Codeudor]:
        """Lista todos los codeudores activos."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        self.db.get_placeholder()

        cursor.execute("SELECT * FROM CODEUDORES WHERE ESTADO_REGISTRO = TRUE")

        return [self._row_to_entity(row) for row in cursor.fetchall()]

    def crear(self, codeudor: Codeudor, usuario_sistema: str) -> Codeudor:
        """Crea un nuevo codeudor."""
        with self.db.obtener_conexion() as conn:
            cursor = conn.cursor()
            placeholder = self.db.get_placeholder()

            cursor.execute(
                f"""
                INSERT INTO CODEUDORES (
                    ID_PERSONA,
                    FECHA_INGRESO_CODEUDOR,
                    ESTADO_REGISTRO,
                    CREATED_AT,
                    CREATED_BY
                ) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
                """,
                (
                    codeudor.id_persona,
                    codeudor.fecha_ingreso_codeudor or datetime.now().isoformat(),
                    (
                        bool(codeudor.estado_registro)
                        if codeudor.estado_registro is not None
                        else True
                    ),
                    datetime.now().isoformat(),
                    usuario_sistema,
                ),
            )

            conn.commit()
            codeudor.id_codeudor = self.db.get_last_insert_id(cursor, "CODEUDORES", "ID_CODEUDOR")

            return codeudor

    def inactivar(self, id_codeudor: int, motivo: str, usuario_sistema: str) -> bool:
        """Inactiva un codeudor (soft delete)."""
        with self.db.obtener_conexion() as conn:
            cursor = conn.cursor()
            placeholder = self.db.get_placeholder()

            cursor.execute(
                f"""
                UPDATE CODEUDORES SET
                    ESTADO_REGISTRO = FALSE,
                    MOTIVO_INACTIVACION = {placeholder}
                WHERE ID_CODEUDOR = {placeholder}
                """,
                (motivo, id_codeudor),
            )

            conn.commit()
            return cursor.rowcount > 0

    def eliminar_por_persona(self, id_persona: int) -> bool:
        """Elimina físicamente el registro de codeudor asociado a una persona."""
        with self.db.obtener_conexion() as conn:
            cursor = conn.cursor()
            placeholder = self.db.get_placeholder()

            cursor.execute(f"DELETE FROM CODEUDORES WHERE ID_PERSONA = {placeholder}", (id_persona,))
            conn.commit()
            return cursor.rowcount > 0
