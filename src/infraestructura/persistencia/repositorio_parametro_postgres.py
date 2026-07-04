"""
Repositorio Postgres para ParametroSistema.
Implementa mapeo 1:1 con tabla PARAMETROS_SISTEMA.
"""

from typing import List, Optional
from datetime import datetime

from src.dominio.entidades.parametro_sistema import ParametroSistema
from src.infraestructura.persistencia.database import DatabaseManager


class RepositorioParametroPostgres:
    """Repositorio Postgres para la entidad ParametroSistema."""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def _row_to_entity(self, row: dict) -> Optional[ParametroSistema]:
        """Convierte una fila SQL a entidad ParametroSistema."""
        if row is None:
            return None

        if hasattr(row, "keys"):
            row_dict = dict(row)
        else:
            row_dict = row

        return ParametroSistema(
            id_parametro=(row_dict.get("id_parametro") or row_dict.get("ID_PARAMETRO")),
            nombre_parametro=(
                row_dict.get("nombre_parametro") or row_dict.get("NOMBRE_PARAMETRO")
            ),
            valor_parametro=(
                row_dict.get("valor_parametro") or row_dict.get("VALOR_PARAMETRO")
            ),
            tipo_dato=(row_dict.get("tipo_dato") or row_dict.get("TIPO_DATO")),
            descripcion=(row_dict.get("descripcion") or row_dict.get("DESCRIPCION")),
            categoria=(row_dict.get("categoria") or row_dict.get("CATEGORIA")),
            modificable=(row_dict.get("modificable") or row_dict.get("MODIFICABLE")),
            created_at=(row_dict.get("created_at") or row_dict.get("CREATED_AT")),
            updated_at=(row_dict.get("updated_at") or row_dict.get("UPDATED_AT")),
            updated_by=(row_dict.get("updated_by") or row_dict.get("UPDATED_BY")),
        )

    def listar_todos(self) -> List[ParametroSistema]:
        """Lista todos los parámetros del sistema."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)

        cursor.execute(
            "SELECT * FROM PARAMETROS_SISTEMA ORDER BY CATEGORIA, NOMBRE_PARAMETRO"
        )
        return [self._row_to_entity(row) for row in cursor.fetchall() if row]

    def listar_categorias(self) -> List[str]:
        """Obtiene la lista de categorías únicas de parámetros."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)

        cursor.execute(
            "SELECT DISTINCT CATEGORIA FROM PARAMETROS_SISTEMA WHERE CATEGORIA IS NOT NULL ORDER BY CATEGORIA"
        )
        return [
            row.get("categoria") or row.get("CATEGORIA") for row in cursor.fetchall()
        ]

    def obtener_por_categoria(self, categoria: str) -> List[ParametroSistema]:
        """Obtiene todos los parámetros de una categoría específica."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        placeholder = self.db.get_placeholder()

        cursor.execute(
            f"SELECT * FROM PARAMETROS_SISTEMA WHERE CATEGORIA = {placeholder} ORDER BY NOMBRE_PARAMETRO",
            (categoria,),
        )
        return [self._row_to_entity(row) for row in cursor.fetchall() if row]

    def obtener_por_nombre(self, nombre: str) -> Optional[ParametroSistema]:
        """Obtiene un parámetro por su nombre exacto."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        placeholder = self.db.get_placeholder()

        cursor.execute(
            f"SELECT * FROM PARAMETROS_SISTEMA WHERE NOMBRE_PARAMETRO = {placeholder}",
            (nombre,),
        )
        row = cursor.fetchone()
        return self._row_to_entity(row) if row else None

    def obtener_por_id(self, id_parametro: int) -> Optional[ParametroSistema]:
        """Obtiene un parámetro por su ID."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        placeholder = self.db.get_placeholder()

        cursor.execute(
            f"SELECT * FROM PARAMETROS_SISTEMA WHERE ID_PARAMETRO = {placeholder}",
            (id_parametro,),
        )
        row = cursor.fetchone()
        return self._row_to_entity(row) if row else None

    def crear(self, parametro: ParametroSistema, usuario: str) -> ParametroSistema:
        """Crea un nuevo parámetro de sistema."""
        with self.db.transaccion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            placeholder = self.db.get_placeholder()
            query = f"""
                INSERT INTO PARAMETROS_SISTEMA (
                    NOMBRE_PARAMETRO, VALOR_PARAMETRO, TIPO_DATO,
                    DESCRIPCION, CATEGORIA, MODIFICABLE,
                    CREATED_AT, UPDATED_BY
                ) VALUES (
                    {placeholder}, {placeholder}, {placeholder},
                    {placeholder}, {placeholder}, {placeholder},
                    {placeholder}, {placeholder}
                )
            """

            created_at = datetime.now().isoformat()

            if self.db.use_postgresql:
                query += " RETURNING id_parametro"
                cursor.execute(
                    query,
                    (
                        parametro.nombre_parametro,
                        parametro.valor_parametro,
                        parametro.tipo_dato,
                        parametro.descripcion,
                        parametro.categoria,
                        parametro.modificable,
                        created_at,
                        usuario,
                    ),
                )
                row = cursor.fetchone()
                parametro.id_parametro = row.get("id_parametro") or row.get(
                    "ID_PARAMETRO"
                )
            else:
                cursor.execute(
                    query,
                    (
                        parametro.nombre_parametro,
                        parametro.valor_parametro,
                        parametro.tipo_dato,
                        parametro.descripcion,
                        parametro.categoria,
                        parametro.modificable,
                        created_at,
                        usuario,
                    ),
                )
                parametro.id_parametro = self.db.get_last_insert_id(
                    cursor, "PARAMETROS_SISTEMA", "ID_PARAMETRO"
                )

            return parametro

    def actualizar(self, parametro: ParametroSistema, usuario: str) -> bool:
        """
        Actualiza el valor de un parámetro existente.
        """
        if not parametro.es_modificable:
            raise PermissionError(
                f"El parámetro '{parametro.nombre_parametro}' no es modificable"
            )

        with self.db.obtener_conexion() as conn:
            cursor = conn.cursor()
            placeholder = self.db.get_placeholder()

            updated_at = datetime.now().isoformat()

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
                    updated_at,
                    usuario,
                    parametro.id_parametro,
                ),
            )

            conn.commit()
            return cursor.rowcount > 0
