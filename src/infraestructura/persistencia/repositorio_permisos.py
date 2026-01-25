"""
Repositorio para gestión de permisos del sistema.
"""

from datetime import datetime
from typing import List, Optional

from src.dominio.entidades.permiso import Permiso, RolPermiso
from src.infraestructura.persistencia.database import DatabaseManager


class RepositorioPermisos:
    """
    Repositorio para operaciones CRUD de permisos y asignaciones a roles.
    """

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    # ===== OPERACIONES SOBRE PERMISOS =====

    def listar_permisos(self) -> List[Permiso]:
        """Lista todos los permisos disponibles en el sistema."""
        conn = self.db.obtener_conexion()
        self.db.get_placeholder()

        try:
            cursor = self.db.get_dict_cursor(conn)

            cursor.execute(
                """
                SELECT * FROM PERMISOS 
                ORDER BY CATEGORIA, MODULO, ACCION
            """
            )

            permisos = []
            for row in cursor.fetchall():
                # Handle potential case sensitivity issues in result dict keys if wrapper fails
                row_dict = dict(row) if hasattr(row, "keys") else row
                permisos.append(
                    Permiso(
                        id_permiso=row_dict.get("id_permiso") or row_dict.get("ID_PERMISO"),
                        modulo=row_dict.get("modulo") or row_dict.get("MODULO"),
                        ruta=row_dict.get("ruta") or row_dict.get("RUTA"),
                        accion=row_dict.get("accion") or row_dict.get("ACCION"),
                        descripcion=row_dict.get("descripcion") or row_dict.get("DESCRIPCION"),
                        categoria=row_dict.get("categoria") or row_dict.get("CATEGORIA"),
                        created_at=row_dict.get("created_at") or row_dict.get("CREATED_AT"),
                    )
                )

            return permisos
        except Exception as e:
            conn.rollback()
            raise e

    def obtener_permiso(self, id_permiso: int) -> Optional[Permiso]:
        """Obtiene un permiso por su ID."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        placeholder = self.db.get_placeholder()

        cursor.execute(f"SELECT * FROM PERMISOS WHERE ID_PERMISO = {placeholder}", (id_permiso,))

        row = cursor.fetchone()
        if not row:
            return None

        row_dict = dict(row) if hasattr(row, "keys") else row
        return Permiso(
            id_permiso=row_dict.get("id_permiso") or row_dict.get("ID_PERMISO"),
            modulo=row_dict.get("modulo") or row_dict.get("MODULO"),
            ruta=row_dict.get("ruta") or row_dict.get("RUTA"),
            accion=row_dict.get("accion") or row_dict.get("ACCION"),
            descripcion=row_dict.get("descripcion") or row_dict.get("DESCRIPCION"),
            categoria=row_dict.get("categoria") or row_dict.get("CATEGORIA"),
            created_at=row_dict.get("created_at") or row_dict.get("CREATED_AT"),
        )

    def crear_permiso(self, permiso: Permiso) -> Permiso:
        """Crea un nuevo permiso en el sistema."""
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        placeholder = self.db.get_placeholder()

        try:
            cursor.execute(
                f"""
                INSERT INTO PERMISOS (MODULO, RUTA, ACCION, DESCRIPCION, CATEGORIA)
                VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
                """,
                (
                    permiso.modulo,
                    permiso.ruta,
                    permiso.accion,
                    permiso.descripcion,
                    permiso.categoria,
                ),
            )

            conn.commit()
            permiso.id_permiso = self.db.get_last_insert_id(cursor, "PERMISOS", "ID_PERMISO")
            return permiso
        except Exception as e:
            conn.rollback()
            raise e

    # ===== OPERACIONES SOBRE ROL_PERMISOS =====

    def obtener_permisos_por_rol(self, rol: str) -> List[Permiso]:
        """Obtiene todos los permisos asignados a un rol específico."""
        conn = self.db.obtener_conexion()
        placeholder = self.db.get_placeholder()

        try:
            cursor = self.db.get_dict_cursor(conn)

            cursor.execute(
                f"""
                SELECT p.* 
                FROM PERMISOS p
                INNER JOIN public.ROL_PERMISOS rp ON p.ID_PERMISO = rp.ID_PERMISO
                WHERE rp.ROL = {placeholder} AND rp.ACTIVO = TRUE
                ORDER BY p.CATEGORIA, p.MODULO, p.ACCION
                """,
                (rol,),
            )

            permisos = []
            for row in cursor.fetchall():
                row_dict = dict(row) if hasattr(row, "keys") else row
                permisos.append(
                    Permiso(
                        id_permiso=row_dict.get("id_permiso") or row_dict.get("ID_PERMISO"),
                        modulo=row_dict.get("modulo") or row_dict.get("MODULO"),
                        ruta=row_dict.get("ruta") or row_dict.get("RUTA"),
                        accion=row_dict.get("accion") or row_dict.get("ACCION"),
                        descripcion=row_dict.get("descripcion") or row_dict.get("DESCRIPCION"),
                        categoria=row_dict.get("categoria") or row_dict.get("CATEGORIA"),
                        created_at=row_dict.get("created_at") or row_dict.get("CREATED_AT"),
                    )
                )

            return permisos
        except Exception as e:
            conn.rollback()
            raise e

    def asignar_permiso_a_rol(self, rol: str, id_permiso: int, usuario: str) -> RolPermiso:
        """Asigna un permiso a un rol."""
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        placeholder = self.db.get_placeholder()

        try:
            cursor.execute(
                f"""
                INSERT INTO public.ROL_PERMISOS (ROL, ID_PERMISO, ACTIVO, CREATED_BY, CREATED_AT)
                VALUES ({placeholder}, {placeholder}, TRUE, {placeholder}, {placeholder})
                ON CONFLICT (ROL, ID_PERMISO) 
                DO UPDATE SET ACTIVO = TRUE, UPDATED_BY = {placeholder}, UPDATED_AT = {placeholder}
                """,
                (
                    rol,
                    id_permiso,
                    usuario,
                    datetime.now().isoformat(),
                    usuario,
                    datetime.now().isoformat(),
                ),
            )

            conn.commit()

            return RolPermiso(
                rol=rol,
                id_permiso=id_permiso,
                activo=True,
                created_by=usuario,
                created_at=datetime.now().isoformat(),
            )
        except Exception as e:
            conn.rollback()
            raise e

    def revocar_permiso_de_rol(self, rol: str, id_permiso: int, usuario: str) -> bool:
        """Revoca un permiso de un rol."""
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        placeholder = self.db.get_placeholder()

        try:
            cursor.execute(
                f"""
                UPDATE public.ROL_PERMISOS 
                SET ACTIVO = FALSE, UPDATED_BY = {placeholder}, UPDATED_AT = {placeholder}
                WHERE ROL = {placeholder} AND ID_PERMISO = {placeholder}
                """,
                (usuario, datetime.now().isoformat(), rol, id_permiso),
            )

            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            raise e

    def limpiar_permisos_rol(self, rol: str) -> bool:
        """Elimina todos los permisos de un rol."""
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        placeholder = self.db.get_placeholder()

        try:
            cursor.execute(f"DELETE FROM public.ROL_PERMISOS WHERE ROL = {placeholder}", (rol,))

            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise e

    def verificar_permiso(self, rol: str, modulo: str, accion: str) -> bool:
        """Verifica si un rol tiene un permiso específico."""
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        placeholder = self.db.get_placeholder()

        cursor.execute(
            f"""
            SELECT COUNT(*) 
            FROM PERMISOS p
            INNER JOIN ROL_PERMISOS rp ON p.ID_PERMISO = rp.ID_PERMISO
            WHERE rp.ROL = {placeholder} 
            AND p.MODULO = {placeholder} 
            AND p.ACCION = {placeholder}
            AND rp.ACTIVO = TRUE
            """,
            (rol, modulo, accion),
        )

        result = cursor.fetchone()
        count = result[0] if isinstance(result, tuple) else list(result.values())[0]
        return count > 0
