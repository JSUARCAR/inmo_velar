"""
Repositorio SQLite para Liquidación.
Implementa persistencia para estados de cuenta del propietario.
"""

from datetime import datetime
from typing import List, Optional

from src.dominio.entidades.liquidacion import Liquidacion
from src.infraestructura.persistencia.database import DatabaseManager


class RepositorioLiquidacionSQLite:
    """Repositorio SQLite para la entidad Liquidacion."""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self._crear_tabla_si_no_existe()

    def _crear_tabla_si_no_existe(self):
        if self.db.use_postgresql:
            return

        """Crea la tabla LIQUIDACIONES si no existe"""
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()

        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS LIQUIDACIONES (
            ID_LIQUIDACION INTEGER PRIMARY KEY AUTOINCREMENT,
            ID_CONTRATO_M INTEGER NOT NULL,
            PERIODO TEXT NOT NULL,
            FECHA_GENERACION TEXT NOT NULL,
            
            -- Ingresos
            CANON_BRUTO INTEGER NOT NULL,
            OTROS_INGRESOS INTEGER DEFAULT 0,
            TOTAL_INGRESOS INTEGER NOT NULL,
            
            -- Egresos
            COMISION_PORCENTAJE INTEGER NOT NULL,
            COMISION_MONTO INTEGER NOT NULL,
            IVA_COMISION INTEGER NOT NULL,
            IMPUESTO_4X1000 INTEGER NOT NULL,
            GASTOS_ADMINISTRACION INTEGER DEFAULT 0,
            GASTOS_SERVICIOS INTEGER DEFAULT 0,
            GASTOS_REPARACIONES INTEGER DEFAULT 0,
            OTROS_EGRESOS INTEGER DEFAULT 0,
            TOTAL_EGRESOS INTEGER NOT NULL,
            
            -- Resultado
            NETO_A_PAGAR INTEGER NOT NULL,
            
            -- Estado
            ESTADO_LIQUIDACION TEXT DEFAULT 'En Proceso' CHECK(ESTADO_LIQUIDACION IN ('En Proceso', 'Aprobada', 'Pagada', 'Cancelada')),
            
            -- Pago
            FECHA_PAGO TEXT,
            METODO_PAGO TEXT,
            REFERENCIA_PAGO TEXT,
            
            -- Notas
            OBSERVACIONES TEXT,
            MOTIVO_CANCELACION TEXT,
            
            -- Auditoría de Estado
            APROBADA_POR TEXT,
            APROBADA_EN TEXT,
            PAGADA_POR TEXT,
            PAGADA_EN TEXT,
            
            CREATED_AT TEXT DEFAULT (datetime('now', 'localtime')),
            CREATED_BY TEXT,
            UPDATED_AT TEXT,
            UPDATED_BY TEXT,
            
            FOREIGN KEY (ID_CONTRATO_M) REFERENCES CONTRATOS_MANDATOS(ID_CONTRATO_M),
            UNIQUE(ID_CONTRATO_M, PERIODO)
        )
        """
        )

        conn.commit()

    def _get_row_dict(self, row):
        if row is None:
            return None
        if hasattr(row, "keys"):
            return dict(row)
        return row

    def _row_to_entity(self, row) -> Liquidacion:
        """Convierte una fila SQL a entidad Liquidacion"""
        row_dict = self._get_row_dict(row)
        if not row_dict:
            return None

        return Liquidacion(
            id_liquidacion=(row_dict.get("id_liquidacion") or row_dict.get("ID_LIQUIDACION")),
            id_contrato_m=(row_dict.get("id_contrato_m") or row_dict.get("ID_CONTRATO_M")),
            periodo=(row_dict.get("periodo") or row_dict.get("PERIODO")),
            fecha_generacion=(row_dict.get("fecha_generacion") or row_dict.get("FECHA_GENERACION")),
            canon_bruto=(row_dict.get("canon_bruto") or row_dict.get("CANON_BRUTO")),
            otros_ingresos=(row_dict.get("otros_ingresos") or row_dict.get("OTROS_INGRESOS")),
            total_ingresos=(row_dict.get("total_ingresos") or row_dict.get("TOTAL_INGRESOS")),
            comision_porcentaje=(
                row_dict.get("comision_porcentaje") or row_dict.get("COMISION_PORCENTAJE")
            ),
            comision_monto=(row_dict.get("comision_monto") or row_dict.get("COMISION_MONTO")),
            iva_comision=(row_dict.get("iva_comision") or row_dict.get("IVA_COMISION")),
            impuesto_4x1000=(row_dict.get("impuesto_4x1000") or row_dict.get("IMPUESTO_4X1000")),
            gastos_administracion=(
                row_dict.get("gastos_administracion") or row_dict.get("GASTOS_ADMINISTRACION")
            ),
            gastos_servicios=(row_dict.get("gastos_servicios") or row_dict.get("GASTOS_SERVICIOS")),
            gastos_reparaciones=(
                row_dict.get("gastos_reparaciones") or row_dict.get("GASTOS_REPARACIONES")
            ),
            otros_egresos=(row_dict.get("otros_egresos") or row_dict.get("OTROS_EGRESOS")),
            total_egresos=(row_dict.get("total_egresos") or row_dict.get("TOTAL_EGRESOS")),
            neto_a_pagar=(row_dict.get("neto_a_pagar") or row_dict.get("NETO_A_PAGAR")),
            estado_liquidacion=(
                row_dict.get("estado_liquidacion") or row_dict.get("ESTADO_LIQUIDACION")
            ),
            fecha_pago=(row_dict.get("fecha_pago") or row_dict.get("FECHA_PAGO")),
            metodo_pago=(row_dict.get("metodo_pago") or row_dict.get("METODO_PAGO")),
            referencia_pago=(row_dict.get("referencia_pago") or row_dict.get("REFERENCIA_PAGO")),
            observaciones=(row_dict.get("observaciones") or row_dict.get("OBSERVACIONES")),
            motivo_cancelacion=(
                row_dict.get("motivo_cancelacion") or row_dict.get("MOTIVO_CANCELACION")
            ),
            aprobada_por=(row_dict.get("aprobada_por") or row_dict.get("APROBADA_POR")),
            aprobada_en=(row_dict.get("aprobada_en") or row_dict.get("APROBADA_EN")),
            pagada_por=(row_dict.get("pagada_por") or row_dict.get("PAGADA_POR")),
            pagada_en=(row_dict.get("pagada_en") or row_dict.get("PAGADA_EN")),
            created_at=(row_dict.get("created_at") or row_dict.get("CREATED_AT")),
            created_by=(row_dict.get("created_by") or row_dict.get("CREATED_BY")),
            updated_at=(row_dict.get("updated_at") or row_dict.get("UPDATED_AT")),
            updated_by=(row_dict.get("updated_by") or row_dict.get("UPDATED_BY")),
        )

    def crear(self, liquidacion: Liquidacion, usuario_sistema: str) -> Liquidacion:
        """Crea una nueva liquidación"""
        # Calcular totales antes de guardar
        liquidacion.calcular_totales()

        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        placeholder = self.db.get_placeholder()

        cursor.execute(
            f"""
            INSERT INTO LIQUIDACIONES (
                ID_CONTRATO_M, PERIODO, FECHA_GENERACION,
                CANON_BRUTO, OTROS_INGRESOS, TOTAL_INGRESOS,
                COMISION_PORCENTAJE, COMISION_MONTO, IVA_COMISION, IMPUESTO_4X1000,
                GASTOS_ADMINISTRACION, GASTOS_SERVICIOS, GASTOS_REPARACIONES, OTROS_EGRESOS,
                TOTAL_EGRESOS, NETO_A_PAGAR,
                ESTADO_LIQUIDACION, OBSERVACIONES,
                CREATED_AT, CREATED_BY
            ) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
        """,
            (
                liquidacion.id_contrato_m,
                liquidacion.periodo,
                liquidacion.fecha_generacion,
                liquidacion.canon_bruto,
                liquidacion.otros_ingresos,
                liquidacion.total_ingresos,
                liquidacion.comision_porcentaje,
                liquidacion.comision_monto,
                liquidacion.iva_comision,
                liquidacion.impuesto_4x1000,
                liquidacion.gastos_administracion,
                liquidacion.gastos_servicios,
                liquidacion.gastos_reparaciones,
                liquidacion.otros_egresos,
                liquidacion.total_egresos,
                liquidacion.neto_a_pagar,
                liquidacion.estado_liquidacion,
                liquidacion.observaciones,
                datetime.now().isoformat(),
                usuario_sistema,
            ),
        )

        liquidacion.id_liquidacion = self.db.get_last_insert_id(
            cursor, "LIQUIDACIONES", "ID_LIQUIDACION"
        )
        conn.commit()

        return liquidacion

    def obtener_por_id(self, id_liquidacion: int) -> Optional[Liquidacion]:
        """Obtiene una liquidación por su ID"""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        placeholder = self.db.get_placeholder()

        cursor.execute(
            f"SELECT * FROM LIQUIDACIONES WHERE ID_LIQUIDACION = {placeholder}", (id_liquidacion,)
        )
        row = cursor.fetchone()

        return self._row_to_entity(row) if row else None

    def obtener_por_contrato_y_periodo(
        self, id_contrato_m: int, periodo: str
    ) -> Optional[Liquidacion]:
        """Obtiene la liquidación de un contrato para un período específico"""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        placeholder = self.db.get_placeholder()

        cursor.execute(
            f"SELECT * FROM LIQUIDACIONES WHERE ID_CONTRATO_M = {placeholder} AND PERIODO = {placeholder}",
            (id_contrato_m, periodo),
        )
        row = cursor.fetchone()

        return self._row_to_entity(row) if row else None

    def listar_por_contrato(self, id_contrato_m: int) -> List[Liquidacion]:
        """Lista todas las liquidaciones de un contrato"""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        placeholder = self.db.get_placeholder()

        cursor.execute(
            f"SELECT * FROM LIQUIDACIONES WHERE ID_CONTRATO_M = {placeholder} ORDER BY PERIODO DESC",
            (id_contrato_m,),
        )

        return [self._row_to_entity(row) for row in cursor.fetchall()]

    def listar_todas(self):
        """
        Lista todas las liquidaciones del sistema con información del contrato.

        Returns:
            List[Dict]: Lista de diccionarios con información completa para UI
        """
        query = """
        SELECT 
            l.ID_LIQUIDACION,
            l.PERIODO,
            l.FECHA_GENERACION,
            l.CANON_BRUTO,
            l.OTROS_INGRESOS,
            l.TOTAL_INGRESOS,
            l.COMISION_MONTO,
            l.IVA_COMISION,
            l.IMPUESTO_4X1000,
           l.GASTOS_ADMINISTRACION,
            l.GASTOS_SERVICIOS,
            l.GASTOS_REPARACIONES,
            l.OTROS_EGRESOS,
            l.TOTAL_EGRESOS,
            l.NETO_A_PAGAR,
            l.ESTADO_LIQUIDACION,
            l.FECHA_PAGO,
            l.OBSERVACIONES,
            l.CREATED_AT,
            cm.ID_CONTRATO_M,
            cm.ID_PROPIEDAD,
            p.DIRECCION_PROPIEDAD,
            p.MATRICULA_INMOBILIARIA,
            per.NOMBRE_COMPLETO as NOMBRE_PROPIETARIO
        FROM LIQUIDACIONES l
        INNER JOIN CONTRATOS_MANDATOS cm ON l.ID_CONTRATO_M = cm.ID_CONTRATO_M
        INNER JOIN PROPIEDADES p ON cm.ID_PROPIEDAD = p.ID_PROPIEDAD
        INNER JOIN PROPIETARIOS prop ON cm.ID_PROPIETARIO = prop.ID_PROPIETARIO
        INNER JOIN PERSONAS per ON prop.ID_PERSONA = per.ID_PERSONA
        ORDER BY l.PERIODO DESC, l.CREATED_AT DESC
        """

        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        self.db.get_placeholder()
        cursor.execute(query)

        results = []
        for row in cursor.fetchall():
            row_dict = self._get_row_dict(row)
            results.append(
                {
                    "id": (row_dict.get("id_liquidacion") or row_dict.get("ID_LIQUIDACION")),
                    "periodo": (row_dict.get("periodo") or row_dict.get("PERIODO")),
                    "fecha_generacion": (
                        row_dict.get("fecha_generacion") or row_dict.get("FECHA_GENERACION")
                    ),
                    "contrato": f"{(row_dict.get('direccion_propiedad') or row_dict.get('DIRECCION_PROPIEDAD'))} - {(row_dict.get('nombre_propietario') or row_dict.get('NOMBRE_PROPIETARIO'))}",
                    "id_contrato_m": (
                        row_dict.get("id_contrato_m") or row_dict.get("ID_CONTRATO_M")
                    ),
                    "direccion": (
                        row_dict.get("direccion_propiedad") or row_dict.get("DIRECCION_PROPIEDAD")
                    ),
                    "matricula": (
                        row_dict.get("matricula_inmobiliaria")
                        or row_dict.get("MATRICULA_INMOBILIARIA")
                    ),
                    "propietario": (
                        row_dict.get("nombre_propietario") or row_dict.get("NOMBRE_PROPIETARIO")
                    ),
                    "canon": (row_dict.get("canon_bruto") or row_dict.get("CANON_BRUTO")),
                    "otros_ingresos": (
                        row_dict.get("otros_ingresos") or row_dict.get("OTROS_INGRESOS")
                    ),
                    "total_ingresos": (
                        row_dict.get("total_ingresos") or row_dict.get("TOTAL_INGRESOS")
                    ),
                    "comision": (row_dict.get("comision_monto") or row_dict.get("COMISION_MONTO")),
                    "iva": (row_dict.get("iva_comision") or row_dict.get("IVA_COMISION")),
                    "impuesto": (
                        row_dict.get("impuesto_4x1000") or row_dict.get("IMPUESTO_4X1000")
                    ),
                    "gastos_admin": (
                        row_dict.get("gastos_administracion")
                        or row_dict.get("GASTOS_ADMINISTRACION")
                    ),
                    "gastos_servicios": (
                        row_dict.get("gastos_servicios") or row_dict.get("GASTOS_SERVICIOS")
                    ),
                    "gastos_reparaciones": (
                        row_dict.get("gastos_reparaciones") or row_dict.get("GASTOS_REPARACIONES")
                    ),
                    "otros_egresos": (
                        row_dict.get("otros_egresos") or row_dict.get("OTROS_EGRESOS")
                    ),
                    "total_egresos": (
                        row_dict.get("total_egresos") or row_dict.get("TOTAL_EGRESOS")
                    ),
                    "neto": (row_dict.get("neto_a_pagar") or row_dict.get("NETO_A_PAGAR")),
                    "estado": (
                        row_dict.get("estado_liquidacion") or row_dict.get("ESTADO_LIQUIDACION")
                    ),
                    "fecha_pago": (row_dict.get("fecha_pago") or row_dict.get("FECHA_PAGO")),
                    "observaciones": (
                        row_dict.get("observaciones") or row_dict.get("OBSERVACIONES")
                    ),
                    "created_at": (row_dict.get("created_at") or row_dict.get("CREATED_AT")),
                }
            )

        return results

    def actualizar(self, liquidacion: Liquidacion, usuario_sistema: str) -> None:
        """Actualiza una liquidación existente (solo en estado 'En Proceso')"""
        # Recalcular totales
        liquidacion.calcular_totales()

        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        placeholder = self.db.get_placeholder()

        cursor.execute(
            f"""
            UPDATE LIQUIDACIONES SET
                FECHA_GENERACION = {placeholder},
                CANON_BRUTO = {placeholder}, OTROS_INGRESOS = {placeholder}, TOTAL_INGRESOS = {placeholder},
                COMISION_PORCENTAJE = {placeholder}, COMISION_MONTO = {placeholder}, IVA_COMISION = {placeholder}, IMPUESTO_4X1000 = {placeholder},
                GASTOS_ADMINISTRACION = {placeholder}, GASTOS_SERVICIOS = {placeholder}, GASTOS_REPARACIONES = {placeholder}, OTROS_EGRESOS = {placeholder},
                TOTAL_EGRESOS = {placeholder}, NETO_A_PAGAR = {placeholder},
                OBSERVACIONES = {placeholder},
                UPDATED_AT = {placeholder},
                UPDATED_BY = {placeholder}
            WHERE ID_LIQUIDACION = {placeholder}
        """,
            (
                liquidacion.fecha_generacion,
                liquidacion.canon_bruto,
                liquidacion.otros_ingresos,
                liquidacion.total_ingresos,
                liquidacion.comision_porcentaje,
                liquidacion.comision_monto,
                liquidacion.iva_comision,
                liquidacion.impuesto_4x1000,
                liquidacion.gastos_administracion,
                liquidacion.gastos_servicios,
                liquidacion.gastos_reparaciones,
                liquidacion.otros_egresos,
                liquidacion.total_egresos,
                liquidacion.neto_a_pagar,
                liquidacion.observaciones,
                datetime.now().isoformat(),
                usuario_sistema,
                liquidacion.id_liquidacion,
            ),
        )

        conn.commit()

    def aprobar(self, id_liquidacion: int, usuario_sistema: str) -> None:
        """Cambia el estado de 'En Proceso' a 'Aprobada'"""
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        placeholder = self.db.get_placeholder()

        cursor.execute(
            f"""
            UPDATE LIQUIDACIONES SET
                ESTADO_LIQUIDACION = 'Aprobada',
                APROBADA_POR = {placeholder},
                APROBADA_EN = {placeholder},
                UPDATED_AT = {placeholder},
                UPDATED_BY = {placeholder}
            WHERE ID_LIQUIDACION = {placeholder} AND ESTADO_LIQUIDACION = 'En Proceso'
        """,
            (
                usuario_sistema,
                datetime.now().isoformat(),
                datetime.now().isoformat(),
                usuario_sistema,
                id_liquidacion,
            ),
        )

        if cursor.rowcount == 0:
            raise ValueError("La liquidación no existe o no está en estado 'En Proceso'")

        conn.commit()

    def marcar_como_pagada(
        self,
        id_liquidacion: int,
        fecha_pago: str,
        metodo_pago: str,
        referencia_pago: str,
        usuario_sistema: str,
    ) -> None:
        """Cambia el estado de 'Aprobada' a 'Pagada' al registrar el comprobante de pago"""
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        placeholder = self.db.get_placeholder()

        cursor.execute(
            f"""
            UPDATE LIQUIDACIONES SET
                ESTADO_LIQUIDACION = 'Pagada',
                FECHA_PAGO = {placeholder},
                METODO_PAGO = {placeholder},
                REFERENCIA_PAGO = {placeholder},
                PAGADA_POR = {placeholder},
                PAGADA_EN = {placeholder},
                UPDATED_AT = {placeholder},
                UPDATED_BY = {placeholder}
            WHERE ID_LIQUIDACION = {placeholder} AND ESTADO_LIQUIDACION = 'Aprobada'
        """,
            (
                fecha_pago,
                metodo_pago,
                referencia_pago,
                usuario_sistema,
                datetime.now().isoformat(),
                datetime.now().isoformat(),
                usuario_sistema,
                id_liquidacion,
            ),
        )

        if cursor.rowcount == 0:
            raise ValueError("La liquidación no existe o no está en estado 'Aprobada'")

        conn.commit()

    def cancelar(self, id_liquidacion: int, motivo: str, usuario_sistema: str) -> None:
        """Cancela una liquidación (solo por Gerente, casos excepcionales)"""
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        placeholder = self.db.get_placeholder()

        cursor.execute(
            f"""
            UPDATE LIQUIDACIONES SET
                ESTADO_LIQUIDACION = 'Cancelada',
                MOTIVO_CANCELACION = {placeholder},
                UPDATED_AT = {placeholder},
                UPDATED_BY = {placeholder}
            WHERE ID_LIQUIDACION = {placeholder}
        """,
            (motivo, datetime.now().isoformat(), usuario_sistema, id_liquidacion),
        )

        conn.commit()

    def reversar(self, id_liquidacion: int, usuario_sistema: str) -> None:
        """Reversa una liquidación de 'Aprobada' a 'En Proceso'"""
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        placeholder = self.db.get_placeholder()

        cursor.execute(
            f"""
            UPDATE LIQUIDACIONES SET
                ESTADO_LIQUIDACION = 'En Proceso',
                APROBADA_POR = NULL,
                APROBADA_EN = NULL,
                UPDATED_AT = {placeholder},
                UPDATED_BY = {placeholder}
            WHERE ID_LIQUIDACION = {placeholder} AND ESTADO_LIQUIDACION = 'Aprobada'
        """,
            (datetime.now().isoformat(), usuario_sistema, id_liquidacion),
        )

        if cursor.rowcount == 0:
            raise ValueError("La liquidación no existe o no está en estado 'Aprobada'")

        conn.commit()

    def cancelar_masivamente(
        self, ids_liquidaciones: List[int], motivo: str, usuario_sistema: str
    ) -> dict:
        """
        Cancela múltiples liquidaciones.

        Returns:
            {'exitosas': [id1, id2], 'fallidas': [id3, id4]}
        """
        exitosas = []
        fallidas = []

        for id_liq in ids_liquidaciones:
            try:
                self.cancelar(id_liq, motivo, usuario_sistema)
                exitosas.append(id_liq)
            except Exception:
                fallidas.append(id_liq)

        return {"exitosas": exitosas, "fallidas": fallidas}

    def reversar_masivamente(self, ids_liquidaciones: List[int], usuario_sistema: str) -> dict:
        """
        Reversa múltiples liquidaciones.

        Returns:
            {'exitosas': [id1, id2], 'fallidas': [id3, id4]}
        """
        exitosas = []
        fallidas = []

        for id_liq in ids_liquidaciones:
            try:
                self.reversar(id_liq, usuario_sistema)
                exitosas.append(id_liq)
            except Exception:
                fallidas.append(id_liq)

        return {"exitosas": exitosas, "fallidas": fallidas}

    def cancelar_por_propietario_y_periodo(
        self, id_propietario: int, periodo: str, motivo: str, usuario_sistema: str
    ) -> int:
        """
        Cancela todas las liquidaciones de un propietario para un período específico.

        Returns:
            Cantidad de liquidaciones canceladas
        """
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        placeholder = self.db.get_placeholder()

        cursor.execute(
            f"""
            UPDATE LIQUIDACIONES 
            SET 
                ESTADO_LIQUIDACION = 'Cancelada',
                MOTIVO_CANCELACION = {placeholder},
                UPDATED_AT = {placeholder},
                UPDATED_BY = {placeholder}
            WHERE ID_CONTRATO_M IN (
                SELECT ID_CONTRATO_M 
                FROM CONTRATOS_MANDATOS 
                WHERE ID_PROPIETARIO = {placeholder}
            )
            AND PERIODO = {placeholder}
            AND ESTADO_LIQUIDACION IN ('En Proceso', 'Aprobada')
        """,
            (motivo, datetime.now().isoformat(), usuario_sistema, id_propietario, periodo),
        )

        affected = cursor.rowcount
        conn.commit()

        return affected

    def reversar_por_propietario_y_periodo(
        self, id_propietario: int, periodo: str, usuario_sistema: str
    ) -> int:
        """
        Reversa todas las liquidaciones aprobadas de un propietario para un período específico.

        Returns:
            Cantidad de liquidaciones reversadas
        """
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        placeholder = self.db.get_placeholder()

        cursor.execute(
            f"""
            UPDATE LIQUIDACIONES 
            SET 
                ESTADO_LIQUIDACION = 'En Proceso',
                APROBADA_POR = NULL,
                APROBADA_EN = NULL,
                UPDATED_AT = {placeholder},
                UPDATED_BY = {placeholder}
            WHERE ID_CONTRATO_M IN (
                SELECT ID_CONTRATO_M 
                FROM CONTRATOS_MANDATOS 
                WHERE ID_PROPIETARIO = {placeholder}
            )
            AND PERIODO = {placeholder}
            AND ESTADO_LIQUIDACION = 'Aprobada'
        """,
            (datetime.now().isoformat(), usuario_sistema, id_propietario, periodo),
        )

        affected = cursor.rowcount
        conn.commit()

        return affected

    def listar_por_propietario_y_periodo(
        self, id_propietario: int, periodo: str
    ) -> List[Liquidacion]:
        """Lista todas las liquidaciones de un propietario para un período específico"""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        placeholder = self.db.get_placeholder()

        cursor.execute(
            f"""
            SELECT l.* FROM LIQUIDACIONES l 
            JOIN CONTRATOS_MANDATOS cm ON l.ID_CONTRATO_M = cm.ID_CONTRATO_M 
            WHERE cm.ID_PROPIETARIO = {placeholder} AND l.PERIODO = {placeholder} 
            ORDER BY l.ID_LIQUIDACION
        """,
            (id_propietario, periodo),
        )

        return [self._row_to_entity(row) for row in cursor.fetchall()]

    def listar_agrupadas_por_propietario_paginado(
        self,
        page: int = 1,
        page_size: int = 25,
        estado: Optional[str] = None,
        periodo: Optional[str] = None,
        busqueda: Optional[str] = None,
    ):
        """
        Lista liquidaciones agrupadas por propietario con totales consolidados.
        Retorna un resultado paginado con información agregada.
        """
        from src.dominio.modelos.pagination import PaginatedResult, PaginationParams

        params = PaginationParams(page=page, page_size=page_size)
        placeholder = self.db.get_placeholder()

        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)

            # Base query con agregaciones
            base_select = """
                SELECT 
                    cm.ID_PROPIETARIO,
                    l.PERIODO,
                    per.NOMBRE_COMPLETO as NOMBRE_PROPIETARIO,
                    per.NUMERO_DOCUMENTO as DOCUMENTO_PROPIETARIO,
                    COUNT(DISTINCT l.ID_LIQUIDACION) as CANTIDAD_PROPIEDADES,
                    SUM(l.CANON_BRUTO) as TOTAL_CANON_BRUTO,
                    SUM(l.OTROS_INGRESOS) as TOTAL_OTROS_INGRESOS,
                    SUM(l.TOTAL_INGRESOS) as TOTAL_INGRESOS,
                    SUM(l.COMISION_MONTO) as TOTAL_COMISION,
                    SUM(l.IVA_COMISION) as TOTAL_IVA,
                    SUM(l.IMPUESTO_4X1000) as TOTAL_IMPUESTO,
                    SUM(l.GASTOS_ADMINISTRACION) as TOTAL_GASTOS_ADMIN,
                    SUM(l.GASTOS_SERVICIOS) as TOTAL_GASTOS_SERV,
                    SUM(l.GASTOS_REPARACIONES) as TOTAL_GASTOS_REP,
                    SUM(l.OTROS_EGRESOS) as TOTAL_OTROS_EGRESOS,
                    SUM(l.TOTAL_EGRESOS) as TOTAL_EGRESOS,
                    SUM(l.NETO_A_PAGAR) as NETO_TOTAL
            """

            base_from = """
                FROM LIQUIDACIONES l
                JOIN CONTRATOS_MANDATOS cm ON l.ID_CONTRATO_M = cm.ID_CONTRATO_M
                JOIN PROPIETARIOS prop ON cm.ID_PROPIETARIO = prop.ID_PROPIETARIO
                JOIN PERSONAS per ON prop.ID_PERSONA = per.ID_PERSONA
            """

            conditions = []
            query_params = []

            # Filtros
            if estado and estado != "Todos":
                conditions.append(f"l.ESTADO_LIQUIDACION = {placeholder}")
                query_params.append(estado)

            if periodo:
                conditions.append(f"l.PERIODO = {placeholder}")
                query_params.append(periodo)

            if busqueda:
                conditions.append(
                    f"""(
                    per.NOMBRE_COMPLETO ILIKE {placeholder} OR
                    per.NUMERO_DOCUMENTO LIKE {placeholder}
                )"""
                )
                term = f"%{busqueda}%"
                query_params.extend([term, term])

            where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
            group_by = (
                " GROUP BY cm.ID_PROPIETARIO, l.PERIODO, per.NOMBRE_COMPLETO, per.NUMERO_DOCUMENTO"
            )

            # Count de grupos (propietarios únicos con liquidaciones)
            count_query = f"""
                SELECT COUNT(*) as TOTAL FROM (
                    SELECT cm.ID_PROPIETARIO, l.PERIODO
                    {base_from}
                    {where_clause}
                    {group_by}
                ) AS grupos
            """
            cursor.execute(count_query, query_params)
            total = cursor.fetchone()["TOTAL"]

            # Data query con ordenamiento
            data_query = f"""
                {base_select}
                {base_from}
                {where_clause}
                {group_by}
                ORDER BY l.PERIODO DESC, per.NOMBRE_COMPLETO
                LIMIT {placeholder} OFFSET {placeholder}
            """

            cursor.execute(data_query, query_params + [params.page_size, params.offset])

            items = []
            for row in cursor.fetchall():
                # Determinar estado consolidado
                # Consultar estados individuales para determinar consolidado
                cursor.execute(
                    f"""
                    SELECT ESTADO_LIQUIDACION, COUNT(*) as CNT
                    FROM LIQUIDACIONES l
                    JOIN CONTRATOS_MANDATOS cm ON l.ID_CONTRATO_M = cm.ID_CONTRATO_M
                    WHERE cm.ID_PROPIETARIO = {placeholder} AND l.PERIODO = {placeholder}
                    GROUP BY ESTADO_LIQUIDACION
                """,
                    (row["ID_PROPIETARIO"], row["PERIODO"]),
                )

                estados_map = {e["ESTADO_LIQUIDACION"]: e["CNT"] for e in cursor.fetchall()}
                total_liq = sum(estados_map.values())

                # Lógica de estado consolidado
                if estados_map.get("En Proceso", 0) > 0:
                    estado_consolidado = "En Proceso"
                elif estados_map.get("Aprobada", 0) == total_liq:
                    estado_consolidado = "Aprobada"
                elif estados_map.get("Pagada", 0) == total_liq:
                    estado_consolidado = "Pagada"
                elif estados_map.get("Cancelada", 0) == total_liq:
                    estado_consolidado = "Cancelada"
                else:
                    estado_consolidado = "Mixto"

                items.append(
                    {
                        "id_propietario": row["ID_PROPIETARIO"],
                        "periodo": row["PERIODO"],
                        "propietario": row["NOMBRE_PROPIETARIO"],
                        "documento": row["DOCUMENTO_PROPIETARIO"],
                        "cantidad_propiedades": row["CANTIDAD_PROPIEDADES"],
                        "canon": row["TOTAL_CANON_BRUTO"],
                        "neto": row["NETO_TOTAL"],
                        "total_ingresos": row["TOTAL_INGRESOS"],
                        "total_egresos": row["TOTAL_EGRESOS"],
                        "estado": estado_consolidado,
                    }
                )

            return PaginatedResult(
                items=items, total=total, page=params.page, page_size=params.page_size
            )

    def aprobar_por_propietario_y_periodo(
        self, id_propietario: int, periodo: str, usuario_sistema: str
    ) -> int:
        """
        Aprueba todas las liquidaciones de un propietario para un período específico.

        Returns:
            Cantidad de liquidaciones aprobadas
        """
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        placeholder = self.db.get_placeholder()

        cursor.execute(
            f"""
            UPDATE LIQUIDACIONES 
            SET 
                ESTADO_LIQUIDACION = 'Aprobada',
                APROBADA_POR = {placeholder},
                APROBADA_EN = {placeholder},
                UPDATED_AT = {placeholder},
                UPDATED_BY = {placeholder}
            WHERE ID_CONTRATO_M IN (
                SELECT ID_CONTRATO_M 
                FROM CONTRATOS_MANDATOS 
                WHERE ID_PROPIETARIO = {placeholder}
            )
            AND PERIODO = {placeholder}
            AND ESTADO_LIQUIDACION = 'En Proceso'
        """,
            (
                usuario_sistema,
                datetime.now().isoformat(),
                datetime.now().isoformat(),
                usuario_sistema,
                id_propietario,
                periodo,
            ),
        )

        affected = cursor.rowcount
        conn.commit()

        return affected

    def marcar_como_pagadas_por_propietario(
        self,
        id_propietario: int,
        periodo: str,
        fecha_pago: str,
        metodo_pago: str,
        referencia_pago: str,
        usuario_sistema: str,
    ) -> int:
        """
        Marca como pagadas todas las liquidaciones aprobadas de un propietario para un período.

        Returns:
            Cantidad de liquidaciones marcadas como pagadas
        """
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        placeholder = self.db.get_placeholder()

        cursor.execute(
            f"""
            UPDATE LIQUIDACIONES 
            SET 
                ESTADO_LIQUIDACION = 'Pagada',
                FECHA_PAGO = {placeholder},
                METODO_PAGO = {placeholder},
                REFERENCIA_PAGO = {placeholder},
                PAGADA_POR = {placeholder},
                PAGADA_EN = {placeholder},
                UPDATED_AT = {placeholder},
                UPDATED_BY = {placeholder}
            WHERE ID_CONTRATO_M IN (
                SELECT ID_CONTRATO_M 
                FROM CONTRATOS_MANDATOS 
                WHERE ID_PROPIETARIO = {placeholder}
            )
            AND PERIODO = {placeholder}
            AND ESTADO_LIQUIDACION = 'Aprobada'
        """,
            (
                fecha_pago,
                metodo_pago,
                referencia_pago,
                usuario_sistema,
                datetime.now().isoformat(),
                datetime.now().isoformat(),
                usuario_sistema,
                id_propietario,
                periodo,
            ),
        )

        affected = cursor.rowcount
        conn.commit()

        return affected
