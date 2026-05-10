"""
Repositorio para Recaudo.
Implementa persistencia para pagos recibidos de inquilinos.
Compatible con PostgreSQL (Producción) y SQLite (Desarrollo).
"""

import logging
from datetime import datetime
from typing import List, Optional, Any, Dict

logger = logging.getLogger(__name__)

from src.dominio.entidades.recaudo import Recaudo
from src.dominio.entidades.recaudo_concepto import RecaudoConcepto
from src.infraestructura.persistencia.database import DatabaseManager


class RepositorioRecaudo:
    """Repositorio para la entidad Recaudo con soporte Dual."""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self._crear_tablas_si_no_existen()

    def _crear_tablas_si_no_existen(self):
        if self.db.use_postgresql:
            return

        """Crea las tablas RECAUDOS y RECAUDO_CONCEPTOS si no existen (SQLite)"""
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()

        # Tabla RECAUDOS
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS RECAUDOS (
            ID_RECAUDO INTEGER PRIMARY KEY AUTOINCREMENT,
            ID_CONTRATO_A INTEGER NOT NULL,
            FECHA_PAGO TEXT NOT NULL,
            VALOR_TOTAL INTEGER NOT NULL CHECK(VALOR_TOTAL > 0),
            METODO_PAGO TEXT NOT NULL CHECK(METODO_PAGO IN ('Efectivo', 'Transferencia', 'PSE', 'Consignación')),
            REFERENCIA_BANCARIA TEXT,
            ESTADO_RECAUDO TEXT DEFAULT 'Pendiente' CHECK(ESTADO_RECAUDO IN ('Pendiente', 'Aplicado', 'Reversado')),
            OBSERVACIONES TEXT,
            CREATED_AT TEXT DEFAULT (datetime('now', 'localtime')),
            CREATED_BY TEXT,
            UPDATED_AT TEXT,
            UPDATED_BY TEXT,
            FOREIGN KEY (ID_CONTRATO_A) REFERENCES CONTRATOS_ARRENDAMIENTOS(ID_CONTRATO_A)
        )
        """
        )

        # Tabla RECAUDO_CONCEPTOS
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS RECAUDO_CONCEPTOS (
            ID_RECAUDO_CONCEPTO INTEGER PRIMARY KEY AUTOINCREMENT,
            ID_RECAUDO INTEGER NOT NULL,
            TIPO_CONCEPTO TEXT NOT NULL CHECK(TIPO_CONCEPTO IN ('Canon', 'Administración', 'Mora', 'Servicios', 'Otro')),
            PERIODO TEXT NOT NULL,
            VALOR INTEGER NOT NULL CHECK(VALOR > 0),
            CREATED_AT TEXT DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (ID_RECAUDO) REFERENCES RECAUDOS(ID_RECAUDO) ON DELETE CASCADE
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

    def _row_to_entity(self, row) -> Recaudo:
        """Convierte una fila SQL a entidad Recaudo"""
        row_dict = self._get_row_dict(row)
        if not row_dict:
            return None

        # Handle case-insensitive keys from different DBs
        def get_val(key):
            return row_dict.get(key.lower()) or row_dict.get(key.upper())

        return Recaudo(
            id_recaudo=get_val("ID_RECAUDO"),
            id_contrato_a=get_val("ID_CONTRATO_A"),
            fecha_pago=get_val("FECHA_PAGO"),
            valor_total=get_val("VALOR_TOTAL"),
            metodo_pago=get_val("METODO_PAGO"),
            referencia_bancaria=get_val("REFERENCIA_BANCARIA"),
            estado_recaudo=get_val("ESTADO_RECAUDO"),
            observaciones=get_val("OBSERVACIONES"),
            created_at=get_val("CREATED_AT"),
            created_by=get_val("CREATED_BY"),
            updated_at=get_val("UPDATED_AT"),
            updated_by=get_val("UPDATED_BY"),
        )

    def _concepto_row_to_entity(self, row) -> RecaudoConcepto:
        """Convierte una fila SQL a entidad RecaudoConcepto"""
        row_dict = self._get_row_dict(row)
        if not row_dict:
            return None

        def get_val(key):
            return row_dict.get(key.lower()) or row_dict.get(key.upper())

        return RecaudoConcepto(
            id_recaudo_concepto=get_val("ID_RECAUDO_CONCEPTO"),
            id_recaudo=get_val("ID_RECAUDO"),
            tipo_concepto=get_val("TIPO_CONCEPTO"),
            periodo=get_val("PERIODO"),
            valor=get_val("VALOR"),
            created_at=get_val("CREATED_AT"),
        )

    def crear(
        self, recaudo: Recaudo, conceptos: List[RecaudoConcepto], usuario_sistema: str
    ) -> Recaudo:
        """
        Crea un nuevo recaudo con sus conceptos asociados.
        Valida que la suma de conceptos = valor_total.
        """
        suma_conceptos = sum(c.valor for c in conceptos)
        if suma_conceptos != recaudo.valor_total:
            raise ValueError(
                f"La suma de conceptos ({suma_conceptos}) no coincide con el valor total ({recaudo.valor_total})"
            )

        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        placeholder = self.db.get_placeholder()

        # Insertar recaudo con RETURNING para PostgreSQL elite compatibility
        sql_recaudo = f"""
            INSERT INTO RECAUDOS (
                ID_CONTRATO_A, FECHA_PAGO, VALOR_TOTAL, METODO_PAGO,
                REFERENCIA_BANCARIA, ESTADO_RECAUDO, OBSERVACIONES,
                CREATED_AT, CREATED_BY
            ) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
            RETURNING ID_RECAUDO
        """

        # En PostgreSQL RealDictCursor/UpperCaseWrapper retornan dict, en SQLite fetchone retorna Row
        cursor.execute(
            sql_recaudo,
            (
                recaudo.id_contrato_a,
                recaudo.fecha_pago,
                recaudo.valor_total,
                recaudo.metodo_pago,
                recaudo.referencia_bancaria,
                recaudo.estado_recaudo,
                recaudo.observaciones,
                datetime.now().isoformat(),
                usuario_sistema,
            ),
        )

        res = cursor.fetchone()
        if res:
            if hasattr(res, "keys"):  # Wrapper dict
                recaudo.id_recaudo = res.get("ID_RECAUDO") or res.get("id_recaudo")
            else:  # Row or Tuple
                recaudo.id_recaudo = res[0]

        # Insertar conceptos
        for concepto in conceptos:
            concepto.id_recaudo = recaudo.id_recaudo
            cursor.execute(
                f"""
                INSERT INTO RECAUDO_CONCEPTOS (
                    ID_RECAUDO, TIPO_CONCEPTO, PERIODO, VALOR, CREATED_AT
                ) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
            """,
                (
                    concepto.id_recaudo,
                    concepto.tipo_concepto,
                    concepto.periodo,
                    concepto.valor,
                    datetime.now().isoformat(),
                ),
            )

        conn.commit()
        return recaudo

    def obtener_por_id(self, id_recaudo: int) -> Optional[Recaudo]:
        """Obtiene un recaudo por su ID"""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        placeholder = self.db.get_placeholder()

        cursor.execute(
            f"SELECT * FROM RECAUDOS WHERE ID_RECAUDO = {placeholder}", (id_recaudo,)
        )
        row = cursor.fetchone()

        return self._row_to_entity(row) if row else None

    def obtener_conceptos_por_recaudo(self, id_recaudo: int) -> List[RecaudoConcepto]:
        """Obtiene todos los conceptos de un recaudo"""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        placeholder = self.db.get_placeholder()

        cursor.execute(
            f"SELECT * FROM RECAUDO_CONCEPTOS WHERE ID_RECAUDO = {placeholder} ORDER BY PERIODO",
            (id_recaudo,),
        )

        return [self._concepto_row_to_entity(row) for row in cursor.fetchall()]

    def listar_por_contrato(self, id_contrato_a: int) -> List[Recaudo]:
        """Lista todos los recaudos de un contrato"""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        placeholder = self.db.get_placeholder()

        cursor.execute(
            f"SELECT * FROM RECAUDOS WHERE ID_CONTRATO_A = {placeholder} ORDER BY FECHA_PAGO DESC",
            (id_contrato_a,),
        )

        return [self._row_to_entity(row) for row in cursor.fetchall()]

    def obtener_estado_pago_actual(
        self, id_contrato_a: int, periodo: Optional[str] = None
    ) -> str:
        """
        Obtiene el estado de pago para un contrato en el período actual.
        Consulta el período en RECAUDO_CONCEPTOS.

        Returns:
            'AL_DIA' si existe recaudo aplicado en período, 'PENDIENTE' otherwise
        """
        from src.dominio.value_objects.estado_cumplimiento import obtener_periodo_actual

        periodo = periodo or obtener_periodo_actual()

        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        placeholder = self.db.get_placeholder()

        # Query directo a RECAUDO_CONCEPTOS para buscar el período
        query = f"""
            SELECT rc.PERIODO, r.ESTADO_RECAUDO
            FROM RECAUDO_CONCEPTOS rc
            JOIN RECAUDOS r ON rc.ID_RECAUDO = r.ID_RECAUDO
            WHERE r.ID_CONTRATO_A = {placeholder}
              AND rc.PERIODO = {placeholder}
              AND r.ESTADO_RECAUDO = 'Aplicado'
            LIMIT 1
        """

        cursor.execute(query, (id_contrato_a, periodo))
        row = cursor.fetchone()

        if row:
            return "AL_DIA"

        return "PENDIENTE"

    def cambiar_estado(
        self, id_recaudo: int, nuevo_estado: str, usuario_sistema: str
    ) -> None:
        """Cambia el estado de un recaudo (Pendiente → Aplicado o Reversado)"""
        if nuevo_estado not in ["Pendiente", "Aplicado", "Reversado"]:
            raise ValueError(f"Estado inválido: {nuevo_estado}")

        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        placeholder = self.db.get_placeholder()

        cursor.execute(
            f"""
            UPDATE RECAUDOS SET
                ESTADO_RECAUDO = {placeholder},
                UPDATED_AT = {placeholder},
                UPDATED_BY = {placeholder}
            WHERE ID_RECAUDO = {placeholder}
        """,
            (nuevo_estado, datetime.now().isoformat(), usuario_sistema, id_recaudo),
        )

        conn.commit()

    def eliminar(self, id_recaudo: int, usuario_sistema: str) -> None:
        """Elimina un recaudo y sus conceptos asociados."""
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        placeholder = self.db.get_placeholder()

        cursor.execute(
            f"DELETE FROM RECAUDO_CONCEPTOS WHERE ID_RECAUDO = {placeholder}",
            (id_recaudo,),
        )

        cursor.execute(
            f"DELETE FROM RECAUDOS WHERE ID_RECAUDO = {placeholder}",
            (id_recaudo,),
        )

        conn.commit()

    def actualizar(
        self,
        recaudo: Recaudo,
        usuario_sistema: str,
        conceptos: Optional[List[RecaudoConcepto]] = None,
    ) -> None:
        """Actualiza un recaudo existente y sus conceptos."""
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        placeholder = self.db.get_placeholder()

        try:
            # 1. Actualizar el recaudo principal
            cursor.execute(
                f"""
                UPDATE RECAUDOS SET
                    FECHA_PAGO = {placeholder},
                    VALOR_TOTAL = {placeholder},
                    METODO_PAGO = {placeholder},
                    REFERENCIA_BANCARIA = {placeholder},
                    OBSERVACIONES = {placeholder},
                    UPDATED_AT = {placeholder},
                    UPDATED_BY = {placeholder}
                WHERE ID_RECAUDO = {placeholder}
            """,
                (
                    recaudo.fecha_pago,
                    recaudo.valor_total,
                    recaudo.metodo_pago,
                    recaudo.referencia_bancaria,
                    recaudo.observaciones,
                    datetime.now().isoformat(),
                    usuario_sistema,
                    recaudo.id_recaudo,
                ),
            )

            # 2. Actualizar conceptos si se proporcionan
            if conceptos is not None:
                # Eliminar conceptos anteriores
                cursor.execute(
                    f"DELETE FROM RECAUDO_CONCEPTOS WHERE ID_RECAUDO = {placeholder}",
                    (recaudo.id_recaudo,),
                )

                # Insertar nuevos conceptos
                for concepto in conceptos:
                    cursor.execute(
                        f"""
                        INSERT INTO RECAUDO_CONCEPTOS (
                            ID_RECAUDO, TIPO_CONCEPTO, PERIODO, VALOR, 
                            CREATED_AT
                        ) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
                    """,
                        (
                            recaudo.id_recaudo,
                            concepto.tipo_concepto,
                            concepto.periodo,
                            concepto.valor,
                            datetime.now().isoformat(),
                        ),
                    )

            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Error al actualizar recaudo: {e}")
            raise e
        finally:
            cursor.close()

    def contar_con_filtros(
        self,
        estado: Optional[str] = None,
        fecha_desde: Optional[str] = None,
        fecha_hasta: Optional[str] = None,
        busqueda: Optional[str] = None,
    ) -> int:
        """Cuenta total de recaudos filtrados."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        placeholder = self.db.get_placeholder()

        base_from = """
            FROM RECAUDOS r
            JOIN CONTRATOS_ARRENDAMIENTOS ca ON r.ID_CONTRATO_A = ca.ID_CONTRATO_A
            JOIN PROPIEDADES p ON ca.ID_PROPIEDAD = p.ID_PROPIEDAD
        """

        conditions = []
        query_params = []

        if estado and estado != "Todos":
            conditions.append(f"r.ESTADO_RECAUDO = {placeholder}")
            query_params.append(estado)

        if fecha_desde:
            conditions.append(f"r.FECHA_PAGO >= {placeholder}")
            query_params.append(fecha_desde)

        if fecha_hasta:
            conditions.append(f"r.FECHA_PAGO <= {placeholder}")
            query_params.append(fecha_hasta)

        if busqueda:
            cols = [
                "r.REFERENCIA_BANCARIA",
                "p.DIRECCION_PROPIEDAD",
                "CAST(r.ID_RECAUDO AS TEXT)",
            ]
            cond = self.db.get_search_condition(cols)
            conditions.append(f"({cond})")

            term_norm = f"%{self.db.normalize_search_term(busqueda)}%"
            query_params.extend([term_norm] * len(cols))

        where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
        query = f"SELECT COUNT(*) AS total {base_from} {where_clause}"

        cursor.execute(query, query_params)
        row = cursor.fetchone()
        if row:
            if hasattr(row, "keys"):
                return row.get("total") or row.get("TOTAL") or 0
            return row[0]
        return 0

    def obtener_ids_contratos_con_recaudo(self, periodo: str) -> List[int]:
        """Retorna los IDs de contratos que ya tienen un recaudo en el periodo indicado."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        placeholder = self.db.get_placeholder()

        query = f"""
            SELECT DISTINCT r.ID_CONTRATO_A 
            FROM RECAUDO_CONCEPTOS rc
            JOIN RECAUDOS r ON rc.ID_RECAUDO = r.ID_RECAUDO
            WHERE rc.PERIODO = {placeholder}
        """
        cursor.execute(query, (periodo,))
        return [
            row["ID_CONTRATO_A"] or row["id_contrato_a"] for row in cursor.fetchall()
        ]

    def crear_masivo(
        self,
        recaudos_y_conceptos: List[tuple[Recaudo, List[RecaudoConcepto]]],
        usuario_sistema: str,
    ) -> int:
        """Crea múltiples recaudos y sus conceptos en una sola transacción."""
        if not recaudos_y_conceptos:
            return 0

        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        placeholder = self.db.get_placeholder()
        ahora = datetime.now().isoformat()
        count = 0

        try:
            for recaudo, conceptos in recaudos_y_conceptos:
                suma_conceptos = sum(c.valor for c in conceptos)
                if suma_conceptos != recaudo.valor_total:
                    continue

                sql_recaudo = f"""
                    INSERT INTO RECAUDOS (
                        ID_CONTRATO_A, FECHA_PAGO, VALOR_TOTAL, METODO_PAGO,
                        REFERENCIA_BANCARIA, ESTADO_RECAUDO, OBSERVACIONES,
                        CREATED_AT, CREATED_BY
                    ) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
                    RETURNING ID_RECAUDO
                """

                cursor.execute(
                    sql_recaudo,
                    (
                        recaudo.id_contrato_a,
                        recaudo.fecha_pago,
                        recaudo.valor_total,
                        recaudo.metodo_pago,
                        recaudo.referencia_bancaria,
                        recaudo.estado_recaudo,
                        recaudo.observaciones,
                        ahora,
                        usuario_sistema,
                    ),
                )

                res = cursor.fetchone()
                if res:
                    if hasattr(res, "keys"):  # Wrapper dict
                        id_recaudo = res.get("ID_RECAUDO") or res.get("id_recaudo")
                    else:  # Row or Tuple
                        id_recaudo = res[0]
                else:
                    # Fallback for old SQLite without RETURNING if needed, but we assume modern or DB Manager handling
                    id_recaudo = self.db.get_last_insert_id(
                        cursor, "RECAUDOS", "ID_RECAUDO"
                    )

                # Insertar conceptos
                for concepto in conceptos:
                    cursor.execute(
                        f"""
                        INSERT INTO RECAUDO_CONCEPTOS (
                            ID_RECAUDO, TIPO_CONCEPTO, PERIODO, VALOR, CREATED_AT
                        ) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
                        """,
                        (
                            id_recaudo,
                            concepto.tipo_concepto,
                            concepto.periodo,
                            concepto.valor,
                            ahora,
                        ),
                    )
                count += 1

            conn.commit()
            return count
        except Exception as e:
            conn.rollback()
            raise e

    def listar_paginado(
        self,
        limit: int,
        offset: int,
        estado: Optional[str] = None,
        fecha_desde: Optional[str] = None,
        fecha_hasta: Optional[str] = None,
        busqueda: Optional[str] = None,
        sort_by: str = "fecha_pago",
        sort_order: str = "desc",
    ) -> List[Dict[str, Any]]:
        """
        Lista recaudos paginados con JOINs a contratos, propiedades y arrendatarios.
        Incluye fecha de pago contractual y ordenamiento dinámico.
        """
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        placeholder = self.db.get_placeholder()

        # Mapeo de columnas para ordenamiento (Whitelisting contra SQL Injection)
        SORT_COLUMNS = {
            "id_recaudo": "r.ID_RECAUDO",
            "fecha_pago": "r.FECHA_PAGO",
            "fecha_pago_contrato": "ca.FECHA_PAGO",
            "valor_total": "r.VALOR_TOTAL",
            "estado": "r.ESTADO_RECAUDO",
            "arrendatario": "per.NOMBRE_COMPLETO",
            "direccion": "p.DIRECCION_PROPIEDAD"
        }
        
        sort_col = SORT_COLUMNS.get(sort_by, "r.FECHA_PAGO")
        order = "ASC" if sort_order.lower() == "asc" else "DESC"

        query = """
            SELECT 
                r.ID_RECAUDO,
                r.ID_CONTRATO_A,
                r.FECHA_PAGO,
                ca.FECHA_PAGO AS FECHA_PAGO_CONTRATO,
                r.VALOR_TOTAL,
                r.METODO_PAGO,
                r.REFERENCIA_BANCARIA,
                r.ESTADO_RECAUDO,
                r.OBSERVACIONES,
                p.DIRECCION_PROPIEDAD,
                p.MATRICULA_INMOBILIARIA,
                per.NOMBRE_COMPLETO as NOMBRE_ARRENDATARIO
            FROM RECAUDOS r
            INNER JOIN CONTRATOS_ARRENDAMIENTOS ca ON r.ID_CONTRATO_A = ca.ID_CONTRATO_A
            INNER JOIN PROPIEDADES p ON ca.ID_PROPIEDAD = p.ID_PROPIEDAD
            INNER JOIN ARRENDATARIOS arr ON ca.ID_ARRENDATARIO = arr.ID_ARRENDATARIO
            INNER JOIN PERSONAS per ON arr.ID_PERSONA = per.ID_PERSONA
            WHERE 1=1
        """
        params: list = []

        if estado and estado != "Todos":
            query += f" AND r.ESTADO_RECAUDO = {placeholder}"
            params.append(estado)

        if fecha_desde:
            query += f" AND r.FECHA_PAGO >= {placeholder}"
            params.append(fecha_desde)

        if fecha_hasta:
            query += f" AND r.FECHA_PAGO <= {placeholder}"
            params.append(fecha_hasta)

        if busqueda:
            cols = [
                "r.REFERENCIA_BANCARIA",
                "p.DIRECCION_PROPIEDAD",
                "per.NOMBRE_COMPLETO",
                "CAST(r.ID_RECAUDO AS TEXT)",
            ]
            cond = self.db.get_search_condition(cols)
            query += f" AND ({cond})"

            term_norm = f"%{self.db.normalize_search_term(busqueda)}%"
            params.extend([term_norm] * len(cols))

        query += f" ORDER BY {sort_col} {order}"
        query += f" LIMIT {placeholder} OFFSET {placeholder}"
        params.extend([limit, offset])

        cursor.execute(query, params)
        rows = cursor.fetchall()

        return [
            {
                "id_recaudo": row["ID_RECAUDO"],
                "id_contrato": row["ID_CONTRATO_A"],
                "codigo_contrato": f"ID:{row['ID_CONTRATO_A']}",
                "direccion": row["DIRECCION_PROPIEDAD"],
                "matricula": row["MATRICULA_INMOBILIARIA"],
                "arrendatario": row["NOMBRE_ARRENDATARIO"],
                "fecha_pago": row["FECHA_PAGO"],
                "fecha_pago_contrato": row["FECHA_PAGO_CONTRATO"] or "N/A",
                "valor_total": row["VALOR_TOTAL"],
                "metodo_pago": row["METODO_PAGO"],
                "referencia": row["REFERENCIA_BANCARIA"] or "",
                "estado": row["ESTADO_RECAUDO"],
                "observaciones": row["OBSERVACIONES"] or "",
            }
            for row in rows
        ]

    def obtener_recaudos_por_periodo(self, periodo: str) -> List[Dict[str, Any]]:
        """Obtiene recaudos con datos enriquecidos por período para generación masiva de PDFs.

        Args:
            periodo: Período en formato YYYY-MM.

        Returns:
            Lista de diccionarios con datos completos (recaudo + propiedad + arrendatario + conceptos).
        """
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        placeholder = self.db.get_placeholder()

        # Query principal: recaudos con JOINs enriquecidos
        query = f"""
            SELECT DISTINCT
                r.ID_RECAUDO,
                r.ID_CONTRATO_A,
                r.FECHA_PAGO,
                r.VALOR_TOTAL,
                r.METODO_PAGO,
                r.REFERENCIA_BANCARIA,
                r.ESTADO_RECAUDO,
                r.OBSERVACIONES,
                p.DIRECCION_PROPIEDAD,
                p.MATRICULA_INMOBILIARIA,
                m.NOMBRE_MUNICIPIO AS MUNICIPIO,
                m.DEPARTAMENTO,
                per.NOMBRE_COMPLETO AS NOMBRE_ARRENDATARIO,
                per.NUMERO_DOCUMENTO AS DOCUMENTO_ARRENDATARIO,
                per.CORREO_ELECTRONICO AS EMAIL_ARRENDATARIO,
                per.TELEFONO_PRINCIPAL AS TELEFONO_ARRENDATARIO
            FROM RECAUDOS r
            INNER JOIN RECAUDO_CONCEPTOS rc ON r.ID_RECAUDO = rc.ID_RECAUDO
            INNER JOIN CONTRATOS_ARRENDAMIENTOS ca ON r.ID_CONTRATO_A = ca.ID_CONTRATO_A
            INNER JOIN PROPIEDADES p ON ca.ID_PROPIEDAD = p.ID_PROPIEDAD
            LEFT JOIN MUNICIPIOS m ON p.ID_MUNICIPIO = m.ID_MUNICIPIO
            INNER JOIN ARRENDATARIOS arr ON ca.ID_ARRENDATARIO = arr.ID_ARRENDATARIO
            INNER JOIN PERSONAS per ON arr.ID_PERSONA = per.ID_PERSONA
            WHERE rc.PERIODO = {placeholder}
            ORDER BY r.ID_RECAUDO
        """

        cursor.execute(query, (periodo,))
        recaudos_rows = cursor.fetchall()

        resultados: List[Dict[str, Any]] = []

        for row in recaudos_rows:
            id_recaudo = row["ID_RECAUDO"]

            # Obtener conceptos para este recaudo
            query_conceptos = f"""
                SELECT TIPO_CONCEPTO, VALOR, PERIODO
                FROM RECAUDO_CONCEPTOS
                WHERE ID_RECAUDO = {placeholder}
                ORDER BY TIPO_CONCEPTO
            """
            cursor.execute(query_conceptos, (id_recaudo,))
            conceptos_rows = cursor.fetchall()

            resultados.append({
                "id_recaudo": row["ID_RECAUDO"],
                "id_contrato_a": row["ID_CONTRATO_A"],
                "fecha_pago": row["FECHA_PAGO"],
                "valor_total": row["VALOR_TOTAL"],
                "metodo_pago": row["METODO_PAGO"],
                "referencia_bancaria": row.get("REFERENCIA_BANCARIA") or "",
                "estado_recaudo": row["ESTADO_RECAUDO"],
                "observaciones": row.get("OBSERVACIONES") or "",
                "direccion_propiedad": row["DIRECCION_PROPIEDAD"],
                "matricula_inmobiliaria": row.get("MATRICULA_INMOBILIARIA") or "Sin matrícula",
                "municipio": row.get("MUNICIPIO", "Armenia"),
                "departamento": row.get("DEPARTAMENTO", "Quindío"),
                "nombre_arrendatario": row["NOMBRE_ARRENDATARIO"],
                "documento_arrendatario": row["DOCUMENTO_ARRENDATARIO"],
                "email_arrendatario": row.get("EMAIL_ARRENDATARIO") or "No registrado",
                "telefono_arrendatario": row.get("TELEFONO_ARRENDATARIO") or "No registrado",
                "conceptos": [
                    {
                        "tipo_concepto": c["TIPO_CONCEPTO"],
                        "valor": c["VALOR"],
                        "periodo": c["PERIODO"],
                    }
                    for c in conceptos_rows
                ],
            })

        return resultados
