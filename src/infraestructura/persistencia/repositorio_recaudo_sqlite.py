"""
Repositorio SQLite para Recaudo.
Implementa persistencia para pagos recibidos de inquilinos.
"""

from datetime import datetime
from typing import List, Optional, Any, Dict

from src.dominio.entidades.recaudo import Recaudo
from src.dominio.entidades.recaudo_concepto import RecaudoConcepto
from src.infraestructura.persistencia.database import DatabaseManager


class RepositorioRecaudoSQLite:
    """Repositorio SQLite para la entidad Recaudo."""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self._crear_tablas_si_no_existen()

    def _crear_tablas_si_no_existen(self):
        if self.db.use_postgresql:
            return

        """Crea las tablas RECAUDOS y RECAUDO_CONCEPTOS si no existen"""
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

        return Recaudo(
            id_recaudo=(row_dict.get("id_recaudo") or row_dict.get("ID_RECAUDO")),
            id_contrato_a=(row_dict.get("id_contrato_a") or row_dict.get("ID_CONTRATO_A")),
            fecha_pago=(row_dict.get("fecha_pago") or row_dict.get("FECHA_PAGO")),
            valor_total=(row_dict.get("valor_total") or row_dict.get("VALOR_TOTAL")),
            metodo_pago=(row_dict.get("metodo_pago") or row_dict.get("METODO_PAGO")),
            referencia_bancaria=(
                row_dict.get("referencia_bancaria") or row_dict.get("REFERENCIA_BANCARIA")
            ),
            estado_recaudo=(row_dict.get("estado_recaudo") or row_dict.get("ESTADO_RECAUDO")),
            observaciones=(row_dict.get("observaciones") or row_dict.get("OBSERVACIONES")),
            created_at=(row_dict.get("created_at") or row_dict.get("CREATED_AT")),
            created_by=(row_dict.get("created_by") or row_dict.get("CREATED_BY")),
            updated_at=(row_dict.get("updated_at") or row_dict.get("UPDATED_AT")),
            updated_by=(row_dict.get("updated_by") or row_dict.get("UPDATED_BY")),
        )

    def _concepto_row_to_entity(self, row) -> RecaudoConcepto:
        """Convierte una fila SQL a entidad RecaudoConcepto"""
        row_dict = self._get_row_dict(row)
        if not row_dict:
            return None

        return RecaudoConcepto(
            id_recaudo_concepto=(
                row_dict.get("id_recaudo_concepto") or row_dict.get("ID_RECAUDO_CONCEPTO")
            ),
            id_recaudo=(row_dict.get("id_recaudo") or row_dict.get("ID_RECAUDO")),
            tipo_concepto=(row_dict.get("tipo_concepto") or row_dict.get("TIPO_CONCEPTO")),
            periodo=(row_dict.get("periodo") or row_dict.get("PERIODO")),
            valor=(row_dict.get("valor") or row_dict.get("VALOR")),
            created_at=(row_dict.get("created_at") or row_dict.get("CREATED_AT")),
        )

    def crear(
        self, recaudo: Recaudo, conceptos: List[RecaudoConcepto], usuario_sistema: str
    ) -> Recaudo:
        """
        Crea un nuevo recaudo con sus conceptos asociados.
        Valida que la suma de conceptos = valor_total.
        """
        # Validar que la suma de conceptos sea igual al valor total
        suma_conceptos = sum(c.valor for c in conceptos)
        if suma_conceptos != recaudo.valor_total:
            raise ValueError(
                f"La suma de conceptos ({suma_conceptos}) no coincide con el valor total ({recaudo.valor_total})"
            )

        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        placeholder = self.db.get_placeholder()

        # Insertar recaudo
        cursor.execute(
            f"""
            INSERT INTO RECAUDOS (
                ID_CONTRATO_A, FECHA_PAGO, VALOR_TOTAL, METODO_PAGO,
                REFERENCIA_BANCARIA, ESTADO_RECAUDO, OBSERVACIONES,
                CREATED_AT, CREATED_BY
            ) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
        """,
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

        recaudo.id_recaudo = self.db.get_last_insert_id(cursor, "RECAUDOS", "ID_RECAUDO")

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

        cursor.execute(f"SELECT * FROM RECAUDOS WHERE ID_RECAUDO = {placeholder}", (id_recaudo,))
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

    def listar_todos(self) -> List[Recaudo]:
        """
        Lista todos los recaudos del sistema con información del contrato.

        Returns:
            Lista de todos los recaudos ordenados por fecha descendente
        """
        query = """
        SELECT 
            r.*,
            ca.ID_PROPIEDAD,
            p.DIRECCION_PROPIEDAD as direccion_propiedad
        FROM RECAUDOS r
        INNER JOIN CONTRATOS_ARRENDAMIENTOS ca ON r.ID_CONTRATO_A = ca.ID_CONTRATO_A
        INNER JOIN PROPIEDADES p ON ca.ID_PROPIEDAD = p.ID_PROPIEDAD
        ORDER BY r.FECHA_PAGO DESC, r.ID_RECAUDO DESC
        """

        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        self.db.get_placeholder()
        cursor.execute(query)
        rows = cursor.fetchall()

        recaudos = []
        for row in rows:
            recaudo = self._row_to_entity(row)
            if recaudo:
                # Agregar información adicional del contrato/propiedad
                # Usar helper _get_row_dict para seguridad
                row_dict = self._get_row_dict(row)
                recaudo.direccion_propiedad = row_dict.get("direccion_propiedad") or row_dict.get(
                    "direccion_propiedad"
                )
                recaudos.append(recaudo)

        return recaudos

    def cambiar_estado(self, id_recaudo: int, nuevo_estado: str, usuario_sistema: str) -> None:
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
        """Elimina un recaudo y sus conceptos asociados (soft delete o hard delete)."""
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        placeholder = self.db.get_placeholder()

        # Primero eliminar conceptos asociados
        cursor.execute(
            f"""
            DELETE FROM RECAUDO_CONCEPTOS WHERE ID_RECAUDO = {placeholder}
        """,
            (id_recaudo,),
        )

        # Luego eliminar el recaudo
        cursor.execute(
            f"""
            DELETE FROM RECAUDOS WHERE ID_RECAUDO = {placeholder}
        """,
            (id_recaudo,),
        )

        conn.commit()

    def actualizar(self, recaudo: Recaudo, usuario_sistema: str) -> None:
        """Actualiza un recaudo existente."""
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        placeholder = self.db.get_placeholder()

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

        conn.commit()

    def listar_paginado(
        self,
        limit: int,
        offset: int,
        estado: Optional[str] = None,
        fecha_desde: Optional[str] = None,
        fecha_hasta: Optional[str] = None,
        busqueda: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Lista recaudos con paginación y filtros complejos."""
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
            conditions.append(
                f"(r.REFERENCIA_BANCARIA LIKE {placeholder} OR p.DIRECCION_PROPIEDAD LIKE {placeholder} OR CAST(r.ID_RECAUDO AS TEXT) LIKE {placeholder})"
            )
            term = f"%{busqueda}%"
            query_params.extend([term, term, term])

        where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""

        query = f"""
            SELECT 
                r.ID_RECAUDO, r.FECHA_PAGO, r.ESTADO_RECAUDO, r.VALOR_TOTAL, r.METODO_PAGO,
                p.DIRECCION_PROPIEDAD
            {base_from} {where_clause}
            ORDER BY r.FECHA_PAGO DESC, r.ID_RECAUDO DESC
            LIMIT {placeholder} OFFSET {placeholder}
        """

        cursor.execute(query, query_params + [limit, offset])
        return [
            {
                "id": row["ID_RECAUDO"],
                "fecha": row["FECHA_PAGO"],
                "estado": row["ESTADO_RECAUDO"],
                "valor": row["VALOR_TOTAL"],
                "metodo": row["METODO_PAGO"],
                "contrato": row["DIRECCION_PROPIEDAD"]
            }
            for row in cursor.fetchall()
        ]

    def contar_con_filtros(
        self,
        estado: Optional[str] = None,
        fecha_desde: Optional[str] = None,
        fecha_hasta: Optional[str] = None,
        busqueda: Optional[str] = None
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
            conditions.append(
                f"(r.REFERENCIA_BANCARIA LIKE {placeholder} OR p.DIRECCION_PROPIEDAD LIKE {placeholder} OR CAST(r.ID_RECAUDO AS TEXT) LIKE {placeholder})"
            )
            term = f"%{busqueda}%"
            query_params.extend([term, term, term])

        where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
        query = f"SELECT COUNT(*) AS total {base_from} {where_clause}"

        cursor.execute(query, query_params)
        row = cursor.fetchone()
        if row:
            if hasattr(row, "keys"):
                return row["total"]
            return row[0]
        return 0
