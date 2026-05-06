"""
Repositorio para Sesiones de Usuario.
Soporta SQLite y PostgreSQL con RETURNING id.
"""

from typing import Optional
from datetime import datetime

from src.dominio.entidades.sesion_usuario import SesionUsuario
from src.infraestructura.persistencia.database import DatabaseManager


class RepositorioSesion:
    """
    Repositorio para la entidad SesionUsuario.
    """

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def guardar(self, sesion: SesionUsuario) -> SesionUsuario:
        """
        Guarda una nueva sesión. Usa RETURNING para PostgreSQL.
        """
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        placeholder = self.db.get_placeholder()

        try:
            query = f"""
                INSERT INTO SESIONES_USUARIO (
                    ID_USUARIO,
                    FECHA_INICIO,
                    FECHA_FIN,
                    TOKEN_SESION
                ) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder})
            """

            if self.db.use_postgresql:
                query += " RETURNING ID_SESION"
                cursor.execute(query, (
                    sesion.id_usuario, 
                    sesion.fecha_inicio, 
                    sesion.fecha_fin, 
                    sesion.token_sesion
                ))
                row = cursor.fetchone()
                if isinstance(row, dict):
                    sesion.id_sesion = list(row.values())[0]
                else:
                    sesion.id_sesion = row[0]
            else:
                # SQLite
                cursor.execute(query, (
                    sesion.id_usuario, 
                    sesion.fecha_inicio, 
                    sesion.fecha_fin, 
                    sesion.token_sesion
                ))
                sesion.id_sesion = cursor.lastrowid

            conn.commit()
            return sesion
        except Exception as e:
            conn.rollback()
            
            # Auto-healing: Detectar desincronización de secuencia en PostgreSQL
            is_postgres_unique = (
                self.db.use_postgresql
                and "UniqueViolation" in str(type(e))
                and "sesiones_usuario_pkey" in str(e)
            )

            if is_postgres_unique:
                try:
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
                    # Reintentar con el mismo flujo que arriba
                    return self.guardar(sesion)
                except Exception:
                    conn.rollback()
                    raise e
            
            raise e

    def obtener_por_token(self, token: str) -> Optional[SesionUsuario]:
        """Busca una sesión por su token."""
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

        # Normalizar a minúsculas
        row_dict = {k.lower(): v for k, v in row_dict.items()}

        return SesionUsuario(
            id_sesion=row_dict.get("id_sesion"),
            id_usuario=row_dict.get("id_usuario"),
            fecha_inicio=row_dict.get("fecha_inicio"),
            fecha_fin=row_dict.get("fecha_fin"),
            token_sesion=row_dict.get("token_sesion"),
        )
    
    def cerrar_sesion(self, token: str) -> bool:
        """Cierra una sesión (limpia token o actualiza fecha_fin)."""
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        placeholder = self.db.get_placeholder()

        try:
            cursor.execute(
                f"UPDATE SESIONES_USUARIO SET FECHA_FIN = {placeholder} WHERE TOKEN_SESION = {placeholder}",
                (datetime.now().isoformat(), token),
            )
            conn.commit()
            return cursor.rowcount > 0
        except Exception:
            conn.rollback()
            return False
