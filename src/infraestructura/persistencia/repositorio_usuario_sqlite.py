"""
Repositorio SQLite para Usuario.
Implementa mapeo 1:1 estricto con tabla USUARIOS.
"""

import sqlite3
from typing import Optional, List
from datetime import datetime

from src.dominio.entidades.usuario import Usuario
from src.infraestructura.persistencia.database import DatabaseManager


class RepositorioUsuarioSQLite:
    """
    Repositorio SQLite para la entidad Usuario.
    Garantiza mapeo 1:1 con tabla USUARIOS.
    """
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def _to_boolean(self, value) -> bool:
        """
        Convierte valores a boolean de manera segura para PostgreSQL.
        
        Args:
            value: Valor a convertir (puede ser int, bool, None)
        
        Returns:
            bool: Valor convertido a boolean
        """
        if isinstance(value, bool):
            return value
        if isinstance(value, int):
            return value == 1
        if value is None:
            return False
        return bool(value)
    
    def _row_to_entity(self, row) -> Usuario:
        """Convierte una fila SQL a entidad Usuario."""
        # Manejar tanto sqlite3.Row como dict (PostgreSQL)
        if row is None:
            return None
        
        # Convertir a dict si es necesario
        if hasattr(row, 'keys'):  # sqlite3.Row o psycopg2.extras.RealDictRow
            row_dict = dict(row)
        else:
            row_dict = row
        
        # Obtener estado_usuario y convertir a boolean
        estado_raw = row_dict.get('estado_usuario') or row_dict.get('ESTADO_USUARIO')
        
        return Usuario(
            id_usuario=row_dict.get('id_usuario') or row_dict.get('ID_USUARIO'),
            nombre_usuario=row_dict.get('nombre_usuario') or row_dict.get('NOMBRE_USUARIO'),
            contrasena_hash=row_dict.get('contrasena_hash') or row_dict.get('CONTRASENA_HASH'),
            rol=row_dict.get('rol') or row_dict.get('ROL'),
            estado_usuario=self._to_boolean(estado_raw),
            ultimo_acceso=row_dict.get('ultimo_acceso') or row_dict.get('ULTIMO_ACCESO'),
            fecha_creacion=row_dict.get('fecha_creacion') or row_dict.get('FECHA_CREACION'),
            created_by=row_dict.get('created_by') or row_dict.get('CREATED_BY'),
            updated_at=row_dict.get('updated_at') or row_dict.get('UPDATED_AT'),
            updated_by=row_dict.get('updated_by') or row_dict.get('UPDATED_BY')
        )
    
    def obtener_por_id(self, id_usuario: int) -> Optional[Usuario]:
        """Obtiene un usuario por su ID."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        placeholder = self.db.get_placeholder()
        
        cursor.execute(
            f"SELECT * FROM USUARIOS WHERE ID_USUARIO = {placeholder}",
            (id_usuario,)
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
            (nombre_usuario,)
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
        Crea un nuevo usuario en la BD.
        
        Args:
            usuario: Entidad Usuario a crear
            usuario_sistema: Usuario que ejecuta la operación (para auditoría)
        
        Returns:
            Usuario con ID asignado
        """
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        placeholder = self.db.get_placeholder()
        
        try:
            cursor.execute(
                f"""
                INSERT INTO USUARIOS (
                    NOMBRE_USUARIO,
                    CONTRASENA_HASH,
                    ROL,
                    ESTADO_USUARIO,
                    ULTIMO_ACCESO,
                    FECHA_CREACION,
                    CREATED_BY
                ) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
                """,
                (
                    usuario.nombre_usuario,
                    usuario.contrasena_hash,
                    usuario.rol,
                    self._to_boolean(usuario.estado_usuario),
                    usuario.ultimo_acceso,
                    usuario.fecha_creacion or datetime.now().isoformat(),
                    usuario_sistema
                )
            )
            
            conn.commit()
            usuario.id_usuario = self.db.get_last_insert_id(cursor, 'USUARIOS', 'ID_USUARIO')
            
            return usuario
        except Exception as e:
            conn.rollback()
            raise e
    
    def actualizar(self, usuario: Usuario, usuario_sistema: str) -> bool:
        """
        Actualiza un usuario existente.
        
        Returns:
            True si se actualizó, False si no existe
        """
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
                    self._to_boolean(usuario.estado_usuario),
                    usuario.ultimo_acceso,
                    datetime.now().isoformat(),
                    usuario_sistema,
                    usuario.id_usuario
                )
            )
            
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            raise e
    
    def eliminar(self, id_usuario: int) -> bool:
        """
        Elimina un usuario (soft delete: marca como inactivo).
        
        Returns:
            True si se eliminó, False si no existe
        """
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        placeholder = self.db.get_placeholder()
        
        try:
            # Usar FALSE para PostgreSQL compatibility
            cursor.execute(
                f"UPDATE USUARIOS SET ESTADO_USUARIO = {placeholder} WHERE ID_USUARIO = {placeholder}",
                (False, id_usuario)
            )
            
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            conn.rollback()
            raise e
