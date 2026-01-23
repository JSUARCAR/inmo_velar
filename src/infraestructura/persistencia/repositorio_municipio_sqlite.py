"""
Repositorio SQLite para Municipio.
Implementa mapeo 1:1 estricto con tabla MUNICIPIOS.
"""

import sqlite3
from typing import Optional, List
from datetime import datetime

from src.dominio.entidades.municipio import Municipio
from src.infraestructura.persistencia.database import DatabaseManager


class RepositorioMunicipioSQLite:
    """Repositorio SQLite para la entidad Municipio."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def _row_to_entity(self, row: sqlite3.Row) -> Municipio:
        """Convierte una fila SQL a entidad Municipio."""

    
        # Manejar tanto sqlite3.Row como dict (PostgreSQL)

    
        if row is None:

    
            return None

    
        

    
        # Convertir a dict si es necesario

    
        if hasattr(row, 'keys'):

    
            row_dict = dict(row)

    
        else:

    
            row_dict = row

        return Municipio(
            id_municipio=(row_dict.get('id_municipio') or row_dict.get('ID_MUNICIPIO')),
            nombre_municipio=(row_dict.get('nombre_municipio') or row_dict.get('NOMBRE_MUNICIPIO')),
            departamento=(row_dict.get('departamento') or row_dict.get('DEPARTAMENTO')),
            estado_registro=(row_dict.get('estado_registro') or row_dict.get('ESTADO_REGISTRO')),
            created_at=(row_dict.get('created_at') or row_dict.get('CREATED_AT')),
            created_by=(row_dict.get('created_by') or row_dict.get('CREATED_BY'))
        )
    
    def obtener_por_id(self, id_municipio: int) -> Optional[Municipio]:
        """Obtiene un municipio por su ID."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        placeholder = self.db.get_placeholder()
            
        cursor.execute(
            f"SELECT * FROM MUNICIPIOS WHERE ID_MUNICIPIO = {placeholder}",
            (id_municipio,)
        )
            
        row = cursor.fetchone()
        return self._row_to_entity(row) if row else None
    
    def listar_todos(self) -> List[Municipio]:
        """Lista todos los municipios."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        placeholder = self.db.get_placeholder()
            
        cursor.execute(
            """
            SELECT * FROM MUNICIPIOS 
            WHERE ESTADO_REGISTRO = TRUE
            ORDER BY DEPARTAMENTO, NOMBRE_MUNICIPIO
            """
        )
            
        return [self._row_to_entity(row) for row in cursor.fetchall()]
    
    def listar_por_departamento(self, departamento: str) -> List[Municipio]:
        """Lista todos los municipios de un departamento."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        placeholder = self.db.get_placeholder()
            
        cursor.execute(
            """
            SELECT * FROM MUNICIPIOS 
            WHERE DEPARTAMENTO = {placeholder} AND ESTADO_REGISTRO = TRUE
            ORDER BY NOMBRE_MUNICIPIO
            """,
            (departamento,)
        )
            
        return [self._row_to_entity(row) for row in cursor.fetchall()]
