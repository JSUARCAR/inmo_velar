from typing import Optional

from src.dominio.entidades.sesion_usuario import SesionUsuario
from src.infraestructura.persistencia.database import DatabaseManager


class RepositorioSesionSQLite:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def guardar(self, sesion: SesionUsuario) -> SesionUsuario:
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        placeholder = self.db.get_placeholder()

        try:
            cursor.execute(
                f"""
                INSERT INTO SESIONES_USUARIO (
                    ID_USUARIO,
                    FECHA_INICIO,
                    FECHA_FIN,
                    TOKEN_SESION
                ) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder})
                """,
                (sesion.id_usuario, sesion.fecha_inicio, sesion.fecha_fin, sesion.token_sesion),
            )

            conn.commit()
            sesion.id_sesion = self.db.get_last_insert_id(cursor, "SESIONES_USUARIO", "ID_SESION")

            return sesion
        except Exception as e:
            conn.rollback()

            # Auto-healing: Detectar desincronización de secuencia en PostgreSQL
            # Error típico: duplicate key value violates unique constraint "sesiones_usuario_pkey"
            is_postgres_unique = (
                self.db.use_postgresql
                and "UniqueViolation" in str(type(e))
                and "sesiones_usuario_pkey" in str(e)
            )

            if is_postgres_unique:
                try:
                    # Intentar resincronizar la secuencia al MAX(id) + 1
                    # Usamos nombres en minúsculas para pg_get_serial_sequence que es case-sensitive con quotes
                    cursor.execute(
                        """
                        SELECT setval(
                            pg_get_serial_sequence('sesiones_usuario', 'id_sesion'),
                            COALESCE((SELECT MAX(id_sesion) FROM sesiones_usuario), 0) + 1,
                            false
                        )
                        """
                    )
                    conn.commit()

                    # Reintentar la inserción original
                    cursor.execute(
                        f"""
                        INSERT INTO SESIONES_USUARIO (
                            ID_USUARIO,
                            FECHA_INICIO,
                            FECHA_FIN,
                            TOKEN_SESION
                        ) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder})
                        """,
                        (sesion.id_usuario, sesion.fecha_inicio, sesion.fecha_fin, sesion.token_sesion),
                    )
                    conn.commit()
                    sesion.id_sesion = self.db.get_last_insert_id(cursor, "SESIONES_USUARIO", "ID_SESION")
                    return sesion

                except Exception as healing_error:
                    # Si falla el healing, restaurar y lanzar el error original
                    conn.rollback()
                    raise e
            
            # Si no es error de secuencia o no es Postgres, lanzar el error original
            raise e

    def obtener_por_token(self, token: str) -> Optional[SesionUsuario]:
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        placeholder = self.db.get_placeholder()

        cursor.execute(
            f"SELECT * FROM SESIONES_USUARIO WHERE TOKEN_SESION = {placeholder}", (token,)
        )

        row = cursor.fetchone()
        if not row:
            return None

        # Convert row to entity
        if hasattr(row, "keys"):
            row_dict = dict(row)
        else:
            row_dict = row

        return SesionUsuario(
            id_sesion=row_dict.get("id_sesion") or row_dict.get("ID_SESION"),
            id_usuario=row_dict.get("id_usuario") or row_dict.get("ID_USUARIO"),
            fecha_inicio=row_dict.get("fecha_inicio") or row_dict.get("FECHA_INICIO"),
            fecha_fin=row_dict.get("fecha_fin") or row_dict.get("FECHA_FIN"),
            token_sesion=row_dict.get("token_sesion") or row_dict.get("TOKEN_SESION"),
        )
