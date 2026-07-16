"""
Repositorio Postgres para Liquidación.
Implementa persistencia para estados de cuenta del propietario.
"""

from datetime import datetime
from typing import List, Optional, Any, Dict

from src.dominio.entidades.liquidacion import Liquidacion
from src.infraestructura.persistencia.database import DatabaseManager


class RepositorioLiquidacionPostgres:
    """Repositorio Postgres para la entidad Liquidacion."""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self._crear_tabla_si_no_existe()

    def _crear_tabla_si_no_existe(self):
        if self.db.use_postgresql:
            return

        """Crea la tabla LIQUIDACIONES si no existe"""
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()

        cursor.execute("""
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
            VALOR_INCIDENTES INTEGER DEFAULT 0,
            PAGO_PREDIAL INTEGER DEFAULT 0,
            SEGURO_MONTO INTEGER DEFAULT 0,
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
        """)

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
            id_liquidacion=(
                row_dict.get("id_liquidacion") or row_dict.get("ID_LIQUIDACION")
            ),
            id_contrato_m=(
                row_dict.get("id_contrato_m") or row_dict.get("ID_CONTRATO_M")
            ),
            periodo=(row_dict.get("periodo") or row_dict.get("PERIODO")),
            fecha_generacion=(
                row_dict.get("fecha_generacion") or row_dict.get("FECHA_GENERACION")
            ),
            canon_bruto=(row_dict.get("canon_bruto") or row_dict.get("CANON_BRUTO")),
            otros_ingresos=(
                row_dict.get("otros_ingresos") or row_dict.get("OTROS_INGRESOS")
            ),
            total_ingresos=(
                row_dict.get("total_ingresos") or row_dict.get("TOTAL_INGRESOS")
            ),
            comision_porcentaje=(
                row_dict.get("comision_porcentaje")
                or row_dict.get("COMISION_PORCENTAJE")
            ),
            comision_monto=(
                row_dict.get("comision_monto") or row_dict.get("COMISION_MONTO")
            ),
            iva_comision=(row_dict.get("iva_comision") or row_dict.get("IVA_COMISION")),
            impuesto_4x1000=(
                row_dict.get("impuesto_4x1000") or row_dict.get("IMPUESTO_4X1000")
            ),
            gastos_administracion=(
                row_dict.get("gastos_administracion")
                or row_dict.get("GASTOS_ADMINISTRACION")
            ),
            gastos_servicios=(
                row_dict.get("gastos_servicios") or row_dict.get("GASTOS_SERVICIOS")
            ),
            gastos_reparaciones=(
                row_dict.get("gastos_reparaciones")
                or row_dict.get("GASTOS_REPARACIONES")
            ),
            valor_incidentes=(
                row_dict.get("valor_incidentes")
                or row_dict.get("VALOR_INCIDENTES")
                or 0
            ),
            pago_predial=(
                row_dict.get("pago_predial") or row_dict.get("PAGO_PREDIAL") or 0
            ),
            seguro_monto=(
                row_dict.get("seguro_monto") or row_dict.get("SEGURO_MONTO") or 0
            ),
            otros_egresos=(
                row_dict.get("otros_egresos") or row_dict.get("OTROS_EGRESOS") or 0
            ),
            total_egresos=(
                row_dict.get("total_egresos") or row_dict.get("TOTAL_EGRESOS")
            ),
            neto_a_pagar=(row_dict.get("neto_a_pagar") or row_dict.get("NETO_A_PAGAR")),
            estado_liquidacion=(
                row_dict.get("estado_liquidacion") or row_dict.get("ESTADO_LIQUIDACION")
            ),
            fecha_pago=(row_dict.get("fecha_pago") or row_dict.get("FECHA_PAGO")),
            metodo_pago=(row_dict.get("metodo_pago") or row_dict.get("METODO_PAGO")),
            referencia_pago=(
                row_dict.get("referencia_pago") or row_dict.get("REFERENCIA_PAGO")
            ),
            observaciones=(
                row_dict.get("observaciones") or row_dict.get("OBSERVACIONES")
            ),
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
                GASTOS_ADMINISTRACION, GASTOS_SERVICIOS, GASTOS_REPARACIONES, VALOR_INCIDENTES, PAGO_PREDIAL, SEGURO_MONTO, OTROS_EGRESOS,
                TOTAL_EGRESOS, NETO_A_PAGAR,
                ESTADO_LIQUIDACION, OBSERVACIONES,
                CREATED_AT, CREATED_BY
            ) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
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
                liquidacion.valor_incidentes,
                liquidacion.pago_predial,
                liquidacion.seguro_monto,
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
            f"SELECT * FROM LIQUIDACIONES WHERE ID_LIQUIDACION = {placeholder} AND eliminada = FALSE",
            (id_liquidacion,),
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
            f"SELECT * FROM LIQUIDACIONES WHERE ID_CONTRATO_M = {placeholder} AND PERIODO = {placeholder} AND eliminada = FALSE",
            (id_contrato_m, periodo),
        )
        row = cursor.fetchone()

        return self._row_to_entity(row) if row else None

    def obtener_estado_pago_actual(
        self, id_contrato_m: int, periodo: Optional[str] = None
    ) -> str:
        """
        Obtiene el estado de pago para un contrato en el período actual.

        Returns:
            'AL_DIA' si liquidacionPagada, 'PENDIENTE' otherwise
        """
        from src.dominio.value_objects.estado_cumplimiento import obtener_periodo_actual

        periodo = periodo or obtener_periodo_actual()

        liquidacion = self.obtener_por_contrato_y_periodo(id_contrato_m, periodo)

        if liquidacion and liquidacion.estado_liquidacion == "Pagada":
            return "AL_DIA"
        elif liquidacion and liquidacion.estado_liquidacion in (
            "En Proceso",
            "Aprobada",
        ):
            return "PENDIENTE"

        return "PENDIENTE"

    def listar_por_contrato(self, id_contrato_m: int) -> List[Liquidacion]:
        """Lista todas las liquidaciones de un contrato"""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        placeholder = self.db.get_placeholder()

        cursor.execute(
            f"SELECT * FROM LIQUIDACIONES WHERE ID_CONTRATO_M = {placeholder} AND eliminada = FALSE ORDER BY PERIODO DESC",
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
            l.PAGO_PREDIAL,
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
        WHERE l.eliminada = FALSE
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
                    "id": (
                        row_dict.get("id_liquidacion") or row_dict.get("ID_LIQUIDACION")
                    ),
                    "periodo": (row_dict.get("periodo") or row_dict.get("PERIODO")),
                    "fecha_generacion": (
                        row_dict.get("fecha_generacion")
                        or row_dict.get("FECHA_GENERACION")
                    ),
                    "contrato": f"{(row_dict.get('direccion_propiedad') or row_dict.get('DIRECCION_PROPIEDAD'))} - {(row_dict.get('nombre_propietario') or row_dict.get('NOMBRE_PROPIETARIO'))}",
                    "id_contrato_m": (
                        row_dict.get("id_contrato_m") or row_dict.get("ID_CONTRATO_M")
                    ),
                    "direccion": (
                        row_dict.get("direccion_propiedad")
                        or row_dict.get("DIRECCION_PROPIEDAD")
                    ),
                    "matricula": (
                        row_dict.get("matricula_inmobiliaria")
                        or row_dict.get("MATRICULA_INMOBILIARIA")
                    ),
                    "propietario": (
                        row_dict.get("nombre_propietario")
                        or row_dict.get("NOMBRE_PROPIETARIO")
                    ),
                    "canon": (
                        row_dict.get("canon_bruto") or row_dict.get("CANON_BRUTO")
                    ),
                    "otros_ingresos": (
                        row_dict.get("otros_ingresos") or row_dict.get("OTROS_INGRESOS")
                    ),
                    "total_ingresos": (
                        row_dict.get("total_ingresos") or row_dict.get("TOTAL_INGRESOS")
                    ),
                    "comision": (
                        row_dict.get("comision_monto") or row_dict.get("COMISION_MONTO")
                    ),
                    "iva": (
                        row_dict.get("iva_comision") or row_dict.get("IVA_COMISION")
                    ),
                    "impuesto": (
                        row_dict.get("impuesto_4x1000")
                        or row_dict.get("IMPUESTO_4X1000")
                    ),
                    "gastos_admin": (
                        row_dict.get("gastos_administracion")
                        or row_dict.get("GASTOS_ADMINISTRACION")
                    ),
                    "gastos_servicios": (
                        row_dict.get("gastos_servicios")
                        or row_dict.get("GASTOS_SERVICIOS")
                    ),
                    "gastos_reparaciones": (
                        row_dict.get("gastos_reparaciones")
                        or row_dict.get("GASTOS_REPARACIONES")
                    ),
                    "pago_predial": (
                        row_dict.get("pago_predial")
                        or row_dict.get("PAGO_PREDIAL")
                        or 0
                    ),
                    "seguro_monto": (
                        row_dict.get("seguro_monto")
                        or row_dict.get("SEGURO_MONTO")
                        or 0
                    ),
                    "otros_egresos": (
                        row_dict.get("otros_egresos")
                        or row_dict.get("OTROS_EGRESOS")
                        or 0
                    ),
                    "total_egresos": (
                        row_dict.get("total_egresos") or row_dict.get("TOTAL_EGRESOS")
                    ),
                    "neto": (
                        row_dict.get("neto_a_pagar") or row_dict.get("NETO_A_PAGAR")
                    ),
                    "estado": (
                        row_dict.get("estado_liquidacion")
                        or row_dict.get("ESTADO_LIQUIDACION")
                    ),
                    "fecha_pago": (
                        row_dict.get("fecha_pago") or row_dict.get("FECHA_PAGO")
                    ),
                    "observaciones": (
                        row_dict.get("observaciones") or row_dict.get("OBSERVACIONES")
                    ),
                    "created_at": (
                        row_dict.get("created_at") or row_dict.get("CREATED_AT")
                    ),
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
                GASTOS_ADMINISTRACION = {placeholder}, GASTOS_SERVICIOS = {placeholder}, GASTOS_REPARACIONES = {placeholder}, PAGO_PREDIAL = {placeholder}, SEGURO_MONTO = {placeholder}, OTROS_EGRESOS = {placeholder},
                VALOR_INCIDENTES = {placeholder},
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
                liquidacion.pago_predial,
                liquidacion.seguro_monto,
                liquidacion.otros_egresos,
                liquidacion.valor_incidentes,
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
            raise ValueError(
                "La liquidación no existe o no está en estado 'En Proceso'"
            )

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

    def eliminar(self, id_liquidacion: int, usuario_sistema: str) -> None:
        """
        Elimina lógicamente una liquidación (soft delete).
        Idempotente: si ya fue eliminada, no retorna error.
        """
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        placeholder = self.db.get_placeholder()

        cursor.execute(
            f"""
            UPDATE LIQUIDACIONES SET
                eliminada = TRUE,
                UPDATED_AT = {placeholder},
                UPDATED_BY = {placeholder}
            WHERE ID_LIQUIDACION = {placeholder} AND eliminada = FALSE
        """,
            (datetime.now().isoformat(), usuario_sistema, id_liquidacion),
        )

        conn.commit()

    def reversar_pago(
        self, id_liquidacion: int, usuario_sistema: str, motivo: str
    ) -> dict:
        """
        Reversa el pago de una liquidación ('Pagada' → 'Aprobada').
        Limpia campos de pago, registra motivo en AUDITORIA_CAMBIOS.
        Idempotente: si no está en 'Pagada', retorna éxito sin cambios.
        """
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        placeholder = self.db.get_placeholder()

        cursor.execute(
            f"""
            UPDATE LIQUIDACIONES SET
                ESTADO_LIQUIDACION = 'Aprobada',
                FECHA_PAGO = NULL,
                METODO_PAGO = NULL,
                REFERENCIA_PAGO = NULL,
                PAGADA_POR = NULL,
                PAGADA_EN = NULL,
                UPDATED_AT = {placeholder},
                UPDATED_BY = {placeholder}
            WHERE ID_LIQUIDACION = {placeholder} AND ESTADO_LIQUIDACION = 'Pagada'
        """,
            (datetime.now().isoformat(), usuario_sistema, id_liquidacion),
        )

        if cursor.rowcount > 0:
            # Insertar registro explícito de AUDITORIA_CAMBIOS para el motivo
            try:
                cursor.execute(
                    f"""
                    INSERT INTO AUDITORIA_CAMBIOS (TABLA_MODIFICADA, ID_REGISTRO, CAMPO_MODIFICADO, VALOR_NUEVO, USUARIO, FECHA_MODIFICACION)
                    VALUES ('LIQUIDACIONES', {placeholder}, 'MOTIVO_REVERSION', {placeholder}, {placeholder}, {placeholder})
                """,
                    (
                        id_liquidacion,
                        motivo,
                        usuario_sistema,
                        datetime.now().isoformat(),
                    ),
                )
            except Exception:
                pass  # Tabla AUDITORIA_CAMBIOS puede no existir en SQLite

        conn.commit()

        return {
            "exitosa": cursor.rowcount > 0 or True,
            "mensaje": (
                "Liquidación reversada exitosamente"
                if cursor.rowcount > 0
                else "La liquidación ya estaba en estado 'Aprobada'"
            ),
            "id_liquidacion": id_liquidacion,
            "estado_anterior": "Pagada",
            "estado_nuevo": "Aprobada",
        }

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

    def reversar_masivamente(
        self, ids_liquidaciones: List[int], usuario_sistema: str
    ) -> dict:
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
            (
                motivo,
                datetime.now().isoformat(),
                usuario_sistema,
                id_propietario,
                periodo,
            ),
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

    def reversar_pago_por_propietario_y_periodo(
        self, id_propietario: int, periodo: str, usuario_sistema: str, motivo: str
    ) -> dict:
        """
        Reversa pagos de liquidaciones de un propietario para un período.
        Solo revierte liquidaciones en estado 'Pagada'.
        Returns:
            dict con 'reversadas', 'ignoradas', y listas de IDs.
        """
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        placeholder = self.db.get_placeholder()

        # Obtener liquidaciones pagadas del propietario en el período
        cursor.execute(
            f"""
            SELECT l.ID_LIQUIDACION FROM LIQUIDACIONES l
            JOIN CONTRATOS_MANDATOS cm ON l.ID_CONTRATO_M = cm.ID_CONTRATO_M
            WHERE cm.ID_PROPIETARIO = {placeholder} AND l.PERIODO = {placeholder}
            AND l.ESTADO_LIQUIDACION = 'Pagada' AND l.eliminada = FALSE
        """,
            (id_propietario, periodo),
        )

        pagadas = [row[0] for row in cursor.fetchall()]
        reversadas = []
        ignoradas = []

        for id_liq in pagadas:
            result = self.reversar_pago(id_liq, usuario_sistema, motivo)
            if result["exitosa"]:
                reversadas.append(id_liq)
            else:
                ignoradas.append(id_liq)

        return {
            "reversadas": reversadas,
            "ignoradas": ignoradas,
            "total_reversadas": len(reversadas),
            "total_ignoradas": len(ignoradas),
        }

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
                        AND l.eliminada = FALSE
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
        id_asesor: Optional[int] = None,
        sort_by: str = "periodo",
        sort_order: str = "desc",
        ciclo_operativo: Optional[str] = None,
        fin_column: Optional[str] = None,
        fin_min: Optional[float] = None,
        fin_max: Optional[float] = None,
    ):
        """
        Lista liquidaciones agrupadas por propietario con totales consolidados.
        Retorna un resultado paginado con información agregada y ordenamiento dinámico.
        """
        from src.dominio.modelos.pagination import PaginatedResult, PaginationParams

        params = PaginationParams(page=page, page_size=page_size)
        placeholder = self.db.get_placeholder()

        # Whitelisting para ordenamiento agrupado
        SORT_COLUMNS = {
            "periodo": "l.PERIODO",
            "propietario": "per.NOMBRE_COMPLETO",
            "documento": "per.NUMERO_DOCUMENTO",
            "cantidad_propiedades": "CANTIDAD_PROPIEDADES",
            "canon": "TOTAL_CANON_BRUTO",
            "otros_ingresos": "TOTAL_OTROS_INGRESOS",
            "gastos_administracion": "TOTAL_GASTOS_ADMIN",
            "gastos_servicios": "TOTAL_GASTOS_SERV",
            "gastos_reparaciones": "TOTAL_GASTOS_REP",
            "valor_incidentes": "TOTAL_VALOR_INCIDENTES",
            "pago_predial": "TOTAL_PAGO_PREDIAL",
            "otros_egresos": "TOTAL_OTROS_EGRESOS",
            "comision_monto": "TOTAL_COMISION",
            "iva_comision": "TOTAL_IVA",
            "neto": "NETO_TOTAL",
        }

        sort_col = SORT_COLUMNS.get(sort_by, "l.PERIODO")
        order = "ASC" if sort_order.lower() == "asc" else "DESC"

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
                    MAX(l.COMISION_PORCENTAJE) as COMISION_PORCENTAJE,
                    SUM(l.IVA_COMISION) as TOTAL_IVA,
                    SUM(l.IMPUESTO_4X1000) as TOTAL_IMPUESTO,
                    SUM(l.GASTOS_ADMINISTRACION) as TOTAL_GASTOS_ADMIN,
                    SUM(l.GASTOS_SERVICIOS) as TOTAL_GASTOS_SERV,
                    SUM(l.GASTOS_REPARACIONES) as TOTAL_GASTOS_REP,
                    SUM(l.VALOR_INCIDENTES) as TOTAL_VALOR_INCIDENTES,
                    SUM(l.PAGO_PREDIAL) as TOTAL_PAGO_PREDIAL,
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

            conditions = ["l.eliminada = FALSE"]
            query_params = []

            # Filtros
            if estado and estado != "Todos":
                conditions.append(f"l.ESTADO_LIQUIDACION = {placeholder}")
                query_params.append(estado)

            if periodo:
                conditions.append(f"l.PERIODO = {placeholder}")
                query_params.append(periodo)

            if busqueda:
                cols = ["per.NOMBRE_COMPLETO", "per.NUMERO_DOCUMENTO"]
                cond = self.db.get_search_condition(cols)
                conditions.append(f"({cond})")

                term_norm = f"%{self.db.normalize_search_term(busqueda)}%"
                query_params.extend([term_norm] * len(cols))

            if id_asesor:
                conditions.append(f"cm.ID_ASESOR = {placeholder}")
                query_params.append(id_asesor)

            if ciclo_operativo and ciclo_operativo != "Todos":
                conditions.append(f"cm.GRUPO_OPERATIVO = {placeholder}")
                query_params.append(ciclo_operativo)

            where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
            group_by = " GROUP BY cm.ID_PROPIETARIO, l.PERIODO, per.NOMBRE_COMPLETO, per.NUMERO_DOCUMENTO"
            
            having_conditions = []
            if fin_column and fin_column != "Ninguna":
                map_agr = {
                    "Otros Ingresos": "SUM(l.OTROS_INGRESOS)",
                    "Gastos Admin": "SUM(l.GASTOS_ADMINISTRACION)",
                    "Gastos Servicios": "SUM(l.GASTOS_SERVICIOS)",
                    "Gastos Reparaciones": "SUM(l.GASTOS_REPARACIONES)",
                    "Valor Incidentes": "SUM(l.VALOR_INCIDENTES)",
                    "Pago Predial": "SUM(l.PAGO_PREDIAL)",
                    "Otros Egresos": "SUM(l.OTROS_EGRESOS)",
                    "IVA Comisión": "SUM(l.IVA_COMISION)",
                }
                col_db = map_agr.get(fin_column)
                if col_db:
                    if fin_min is not None:
                        having_conditions.append(f"{col_db} >= {placeholder}")
                        query_params.append(fin_min)
                    if fin_max is not None:
                        having_conditions.append(f"{col_db} <= {placeholder}")
                        query_params.append(fin_max)
                        
            having_clause = " HAVING " + " AND ".join(having_conditions) if having_conditions else ""

            # Count de grupos
            count_query = f"""
                SELECT COUNT(*) as TOTAL FROM (
                    SELECT cm.ID_PROPIETARIO, l.PERIODO
                    {base_from}
                    {where_clause}
                    {group_by}
                    {having_clause}
                ) AS grupos
            """
            cursor.execute(count_query, query_params)
            total_row = cursor.fetchone()
            total = total_row["TOTAL"] if total_row else 0

            # Data query con ordenamiento
            data_query = f"""
                {base_select}
                {base_from}
                {where_clause}
                {group_by}
                {having_clause}
                ORDER BY {sort_col} {order}, l.PERIODO DESC
                LIMIT {placeholder} OFFSET {placeholder}
            """

            cursor.execute(data_query, query_params + [params.page_size, params.offset])

            rows = cursor.fetchall()
            
            # OPTIMIZACIÓN N+1: Obtener todos los estados de una sola vez
            grupos = [{"ID_PROPIETARIO": r["ID_PROPIETARIO"], "PERIODO": r["PERIODO"]} for r in rows]
            estados_liquidacion = self._obtener_estados_liquidacion_por_grupos(grupos, placeholder)
            estados_recaudo = self._obtener_estados_recaudo_por_grupos(grupos, placeholder)

            items = []
            for row in rows:
                key = (row["ID_PROPIETARIO"], row["PERIODO"])
                
                # Determinar estado consolidado desde el batch
                estados_map = estados_liquidacion.get(key, {})
                total_liq = sum(estados_map.values())

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

                # Determinar estado_recaudo consolidado desde el batch
                recaudo_estados = estados_recaudo.get(key, {})
                if recaudo_estados.get("Pendiente", 0) > 0:
                    estado_recaudo_consolidado = "Pendiente"
                elif recaudo_estados.get("Vencido", 0) > 0:
                    estado_recaudo_consolidado = "Vencido"
                elif (
                    recaudo_estados.get("Aplicado", 0) > 0
                    and sum(recaudo_estados.values()) >= row["CANTIDAD_PROPIEDADES"]
                ):
                    estado_recaudo_consolidado = "Aplicado"
                elif recaudo_estados.get("Reversado", 0) > 0:
                    estado_recaudo_consolidado = "Reversado"
                else:
                    estado_recaudo_consolidado = "Sin Recaudo"

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
                        "estado_recaudo": estado_recaudo_consolidado,
                        "otros_ingresos": row["TOTAL_OTROS_INGRESOS"],
                        "gastos_administracion": row["TOTAL_GASTOS_ADMIN"],
                        "gastos_servicios": row["TOTAL_GASTOS_SERV"],
                        "gastos_reparaciones": row["TOTAL_GASTOS_REP"],
                        "valor_incidentes": row.get("TOTAL_VALOR_INCIDENTES", 0),
                        "pago_predial": row["TOTAL_PAGO_PREDIAL"],
                        "otros_egresos": row["TOTAL_OTROS_EGRESOS"],
                        "comision_monto": row.get("TOTAL_COMISION", 0),
                        "comision_porcentaje": row.get("COMISION_PORCENTAJE", 0),
                        "iva_comision": row["TOTAL_IVA"],
                    }
                )

            return PaginatedResult(
                items=items, total=total, page=params.page, page_size=params.page_size
            )

    def _obtener_estados_liquidacion_por_grupos(
        self, grupos: List[Dict], placeholder: str
    ) -> Dict[str, Dict[str, int]]:
        """
        OPTIMIZACIÓN N+1: Obtiene los estados de liquidación para múltiples grupos en una sola consulta.
        
        Args:
            grupos: Lista de diccionarios con ID_PROPIETARIO y PERIODO
            placeholder: Placeholder para parámetros SQL
            
        Returns:
            Diccionario: {(id_propietario, periodo): {estado: count, ...}}
        """
        if not grupos:
            return {}

        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)

        # Construir condición IN para todos los grupos
        conditions = []
        params = []
        for g in grupos:
            conditions.append(f"(cm.ID_PROPIETARIO = {placeholder} AND l.PERIODO = {placeholder})")
            params.extend([g["ID_PROPIETARIO"], g["PERIODO"]])

        where_grupos = " OR ".join(conditions)

        query = f"""
            SELECT 
                cm.ID_PROPIETARIO,
                l.PERIODO,
                l.ESTADO_LIQUIDACION,
                COUNT(*) as CNT
            FROM LIQUIDACIONES l
            JOIN CONTRATOS_MANDATOS cm ON l.ID_CONTRATO_M = cm.ID_CONTRATO_M
            WHERE ({where_grupos})
            AND l.eliminada = FALSE
            GROUP BY cm.ID_PROPIETARIO, l.PERIODO, l.ESTADO_LIQUIDACION
        """

        cursor.execute(query, params)

        resultado = {}
        for row in cursor.fetchall():
            key = (row["ID_PROPIETARIO"], row["PERIODO"])
            if key not in resultado:
                resultado[key] = {}
            resultado[key][row["ESTADO_LIQUIDACION"]] = row["CNT"]

        return resultado

    def _obtener_estados_recaudo_por_grupos(
        self, grupos: List[Dict], placeholder: str
    ) -> Dict[str, Dict[str, int]]:
        """
        OPTIMIZACIÓN N+1: Obtiene los estados de recaudo para múltiples grupos en una sola consulta.
        
        Args:
            grupos: Lista de diccionarios con ID_PROPIETARIO y PERIODO
            placeholder: Placeholder para parámetros SQL
            
        Returns:
            Diccionario: {(id_propietario, periodo): {estado: count, ...}}
        """
        if not grupos:
            return {}

        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)

        # Construir condición IN para todos los grupos
        conditions = []
        params = []
        for g in grupos:
            conditions.append(f"(cm.ID_PROPIETARIO = {placeholder} AND l.PERIODO = {placeholder})")
            params.extend([g["ID_PROPIETARIO"], g["PERIODO"]])

        where_grupos = " OR ".join(conditions)

        query = f"""
            SELECT 
                cm.ID_PROPIETARIO,
                l.PERIODO,
                COALESCE(
                    (SELECT rrec_sub.ESTADO_RECAUDO
                     FROM RECAUDOS rrec_sub
                     JOIN RECAUDO_CONCEPTOS rconc_sub ON rconc_sub.ID_RECAUDO = rrec_sub.ID_RECAUDO
                     JOIN CONTRATOS_ARRENDAMIENTOS ca_sub ON ca_sub.ID_CONTRATO_A = rrec_sub.ID_CONTRATO_A
                     WHERE ca_sub.ID_PROPIEDAD = cm.ID_PROPIEDAD
                     AND rconc_sub.PERIODO = l.PERIODO
                     AND rrec_sub.ESTADO_RECAUDO != 'Reversado'
                     ORDER BY rrec_sub.FECHA_PAGO DESC
                     LIMIT 1),
                    'Sin Recaudo'
                ) AS ESTADO_RECAUDO,
                COUNT(DISTINCT l.ID_LIQUIDACION) as CNT
            FROM LIQUIDACIONES l
            JOIN CONTRATOS_MANDATOS cm ON l.ID_CONTRATO_M = cm.ID_CONTRATO_M
            WHERE ({where_grupos})
            AND l.eliminada = FALSE
            GROUP BY cm.ID_PROPIETARIO, l.PERIODO, cm.ID_PROPIEDAD, l.PERIODO
        """

        cursor.execute(query, params)

        resultado = {}
        for row in cursor.fetchall():
            key = (row["ID_PROPIETARIO"], row["PERIODO"])
            if key not in resultado:
                resultado[key] = {}
            estado = row["ESTADO_RECAUDO"]
            resultado[key][estado] = resultado[key].get(estado, 0) + row["CNT"]

        return resultado

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

    def obtener_datos_para_pdf(self, id_liquidacion: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene todos los datos necesarios para generar el PDF de liquidación.
        Realiza JOINS con Contratos, Propiedades, Propietarios, Inquilinos, etc.
        """
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        placeholder = self.db.get_placeholder()

        query = f"""
        SELECT 
            l.*,
            cm.ID_CONTRATO_M, cm.FECHA_INICIO_CONTRATO_M, cm.COMISION_PORCENTAJE_CONTRATO_M,
            p.DIRECCION_PROPIEDAD, p.MATRICULA_INMOBILIARIA, p.TIPO_PROPIEDAD, p.AREA_M2, p.VALOR_ADMINISTRACION,
            cm.BANCO_PROPIETARIO, cm.NUMERO_CUENTA_PROPIETARIO, cm.TIPO_CUENTA,
            per_prop.NOMBRE_COMPLETO as NOMBRE_PROPIETARIO,
            per_prop.NUMERO_DOCUMENTO as DOCUMENTO_PROPIETARIO,
            per_prop.TELEFONO_PRINCIPAL as TELEFONO_PROPIETARIO,
            per_prop.CORREO_ELECTRONICO as EMAIL_PROPIETARIO,
            per_prop.DIRECCION_PRINCIPAL as DIRECCION_PROPIEDARIO_RESIDENCIA,
            
            -- Datos del inquilino actual (si hay contrato activo)
            per_arr.NOMBRE_COMPLETO as NOMBRE_ARRENDATARIO,
            per_arr.NUMERO_DOCUMENTO as DOCUMENTO_ARRENDATARIO,

            -- Datos de seguro (Prioridad: Póliza activa -> Seguro del inquilino)
            COALESCE(seg.PORCENTAJE_SEGURO, seg_arr.PORCENTAJE_SEGURO) as PORCENTAJE_SEGURO,
            COALESCE(seg.NOMBRE_SEGURO, seg_arr.NOMBRE_SEGURO) as NOMBRE_SEGURO,

            -- Datos del asesor (Comisión real a aplicar)
            ase.COMISION_PORCENTAJE_ARRIENDO as COMISION_ASESOR
            
        FROM LIQUIDACIONES l
        JOIN CONTRATOS_MANDATOS cm ON l.ID_CONTRATO_M = cm.ID_CONTRATO_M
        JOIN PROPIEDADES p ON cm.ID_PROPIEDAD = p.ID_PROPIEDAD
        JOIN PROPIETARIOS prop ON cm.ID_PROPIETARIO = prop.ID_PROPIETARIO
        JOIN PERSONAS per_prop ON prop.ID_PERSONA = per_prop.ID_PERSONA
        LEFT JOIN ASESORES ase ON cm.ID_ASESOR = ase.ID_ASESOR
        
        -- Left Join para obtener Arrendatario y Seguro
        LEFT JOIN CONTRATOS_ARRENDAMIENTOS ca ON p.ID_PROPIEDAD = ca.ID_PROPIEDAD AND ca.ESTADO_CONTRATO_A = 'ACTIVO'
        LEFT JOIN ARRENDATARIOS arr ON ca.ID_ARRENDATARIO = arr.ID_ARRENDATARIO
        LEFT JOIN PERSONAS per_arr ON arr.ID_PERSONA = per_arr.ID_PERSONA
        
        -- Join 1: A través de Póliza (tabla POLIZAS)
        LEFT JOIN POLIZAS pol ON ca.ID_CONTRATO_A = pol.ID_CONTRATO AND pol.ESTADO = 'Activa'
        LEFT JOIN SEGUROS seg ON pol.ID_SEGURO = seg.ID_SEGURO
        
        -- Join 2: Directo desde Arrendatario (tabla ARRENDATARIOS)
        LEFT JOIN SEGUROS seg_arr ON arr.ID_SEGURO = seg_arr.ID_SEGURO
        
        WHERE l.ID_LIQUIDACION = {placeholder} AND l.eliminada = FALSE
        """

        cursor.execute(query, (id_liquidacion,))
        row = cursor.fetchone()

        if not row:
            return None

        row = dict(row)

        # Mapeo a estructura plana para PDF (Legacy Service compatible)
        return {
            "id": row.get("ID_LIQUIDACION"),
            "id_contrato": row.get("ID_CONTRATO_M"),
            "periodo": row.get("PERIODO"),
            "fecha_generacion": row.get("FECHA_GENERACION"),
            "estado": row.get("ESTADO_LIQUIDACION"),
            # Propietario (Flat)
            "propietario": row.get("NOMBRE_PROPIETARIO"),
            "documento": row.get("DOCUMENTO_PROPIETARIO"),
            "telefono": row.get("TELEFONO_PROPIETARIO"),
            "email": row.get("EMAIL_PROPIETARIO"),
            "direccion_propietario": row.get("DIRECCION_PROPIEDARIO_RESIDENCIA"),
            "banco": row.get("BANCO_PROPIETARIO"),
            "numero_cuenta": row.get("NUMERO_CUENTA_PROPIETARIO"),
            "tipo_cuenta": row.get("TIPO_CUENTA"),
            # Inmueble (Flat)
            "propiedad": row.get("DIRECCION_PROPIEDAD"),
            "matricula": row.get("MATRICULA_INMOBILIARIA"),
            "tipo_propiedad": row.get("TIPO_PROPIEDAD"),
            "area": row.get("AREA_M2"),
            "valor_administracion": row.get("VALOR_ADMINISTRACION"),
            # Inquilino
            "nombre_arrendatario": row.get("NOMBRE_ARRENDATARIO"),
            "documento_arrendatario": row.get("DOCUMENTO_ARRENDATARIO"),
            # Datos adicionales para cálculo/display
            "comision_pct_contrato": row.get("COMISION_PORCENTAJE_CONTRATO_M"),
            "comision_pct_asesor": row.get("COMISION_ASESOR"),
            "seguro_pct": row.get("PORCENTAJE_SEGURO"),
            "nombre_seguro": row.get("NOMBRE_SEGURO"),
            # Detalle Financiero
            "canon": row.get("CANON_BRUTO"),
            "otros_ingresos": row.get("OTROS_INGRESOS"),
            "total_ingresos": row.get("TOTAL_INGRESOS"),
            "comision_pct": row.get("COMISION_PORCENTAJE"),
            "comision_monto": row.get("COMISION_MONTO"),
            "iva_comision": row.get("IVA_COMISION"),
            "impuesto_4x1000": row.get("IMPUESTO_4X1000"),
            "gastos_admin": row.get("GASTOS_ADMINISTRACION"),
            # Claves renombradas para coincidir con servicio PDF legacy
            "gastos_serv": row.get("GASTOS_SERVICIOS"),
            "gastos_rep": row.get("GASTOS_REPARACIONES"),
            "pago_predial": row.get("PAGO_PREDIAL"),
            "seguro_monto": row.get("SEGURO_MONTO") or 0,
            "otros_egr": row.get("OTROS_EGRESOS") or 0,
            "valor_incidentes": row.get("VALOR_INCIDENTES") or 0,
            "total_egresos": row.get("TOTAL_EGRESOS"),
            "neto_pagar": row.get("NETO_A_PAGAR"),
            "observaciones": row.get("OBSERVACIONES"),
            # Datos de pago (si existen en la tabla)
            "fecha_pago": row.get("FECHA_PAGO"),
            "metodo_pago": row.get("METODO_PAGO"),
            "referencia_pago": row.get("REFERENCIA_PAGO"),
        }

    def obtener_consolidado_propietario(
        self, id_propietario: int, periodo: str
    ) -> Optional[Dict[str, Any]]:
        """
        Obtiene datos consolidados de todas las propiedades de un propietario para un periodo.
        """
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        placeholder = self.db.get_placeholder()

        # 1. Obtener datos del propietario (Campos bancarios removidos de PROPIETARIOS)
        query_prop = f"""
        SELECT 
            prop.ID_PROPIETARIO,
            per.NOMBRE_COMPLETO, per.NUMERO_DOCUMENTO, per.TELEFONO_PRINCIPAL, per.CORREO_ELECTRONICO
        FROM PROPIETARIOS prop
        JOIN PERSONAS per ON prop.ID_PERSONA = per.ID_PERSONA
        WHERE prop.ID_PROPIETARIO = {placeholder}
        """
        cursor.execute(query_prop, (id_propietario,))
        propietario = cursor.fetchone()

        if not propietario:
            return None

        propietario = dict(propietario)

        # 2. Obtener liquidaciones con datos bancarios del contrato
        query_liqs = f"""
        SELECT 
            l.*,
            p.ID_PROPIEDAD,
            p.DIRECCION_PROPIEDAD,
            cm.BANCO_PROPIETARIO, cm.NUMERO_CUENTA_PROPIETARIO, cm.TIPO_CUENTA,
            cm.CONSIGNATARIO, cm.DOCUMENTO_CONSIGNATARIO,
            COALESCE(seg.PORCENTAJE_SEGURO, seg_arr.PORCENTAJE_SEGURO, 0) as PORCENTAJE_SEGURO
        FROM LIQUIDACIONES l
        JOIN CONTRATOS_MANDATOS cm ON l.ID_CONTRATO_M = cm.ID_CONTRATO_M
        JOIN PROPIEDADES p ON cm.ID_PROPIEDAD = p.ID_PROPIEDAD
        
        -- Left Join para obtener Arrendatario y Seguro
        LEFT JOIN CONTRATOS_ARRENDAMIENTOS ca ON p.ID_PROPIEDAD = ca.ID_PROPIEDAD AND ca.ESTADO_CONTRATO_A = 'ACTIVO'
        LEFT JOIN ARRENDATARIOS arr ON ca.ID_ARRENDATARIO = arr.ID_ARRENDATARIO
        
        -- Join 1: A través de Póliza (tabla POLIZAS)
        LEFT JOIN POLIZAS pol ON ca.ID_CONTRATO_A = pol.ID_CONTRATO AND pol.ESTADO = 'Activa'
        LEFT JOIN SEGUROS seg ON pol.ID_SEGURO = seg.ID_SEGURO
        
        -- Join 2: Directo desde Arrendatario (tabla ARRENDATARIOS)
        LEFT JOIN SEGUROS seg_arr ON arr.ID_SEGURO = seg_arr.ID_SEGURO

        WHERE cm.ID_PROPIETARIO = {placeholder} AND l.PERIODO = {placeholder}
        AND l.eliminada = FALSE
        """
        cursor.execute(query_liqs, (id_propietario, periodo))
        liquidaciones = [dict(r) for r in cursor.fetchall()]

        if not liquidaciones:
            return None

        # 3. Calcular totales consolidados
        total_ingresos = sum(l.get("TOTAL_INGRESOS", 0) or 0 for l in liquidaciones)
        total_egresos = sum(l.get("TOTAL_EGRESOS", 0) or 0 for l in liquidaciones)
        neto_pagar = sum(l.get("NETO_A_PAGAR", 0) or 0 for l in liquidaciones)

        comision_total = sum(l.get("COMISION_MONTO", 0) or 0 for l in liquidaciones)
        iva_total = sum(l.get("IVA_COMISION", 0) or 0 for l in liquidaciones)
        impuesto_total = sum(l.get("IMPUESTO_4X1000", 0) or 0 for l in liquidaciones)

        gastos_admin = sum(
            l.get("GASTOS_ADMINISTRACION", 0) or 0 for l in liquidaciones
        )
        gastos_serv = sum(l.get("GASTOS_SERVICIOS", 0) or 0 for l in liquidaciones)
        gastos_rep = sum(l.get("GASTOS_REPARACIONES", 0) or 0 for l in liquidaciones)
        pago_predial = sum(l.get("PAGO_PREDIAL", 0) or 0 for l in liquidaciones)
        otros_egr = sum(l.get("OTROS_EGRESOS", 0) or 0 for l in liquidaciones)

        # 4. Datos bancarios (extraídos del primer contrato del periodo)
        primera_liq = liquidaciones[0]
        banco = primera_liq.get("BANCO_PROPIETARIO") or "N/A"
        num_cta = primera_liq.get("NUMERO_CUENTA_PROPIETARIO") or "N/A"
        tipo_cta = primera_liq.get("TIPO_CUENTA") or "N/A"
        consignatario = primera_liq.get("CONSIGNATARIO") or ""
        doc_consignatario = primera_liq.get("DOCUMENTO_CONSIGNATARIO") or ""

        # 5. Formatear lista de propiedades
        propiedades_formateadas = []
        for l in liquidaciones:
            propiedades_formateadas.append(
                {
                    "id": l.get("ID_PROPIEDAD"),
                    "direccion": l.get("DIRECCION_PROPIEDAD"),
                    "canon": l.get("CANON_BRUTO"),
                    "otros_ingresos": l.get("OTROS_INGRESOS"),
                    "comision_monto": l.get("COMISION_MONTO"),
                    "iva_comision": l.get("IVA_COMISION"),
                    "impuesto_4x1000": l.get("IMPUESTO_4X1000"),
                    "gastos_admin": l.get("GASTOS_ADMINISTRACION"),
                    "gastos_serv": l.get("GASTOS_SERVICIOS"),
                    "gastos_rep": l.get("GASTOS_REPARACIONES"),
                    "valor_incidentes": l.get("VALOR_INCIDENTES") or 0,
                    "pago_predial": l.get("PAGO_PREDIAL"),
                    "seguro_monto": l.get("SEGURO_MONTO", 0),
                    "otros_egr": l.get("OTROS_EGRESOS"),
                    "neto": l.get("NETO_A_PAGAR"),
                    "porcentaje_seguro": l.get("PORCENTAJE_SEGURO", 0),
                }
            )

        # 6. Consolidar observaciones
        lista_obs = [
            l.get("OBSERVACIONES") for l in liquidaciones if l.get("OBSERVACIONES")
        ]
        observaciones_final = ""
        if lista_obs:
            observaciones_final = " | ".join(lista_obs)
        else:
            observaciones_final = (
                f"Estado de cuenta consolidado para {len(liquidaciones)} inmuebles."
            )

        return {
            "propietario": propietario["NOMBRE_COMPLETO"],
            "documento": propietario["NUMERO_DOCUMENTO"],
            "telefono": propietario.get("TELEFONO_PRINCIPAL", "N/A"),
            "email": propietario.get("CORREO_ELECTRONICO", "N/A"),
            "banco": banco,
            "tipo_cuenta": tipo_cta,
            "cuenta_bancaria": num_cta,
            "consignatario": consignatario,
            "documento_consignatario": doc_consignatario,
            "periodo": periodo,
            "cantidad_propiedades": len(liquidaciones),
            "fecha_generacion": liquidaciones[0].get("FECHA_GENERACION"),
            "propiedades": propiedades_formateadas,
            "total_ingresos": total_ingresos,
            "total_egresos": total_egresos,
            "neto_pagar": neto_pagar,
            "comision_monto": comision_total,
            "iva_comision": iva_total,
            "impuesto_4x1000": impuesto_total,
            "gastos_admin": gastos_admin,
            "gastos_serv": gastos_serv,
            "gastos_rep": gastos_rep,
            "pago_predial": pago_predial,
            "seguro_monto": sum(l.get("SEGURO_MONTO", 0) or 0 for l in liquidaciones),
            "otros_egr": otros_egr,
            "observaciones": observaciones_final,
        }

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

    def listar_paginado(
        self,
        limit: int,
        offset: int,
        estado: Optional[str] = None,
        periodo: Optional[str] = None,
        busqueda: Optional[str] = None,
        id_asesor: Optional[int] = None,
        sort_by: str = "periodo",
        sort_order: str = "desc",
        ciclo_operativo: Optional[str] = None,
        fin_column: Optional[str] = None,
        fin_min: Optional[float] = None,
        fin_max: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """Lista liquidaciones con paginación y filtros complejos."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        placeholder = self.db.get_placeholder()

        # Mapeo de columnas para ordenamiento (Whitelisting contra SQL Injection)
        SORT_COLUMNS = {
            "id": "l.ID_LIQUIDACION",
            "periodo": "l.PERIODO",
            "fecha_generacion": "l.FECHA_GENERACION",
            "estado": "l.ESTADO_LIQUIDACION",
            "canon": "l.CANON_BRUTO",
            "otros_ingresos": "l.OTROS_INGRESOS",
            "gastos_administracion": "l.GASTOS_ADMINISTRACION",
            "gastos_servicios": "l.GASTOS_SERVICIOS",
            "gastos_reparaciones": "l.GASTOS_REPARACIONES",
            "valor_incidentes": "l.VALOR_INCIDENTES",
            "pago_predial": "l.PAGO_PREDIAL",
            "otros_egresos": "l.OTROS_EGRESOS",
            "comision_monto": "l.COMISION_MONTO",
            "iva_comision": "l.IVA_COMISION",
            "neto": "l.NETO_A_PAGAR",
            "contrato": "p.DIRECCION_PROPIEDAD",
            "matricula": "p.MATRICULA_INMOBILIARIA",
            "propietario": "per.NOMBRE_COMPLETO",
            "documento": "per.NUMERO_DOCUMENTO",
            "dia_pago": "cm.FECHA_PAGO",
        }

        sort_col_raw = SORT_COLUMNS.get(sort_by, "l.PERIODO")
        order = "ASC" if sort_order.lower() == "asc" else "DESC"

        # Tratamiento especial para dia_pago (cast numérico)
        if sort_by == "dia_pago":
            if self.db.use_postgresql:
                sort_col = f"CAST(NULLIF(TRIM({sort_col_raw}), '') AS INTEGER)"
            else:
                sort_col = f"CAST({sort_col_raw} AS INTEGER)"
        else:
            sort_col = sort_col_raw

        base_from = """
            FROM LIQUIDACIONES l
            JOIN CONTRATOS_MANDATOS cm ON l.ID_CONTRATO_M = cm.ID_CONTRATO_M
            JOIN PROPIEDADES p ON cm.ID_PROPIEDAD = p.ID_PROPIEDAD
            JOIN PROPIETARIOS prop ON cm.ID_PROPIETARIO = prop.ID_PROPIETARIO
            JOIN PERSONAS per ON prop.ID_PERSONA = per.ID_PERSONA
        """

        conditions = ["l.eliminada = FALSE"]
        query_params = []

        if estado and estado != "Todos":
            conditions.append(f"l.ESTADO_LIQUIDACION = {placeholder}")
            query_params.append(estado)

        if periodo:
            conditions.append(f"l.PERIODO LIKE {placeholder}")
            query_params.append(f"%{periodo}%")

        if busqueda:
            cols = [
                "p.DIRECCION_PROPIEDAD",
                "per.NOMBRE_COMPLETO",
                "per.NUMERO_DOCUMENTO",
                "CAST(l.ID_CONTRATO_M AS TEXT)",
            ]
            cond = self.db.get_search_condition(cols)
            conditions.append(f"({cond})")

            term_norm = f"%{self.db.normalize_search_term(busqueda)}%"
            query_params.extend([term_norm] * len(cols))

        if id_asesor:
            conditions.append(f"cm.ID_ASESOR = {placeholder}")
            query_params.append(id_asesor)

        if ciclo_operativo and ciclo_operativo != "Todos":
            conditions.append(f"cm.GRUPO_OPERATIVO = {placeholder}")
            query_params.append(ciclo_operativo)
            
        if fin_column and fin_column != "Ninguna":
            map_ind = {
                "Otros Ingresos": "l.OTROS_INGRESOS",
                "Gastos Admin": "l.GASTOS_ADMINISTRACION",
                "Gastos Servicios": "l.GASTOS_SERVICIOS",
                "Gastos Reparaciones": "l.GASTOS_REPARACIONES",
                "Valor Incidentes": "l.VALOR_INCIDENTES",
                "Pago Predial": "l.PAGO_PREDIAL",
                "Otros Egresos": "l.OTROS_EGRESOS",
                "IVA Comisión": "l.IVA_COMISION",
            }
            col_db = map_ind.get(fin_column)
            if col_db:
                if fin_min is not None:
                    conditions.append(f"{col_db} >= {placeholder}")
                    query_params.append(fin_min)
                if fin_max is not None:
                    conditions.append(f"{col_db} <= {placeholder}")
                    query_params.append(fin_max)

        where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""

        query = f"""
            SELECT 
                l.ID_LIQUIDACION, l.PERIODO, l.ESTADO_LIQUIDACION, l.CANON_BRUTO,
                l.OTROS_INGRESOS, l.COMISION_MONTO, l.COMISION_PORCENTAJE, l.IVA_COMISION, l.IMPUESTO_4X1000,
                l.GASTOS_ADMINISTRACION, l.GASTOS_SERVICIOS, l.GASTOS_REPARACIONES, 
                l.VALOR_INCIDENTES, l.PAGO_PREDIAL, l.OTROS_EGRESOS, l.NETO_A_PAGAR,
                p.DIRECCION_PROPIEDAD, per.NOMBRE_COMPLETO as NOMBRE_PROPIETARIO, cm.FECHA_PAGO, cm.GRUPO_OPERATIVO,
                (SELECT rrec_sub.ESTADO_RECAUDO
                 FROM RECAUDOS rrec_sub
                 JOIN RECAUDO_CONCEPTOS rconc_sub ON rconc_sub.ID_RECAUDO = rrec_sub.ID_RECAUDO
                 JOIN CONTRATOS_ARRENDAMIENTOS ca_sub ON ca_sub.ID_CONTRATO_A = rrec_sub.ID_CONTRATO_A
                 WHERE ca_sub.ID_PROPIEDAD = p.ID_PROPIEDAD
                   AND rconc_sub.PERIODO = l.PERIODO
                   AND rrec_sub.ESTADO_RECAUDO != 'Reversado'
                 ORDER BY rrec_sub.FECHA_PAGO DESC
                 LIMIT 1) AS ESTADO_RECAUDO
            {base_from} {where_clause}
            ORDER BY {sort_col} {order}, l.ID_LIQUIDACION DESC
            LIMIT {placeholder} OFFSET {placeholder}
        """

        cursor.execute(query, query_params + [limit, offset])

        items = []
        for row in cursor.fetchall():
            items.append(
                {
                    "id": row["ID_LIQUIDACION"],
                    "periodo": row["PERIODO"],
                    "estado": row["ESTADO_LIQUIDACION"],
                    "canon": row["CANON_BRUTO"],
                    "neto": row["NETO_A_PAGAR"],
                    "contrato": row["DIRECCION_PROPIEDAD"],
                    "propiedad": row["DIRECCION_PROPIEDAD"],
                    "propietario": row.get("NOMBRE_PROPIETARIO", "N/D"),
                    "fecha_pago_mandato": row["FECHA_PAGO"],
                    "grupo_operativo": row.get("GRUPO_OPERATIVO") or 0,
                    "estado_recaudo": row.get("ESTADO_RECAUDO") or "Sin Recaudo",
                    "otros_ingresos": row.get("OTROS_INGRESOS", 0),
                    "gastos_administracion": row.get("GASTOS_ADMINISTRACION", 0),
                    "gastos_servicios": row.get("GASTOS_SERVICIOS", 0),
                    "gastos_reparaciones": row.get("GASTOS_REPARACIONES", 0),
                    "valor_incidentes": row.get("VALOR_INCIDENTES", 0),
                    "pago_predial": row.get("PAGO_PREDIAL", 0),
                    "otros_egresos": row.get("OTROS_EGRESOS", 0),
                    "comision_monto": row.get("COMISION_MONTO", 0),
                    "comision_porcentaje": row.get("COMISION_PORCENTAJE", 0),
                    "iva_comision": row.get("IVA_COMISION", 0),
                }
            )
        return items

    def contar_con_filtros(
        self,
        estado: Optional[str] = None,
        periodo: Optional[str] = None,
        busqueda: Optional[str] = None,
        id_asesor: Optional[int] = None,
        ciclo_operativo: Optional[str] = None,
        fin_column: Optional[str] = None,
        fin_min: Optional[float] = None,
        fin_max: Optional[float] = None,
    ) -> int:
        """Cuenta total de liquidaciones filtradas."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        placeholder = self.db.get_placeholder()

        base_from = """
            FROM LIQUIDACIONES l
            JOIN CONTRATOS_MANDATOS cm ON l.ID_CONTRATO_M = cm.ID_CONTRATO_M
            JOIN PROPIEDADES p ON cm.ID_PROPIEDAD = p.ID_PROPIEDAD
            JOIN PROPIETARIOS prop ON cm.ID_PROPIETARIO = prop.ID_PROPIETARIO
            JOIN PERSONAS per ON prop.ID_PERSONA = per.ID_PERSONA
        """

        conditions = ["l.eliminada = FALSE"]
        query_params = []

        if estado and estado != "Todos":
            conditions.append(f"l.ESTADO_LIQUIDACION = {placeholder}")
            query_params.append(estado)

        if periodo:
            conditions.append(f"l.PERIODO LIKE {placeholder}")
            query_params.append(f"%{periodo}%")

        if busqueda:
            cols = [
                "p.DIRECCION_PROPIEDAD",
                "per.NOMBRE_COMPLETO",
                "per.NUMERO_DOCUMENTO",
                "CAST(l.ID_CONTRATO_M AS TEXT)",
            ]
            cond = self.db.get_search_condition(cols)
            conditions.append(f"({cond})")

            term_norm = f"%{self.db.normalize_search_term(busqueda)}%"
            query_params.extend([term_norm] * len(cols))

        if id_asesor:
            conditions.append(f"cm.ID_ASESOR = {placeholder}")
            query_params.append(id_asesor)

        if ciclo_operativo and ciclo_operativo != "Todos":
            conditions.append(f"cm.GRUPO_OPERATIVO = {placeholder}")
            query_params.append(ciclo_operativo)
            
        if fin_column and fin_column != "Ninguna":
            map_ind = {
                "Otros Ingresos": "l.OTROS_INGRESOS",
                "Gastos Admin": "l.GASTOS_ADMINISTRACION",
                "Gastos Servicios": "l.GASTOS_SERVICIOS",
                "Gastos Reparaciones": "l.GASTOS_REPARACIONES",
                "Valor Incidentes": "l.VALOR_INCIDENTES",
                "Pago Predial": "l.PAGO_PREDIAL",
                "Otros Egresos": "l.OTROS_EGRESOS",
                "IVA Comisión": "l.IVA_COMISION",
            }
            col_db = map_ind.get(fin_column)
            if col_db:
                if fin_min is not None:
                    conditions.append(f"{col_db} >= {placeholder}")
                    query_params.append(fin_min)
                if fin_max is not None:
                    conditions.append(f"{col_db} <= {placeholder}")
                    query_params.append(fin_max)

        where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
        query = f"SELECT COUNT(*) as TOTAL {base_from} {where_clause}"

        cursor.execute(query, query_params)
        row = cursor.fetchone()
        if row:
            # Soporte robusto para sqlite3.Row (acceso key/index) y dict (Postgres wrapper/Uppercase)
            try:
                # Intento 1: Alias explícito (Uppercase común en Postgres wrapper)
                return row["TOTAL"]
            except (KeyError, TypeError):
                try:
                    # Intento 2: Lowercase (SQLite dict factory a veces)
                    return row["total"]
                except (KeyError, TypeError):
                    # Intento 3: Index access (sqlite3.Row o Tuple)
                    try:
                        return row[0]
                    except (IndexError, TypeError):
                        pass
                    # Intento 4: Primer valor de dict (si las keys son raras)
                    if isinstance(row, dict):
                        return list(row.values())[0] if row else 0
        return 0
