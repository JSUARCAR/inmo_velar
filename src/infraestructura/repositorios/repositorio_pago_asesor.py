"""
Repositorio PostgreSQL para entidad PagoAsesor.
Implementa operaciones CRUD bajo estándares Élite.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any

from src.dominio.entidades.pago_asesor import PagoAsesor
from src.infraestructura.persistencia.database import DatabaseManager


class RepositorioPagoAsesor:
    """Repositorio para gestión de pagos a asesores en PostgreSQL"""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def crear(self, pago: PagoAsesor, usuario: str) -> PagoAsesor:
        """
        Crea un nuevo pago con PostgreSQL Native.
        """
        query = """
            INSERT INTO PAGOS_ASESORES (
                ID_LIQUIDACION_ASESOR, ID_ASESOR, VALOR_PAGO, FECHA_PAGO,
                FECHA_PROGRAMADA, MEDIO_PAGO, REFERENCIA_PAGO, ESTADO_PAGO,
                MOTIVO_RECHAZO, COMPROBANTE_PAGO, OBSERVACIONES_PAGO,
                FECHA_CONFIRMACION, CREATED_BY, UPDATED_BY
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING ID_PAGO_ASESOR
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
            usuario,
        )

        try:
            with self.db_manager.transaccion() as conn:
                cursor = self.db_manager.get_dict_cursor(conn)
                cursor.execute(query, params)
                row = cursor.fetchone()
                if row:
                    if hasattr(row, "get") or isinstance(row, dict):
                        pago.id_pago_asesor = row.get("ID_PAGO_ASESOR") or row.get(
                            "id_pago_asesor"
                        )
                    else:
                        pago.id_pago_asesor = row[0]

                pago.created_by = usuario
                pago.updated_by = usuario
                return pago
        except Exception as e:
            if "unique" in str(e).lower():
                raise ValueError(
                    f"Ya existe un pago con la referencia {pago.referencia_pago}"
                )
            raise

    def actualizar(self, pago: PagoAsesor, usuario: str) -> PagoAsesor:
        """Actualiza un pago existente."""
        query = """
            UPDATE PAGOS_ASESORES SET
                FECHA_PAGO = %s, MEDIO_PAGO = %s, REFERENCIA_PAGO = %s,
                ESTADO_PAGO = %s, MOTIVO_RECHAZO = %s, COMPROBANTE_PAGO = %s,
                OBSERVACIONES_PAGO = %s, FECHA_CONFIRMACION = %s,
                UPDATED_AT = CURRENT_TIMESTAMP, UPDATED_BY = %s
            WHERE ID_PAGO_ASESOR = %s
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
            pago.id_pago_asesor,
        )

        with self.db_manager.transaccion() as conn:
            cursor = self.db_manager.get_dict_cursor(conn)
            cursor.execute(query, params)
            if cursor.rowcount == 0:
                raise ValueError(f"No se encontró el pago con ID {pago.id_pago_asesor}")

        pago.updated_by = usuario
        pago.updated_at = datetime.now().isoformat()
        return pago

    def obtener_por_id(self, id_pago: int) -> Optional[PagoAsesor]:
        """Obtiene un pago por su ID."""
        query = "SELECT * FROM PAGOS_ASESORES WHERE ID_PAGO_ASESOR = %s"

        with self.db_manager.obtener_conexion() as conn:
            cursor = self.db_manager.get_dict_cursor(conn)
            cursor.execute(query, (id_pago,))
            row = cursor.fetchone()
            return self._row_to_entity(row) if row else None

    def listar_por_liquidacion(self, id_liquidacion: int) -> List[PagoAsesor]:
        """Lista todos los pagos de una liquidación."""
        query = "SELECT * FROM PAGOS_ASESORES WHERE ID_LIQUIDACION_ASESOR = %s ORDER BY FECHA_PROGRAMADA DESC"

        with self.db_manager.obtener_conexion() as conn:
            cursor = self.db_manager.get_dict_cursor(conn)
            cursor.execute(query, (id_liquidacion,))
            rows = cursor.fetchall()
            return [self._row_to_entity(row) for row in rows]

    def listar_por_estado(self, estado: str) -> List[PagoAsesor]:
        """Lista pagos por estado."""
        query = "SELECT * FROM PAGOS_ASESORES WHERE ESTADO_PAGO = %s ORDER BY FECHA_PROGRAMADA ASC"

        with self.db_manager.obtener_conexion() as conn:
            cursor = self.db_manager.get_dict_cursor(conn)
            cursor.execute(query, (estado,))
            rows = cursor.fetchall()
            return [self._row_to_entity(row) for row in rows]

    def listar_pendientes(self) -> List[PagoAsesor]:
        """Lista pagos pendientes o programados."""
        query = "SELECT * FROM PAGOS_ASESORES WHERE ESTADO_PAGO IN ('Pendiente', 'Programado') ORDER BY FECHA_PROGRAMADA ASC"

        with self.db_manager.obtener_conexion() as conn:
            cursor = self.db_manager.get_dict_cursor(conn)
            cursor.execute(query)
            rows = cursor.fetchall()
            return [self._row_to_entity(row) for row in rows]

    def obtener_por_referencia(self, referencia: str) -> Optional[PagoAsesor]:
        """Obtiene un pago por su referencia."""
        query = "SELECT * FROM PAGOS_ASESORES WHERE REFERENCIA_PAGO = %s"

        with self.db_manager.obtener_conexion() as conn:
            cursor = self.db_manager.get_dict_cursor(conn)
            cursor.execute(query, (referencia,))
            row = cursor.fetchone()
            return self._row_to_entity(row) if row else None

    def _row_to_entity(self, row: Dict[str, Any]) -> PagoAsesor:
        """Helper para mapeo de fila a entidad."""

        def gv(k):
            return row.get(k) or row.get(k.upper()) or row.get(k.lower())

        return PagoAsesor(
            id_pago_asesor=gv("ID_PAGO_ASESOR"),
            id_liquidacion_asesor=gv("ID_LIQUIDACION_ASESOR"),
            id_asesor=gv("ID_ASESOR"),
            valor_pago=gv("VALOR_PAGO"),
            fecha_pago=gv("FECHA_PAGO"),
            fecha_programada=gv("FECHA_PROGRAMADA"),
            medio_pago=gv("MEDIO_PAGO"),
            referencia_pago=gv("REFERENCIA_PAGO"),
            estado_pago=gv("ESTADO_PAGO"),
            motivo_rechazo=gv("MOTIVO_RECHAZO"),
            comprobante_pago=gv("COMPROBANTE_PAGO"),
            observaciones_pago=gv("OBSERVACIONES_PAGO"),
            fecha_confirmacion=gv("FECHA_CONFIRMACION"),
            created_at=gv("CREATED_AT"),
            created_by=gv("CREATED_BY"),
            updated_at=gv("UPDATED_AT"),
            updated_by=gv("UPDATED_BY"),
        )
