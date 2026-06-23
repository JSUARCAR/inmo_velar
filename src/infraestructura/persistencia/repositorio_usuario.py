"""
Repositorio para Usuario.
Implementa mapeo 1:1 estricto con tabla USUARIOS.
Soporta SQLite y PostgreSQL dinámicamente.
"""

from datetime import datetime
from typing import List, Optional

from src.dominio.entidades.usuario import Usuario
from src.infraestructura.persistencia.database import DatabaseManager


class RepositorioUsuario:
    """
    Repositorio para la entidad Usuario.
    Garantiza mapeo 1:1 con tabla USUARIOS.
    """

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def _to_boolean(self, value) -> bool:
        """Convierte valores a boolean de manera segura."""
        if isinstance(value, bool):
            return value
        if isinstance(value, int):
            return value == 1
        if value is None:
            return False
        return bool(value)

    def _row_to_entity(self, row) -> Usuario:
        """Convierte una fila SQL a entidad Usuario."""
        if row is None:
            return None

        # Convertir a dict si es necesario
        if hasattr(row, "keys"):
            row_dict = dict(row)
        else:
            row_dict = row

        # Normalizar nombres de columnas a minúsculas
        row_dict = {k.lower(): v for k, v in row_dict.items()}

        return Usuario(
            id_usuario=row_dict.get("id_usuario"),
            nombre_usuario=row_dict.get("nombre_usuario"),
            contrasena_hash=row_dict.get("contrasena_hash"),
            rol=row_dict.get("rol"),
            estado_usuario=self._to_boolean(row_dict.get("estado_usuario")),
            ultimo_acceso=row_dict.get("ultimo_acceso"),
            fecha_creacion=row_dict.get("fecha_creacion"),
            created_by=row_dict.get("created_by"),
            updated_at=row_dict.get("updated_at"),
            updated_by=row_dict.get("updated_by"),
        )

    def obtener_por_id(self, id_usuario: int) -> Optional[Usuario]:
        """Obtiene un usuario por su ID."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        placeholder = self.db.get_placeholder()

        cursor.execute(
            f"SELECT * FROM USUARIOS WHERE ID_USUARIO = {placeholder}", (id_usuario,)
        )

        row = cursor.fetchone()
        return self._row_to_entity(row) if row else None

    def obtener_por_nombre(self, nombre_usuario: str) -> Optional[Usuario]:
        """Obtiene un usuario por su nombre de usuario."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        placeholder = self.db.get_placeholder()

        cursor.execute(
            f"SELECT * FROM USUARIOS WHERE NOMBRE_USUARIO = {placeholder}",
            (nombre_usuario,),
        )

        row = cursor.fetchone()
        return self._row_to_entity(row) if row else None

    def listar_todos(self) -> List[Usuario]:
        """Lista todos los usuarios."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)

        cursor.execute("SELECT * FROM USUARIOS ORDER BY ID_USUARIO")

        return [self._row_to_entity(row) for row in cursor.fetchall()]

    def crear(self, usuario: Usuario, usuario_sistema: str) -> Usuario:
        """
        Crea un nuevo usuario en la BD usando RETURNING para PostgreSQL.
        """
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        placeholder = self.db.get_placeholder()

        try:
            query = f"""
                INSERT INTO USUARIOS (
                    NOMBRE_USUARIO,
                    CONTRASENA_HASH,
                    ROL,
                    ESTADO_USUARIO,
                    ULTIMO_ACCESO,
                    FECHA_CREACION,
                    CREATED_BY
                ) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
            """

            # ELITE: Uso de RETURNING para PostgreSQL según reglas del usuario
            if self.db.use_postgresql:
                query += " RETURNING ID_USUARIO"
                cursor.execute(
                    query,
                    (
                        usuario.nombre_usuario,
                        usuario.contrasena_hash,
                        usuario.rol,
                        usuario.estado_usuario,
                        usuario.ultimo_acceso,
                        usuario.fecha_creacion or datetime.now().isoformat(),
                        usuario_sistema,
                    ),
                )
                row = cursor.fetchone()
                # El cursor de DBManager ya wrappea dicts
                if isinstance(row, dict):
                    usuario.id_usuario = list(row.values())[0]
                else:
                    usuario.id_usuario = row[0]
            else:
                # SQLite fallback: True/False también funcionan en SQLite
                cursor.execute(
                    query,
                    (
                        usuario.nombre_usuario,
                        usuario.contrasena_hash,
                        usuario.rol,
                        bool(usuario.estado_usuario),
                        usuario.ultimo_acceso,
                        usuario.fecha_creacion or datetime.now().isoformat(),
                        usuario_sistema,
                    ),
                )
                usuario.id_usuario = cursor.lastrowid

            conn.commit()
            return usuario
        except Exception as e:
            conn.rollback()
            raise e

    def actualizar(self, usuario: Usuario, usuario_sistema: str) -> bool:
        """Actualiza un usuario existente."""
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        placeholder = self.db.get_placeholder()

        try:
            cursor.execute(
                f"""
                UPDATE USUARIOS SET
                    NOMBRE_USUARIO = {placeholder},
                    CONTRASENA_HASH = {placeholder},
                    ROL = {placeholder},
                    ESTADO_USUARIO = {placeholder},
                    ULTIMO_ACCESO = {placeholder},
                    UPDATED_AT = {placeholder},
                    UPDATED_BY = {placeholder}
                WHERE ID_USUARIO = {placeholder}
                """,
                (
                    usuario.nombre_usuario,
                    usuario.contrasena_hash,
                    usuario.rol,
                    bool(usuario.estado_usuario),
                    usuario.ultimo_acceso,
                    datetime.now().isoformat(),
                    usuario_sistema,
                    usuario.id_usuario,
                ),
            )

            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            raise e

    def eliminar(self, id_usuario: int) -> bool:
        """Elimina un usuario (soft delete)."""
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        placeholder = self.db.get_placeholder()

        try:
            cursor.execute(
                f"UPDATE USUARIOS SET ESTADO_USUARIO = {placeholder} WHERE ID_USUARIO = {placeholder}",
                (False, id_usuario),
            )

            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            raise e
