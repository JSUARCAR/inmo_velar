"""
Repositorio Postgres para PagosAdministracion.
Implementa mapeo 1:1 con tabla PAGOS_ADMINISTRACION.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.dominio.entidades.pagos_administracion import PagosAdministracion
from src.infraestructura.persistencia.database import DatabaseManager

logger = logging.getLogger(__name__)


class RepositorioPagosAdminPostgres:
    """Repositorio para la entidad PagosAdministracion."""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def _row_to_entity(self, row: Dict) -> Optional[PagosAdministracion]:
        if not row:
            return None

        def get_val(key):
            return row.get(key) or row.get(key.upper()) or row.get(key.lower())

        return PagosAdministracion(
            id_pago_admin=get_val("ID_PAGO_ADMIN"),
            id_propiedad=get_val("ID_PROPIEDAD"),
            nombre_propietario=get_val("NOMBRE_PROPIETARIO"),
            direccion_propiedad=get_val("DIRECCION_PROPIEDAD"),
            valor_administracion=get_val("VALOR_ADMINISTRACION"),
            fecha_pago=get_val("FECHA_PAGO") or 1,
            link_pago=get_val("LINK_PAGO"),
            periodo_pago=get_val("PERIODO_PAGO"),
            estado_pago=get_val("ESTADO_PAGO"),
            created_at=get_val("CREATED_AT") or get_val("FECHA_GENERACION"),
            fecha_pago_real=get_val("FECHA_PAGO_REAL"),
        )

    def crear(
        self, pago: PagosAdministracion, usuario_sistema: str
    ) -> PagosAdministracion:
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        p = self.db.get_placeholder()

        query = f"""
            INSERT INTO PAGOS_ADMINISTRACION (
                ID_PROPIEDAD, NOMBRE_PROPIETARIO, DIRECCION_PROPIEDAD,
                VALOR_ADMINISTRACION, FECHA_PAGO, LINK_PAGO,
                PERIODO_PAGO, ESTADO_PAGO, FECHA_GENERACION
            )
            VALUES ({p}, {p}, {p}, {p}, {p}, {p}, {p}, {p}, {p})
            RETURNING ID_PAGO_ADMIN
        """

        cursor.execute(
            query,
            (
                pago.id_propiedad,
                pago.nombre_propietario,
                pago.direccion_propiedad,
                pago.valor_administracion,
                pago.fecha_pago,
                pago.link_pago,
                pago.periodo_pago,
                pago.estado_pago,
                datetime.now().isoformat(),
            ),
        )

        result = cursor.fetchone()
        if result:
            pago.id_pago_admin = result.get("ID_PAGO_ADMIN") or result.get(
                "id_pago_admin"
            )

        conn.commit()
        cursor.close()
        return pago

    def obtener_por_id(self, id_pago: int) -> Optional[PagosAdministracion]:
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        p = self.db.get_placeholder()

        query = f"SELECT * FROM PAGOS_ADMINISTRACION WHERE ID_PAGO_ADMIN = {p}"
        cursor.execute(query, (id_pago,))

        row = cursor.fetchone()
        cursor.close()
        return self._row_to_entity(row) if row else None

    def obtener_por_periodo(self, periodo: str) -> List[PagosAdministracion]:
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        p = self.db.get_placeholder()

        query = f"""
            SELECT * FROM PAGOS_ADMINISTRACION
            WHERE PERIODO_PAGO = {p}
            ORDER BY DIRECCION_PROPIEDAD
        """
        cursor.execute(query, (periodo,))

        rows = cursor.fetchall()
        cursor.close()
        return [self._row_to_entity(row) for row in rows]

    def obtener_por_propiedad_y_periodo(
        self, id_propiedad: int, periodo: str
    ) -> Optional[PagosAdministracion]:
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        p = self.db.get_placeholder()

        query = f"""
            SELECT * FROM PAGOS_ADMINISTRACION
            WHERE ID_PROPIEDAD = {p} AND PERIODO_PAGO = {p}
        """
        cursor.execute(query, (id_propiedad, periodo))

        row = cursor.fetchone()
        cursor.close()
        return self._row_to_entity(row) if row else None

    def listar(
        self,
        filtro_periodo: Optional[str] = None,
        filtro_estado: Optional[str] = None,
        filtro_propiedad: Optional[int] = None,
        filtro_nombre: Optional[str] = None,
    ) -> List[PagosAdministracion]:
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        p = self.db.get_placeholder()

        query = "SELECT * FROM PAGOS_ADMINISTRACION WHERE 1=1"
        params = []

        if filtro_periodo:
            query += f" AND PERIODO_PAGO = {p}"
            params.append(filtro_periodo)

        if filtro_estado:
            query += f" AND ESTADO_PAGO = {p}"
            params.append(filtro_estado)

        if filtro_propiedad:
            query += f" AND ID_PROPIEDAD = {p}"
            params.append(filtro_propiedad)

        if filtro_nombre:
            query += f" AND NOMBRE_PROPIETARIO ILIKE {p}"
            params.append(f"%{filtro_nombre}%")

        query += " ORDER BY PERIODO_PAGO DESC, DIRECCION_PROPIEDAD"

        cursor.execute(query, params)
        rows = cursor.fetchall()
        cursor.close()
        return [self._row_to_entity(row) for row in rows]

    def marcar_pagado(self, id_pago: int, usuario_sistema: str) -> bool:
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        p = self.db.get_placeholder()

        # Verificar estado actual antes de proceder (Idempotencia)
        query_check = f"SELECT ESTADO_PAGO FROM PAGOS_ADMINISTRACION WHERE ID_PAGO_ADMIN = {p}"
        cursor.execute(query_check, (id_pago,))
        row = cursor.fetchone()
        
        if not row:
            cursor.close()
            raise ValueError(f"Pago con ID {id_pago} no encontrado.")
            
        estado = row.get("ESTADO_PAGO") or row.get("estado_pago")
        if estado == "Pagado":
            cursor.close()
            return True # Ya está pagado, no hacer nada

        query_update = f"""
            UPDATE PAGOS_ADMINISTRACION
            SET ESTADO_PAGO = 'Pagado', FECHA_PAGO_REAL = {p}
            WHERE ID_PAGO_ADMIN = {p}
        """

        cursor.execute(query_update, (datetime.now().isoformat(), id_pago))
        conn.commit()
        cursor.close()
        return True

    def marcar_vencido(self, id_pago: int) -> bool:
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        p = self.db.get_placeholder()

        query = f"""
            UPDATE PAGOS_ADMINISTRACION
            SET ESTADO_PAGO = 'Vencido'
            WHERE ID_PAGO_ADMIN = {p} AND ESTADO_PAGO = 'Pendiente'
        """

        cursor.execute(query, (id_pago,))
        conn.commit()
        cursor.close()
        return True

    def actualizar(self, pago: PagosAdministracion, usuario_sistema: str) -> bool:
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        p = self.db.get_placeholder()

        query = f"""
            UPDATE PAGOS_ADMINISTRACION SET
                ID_PROPIEDAD = {p},
                NOMBRE_PROPIETARIO = {p},
                DIRECCION_PROPIEDAD = {p},
                VALOR_ADMINISTRACION = {p},
                FECHA_PAGO = {p},
                LINK_PAGO = {p},
                PERIODO_PAGO = {p},
                ESTADO_PAGO = {p}
            WHERE ID_PAGO_ADMIN = {p}
        """

        cursor.execute(
            query,
            (
                pago.id_propiedad,
                pago.nombre_propietario,
                pago.direccion_propiedad,
                pago.valor_administracion,
                pago.fecha_pago,
                pago.link_pago,
                pago.periodo_pago,
                pago.estado_pago,
                pago.id_pago_admin,
            ),
        )
        conn.commit()
        cursor.close()
        return True

    def obtener_elegibles(self) -> List[Dict[str, Any]]:
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)

        logger.debug("Ejecutando query obtener_elegibles()...")

        query = """
            SELECT 
                p.ID_PROPIEDAD,
                p.DIRECCION_PROPIEDAD,
                p.VALOR_ADMINISTRACION,
                p.FECHA_PAGO_ADMINISTRACION,
                p.LINK_PAGO_ADMINISTRACION,
                cm.ID_PROPIETARIO,
                cm.ID_ASESOR,
                prop.NOMBRE_COMPLETO as NOMBRE_PROPIETARIO,
                CASE WHEN prop_apoderado.NOMBRE_COMPLETO IS NOT NULL THEN prop_apoderado.NOMBRE_COMPLETO 
                     ELSE 'No asignado' END as NOMBRE_ASESOR
            FROM PROPIEDADES p
            JOIN CONTRATOS_MANDATOS cm ON p.ID_PROPIEDAD = cm.ID_PROPIEDAD
            JOIN PROPIETARIOS prop_jun ON cm.ID_PROPIETARIO = prop_jun.ID_PROPIETARIO
            JOIN PERSONAS prop ON prop_jun.ID_PERSONA = prop.ID_PERSONA
            LEFT JOIN PROPIETARIOS apo_jun ON cm.ID_ASESOR = apo_jun.ID_PROPIETARIO
            LEFT JOIN PERSONAS prop_apoderado ON apo_jun.ID_PERSONA = prop_apoderado.ID_PERSONA
            WHERE cm.ESTADO_CONTRATO_M = 'Activo'
              AND p.VALOR_ADMINISTRACION IS NOT NULL
              AND p.VALOR_ADMINISTRACION > 0
        """

        cursor.execute(query)
        rows = cursor.fetchall()
        logger.debug(f"Filas obtenidas: {len(rows)}")
        cursor.close()

        if not rows:
            return []

        resultados = []
        for row in rows:
            resultados.append(
                {
                    "id_propiedad": row.get("ID_PROPIEDAD"),
                    "direccion_propiedad": row.get("DIRECCION_PROPIEDAD"),
                    "valor_administracion": row.get("VALOR_ADMINISTRACION"),
                    "fecha_pago_administracion": row.get("FECHA_PAGO_ADMINISTRACION")
                    or 1,
                    "link_pago_administracion": row.get("LINK_PAGO_ADMINISTRACION"),
                    "id_propietario": row.get("ID_PROPIETARIO"),
                    "id_asesor": row.get("ID_ASESOR"),
                    "nombre_propietario": row.get("NOMBRE_PROPIETARIO"),
                    "nombre_asesor": row.get("NOMBRE_ASESOR"),
                }
            )

        return resultados
