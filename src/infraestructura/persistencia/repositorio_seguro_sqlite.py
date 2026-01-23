"""
Repositorio SQLite para la entidad Seguro.
Implementa el acceso a datos de seguros de arrendamiento.
"""

from typing import List, Optional
from datetime import datetime
from src.dominio.entidades.seguro import Seguro
from src.infraestructura.persistencia.database import DatabaseManager


class RepositorioSeguroSQLite:
    """
    Repositorio para gestionar seguros en SQLite.
    """
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def crear(self, seguro: Seguro, usuario_sistema: str) -> Seguro:
        """
        Crea un nuevo seguro en la base de datos.
        
        Args:
            seguro: Entidad Seguro a crear
            usuario_sistema: Usuario que realiza la operación
            
        Returns:
            Seguro creado con ID asignado
        """
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            placeholder = self.db.get_placeholder()
            
            ahora = datetime.now().isoformat()
            
            cursor.execute(f"""
                INSERT INTO SEGUROS (
                    NOMBRE_SEGURO,
                    FECHA_INICIO_SEGURO,
                    PORCENTAJE_SEGURO,
                    ESTADO_SEGURO,
                    FECHA_INGRESO_SEGURO,
                    CREATED_AT,
                    CREATED_BY
                ) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
            """, (
                seguro.nombre_seguro,
                seguro.fecha_inicio_seguro,
                seguro.porcentaje_seguro,
                seguro.estado_seguro,
                seguro.fecha_ingreso_seguro or datetime.now().date().isoformat(),
                ahora,
                usuario_sistema
            ))
            
            seguro.id_seguro = self.db.get_last_insert_id(cursor, 'SEGUROS', 'ID_SEGURO')
            seguro.created_at = ahora
            seguro.created_by = usuario_sistema
            
            conn.commit()
            
        return seguro
    
    def obtener_por_id(self, id_seguro: int) -> Optional[Seguro]:
        """
        Obtiene un seguro por su ID.
        
        Args:
            id_seguro: ID del seguro
            
        Returns:
            Seguro encontrado o None
        """
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            placeholder = self.db.get_placeholder()
            
            cursor.execute(f"""
                SELECT 
                    ID_SEGURO,
                    NOMBRE_SEGURO,
                    FECHA_INICIO_SEGURO,
                    PORCENTAJE_SEGURO,
                    ESTADO_SEGURO,
                    FECHA_INGRESO_SEGURO,
                    MOTIVO_INACTIVACION,
                    CREATED_AT,
                    CREATED_BY,
                    UPDATED_AT,
                    UPDATED_BY
                FROM SEGUROS
                WHERE ID_SEGURO = {placeholder}
            """, (id_seguro,))
            
            row = cursor.fetchone()
            
            if row:
                return self._row_a_seguro(row)
            
            return None
    
    def obtener_por_nombre(self, nombre_seguro: str) -> Optional[Seguro]:
        """
        Obtiene un seguro por su nombre.
        
        Args:
            nombre_seguro: Nombre del seguro
            
        Returns:
            Seguro encontrado o None
        """
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            placeholder = self.db.get_placeholder()
            
            cursor.execute(f"""
                SELECT 
                    ID_SEGURO,
                    NOMBRE_SEGURO,
                    FECHA_INICIO_SEGURO,
                    PORCENTAJE_SEGURO,
                    ESTADO_SEGURO,
                    FECHA_INGRESO_SEGURO,
                    MOTIVO_INACTIVACION,
                    CREATED_AT,
                    CREATED_BY,
                    UPDATED_AT,
                    UPDATED_BY
                FROM SEGUROS
                WHERE NOMBRE_SEGURO = {placeholder}
            """, (nombre_seguro,))
            
            row = cursor.fetchone()
            
            if row:
                return self._row_a_seguro(row)
            
            return None
    
    def listar_todos(self, solo_activos: Optional[bool] = True) -> List[Seguro]:
        """
        Lista todos los seguros.
        
        Args:
            solo_activos: Si True, solo seguros activos. Si False, solo inactivos. Si None, todos.
            
        Returns:
            Lista de seguros
        """
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            placeholder = self.db.get_placeholder()
            
            query = """
                SELECT 
                    ID_SEGURO,
                    NOMBRE_SEGURO,
                    FECHA_INICIO_SEGURO,
                    PORCENTAJE_SEGURO,
                    ESTADO_SEGURO,
                    FECHA_INGRESO_SEGURO,
                    MOTIVO_INACTIVACION,
                    CREATED_AT,
                    CREATED_BY,
                    UPDATED_AT,
                    UPDATED_BY
                FROM SEGUROS
            """
            
            # Filtrar por estado si se especifica
            if solo_activos is not None:
                query += f" WHERE ESTADO_SEGURO = {placeholder}"
            
            query += " ORDER BY NOMBRE_SEGURO"
            
            # Ejecutar consulta
            if solo_activos is not None:
                cursor.execute(query, (solo_activos,))
            else:
                cursor.execute(query)
            
            return [self._row_a_seguro(row) for row in cursor.fetchall()]
    
    def actualizar(self, seguro: Seguro, usuario_sistema: str) -> Seguro:
        """
        Actualiza un seguro existente.
        
        Args:
            seguro: Entidad Seguro con datos actualizados
            usuario_sistema: Usuario que realiza la operación
            
        Returns:
            Seguro actualizado
        """
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            placeholder = self.db.get_placeholder()
            
            ahora = datetime.now().isoformat()
            
            cursor.execute(f"""
                UPDATE SEGUROS SET
                    NOMBRE_SEGURO = {placeholder},
                    FECHA_INICIO_SEGURO = {placeholder},
                    PORCENTAJE_SEGURO = {placeholder},
                    ESTADO_SEGURO = {placeholder},
                    UPDATED_AT = {placeholder},
                    UPDATED_BY = {placeholder}
                WHERE ID_SEGURO = {placeholder}
            """, (
                seguro.nombre_seguro,
                seguro.fecha_inicio_seguro,
                seguro.porcentaje_seguro,
                seguro.estado_seguro,
                ahora,
                usuario_sistema,
                seguro.id_seguro
            ))
            
            seguro.updated_at = ahora
            seguro.updated_by = usuario_sistema
            
            conn.commit()
            
        return seguro
    
    def desactivar(self, id_seguro: int, motivo: str, usuario_sistema: str) -> bool:
        """
        Desactiva un seguro (soft delete).
        
        Args:
            id_seguro: ID del seguro a desactivar
            motivo: Motivo de la desactivación
            usuario_sistema: Usuario que realiza la operación
            
        Returns:
            True si se desactivó exitosamente
        """
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            placeholder = self.db.get_placeholder()
            
            ahora = datetime.now().isoformat()
            
            cursor.execute(f"""
                UPDATE SEGUROS SET
                    ESTADO_SEGURO = FALSE,
                    MOTIVO_INACTIVACION = {placeholder},
                    UPDATED_AT = {placeholder},
                    UPDATED_BY = {placeholder}
                WHERE ID_SEGURO = {placeholder}
            """, (motivo, ahora, usuario_sistema, id_seguro))
            
            conn.commit()
            
            return cursor.rowcount > 0
    
    def activar(self, id_seguro: int, usuario_sistema: str) -> bool:
        """
        Reactiva un seguro desactivado.
        
        Args:
            id_seguro: ID del seguro a activar
            usuario_sistema: Usuario que realiza la operación
            
        Returns:
            True si se activó exitosamente
        """
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            placeholder = self.db.get_placeholder()
            
            ahora = datetime.now().isoformat()
            
            cursor.execute(f"""
                UPDATE SEGUROS SET
                    ESTADO_SEGURO = TRUE,
                    MOTIVO_INACTIVACION = NULL,
                    UPDATED_AT = {placeholder},
                    UPDATED_BY = {placeholder}
                WHERE ID_SEGURO = {placeholder}
            """, (ahora, usuario_sistema, id_seguro))
            
            conn.commit()
            
            return cursor.rowcount > 0
    
    def _row_a_seguro(self, row) -> Seguro:
        """
        Convierte una fila de la BD a entidad Seguro.
        
        Args:
            row: Dict con datos de la BD
            
        Returns:
            Entidad Seguro
        """
        # Manejo flexible de diccionarios
        if hasattr(row, 'keys'):
            data = dict(row)
        else:
            data = dict(row)
        
        # Helper para obtener valor ignorando mayúsculas/minúsculas
        def get_val(key):
            return data.get(key) or data.get(key.upper()) or data.get(key.lower())
        
        return Seguro(
            id_seguro=get_val('ID_SEGURO'),
            nombre_seguro=get_val('NOMBRE_SEGURO'),
            fecha_inicio_seguro=get_val('FECHA_INICIO_SEGURO'),
            porcentaje_seguro=get_val('PORCENTAJE_SEGURO'),
            estado_seguro=get_val('ESTADO_SEGURO'),
            fecha_ingreso_seguro=get_val('FECHA_INGRESO_SEGURO'),
            motivo_inactivacion=get_val('MOTIVO_INACTIVACION'),
            created_at=get_val('CREATED_AT'),
            created_by=get_val('CREATED_BY'),
            updated_at=get_val('UPDATED_AT'),
            updated_by=get_val('UPDATED_BY')
        )
