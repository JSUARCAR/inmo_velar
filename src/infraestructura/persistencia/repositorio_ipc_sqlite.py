"""
Repositorio SQLite para IPC.
Implementa mapeo 1:1 estricto con tabla IPC.
"""

import sqlite3
from typing import Optional, List
from datetime import datetime

from src.dominio.entidades.ipc import IPC
from src.infraestructura.persistencia.database import DatabaseManager


class RepositorioIPCSQLite:
    """Repositorio SQLite para la entidad IPC."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def _row_to_entity(self, row: sqlite3.Row) -> IPC:
        """Convierte una fila SQL a entidad IPC."""

    
        # Manejar tanto sqlite3.Row como dict (PostgreSQL)

    
        if row is None:

    
            return None

    
        

    
        # Convertir a dict si es necesario

    
        if hasattr(row, 'keys'):

    
            row_dict = dict(row)

    
        else:

    
            row_dict = row

        return IPC(
            id_ipc=(row_dict.get('id_ipc') or row_dict.get('ID_IPC')),
            anio=(row_dict.get('anio') or row_dict.get('ANIO')),
            valor_ipc=(row_dict.get('valor_ipc') or row_dict.get('VALOR_IPC')),
            fecha_publicacion=(row_dict.get('fecha_publicacion') or row_dict.get('FECHA_PUBLICACION')),
            estado_registro=(row_dict.get('estado_registro') or row_dict.get('ESTADO_REGISTRO')),
            created_at=(row_dict.get('created_at') or row_dict.get('CREATED_AT')),
            created_by=(row_dict.get('created_by') or row_dict.get('CREATED_BY'))
        )
    
    def obtener_por_id(self, id_ipc: int) -> Optional[IPC]:
        """Obtiene un registro IPC por su ID."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        placeholder = self.db.get_placeholder()
            
        cursor.execute(
            f"SELECT * FROM IPC WHERE ID_IPC = {placeholder}",
            (id_ipc,)
        )
            
        row = cursor.fetchone()
        return self._row_to_entity(row) if row else None
    
    def obtener_por_anio(self, anio: int) -> Optional[IPC]:
        """Obtiene el IPC de un año específico."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        placeholder = self.db.get_placeholder()
            
        cursor.execute(
            f"SELECT * FROM IPC WHERE ANIO = {placeholder}",
            (anio,)
        )
            
        row = cursor.fetchone()
        return self._row_to_entity(row) if row else None
    
    def obtener_ultimo(self) -> Optional[IPC]:
        """Obtiene el último IPC registrado."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        placeholder = self.db.get_placeholder()
            
        cursor.execute(
            """
            SELECT * FROM IPC 
            WHERE ESTADO_REGISTRO = TRUE
            ORDER BY ANIO DESC 
            LIMIT 1
            """
        )
            
        row = cursor.fetchone()
        return self._row_to_entity(row) if row else None
    
    def listar_todos(self) -> List[IPC]:
        """Lista todos los registros IPC."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        placeholder = self.db.get_placeholder()
            
        cursor.execute(
            """
            SELECT * FROM IPC 
            WHERE ESTADO_REGISTRO = TRUE
            ORDER BY ANIO DESC
            """
        )
            
        return [self._row_to_entity(row) for row in cursor.fetchall()]
    
    def crear(self, ipc: IPC, usuario_sistema: str) -> IPC:
        """Crea un nuevo registro IPC."""
        with self.db.obtener_conexion() as conn:
            cursor = conn.cursor()
            placeholder = self.db.get_placeholder()
            
            cursor.execute(
                f"""
                INSERT INTO IPC (
                    ANIO,
                    VALOR_IPC,
                    FECHA_PUBLICACION,
                    ESTADO_REGISTRO,
                    CREATED_AT,
                    CREATED_BY
                ) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
                """,
                (
                    ipc.anio,
                    ipc.valor_ipc,
                    ipc.fecha_publicacion or datetime.now().isoformat(),
                    bool(ipc.estado_registro) if ipc.estado_registro is not None else True,
                    datetime.now().isoformat(),
                    usuario_sistema
                )
            )
            
            conn.commit()
            ipc.id_ipc = self.db.get_last_insert_id(cursor, 'IPC', 'ID_IPC')
            
            return ipc
    
    def actualizar(self, ipc: IPC, usuario_sistema: str) -> bool:
        """
        Actualiza un registro IPC existente.
        
        Args:
            ipc: Entidad IPC con valores actualizados
            usuario_sistema: Usuario que ejecuta la operación
            
        Returns:
            True si se actualizó, False si no existe
        """
        with self.db.obtener_conexion() as conn:
            cursor = conn.cursor()
            placeholder = self.db.get_placeholder()
            
            cursor.execute(
                f"""
                UPDATE IPC SET
                    VALOR_IPC = {placeholder},
                    FECHA_PUBLICACION = {placeholder}
                WHERE ID_IPC = {placeholder}
                """,
                (
                    ipc.valor_ipc,
                    ipc.fecha_publicacion,
                    ipc.id_ipc
                )
            )
            
            conn.commit()
            return cursor.rowcount > 0
    
    def eliminar(self, id_ipc: int) -> bool:
        """
        Elimina un registro IPC (soft delete: marca como inactivo).
        
        Returns:
            True si se eliminó, False si no existe
        """
        with self.db.obtener_conexion() as conn:
            cursor = conn.cursor()
            placeholder = self.db.get_placeholder()
            
            cursor.execute(
                f"""
                UPDATE IPC SET ESTADO_REGISTRO = FALSE
                WHERE ID_IPC = {placeholder}
                """,
                (id_ipc,)
            )
            
            conn.commit()
            return cursor.rowcount > 0
