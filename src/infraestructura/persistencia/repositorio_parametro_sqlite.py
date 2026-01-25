"""
Repositorio SQLite para ParametroSistema.
Implementa mapeo 1:1 estricto con tabla PARAMETROS_SISTEMA.
"""

import sqlite3
from datetime import datetime
from typing import List, Optional

from src.dominio.entidades.parametro_sistema import ParametroSistema
from src.infraestructura.persistencia.database import DatabaseManager


class RepositorioParametroSQLite:
    """Repositorio SQLite para la entidad ParametroSistema."""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def _row_to_entity(self, row: sqlite3.Row) -> ParametroSistema:
        """Convierte una fila SQL a entidad ParametroSistema."""

        # Manejar tanto sqlite3.Row como dict (PostgreSQL)

        if row is None:

            return None

        # Convertir a dict si es necesario

        if hasattr(row, "keys"):

            row_dict = dict(row)

        else:

            row_dict = row

        return ParametroSistema(
            id_parametro=(row_dict.get("id_parametro") or row_dict.get("ID_PARAMETRO")),
            nombre_parametro=(row_dict.get("nombre_parametro") or row_dict.get("NOMBRE_PARAMETRO")),
            valor_parametro=(row_dict.get("valor_parametro") or row_dict.get("VALOR_PARAMETRO")),
            tipo_dato=(row_dict.get("tipo_dato") or row_dict.get("TIPO_DATO")),
            descripcion=(row_dict.get("descripcion") or row_dict.get("DESCRIPCION")),
            categoria=(row_dict.get("categoria") or row_dict.get("CATEGORIA")),
            modificable=1 if (row_dict.get("modificable") or row_dict.get("MODIFICABLE")) == 1 else 0,
            created_at=(row_dict.get("created_at") or row_dict.get("CREATED_AT")),
            updated_at=(row_dict.get("updated_at") or row_dict.get("UPDATED_AT")),
            updated_by=(row_dict.get("updated_by") or row_dict.get("UPDATED_BY")),
        )

    def obtener_por_id(self, id_parametro: int) -> Optional[ParametroSistema]:
        """Obtiene un parámetro por su ID."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        placeholder = self.db.get_placeholder()

        cursor.execute(
            f"SELECT * FROM PARAMETROS_SISTEMA WHERE ID_PARAMETRO = {placeholder}", (id_parametro,)
        )

        row = cursor.fetchone()
        return self._row_to_entity(row) if row else None

    def obtener_por_nombre(self, nombre_parametro: str) -> Optional[ParametroSistema]:
        """Obtiene un parámetro por su nombre único."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        placeholder = self.db.get_placeholder()

        cursor.execute(
            f"SELECT * FROM PARAMETROS_SISTEMA WHERE NOMBRE_PARAMETRO = {placeholder}",
            (nombre_parametro,),
        )

        row = cursor.fetchone()
        return self._row_to_entity(row) if row else None

    def obtener_por_categoria(self, categoria: str) -> List[ParametroSistema]:
        """Lista todos los parámetros de una categoría específica."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        self.db.get_placeholder()

        cursor.execute(
            """
            SELECT * FROM PARAMETROS_SISTEMA 
            WHERE CATEGORIA = {placeholder}
            ORDER BY NOMBRE_PARAMETRO
            """,
            (categoria,),
        )

        return [self._row_to_entity(row) for row in cursor.fetchall()]

    def listar_todos(self) -> List[ParametroSistema]:
        """Lista todos los parámetros del sistema."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        self.db.get_placeholder()

        cursor.execute(
            """
            SELECT * FROM PARAMETROS_SISTEMA 
            ORDER BY CATEGORIA, NOMBRE_PARAMETRO
            """
        )

        return [self._row_to_entity(row) for row in cursor.fetchall()]

    def listar_categorias(self) -> List[str]:
        """Lista todas las categorías disponibles."""
        with self.db.obtener_conexion() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                SELECT DISTINCT CATEGORIA FROM PARAMETROS_SISTEMA 
                WHERE CATEGORIA IS NOT NULL
                ORDER BY CATEGORIA
                """
            )

            return [row[0] for row in cursor.fetchall()]

    def actualizar(self, parametro: ParametroSistema, usuario_sistema: str) -> bool:
        """
        Actualiza el valor de un parámetro existente.

        Args:
            parametro: Entidad con los valores actualizados
            usuario_sistema: Usuario que ejecuta la operación

        Returns:
            True si se actualizó, False si no existe o no es modificable

        Raises:
            PermissionError: Si el parámetro no es modificable
        """
        # Verificar si el parámetro existe y es modificable
        existente = self.obtener_por_id(parametro.id_parametro)
        if not existente:
            return False

        if not existente.es_modificable:
            raise PermissionError(f"El parámetro '{existente.nombre_parametro}' no es modificable")

        with self.db.obtener_conexion() as conn:
            cursor = conn.cursor()
            placeholder = self.db.get_placeholder()

            cursor.execute(
                f"""
                UPDATE PARAMETROS_SISTEMA SET
                    VALOR_PARAMETRO = {placeholder},
                    UPDATED_AT = {placeholder},
                    UPDATED_BY = {placeholder}
                WHERE ID_PARAMETRO = {placeholder}
                """,
                (
                    parametro.valor_parametro,
                    datetime.now().isoformat(),
                    usuario_sistema,
                    parametro.id_parametro,
                ),
            )

            conn.commit()
            return cursor.rowcount > 0

    def crear(self, parametro: ParametroSistema, usuario_sistema: str) -> ParametroSistema:
        """
        Crea un nuevo parámetro del sistema.

        Args:
            parametro: Entidad ParametroSistema a crear
            usuario_sistema: Usuario que ejecuta la operación

        Returns:
            Parámetro con ID asignado
        """
        with self.db.obtener_conexion() as conn:
            cursor = conn.cursor()

            cursor.execute(
                """
                INSERT INTO PARAMETROS_SISTEMA (
                    NOMBRE_PARAMETRO,
                    VALOR_PARAMETRO,
                    TIPO_DATO,
                    DESCRIPCION,
                    CATEGORIA,
                    MODIFICABLE,
                    CREATED_AT,
                    UPDATED_AT,
                    UPDATED_BY
                ) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
                """,
                (
                    parametro.nombre_parametro,
                    parametro.valor_parametro,
                    parametro.tipo_dato,
                    parametro.descripcion,
                    parametro.categoria,
                    parametro.modificable,
                    datetime.now().isoformat(),
                    datetime.now().isoformat(),
                    usuario_sistema,
                ),
            )

            conn.commit()
            parametro.id_parametro = cursor.lastrowid

            return parametro
