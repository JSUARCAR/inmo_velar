"""
Repositorio SQLite para entidad ReciboPublico.
Implementa operaciones CRUD y consultas especializadas.
"""

import sqlite3
from datetime import datetime
from typing import List, Optional

from src.dominio.entidades.recibo_publico import ReciboPublico
from src.infraestructura.persistencia.database import DatabaseManager


class RepositorioReciboPublicoSQLite:
    """Repositorio para gestión de recibos públicos en SQLite"""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self.placeholder = self.db_manager.get_placeholder()

    def crear(self, recibo: ReciboPublico, usuario: str) -> ReciboPublico:
        """
        Crea un nuevo recibo público.
        """
        query = f"""
            INSERT INTO RECIBOS_PUBLICOS (
                ID_PROPIEDAD, PERIODO_RECIBO, TIPO_SERVICIO, VALOR_RECIBO,
                FECHA_VENCIMIENTO, FECHA_PAGO, COMPROBANTE, ESTADO,
                FECHA_DESDE, FECHA_HASTA, DIAS_FACTURADOS,
                CREATED_BY, UPDATED_BY
            ) VALUES ({self.placeholder}, {self.placeholder}, {self.placeholder}, {self.placeholder}, {self.placeholder}, {self.placeholder}, {self.placeholder}, {self.placeholder}, {self.placeholder}, {self.placeholder}, {self.placeholder}, {self.placeholder}, {self.placeholder})
        """

        params = (
            recibo.id_propiedad,
            recibo.periodo_recibo,
            recibo.tipo_servicio,
            recibo.valor_recibo,
            recibo.fecha_vencimiento,
            recibo.fecha_pago,
            recibo.comprobante,
            recibo.estado,
            recibo.fecha_desde,
            recibo.fecha_hasta,
            recibo.dias_facturados,
            usuario,
            usuario,
        )

        try:
            with self.db_manager.obtener_conexion() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                recibo.id_recibo_publico = cursor.lastrowid
                return recibo
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed" in str(e):
                raise ValueError(
                    f"Ya existe un recibo de {recibo.tipo_servicio} para esta propiedad "
                    f"en el período {recibo.periodo_recibo}"
                )
            raise

    def actualizar(self, recibo: ReciboPublico, usuario: str) -> ReciboPublico:
        """
        Actualiza un recibo público existente.
        """
        timestamp = datetime.now().isoformat()

        query = f"""
            UPDATE RECIBOS_PUBLICOS SET
                ID_PROPIEDAD = {self.placeholder},
                PERIODO_RECIBO = {self.placeholder},
                TIPO_SERVICIO = {self.placeholder},
                VALOR_RECIBO = {self.placeholder},
                FECHA_VENCIMIENTO = {self.placeholder},
                FECHA_PAGO = {self.placeholder},
                COMPROBANTE = {self.placeholder},
                ESTADO = {self.placeholder},
                FECHA_DESDE = {self.placeholder},
                FECHA_HASTA = {self.placeholder},
                DIAS_FACTURADOS = {self.placeholder},
                UPDATED_AT = {self.placeholder},
                UPDATED_BY = {self.placeholder}
            WHERE ID_RECIBO_PUBLICO = {self.placeholder}
        """

        params = (
            recibo.id_propiedad,
            recibo.periodo_recibo,
            recibo.tipo_servicio,
            recibo.valor_recibo,
            recibo.fecha_vencimiento,
            recibo.fecha_pago,
            recibo.comprobante,
            recibo.estado,
            recibo.fecha_desde,
            recibo.fecha_hasta,
            recibo.dias_facturados,
            timestamp,
            usuario,
            recibo.id_recibo_publico,
        )

        with self.db_manager.obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            if cursor.rowcount == 0:
                raise ValueError(f"No se encontró el recibo con ID {recibo.id_recibo_publico}")

        recibo.updated_by = usuario
        recibo.updated_at = timestamp
        return recibo

    def obtener_por_id(self, id_recibo: int) -> Optional[ReciboPublico]:
        """
        Obtiene un recibo por su ID.
        """
        query = f"""
            SELECT * FROM RECIBOS_PUBLICOS
            WHERE ID_RECIBO_PUBLICO = {self.placeholder}
        """

        with self.db_manager.obtener_conexion() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, (id_recibo,))
            row = cursor.fetchone()

            return self._row_to_entity(row) if row else None

    def listar_todos(self) -> List[ReciboPublico]:
        """
        Lista todos los recibos públicos.
        """
        query = """
            SELECT * FROM RECIBOS_PUBLICOS
            ORDER BY PERIODO_RECIBO DESC, FECHA_VENCIMIENTO DESC
        """

        with self.db_manager.obtener_conexion() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            return [self._row_to_entity(row) for row in rows]

    def listar_por_propiedad(
        self,
        id_propiedad: int,
        periodo_inicio: Optional[str] = None,
        periodo_fin: Optional[str] = None,
    ) -> List[ReciboPublico]:
        """
        Lista recibos de una propiedad, opcionalmente filtrados por rango de períodos.
        """
        query = f"""
            SELECT * FROM RECIBOS_PUBLICOS
            WHERE ID_PROPIEDAD = {self.placeholder}
        """
        params = [id_propiedad]

        if periodo_inicio:
            query += f" AND PERIODO_RECIBO >= {self.placeholder}"
            params.append(periodo_inicio)

        if periodo_fin:
            query += f" AND PERIODO_RECIBO <= {self.placeholder}"
            params.append(periodo_fin)

        query += " ORDER BY PERIODO_RECIBO DESC, TIPO_SERVICIO"

        with self.db_manager.obtener_conexion() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()
            return [self._row_to_entity(row) for row in rows]

    def listar_por_estado(self, estado: str) -> List[ReciboPublico]:
        """
        Lista recibos por estado.
        """
        query = f"""
            SELECT * FROM RECIBOS_PUBLICOS
            WHERE ESTADO = {self.placeholder}
            ORDER BY PERIODO_RECIBO DESC, FECHA_VENCIMIENTO
        """

        with self.db_manager.obtener_conexion() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, (estado,))
            rows = cursor.fetchall()
            return [self._row_to_entity(row) for row in rows]

    def listar_vencidos(self) -> List[ReciboPublico]:
        """
        Lista recibos vencidos.
        """
        if self.db_manager.use_postgresql:
            query = """
                SELECT * FROM RECIBOS_PUBLICOS
                WHERE CAST(FECHA_VENCIMIENTO AS DATE) < CURRENT_DATE
                  AND ESTADO != 'Pagado'
                ORDER BY FECHA_VENCIMIENTO ASC
            """
        else:
            query = """
                SELECT * FROM RECIBOS_PUBLICOS
                WHERE FECHA_VENCIMIENTO < date('now')
                  AND ESTADO != 'Pagado'
                ORDER BY FECHA_VENCIMIENTO ASC
            """

        with self.db_manager.obtener_conexion() as conn:
            cursor = self.db_manager.get_dict_cursor(conn)
            cursor.execute(query)
            rows = cursor.fetchall()
            return [self._row_to_entity(row) for row in rows]

    def listar_proximos_vencer(self, dias: int = 5) -> List[ReciboPublico]:
        """
        Lista recibos pendientes que vencen en los próximos N días.
        No incluye recibos ya vencidos ni pagados.
        """
        if self.db_manager.use_postgresql:
            query = f"""
                SELECT * FROM RECIBOS_PUBLICOS
                WHERE CAST(FECHA_VENCIMIENTO AS DATE) > CURRENT_DATE
                  AND CAST(FECHA_VENCIMIENTO AS DATE) <= CURRENT_DATE + INTERVAL '{dias} day'
                  AND ESTADO != 'Pagado'
                ORDER BY FECHA_VENCIMIENTO ASC
            """
        else:
            query = f"""
                SELECT * FROM RECIBOS_PUBLICOS
                WHERE FECHA_VENCIMIENTO > date('now')
                  AND FECHA_VENCIMIENTO <= date('now', '+{dias} days')
                  AND ESTADO != 'Pagado'
                ORDER BY FECHA_VENCIMIENTO ASC
            """

        with self.db_manager.obtener_conexion() as conn:
            cursor = self.db_manager.get_dict_cursor(conn)
            cursor.execute(query)
            rows = cursor.fetchall()
            return [self._row_to_entity(row) for row in rows]

    def listar_con_filtros(
        self,
        id_propiedad: Optional[int] = None,
        periodo_inicio: Optional[str] = None,
        periodo_fin: Optional[str] = None,
        tipo_servicio: Optional[str] = None,
        estado: Optional[str] = None,
    ) -> List[ReciboPublico]:
        """
        Lista recibos con múltiples filtros.
        """
        query = "SELECT * FROM RECIBOS_PUBLICOS WHERE 1=1"
        params = []

        if id_propiedad is not None:
            query += f" AND ID_PROPIEDAD = {self.placeholder}"
            params.append(id_propiedad)

        if periodo_inicio:
            query += f" AND PERIODO_RECIBO >= {self.placeholder}"
            params.append(periodo_inicio)

        if periodo_fin:
            query += f" AND PERIODO_RECIBO <= {self.placeholder}"
            params.append(periodo_fin)

        if tipo_servicio:
            query += f" AND TIPO_SERVICIO = {self.placeholder}"
            params.append(tipo_servicio)

        if estado:
            query += f" AND ESTADO = {self.placeholder}"
            params.append(estado)

        query += " ORDER BY PERIODO_RECIBO DESC, FECHA_VENCIMIENTO DESC"

        with self.db_manager.obtener_conexion() as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()
            return [self._row_to_entity(row) for row in rows]

    def eliminar(self, id_recibo: int) -> bool:
        """
        Elimina (físicamente) un recibo público.
        """
        query = f"DELETE FROM RECIBOS_PUBLICOS WHERE ID_RECIBO_PUBLICO = {self.placeholder}"

        with self.db_manager.obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (id_recibo,))
            return cursor.rowcount > 0

    def _row_to_entity(self, row: sqlite3.Row) -> ReciboPublico:
        """
        Convierte una fila de BD a entidad ReciboPublico.
        """
        return ReciboPublico(
            id_recibo_publico=row["ID_RECIBO_PUBLICO"],
            id_propiedad=row["ID_PROPIEDAD"],
            periodo_recibo=row["PERIODO_RECIBO"],
            tipo_servicio=row["TIPO_SERVICIO"],
            valor_recibo=row["VALOR_RECIBO"],
            fecha_vencimiento=row["FECHA_VENCIMIENTO"],
            fecha_pago=row["FECHA_PAGO"],
            comprobante=row["COMPROBANTE"],
            estado=row["ESTADO"],
            fecha_desde=row["FECHA_DESDE"] if "FECHA_DESDE" in row.keys() else None,
            fecha_hasta=row["FECHA_HASTA"] if "FECHA_HASTA" in row.keys() else None,
            dias_facturados=row["DIAS_FACTURADOS"] if "DIAS_FACTURADOS" in row.keys() else 0,
            created_at=row["CREATED_AT"],
            created_by=row["CREATED_BY"],
            updated_at=row["UPDATED_AT"],
            updated_by=row["UPDATED_BY"],
        )
