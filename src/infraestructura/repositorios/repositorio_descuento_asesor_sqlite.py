"""
Repositorio SQLite para entidad DescuentoAsesor.
Implementa operaciones CRUD básicas y consultas especializadas.
"""

import sqlite3
from typing import List, Optional
from datetime import datetime

from src.dominio.entidades.descuento_asesor import DescuentoAsesor
from src.infraestructura.persistencia.database import DatabaseManager


class RepositorioDescuentoAsesorSQLite:
    """Repositorio para gestión de descuentos de asesores en SQLite"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def crear(self, descuento: DescuentoAsesor, usuario: str) -> DescuentoAsesor:
        """
        Crea un nuevo descuento.
        
        Args:
            descuento: Entidad DescuentoAsesor a crear
            usuario: Usuario que crea el descuento
        
        Returns:
            DescuentoAsesor con ID asignado
        """
        # One-line hardcoded query
        query = "INSERT INTO DESCUENTOS_ASESORES (ID_LIQUIDACION_ASESOR, TIPO_DESCUENTO, DESCRIPCION_DESCUENTO, VALOR_DESCUENTO, CREATED_BY) VALUES (%s, %s, %s, %s, %s) RETURNING ID_DESCUENTO_ASESOR"
        
        params = (
            descuento.id_liquidacion_asesor,
            descuento.tipo_descuento,
            descuento.descripcion_descuento,
            descuento.valor_descuento,
            usuario
        )
        
        with self.db_manager.obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            # Fetch ID from RETURNING clause
            row = cursor.fetchone()
            if row:
                if hasattr(row, 'keys') or isinstance(row, dict):
                     descuento.id_descuento_asesor = row.get('ID_DESCUENTO_ASESOR') or row.get('id_descuento_asesor')
                else:
                     descuento.id_descuento_asesor = row[0]
            
            descuento.created_by = usuario
            return descuento
    
    def obtener_por_id(self, id_descuento: int) -> Optional[DescuentoAsesor]:
        """
        Obtiene un descuento por su ID.
        
        Args:
            id_descuento: ID del descuento
        
        Returns:
            DescuentoAsesor o None si no existe
        """
        ph = self.db_manager.get_placeholder() if hasattr(self.db_manager, 'get_placeholder') else '?'
        query = f"SELECT * FROM DESCUENTOS_ASESORES WHERE ID_DESCUENTO_ASESOR = {ph}"
        
        with self.db_manager.obtener_conexion() as conn:
            # Try to set row_factory, but respect connection type
            try:
                conn.row_factory = sqlite3.Row
            except:
                pass
                
            cursor = conn.cursor()
            cursor.execute(query, (id_descuento,))
            row = cursor.fetchone()
            
            # If standard cursor in PG, we might need DictCursor or handle tuple
            # Assuming row_to_entity handles both if robust
            return self._row_to_entity(row) if row else None
    
    def listar_por_liquidacion(self, id_liquidacion: int) -> List[DescuentoAsesor]:
        """
        Lista todos los descuentos de una liquidación.
        
        Args:
            id_liquidacion: ID de la liquidación
        
        Returns:
            Lista de DescuentoAsesor
        """
        ph = self.db_manager.get_placeholder() if hasattr(self.db_manager, 'get_placeholder') else '?'
        query = f"SELECT * FROM DESCUENTOS_ASESORES WHERE ID_LIQUIDACION_ASESOR = {ph} ORDER BY FECHA_REGISTRO DESC"
        
        with self.db_manager.obtener_conexion() as conn:
            # Use dict cursor if available via manager, or try setting attribute
            if hasattr(self.db_manager, 'get_dict_cursor'):
                cursor = self.db_manager.get_dict_cursor(conn)
            else:
                 cursor = conn.cursor()
                 
            cursor.execute(query, (id_liquidacion,))
            rows = cursor.fetchall()
            return [self._row_to_entity(row) for row in rows]
    
    def calcular_total_descuentos(self, id_liquidacion: int) -> int:
        """
        Calcula el total de descuentos de una liquidación.
        
        Args:
            id_liquidacion: ID de la liquidación
        
        Returns:
            Total de descuentos (suma)
        """
        ph = self.db_manager.get_placeholder() if hasattr(self.db_manager, 'get_placeholder') else '?'
        query = f"SELECT COALESCE(SUM(VALOR_DESCUENTO), 0) as total FROM DESCUENTOS_ASESORES WHERE ID_LIQUIDACION_ASESOR = {ph}"
        
        with self.db_manager.obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (id_liquidacion,))
            row = cursor.fetchone()
            # Handle possible dict return or tuple
            if hasattr(row, 'keys') or isinstance(row, dict):
                 # Handle case sensitivity (Upper case wrapper returns TOTAL)
                 return row.get('total') or row.get('TOTAL') or 0
            return row[0] if row else 0
    
    def eliminar(self, id_descuento: int) -> bool:
        """
        Elimina (físicamente) un descuento.
        
        Args:
            id_descuento: ID del descuento a eliminar
        
        Returns:
            True si se eliminó, False si no existía
        """
        ph = self.db_manager.get_placeholder() if hasattr(self.db_manager, 'get_placeholder') else '?'
        query = f"DELETE FROM DESCUENTOS_ASESORES WHERE ID_DESCUENTO_ASESOR = {ph}"
        
        with self.db_manager.obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (id_descuento,))
            return cursor.rowcount > 0
    
    def _row_to_entity(self, row) -> DescuentoAsesor:
        """
        Convierte una fila de BD a entidad DescuentoAsesor.
        
        Args:
            row: Fila de SQLite o Dict
        
        Returns:
            DescuentoAsesor
        """
        # Handle dict-like vs tuple access
        if hasattr(row, 'keys') or isinstance(row, dict):
             get = lambda k: row[k] if k in row else row.get(k.lower())
             return DescuentoAsesor(
                id_descuento_asesor=get('ID_DESCUENTO_ASESOR'),
                id_liquidacion_asesor=get('ID_LIQUIDACION_ASESOR'),
                tipo_descuento=get('TIPO_DESCUENTO'),
                descripcion_descuento=get('DESCRIPCION_DESCUENTO'),
                valor_descuento=get('VALOR_DESCUENTO'),
                fecha_registro=get('FECHA_REGISTRO'),
                created_at=get('CREATED_AT'),
                created_by=get('CREATED_BY')
            )
        else:
             # Fallback for tuple (assumes column order matches SELECT *)
             # Assuming standard order: ID, ID_LIQ, TIPO, DESC, VALOR, FECHA, CREATED_AT, CREATED_BY
             return DescuentoAsesor(
                id_descuento_asesor=row[0],
                id_liquidacion_asesor=row[1],
                tipo_descuento=row[2],
                descripcion_descuento=row[3],
                valor_descuento=row[4],
                fecha_registro=row[5],
                created_at=row[6],
                created_by=row[7]
            )
