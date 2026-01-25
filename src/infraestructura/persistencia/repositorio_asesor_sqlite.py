"""
Repositorio SQLite para Asesor.
Implementa mapeo 1:1 estricto con tabla ASESORES.
"""

from datetime import datetime
from typing import List, Optional

from src.dominio.entidades.asesor import Asesor
from src.infraestructura.persistencia.database import DatabaseManager


class RepositorioAsesorSQLite:
    """Repositorio SQLite para la entidad Asesor."""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def _row_to_entity(self, row) -> Asesor:
        """Convierte una fila SQL a entidad Asesor."""
        # Manejar tanto sqlite3.Row como dict (PostgreSQL)
        if row is None:
            return None

        # Convertir a dict si es necesario
        if hasattr(row, "keys"):
            row_dict = dict(row)
        else:
            row_dict = row

        return Asesor(
            id_asesor=(row_dict.get("id_asesor") or row_dict.get("ID_ASESOR")),
            id_persona=(row_dict.get("id_persona") or row_dict.get("ID_PERSONA")),
            id_usuario=(row_dict.get("id_usuario") or row_dict.get("ID_USUARIO")),
            comision_porcentaje_arriendo=(
                row_dict.get("comision_porcentaje_arriendo")
                or row_dict.get("COMISION_PORCENTAJE_ARRIENDO")
            ),
            comision_porcentaje_venta=(
                row_dict.get("comision_porcentaje_venta")
                or row_dict.get("COMISION_PORCENTAJE_VENTA")
            ),
            fecha_ingreso=(row_dict.get("fecha_ingreso") or row_dict.get("FECHA_INGRESO")),
            estado=(row_dict.get("estado") or row_dict.get("ESTADO")),
            motivo_inactivacion=(
                row_dict.get("motivo_inactivacion") or row_dict.get("MOTIVO_INACTIVACION")
            ),
            created_at=(row_dict.get("created_at") or row_dict.get("CREATED_AT")),
            created_by=(row_dict.get("created_by") or row_dict.get("CREATED_BY")),
            updated_at=(row_dict.get("updated_at") or row_dict.get("UPDATED_AT")),
            updated_by=(row_dict.get("updated_by") or row_dict.get("UPDATED_BY")),
        )

    def obtener_por_id(self, id_asesor: int) -> Optional[Asesor]:
        """Obtiene un asesor por su ID."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        placeholder = self.db.get_placeholder()

        cursor.execute(f"SELECT * FROM ASESORES WHERE ID_ASESOR = {placeholder}", (id_asesor,))

        row = cursor.fetchone()
        return self._row_to_entity(row) if row else None

    def obtener_por_persona(self, id_persona: int) -> Optional[Asesor]:
        """Obtiene un asesor por ID de persona."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        placeholder = self.db.get_placeholder()

        cursor.execute(f"SELECT * FROM ASESORES WHERE ID_PERSONA = {placeholder}", (id_persona,))

        row = cursor.fetchone()
        return self._row_to_entity(row) if row else None

    def listar_activos(self) -> List[Asesor]:
        """Lista todos los asesores activos con sus datos personales."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        self.db.get_placeholder()

        cursor.execute(
            """
            SELECT a.*, p.NOMBRE_COMPLETO, p.NUMERO_DOCUMENTO
            FROM ASESORES a
            JOIN PERSONAS p ON a.ID_PERSONA = p.ID_PERSONA
            WHERE a.ESTADO = 1 
            ORDER BY p.NOMBRE_COMPLETO
        """
        )

        asesores = []
        for row in cursor.fetchall():
            asesor = self._row_to_entity(row)

            # Manejar row_dict para campos extra
            row_dict = dict(row) if hasattr(row, "keys") else row

            asesor.nombre_completo = row_dict.get("nombre_completo") or row_dict.get(
                "NOMBRE_COMPLETO"
            )
            asesores.append(asesor)
        return asesores

    def listar_todos(self) -> List[Asesor]:
        """Lista todos los asesores con sus datos personales."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        self.db.get_placeholder()

        cursor.execute(
            """
            SELECT a.*, p.NOMBRE_COMPLETO, p.NUMERO_DOCUMENTO
            FROM ASESORES a
            JOIN PERSONAS p ON a.ID_PERSONA = p.ID_PERSONA
            ORDER BY p.NOMBRE_COMPLETO
        """
        )

        asesores = []
        for row in cursor.fetchall():
            asesor = self._row_to_entity(row)

            # Manejar row_dict para campos extra
            row_dict = dict(row) if hasattr(row, "keys") else row

            asesor.nombre_completo = row_dict.get("nombre_completo") or row_dict.get(
                "NOMBRE_COMPLETO"
            )
            asesores.append(asesor)
        return asesores

    def crear(self, asesor: Asesor, usuario_sistema: str) -> Asesor:
        """Crea un nuevo asesor."""
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        placeholder = self.db.get_placeholder()

        cursor.execute(
            f"""
                INSERT INTO ASESORES (
                    ID_PERSONA,
                    ID_USUARIO,
                    COMISION_PORCENTAJE_ARRIENDO,
                    COMISION_PORCENTAJE_VENTA,
                    FECHA_INGRESO,
                    ESTADO,
                    CREATED_AT,
                    CREATED_BY
                ) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
                """,
            (
                asesor.id_persona,
                asesor.id_usuario,
                asesor.comision_porcentaje_arriendo,
                asesor.comision_porcentaje_venta,
                asesor.fecha_ingreso or datetime.now().isoformat(),
                bool(asesor.estado) if asesor.estado is not None else True,
                datetime.now().isoformat(),
                usuario_sistema,
            ),
        )

        conn.commit()
        asesor.id_asesor = self.db.get_last_insert_id(cursor, "ASESORES", "ID_ASESOR")

        return asesor

    def actualizar(self, asesor: Asesor, usuario_sistema: str) -> bool:
        """Actualiza un asesor existente."""
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        placeholder = self.db.get_placeholder()

        cursor.execute(
            f"""
                UPDATE ASESORES SET
                    COMISION_PORCENTAJE_ARRIENDO = {placeholder},
                    COMISION_PORCENTAJE_VENTA = {placeholder},
                    ESTADO = {placeholder},
                    UPDATED_AT = {placeholder},
                    UPDATED_BY = {placeholder}
                WHERE ID_ASESOR = {placeholder}
                """,
            (
                asesor.comision_porcentaje_arriendo,
                asesor.comision_porcentaje_venta,
                bool(asesor.estado) if asesor.estado is not None else True,
                datetime.now().isoformat(),
                usuario_sistema,
                asesor.id_asesor,
            ),
        )

        conn.commit()
        return cursor.rowcount > 0

    def eliminar_por_persona(self, id_persona: int) -> bool:
        """Elimina físicamente el registro de asesor asociado a una persona."""
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        placeholder = self.db.get_placeholder()

        cursor.execute(f"DELETE FROM ASESORES WHERE ID_PERSONA = {placeholder}", (id_persona,))
        conn.commit()
        return cursor.rowcount > 0
