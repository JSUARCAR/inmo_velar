"""
Repositorio SQLite para entidad PagoAsesor.
Implementa operaciones CRUD y consultas especializadas.
"""

import sqlite3
from typing import List, Optional
from datetime import datetime

from src.dominio.entidades.pago_asesor import PagoAsesor
from src.infraestructura.persistencia.database import DatabaseManager


class RepositorioPagoAsesorSQLite:
    """Repositorio para gestión de pagos a asesores en SQLite"""
    
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
    
    def crear(self, pago: PagoAsesor, usuario: str) -> PagoAsesor:
        """
        Crea un nuevo pago.
        
        Args:
            pago: Entidad PagoAsesor a crear
            usuario: Usuario que crea el pago
        
        Returns:
            PagoAsesor con ID asignado
        
        Raises:
            ValueError: Si viola constraint UNIQUE en referencia_pago
        """
        ph = self.db_manager.get_placeholder()
        query = f"""
            INSERT INTO PAGOS_ASESORES (
                ID_LIQUIDACION_ASESOR, ID_ASESOR, VALOR_PAGO, FECHA_PAGO,
                FECHA_PROGRAMADA, MEDIO_PAGO, REFERENCIA_PAGO, ESTADO_PAGO,
                MOTIVO_RECHAZO, COMPROBANTE_PAGO, OBSERVACIONES_PAGO,
                FECHA_CONFIRMACION, CREATED_BY, UPDATED_BY
            ) VALUES ({ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph}, {ph})
        """
        
        params = (
            pago.id_liquidacion_asesor,
            pago.id_asesor,
            pago.valor_pago,
            pago.fecha_pago,
            pago.fecha_programada,
            pago.medio_pago,
            pago.referencia_pago,
            pago.estado_pago,
            pago.motivo_rechazo,
            pago.comprobante_pago,
            pago.observaciones_pago,
            pago.fecha_confirmacion,
            usuario,
            usuario
        )
        
        try:
            with self.db_manager.obtener_conexion() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                pago.id_pago_asesor = cursor.lastrowid
                pago.created_by = usuario
                pago.updated_by = usuario
                return pago
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed" in str(e):
                raise ValueError(
                    f"Ya existe un pago con la referencia {pago.referencia_pago}"
                )
            raise
    
    def actualizar(self, pago: PagoAsesor, usuario: str) -> PagoAsesor:
        """
        Actualiza un pago existente.
        
        Args:
            pago: Entidad PagoAsesor con datos actualizados
            usuario: Usuario que actualiza
        
        Returns:
            PagoAsesor actualizado
        
        Raises:
            ValueError: Si el pago no existe
        """
        ph = self.db_manager.get_placeholder()
        query = f"""
            UPDATE PAGOS_ASESORES SET
                FECHA_PAGO = {ph},
                MEDIO_PAGO = {ph},
                REFERENCIA_PAGO = {ph},
                ESTADO_PAGO = {ph},
                MOTIVO_RECHAZO = {ph},
                COMPROBANTE_PAGO = {ph},
                OBSERVACIONES_PAGO = {ph},
                FECHA_CONFIRMACION = {ph},
                UPDATED_AT = CURRENT_TIMESTAMP,
                UPDATED_BY = {ph}
            WHERE ID_PAGO_ASESOR = {ph}
        """
        
        params = (
            pago.fecha_pago,
            pago.medio_pago,
            pago.referencia_pago,
            pago.estado_pago,
            pago.motivo_rechazo,
            pago.comprobante_pago,
            pago.observaciones_pago,
            pago.fecha_confirmacion,
            usuario,
            pago.id_pago_asesor
        )
        
        with self.db_manager.obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            if cursor.rowcount == 0:
                raise ValueError(f"No se encontró el pago con ID {pago.id_pago_asesor}")
        
        pago.updated_by = usuario
        pago.updated_at = datetime.now().isoformat()
        return pago
    
    def obtener_por_id(self, id_pago: int) -> Optional[PagoAsesor]:
        """
        Obtiene un pago por su ID.
        
        Args:
            id_pago: ID del pago
        
        Returns:
            PagoAsesor o None si no existe
        """
        ph = self.db_manager.get_placeholder()
        query = f"""
            SELECT * FROM PAGOS_ASESORES
            WHERE ID_PAGO_ASESOR = {ph}
        """
        
        with self.db_manager.obtener_conexion() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, (id_pago,))
            row = cursor.fetchone()
            
            return self._row_to_entity(row) if row else None
    
    def listar_por_liquidacion(self, id_liquidacion: int) -> List[PagoAsesor]:
        """
        Lista todos los pagos de una liquidación.
        
        Args:
            id_liquidacion: ID de la liquidación
        
        Returns:
            Lista de PagoAsesor
        """
        ph = self.db_manager.get_placeholder()
        query = f"""
            SELECT * FROM PAGOS_ASESORES
            WHERE ID_LIQUIDACION_ASESOR = {ph}
            ORDER BY FECHA_PROGRAMADA DESC
        """
        
        with self.db_manager.obtener_conexion() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, (id_liquidacion,))
            rows = cursor.fetchall()
            return [self._row_to_entity(row) for row in rows]
    
    def listar_por_estado(self, estado: str) -> List[PagoAsesor]:
        """
        Lista pagos por estado.
        
        Args:
            estado: Estado a filtrar (Pendiente, Programado, Pagado, etc.)
        
        Returns:
            Lista de PagoAsesor
        """
        ph = self.db_manager.get_placeholder()
        query = f"""
            SELECT * FROM PAGOS_ASESORES
            WHERE ESTADO_PAGO = {ph}
            ORDER BY FECHA_PROGRAMADA ASC
        """
        
        with self.db_manager.obtener_conexion() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, (estado,))
            rows = cursor.fetchall()
            return [self._row_to_entity(row) for row in rows]
    
    def listar_pendientes(self) -> List[PagoAsesor]:
        """
        Lista pagos pendientes o programados.
        
        Returns:
            Lista de PagoAsesor pendientes/programados
        """
        query = """
            SELECT * FROM PAGOS_ASESORES
            WHERE ESTADO_PAGO IN ('Pendiente', 'Programado')
            ORDER BY FECHA_PROGRAMADA ASC
        """
        
        with self.db_manager.obtener_conexion() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            return [self._row_to_entity(row) for row in rows]
    
    def obtener_por_referencia(self, referencia: str) -> Optional[PagoAsesor]:
        """
        Obtiene un pago por su referencia (validación UNIQUE).
        
        Args:
            referencia: Referencia del pago
        
        Returns:
            PagoAsesor o None si no existe
        """
        ph = self.db_manager.get_placeholder()
        query = f"""
            SELECT * FROM PAGOS_ASESORES
            WHERE REFERENCIA_PAGO = {ph}
        """
        
        with self.db_manager.obtener_conexion() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, (referencia,))
            row = cursor.fetchone()
            
            return self._row_to_entity(row) if row else None
    
    def _row_to_entity(self, row: sqlite3.Row) -> PagoAsesor:
        """
        Convierte una fila de BD a entidad PagoAsesor.
        
        Args:
            row: Fila de SQLite
        
        Returns:
            PagoAsesor
        """
        return PagoAsesor(
            id_pago_asesor=row['ID_PAGO_ASESOR'],
            id_liquidacion_asesor=row['ID_LIQUIDACION_ASESOR'],
            id_asesor=row['ID_ASESOR'],
            valor_pago=row['VALOR_PAGO'],
            fecha_pago=row['FECHA_PAGO'],
            fecha_programada=row['FECHA_PROGRAMADA'],
            medio_pago=row['MEDIO_PAGO'],
            referencia_pago=row['REFERENCIA_PAGO'],
            estado_pago=row['ESTADO_PAGO'],
            motivo_rechazo=row['MOTIVO_RECHAZO'],
            comprobante_pago=row['COMPROBANTE_PAGO'],
            observaciones_pago=row['OBSERVACIONES_PAGO'],
            fecha_confirmacion=row['FECHA_CONFIRMACION'],
            created_at=row['CREATED_AT'],
            created_by=row['CREATED_BY'],
            updated_at=row['UPDATED_AT'],
            updated_by=row['UPDATED_BY']
        )
