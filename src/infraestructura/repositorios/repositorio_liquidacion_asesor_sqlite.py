"""
Repositorio SQLite para entidad LiquidacionAsesor.
Implementa operaciones CRUD y consultas especializadas.
"""

import sqlite3
from typing import List, Optional
from datetime import datetime

from src.dominio.entidades.liquidacion_asesor import LiquidacionAsesor
from src.infraestructura.persistencia.database import DatabaseManager


class RepositorioLiquidacionAsesorSQLite:
    """Repositorio para gestión de liquidaciones de asesores en SQLite"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def crear(self, liquidacion: LiquidacionAsesor, usuario: str) -> LiquidacionAsesor:
        """
        Crea una nueva liquidación de asesor.
        
        Args:
            liquidacion: Entidad LiquidacionAsesor a crear
            usuario: Usuario que crea la liquidación
        
        Returns:
            LiquidacionAsesor con ID asignado
        
        Raises:
            ValueError: Si viola constraint UNIQUE (contrato, período)
        """
        ph = self.db_manager.get_placeholder()
        query = f"INSERT INTO LIQUIDACIONES_ASESORES (ID_CONTRATO_A, ID_ASESOR, PERIODO_LIQUIDACION, CANON_ARRENDAMIENTO_LIQUIDADO, PORCENTAJE_COMISION, COMISION_BRUTA, TOTAL_DESCUENTOS, TOTAL_BONIFICACIONES, VALOR_NETO_ASESOR, ESTADO_LIQUIDACION, OBSERVACIONES_LIQUIDACION, USUARIO_CREADOR, CREATED_BY, UPDATED_BY) VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}) RETURNING ID_LIQUIDACION_ASESOR"
        
        params = (
            liquidacion.id_contrato_a,
            liquidacion.id_asesor,
            liquidacion.periodo_liquidacion,
            liquidacion.canon_arrendamiento_liquidado,
            liquidacion.porcentaje_comision,
            liquidacion.comision_bruta,
            liquidacion.total_descuentos,
            liquidacion.total_bonificaciones,
            liquidacion.valor_neto_asesor,
            liquidacion.estado_liquidacion,
            liquidacion.observaciones_liquidacion,
            usuario,
            usuario,
            usuario
        )
        
        try:
            with self.db_manager.obtener_conexion() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                # Fetch ID from RETURNING clause
                row = cursor.fetchone()
                if row:
                    # Check if row is dict-like or tuple
                    if hasattr(row, 'keys') or isinstance(row, dict):
                         # Try uppercase or lowercase key
                         liquidacion.id_liquidacion_asesor = row.get('ID_LIQUIDACION_ASESOR') or row.get('id_liquidacion_asesor')
                    else:
                         liquidacion.id_liquidacion_asesor = row[0]
                
                liquidacion.usuario_creador = usuario
                liquidacion.created_by = usuario
                liquidacion.updated_by = usuario
                return liquidacion
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed" in str(e):
                raise ValueError(
                    f"Ya existe una liquidación para el contrato {liquidacion.id_contrato_a} "
                    f"en el período {liquidacion.periodo_liquidacion}"
                )
            raise
    
    def actualizar(self, liquidacion: LiquidacionAsesor, usuario: str) -> LiquidacionAsesor:
        """
        Actualiza una liquidación existente.
        
        Args:
            liquidacion: Entidad LiquidacionAsesor con datos actualizados
            usuario: Usuario que actualiza
        
        Returns:
            LiquidacionAsesor actualizada
        
        Raises:
            ValueError: Si la liquidación no existe
        """
        ph = self.db_manager.get_placeholder()
        query = f"UPDATE LIQUIDACIONES_ASESORES SET PORCENTAJE_COMISION = {ph}, COMISION_BRUTA = {ph}, TOTAL_DESCUENTOS = {ph}, TOTAL_BONIFICACIONES = {ph}, VALOR_NETO_ASESOR = {ph}, ESTADO_LIQUIDACION = {ph}, FECHA_APROBACION = {ph}, USUARIO_APROBADOR = {ph}, OBSERVACIONES_LIQUIDACION = {ph}, MOTIVO_ANULACION = {ph}, UPDATED_AT = {ph}, UPDATED_BY = {ph} WHERE ID_LIQUIDACION_ASESOR = {ph}"
        
        params = (
            liquidacion.porcentaje_comision,
            liquidacion.comision_bruta,
            liquidacion.total_descuentos,
            liquidacion.total_bonificaciones,
            liquidacion.valor_neto_asesor,
            liquidacion.estado_liquidacion,
            liquidacion.fecha_aprobacion,
            liquidacion.usuario_aprobador,
            liquidacion.observaciones_liquidacion,
            liquidacion.motivo_anulacion,
            datetime.now(),
            usuario,
            liquidacion.id_liquidacion_asesor
        )
        
        with self.db_manager.obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            if cursor.rowcount == 0:
                raise ValueError(f"No se encontró la liquidación con ID {liquidacion.id_liquidacion_asesor}")
        
        liquidacion.updated_by = usuario
        liquidacion.updated_at = datetime.now().isoformat()
        return liquidacion
    
    def obtener_por_id(self, id_liquidacion: int) -> Optional[LiquidacionAsesor]:
        """
        Obtiene una liquidación por su ID.
        
        Args:
            id_liquidacion: ID de la liquidación
        
        Returns:
            LiquidacionAsesor o None si no existe
        """
        ph = self.db_manager.get_placeholder()
        query = f"""
            SELECT 
                la.*,
                p.NOMBRE_COMPLETO as NOMBRE_ASESOR
            FROM LIQUIDACIONES_ASESORES la
            LEFT JOIN ASESORES a ON la.ID_ASESOR = a.ID_ASESOR
            LEFT JOIN PERSONAS p ON a.ID_PERSONA = p.ID_PERSONA
            WHERE la.ID_LIQUIDACION_ASESOR = {ph}
        """
        
        with self.db_manager.obtener_conexion() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, (id_liquidacion,))
            row = cursor.fetchone()
            
            return self._row_to_entity(row) if row else None
    
    def listar_por_asesor(self, id_asesor: int) -> List[LiquidacionAsesor]:
        """
        Lista liquidaciones de un asesor específico.
        
        Args:
            id_asesor: ID del asesor
        
        Returns:
            Lista de LiquidacionAsesor
        """
        ph = self.db_manager.get_placeholder()
        query = f"SELECT * FROM LIQUIDACIONES_ASESORES WHERE ID_ASESOR = {ph} ORDER BY PERIODO_LIQUIDACION DESC"
        
        with self.db_manager.obtener_conexion() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, (id_asesor,))
            rows = cursor.fetchall()
            return [self._row_to_entity(row) for row in rows]
    
    def listar_por_periodo(self, periodo: str) -> List[LiquidacionAsesor]:
        """
        Lista liquidaciones de un período específico.
        
        Args:
            periodo: Período en formato YYYY-MM
        
        Returns:
            Lista de LiquidacionAsesor
        """
        ph = self.db_manager.get_placeholder()
        query = f"SELECT * FROM LIQUIDACIONES_ASESORES WHERE PERIODO_LIQUIDACION = {ph} ORDER BY ID_ASESOR"
        
        with self.db_manager.obtener_conexion() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, (periodo,))
            rows = cursor.fetchall()
            return [self._row_to_entity(row) for row in rows]
    
    def listar_por_estado(self, estado: str) -> List[LiquidacionAsesor]:
        """
        Lista liquidaciones por estado.
        
        Args:
            estado: Estado a filtrar (Pendiente, Aprobada, Pagada, Anulada)
        
        Returns:
            Lista de LiquidacionAsesor
        """
        ph = self.db_manager.get_placeholder()
        query = f"SELECT * FROM LIQUIDACIONES_ASESORES WHERE ESTADO_LIQUIDACION = {ph} ORDER BY PERIODO_LIQUIDACION DESC"
        
        with self.db_manager.obtener_conexion() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, (estado,))
            rows = cursor.fetchall()
            return [self._row_to_entity(row) for row in rows]
    
    def listar_con_filtros(
        self,
        id_asesor: Optional[int] = None,
        periodo: Optional[str] = None,
        estado: Optional[str] = None
    ) -> List[LiquidacionAsesor]:
        """
        Lista liquidaciones con múltiples filtros.
        
        Args:
            id_asesor: Filtrar por asesor
            periodo: Filtrar por período
            estado: Filtrar por estado
        
        Returns:
            Lista de LiquidacionAsesor filtradas
        """
        query = "SELECT * FROM LIQUIDACIONES_ASESORES WHERE 1=1"
        params = []
        
        ph = self.db_manager.get_placeholder()
        if id_asesor is not None:
            query += f" AND ID_ASESOR = {ph}"
            params.append(id_asesor)
        
        if periodo:
            query += f" AND PERIODO_LIQUIDACION = {ph}"
            params.append(periodo)
        
        if estado:
            query += f" AND ESTADO_LIQUIDACION = {ph}"
            params.append(estado)
        
        query += " ORDER BY PERIODO_LIQUIDACION DESC, ID_ASESOR"
        
        with self.db_manager.obtener_conexion() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()
            return [self._row_to_entity(row) for row in rows]
    
    def listar_paginado(
        self,
        page: int,
        page_size: int,
        id_asesor: Optional[int] = None,
        periodo: Optional[str] = None,
        estado: Optional[str] = None
    ) -> tuple[List[LiquidacionAsesor], int]:
        """
        Lista liquidaciones con paginación y filtros.
        
        Args:
            page: Número de página (1-based)
            page_size: Tamaño de página
            id_asesor: Filtro por asesor
            periodo: Filtro por período
            estado: Filtro por estado
            
        Returns:
            Tupla (lista de liquidaciones, total de registros)
        """

        offset = (page - 1) * page_size
    
        # Obtener placeholder dinámico
        ph = self.db_manager.get_placeholder() if hasattr(self.db_manager, 'get_placeholder') else '?'
        
        # Query base con JOIN a ASESORES y PERSONAS para obtener nombre del asesor
        base_query = """
            FROM LIQUIDACIONES_ASESORES la
            LEFT JOIN ASESORES a ON la.ID_ASESOR = a.ID_ASESOR
            LEFT JOIN PERSONAS p ON a.ID_PERSONA = p.ID_PERSONA
            WHERE 1=1
        """
        params = []
        
        if id_asesor is not None:
            base_query += f" AND la.ID_ASESOR = {ph}"
            params.append(id_asesor)
            
        if periodo:
            base_query += f" AND la.PERIODO_LIQUIDACION = {ph}"
            params.append(periodo)
            
        if estado:
            base_query += f" AND la.ESTADO_LIQUIDACION = {ph}"
            params.append(estado)
            
        # Contar total
        count_query = f"SELECT COUNT(*) as total {base_query}"
        
        # Consultar paginado - ahora incluye nombre del asesor
        data_query = f"""
            SELECT 
                la.*,
                p.NOMBRE_COMPLETO as NOMBRE_ASESOR
            {base_query}
            ORDER BY la.PERIODO_LIQUIDACION DESC, la.ID_ASESOR 
            LIMIT {ph} OFFSET {ph}
        """
        data_params = params + [page_size, offset]
        
        with self.db_manager.obtener_conexion() as conn:
            cursor = self.db_manager.get_dict_cursor(conn)
            
            # Obtener total
            cursor.execute(count_query, tuple(params))
            row_count = cursor.fetchone()
            total = row_count.get('TOTAL') or row_count.get('total') or 0
            
            # Obtener datos
            cursor.execute(data_query, tuple(data_params))
            rows = cursor.fetchall()
            
            return [self._row_to_entity(row) for row in rows], total
    
    def listar_todas(self) -> List[LiquidacionAsesor]:
        """
        Lista todas las liquidaciones.
        
        Returns:
            Lista de LiquidacionAsesor
        """
        query = """
            SELECT * FROM LIQUIDACIONES_ASESORES
            ORDER BY PERIODO_LIQUIDACION DESC, ID_ASESOR
        """
        
        with self.db_manager.obtener_conexion() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            return [self._row_to_entity(row) for row in rows]
    
    def obtener_por_contrato_periodo(self, id_contrato: int, periodo: str) -> Optional[LiquidacionAsesor]:
        """
        Obtiene una liquidación por contrato y período (validación UNIQUE LEGACY).
        NOTA: Este método es legacy. Usar obtener_por_asesor_periodo() para la nueva lógica.
        
        Args:
            id_contrato: ID del contrato
            periodo: Período en formato YYYY-MM
        
        Returns:
            LiquidacionAsesor o None si no existe
        """
        ph = self.db_manager.get_placeholder()
        query = f"SELECT * FROM LIQUIDACIONES_ASESORES WHERE ID_CONTRATO_A = {ph} AND PERIODO_LIQUIDACION = {ph}"
        
        with self.db_manager.obtener_conexion() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, (id_contrato, periodo))
            row = cursor.fetchone()
            
            return self._row_to_entity(row) if row else None
    
    def obtener_por_asesor_periodo(self, id_asesor: int, periodo: str) -> Optional[LiquidacionAsesor]:
        """
        Obtiene una liquidación por asesor y período (validación UNIQUE actual).
        Usado para validar duplicados antes de crear una nueva liquidación.
        
        Args:
            id_asesor: ID del asesor
            periodo: Período en formato YYYY-MM
        
        Returns:
            LiquidacionAsesor o None si no existe
        """
        ph = self.db_manager.get_placeholder()
        query = f"SELECT * FROM LIQUIDACIONES_ASESORES WHERE ID_ASESOR = {ph} AND PERIODO_LIQUIDACION = {ph}"
        
        with self.db_manager.obtener_conexion() as conn:
            cursor = self.db_manager.get_dict_cursor(conn)
            cursor.execute(query, (id_asesor, periodo))
            row = cursor.fetchone()
            
            return self._row_to_entity(row) if row else None
    
    def guardar_contratos_liquidacion(self, id_liquidacion: int, contratos_ids_canones: List[tuple], usuario: str):
        """
        Guarda los contratos asociados a una liquidación en la tabla intermedia.
        
        Args:
            id_liquidacion: ID de la liquidación
            contratos_ids_canones: Lista de tuplas (id_contrato, canon)
            usuario: Usuario que crea la relación
        """
        ph = self.db_manager.get_placeholder()
        query = f"""
            INSERT INTO LIQUIDACIONES_CONTRATOS (
                ID_LIQUIDACION_ASESOR, ID_CONTRATO_A, CANON_INCLUIDO, CREATED_BY
            ) VALUES ({ph}, {ph}, {ph}, {ph})
        """
        
        with self.db_manager.obtener_conexion() as conn:
            cursor = conn.cursor()
            for id_contrato, canon in contratos_ids_canones:
                cursor.execute(query, (id_liquidacion, id_contrato, canon, usuario))
    
    def obtener_contratos_de_liquidacion(self, id_liquidacion: int) -> List[dict]:
        """
        Obtiene la lista de contratos asociados a una liquidación con sus detalles.
        
        Args:
            id_liquidacion: ID de la liquidación
        
        Returns:
            Lista de diccionarios con información de cada contrato
        """
        ph = self.db_manager.get_placeholder()
        query = f"SELECT lc.ID_CONTRATO_A, lc.CANON_INCLUIDO, ca.CANON_ARRENDAMIENTO, p.DIRECCION_PROPIEDAD, p.MATRICULA_INMOBILIARIA, per.NOMBRE_COMPLETO as ARRENDATARIO FROM LIQUIDACIONES_CONTRATOS lc JOIN CONTRATOS_ARRENDAMIENTOS ca ON lc.ID_CONTRATO_A = ca.ID_CONTRATO_A JOIN PROPIEDADES p ON ca.ID_PROPIEDAD = p.ID_PROPIEDAD JOIN ARRENDATARIOS arr ON ca.ID_ARRENDATARIO = arr.ID_ARRENDATARIO JOIN PERSONAS per ON arr.ID_PERSONA = per.ID_PERSONA WHERE lc.ID_LIQUIDACION_ASESOR = {ph} ORDER BY p.DIRECCION_PROPIEDAD"
        
        with self.db_manager.obtener_conexion() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, (id_liquidacion,))
            rows = cursor.fetchall()
            
            return [
                {
                    'id_contrato': row['ID_CONTRATO_A'],
                    'canon_incluido': row['CANON_INCLUIDO'],
                    'canon_actual': row['CANON_ARRENDAMIENTO'],
                    'direccion': row['DIRECCION_PROPIEDAD'],
                    'matricula': row['MATRICULA_INMOBILIARIA'],
                    'arrendatario': row['ARRENDATARIO']
                }
                for row in rows
            ]
    
    def _row_to_entity(self, row: sqlite3.Row) -> LiquidacionAsesor:
        """
        Convierte una fila de BD a entidad LiquidacionAsesor.
        
        Args:
            row: Fila de SQLite
        
        Returns:
            LiquidacionAsesor
        """
        return LiquidacionAsesor(
            id_liquidacion_asesor=row.get('ID_LIQUIDACION_ASESOR'),
            id_contrato_a=row.get('ID_CONTRATO_A'),
            id_asesor=row.get('ID_ASESOR'),
            periodo_liquidacion=row.get('PERIODO_LIQUIDACION'),
            canon_arrendamiento_liquidado=row.get('CANON_ARRENDAMIENTO_LIQUIDADO'),
            porcentaje_comision=row.get('PORCENTAJE_COMISION'),
            comision_bruta=row.get('COMISION_BRUTA'),
            total_descuentos=row.get('TOTAL_DESCUENTOS'),
            total_bonificaciones=row.get('TOTAL_BONIFICACIONES') or 0,
            valor_neto_asesor=row.get('VALOR_NETO_ASESOR'),
            estado_liquidacion=row.get('ESTADO_LIQUIDACION'),
            fecha_creacion=row.get('FECHA_CREACION'),
            fecha_aprobacion=row.get('FECHA_APROBACION'),
            usuario_creador=row.get('USUARIO_CREADOR'),
            usuario_aprobador=row.get('USUARIO_APROBADOR'),
            observaciones_liquidacion=row.get('OBSERVACIONES_LIQUIDACION'),
            motivo_anulacion=row.get('MOTIVO_ANULACION'),
            created_at=row.get('CREATED_AT'),
            created_by=row.get('CREATED_BY'),
            updated_at=row.get('UPDATED_AT'),
            updated_by=row.get('UPDATED_BY'),
            nombre_asesor=row.get('NOMBRE_ASESOR')  # Campo adicional del JOIN
        )
