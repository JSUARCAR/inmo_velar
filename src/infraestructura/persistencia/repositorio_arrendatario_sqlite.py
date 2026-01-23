"""
Repositorio SQLite para Arrendatario.
Implementa mapeo 1:1 estricto con tabla ARRENDATARIOS.
"""

import sqlite3
from typing import Optional, List
from datetime import datetime

from src.dominio.entidades.arrendatario import Arrendatario
from src.infraestructura.persistencia.database import DatabaseManager


class RepositorioArrendatarioSQLite:
    """Repositorio SQLite para la entidad Arrendatario."""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def _row_to_entity(self, row: sqlite3.Row) -> Arrendatario:
        """Convierte una fila SQL a entidad Arrendatario."""

    
        # Manejar tanto sqlite3.Row como dict (PostgreSQL)

    
        if row is None:

    
            return None

    
        

    
        # Convertir a dict si es necesario

    
        if hasattr(row, 'keys'):

    
            row_dict = dict(row)

    
        else:

    
            row_dict = row

        return Arrendatario(
            id_arrendatario=(row_dict.get('id_arrendatario') or row_dict.get('ID_ARRENDATARIO')),
            id_persona=(row_dict.get('id_persona') or row_dict.get('ID_PERSONA')),
            id_seguro=(row_dict.get('id_seguro') or row_dict.get('ID_SEGURO')),
            codigo_aprobacion_seguro=(row_dict.get('codigo_aprobacion_seguro') or row_dict.get('CODIGO_APROBACION_SEGURO')),
            direccion_referencia=(row_dict.get('direccion_referencia') or row_dict.get('DIRECCION_REFERENCIA')),
            estado_arrendatario=(row_dict.get('estado_arrendatario') or row_dict.get('ESTADO_ARRENDATARIO')),
            fecha_ingreso_arrendatario=(row_dict.get('fecha_ingreso_arrendatario') or row_dict.get('FECHA_INGRESO_ARRENDATARIO')),
            motivo_inactivacion=(row_dict.get('motivo_inactivacion') or row_dict.get('MOTIVO_INACTIVACION')),
            created_at=(row_dict.get('created_at') or row_dict.get('CREATED_AT')),
            created_by=(row_dict.get('created_by') or row_dict.get('CREATED_BY')),
            updated_at=(row_dict.get('updated_at') or row_dict.get('UPDATED_AT')),
            updated_by=(row_dict.get('updated_by') or row_dict.get('UPDATED_BY'))
        )
    
    def obtener_por_id(self, id_arrendatario: int) -> Optional[Arrendatario]:
        """Obtiene un arrendatario por su ID."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        placeholder = self.db.get_placeholder()
            
        cursor.execute(
            f"SELECT * FROM ARRENDATARIOS WHERE ID_ARRENDATARIO = {placeholder}",
            (id_arrendatario,)
        )
            
        row = cursor.fetchone()
        return self._row_to_entity(row) if row else None
    
    def obtener_por_persona(self, id_persona: int) -> Optional[Arrendatario]:
        """Obtiene un arrendatario por ID de persona."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        placeholder = self.db.get_placeholder()
            
        cursor.execute(
            f"SELECT * FROM ARRENDATARIOS WHERE ID_PERSONA = {placeholder}",
            (id_persona,)
        )
            
        row = cursor.fetchone()
        return self._row_to_entity(row) if row else None
    
    def crear(self, arrendatario: Arrendatario, usuario_sistema: str) -> Arrendatario:
        """Crea un nuevo arrendatario."""
        with self.db.obtener_conexion() as conn:
            cursor = conn.cursor()
            placeholder = self.db.get_placeholder()
            
            cursor.execute(
                f"""
                INSERT INTO ARRENDATARIOS (
                    ID_PERSONA,
                    ID_SEGURO,
                    CODIGO_APROBACION_SEGURO,
                    DIRECCION_REFERENCIA,
                    ESTADO_ARRENDATARIO,
                    FECHA_INGRESO_ARRENDATARIO,
                    CREATED_AT,
                    CREATED_BY
                ) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
                """,
                (
                    arrendatario.id_persona,
                    arrendatario.id_seguro,
                    arrendatario.codigo_aprobacion_seguro,
                    arrendatario.direccion_referencia,
                    bool(arrendatario.estado_arrendatario) if arrendatario.estado_arrendatario is not None else True,
                    arrendatario.fecha_ingreso_arrendatario or datetime.now().isoformat(),
                    datetime.now().isoformat(),
                    usuario_sistema
                )
            )
            
            conn.commit()
            arrendatario.id_arrendatario = self.db.get_last_insert_id(cursor, 'ARRENDATARIOS', 'ID_ARRENDATARIO')
            
            return arrendatario
    
    def actualizar(self, arrendatario: Arrendatario, usuario_sistema: str) -> bool:
        """Actualiza un arrendatario existente."""
        with self.db.obtener_conexion() as conn:
            cursor = conn.cursor()
            placeholder = self.db.get_placeholder()
            
            cursor.execute(
                f"""
                UPDATE ARRENDATARIOS SET
                    ID_SEGURO = {placeholder},
                    CODIGO_APROBACION_SEGURO = {placeholder},
                    DIRECCION_REFERENCIA = {placeholder},
                    ESTADO_ARRENDATARIO = {placeholder},
                    UPDATED_AT = {placeholder},
                    UPDATED_BY = {placeholder}
                WHERE ID_ARRENDATARIO = {placeholder}
                """,
                (
                    arrendatario.id_seguro,
                    arrendatario.codigo_aprobacion_seguro,
                    arrendatario.direccion_referencia,
                    bool(arrendatario.estado_arrendatario) if arrendatario.estado_arrendatario is not None else True,
                    datetime.now().isoformat(),
                    usuario_sistema,
                    arrendatario.id_arrendatario
                )
            )
            
            conn.commit()
            return cursor.rowcount > 0
