"""
Repositorio SQLite: ContratoMandato
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from src.dominio.entidades.contrato_mandato import ContratoMandato
from src.dominio.modelos.pagination import PaginatedResult, PaginationParams
from src.infraestructura.persistencia.database import DatabaseManager


class RepositorioContratoMandatoSQLite:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def crear(self, contrato: ContratoMandato, usuario: str) -> ContratoMandato:
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        placeholder = self.db.get_placeholder()

        cursor.execute(
            f"""
        INSERT INTO CONTRATOS_MANDATOS (
            ID_PROPIEDAD, ID_PROPIETARIO, ID_ASESOR,
            FECHA_INICIO_CONTRATO_M, FECHA_FIN_CONTRATO_M, DURACION_CONTRATO_M,
            CANON_MANDATO, COMISION_PORCENTAJE_CONTRATO_M, IVA_CONTRATO_M,
            ESTADO_CONTRATO_M, ALERTA_VENCIMINETO_CONTRATO_M, FECHA_RENOVACION_CONTRATO_M,
            CREATED_BY, UPDATED_BY
        ) VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
        """,
            (
                contrato.id_propiedad,
                contrato.id_propietario,
                contrato.id_asesor,
                contrato.fecha_inicio_contrato_m,
                contrato.fecha_fin_contrato_m,
                contrato.duracion_contrato_m,
                contrato.canon_mandato,
                contrato.comision_porcentaje_contrato_m,
                contrato.iva_contrato_m,
                contrato.estado_contrato_m,
                contrato.alerta_vencimiento_contrato_m,
                contrato.fecha_renovacion_contrato_m,
                usuario,
                usuario,
            ),
        )

        conn.commit()
        contrato.id_contrato_m = self.db.get_last_insert_id(
            cursor, "CONTRATOS_MANDATOS", "ID_CONTRATO_M"
        )
        return contrato

    def obtener_por_id(self, id_contrato: int) -> Optional[ContratoMandato]:
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        placeholder = self.db.get_placeholder()
        cursor.execute(
            f"SELECT * FROM CONTRATOS_MANDATOS WHERE ID_CONTRATO_M = {placeholder}", (id_contrato,)
        )
        row = cursor.fetchone()
        return self._row_to_entity(row) if row else None

    def obtener_activo_por_propiedad(self, id_propiedad: int) -> Optional[ContratoMandato]:
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        placeholder = self.db.get_placeholder()
        cursor.execute(
            f"""
        SELECT * FROM CONTRATOS_MANDATOS 
        WHERE ID_PROPIEDAD = {placeholder} AND ESTADO_CONTRATO_M = 'Activo'
        """,
            (id_propiedad,),
        )
        row = cursor.fetchone()
        return self._row_to_entity(row) if row else None

    def listar_todos(self) -> List[ContratoMandato]:
        """Lista todos los contratos de mandato."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        self.db.get_placeholder()

        cursor.execute("SELECT * FROM CONTRATOS_MANDATOS ORDER BY ID_CONTRATO_M DESC")

        return [self._row_to_entity(row) for row in cursor.fetchall()]

    def listar_paginado(
        self,
        page: int = 1,
        page_size: int = 25,
        estado: Optional[str] = None,
        busqueda: Optional[str] = None,
        id_asesor: Optional[str] = None,
    ) -> PaginatedResult:
        """Lista contratos de mandato con paginación y filtros."""
        params = PaginationParams(page=page, page_size=page_size)

        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            placeholder = self.db.get_placeholder()

            base_from = """
                FROM CONTRATOS_MANDATOS cm
                JOIN PROPIEDADES p ON cm.ID_PROPIEDAD = p.ID_PROPIEDAD
                JOIN PROPIETARIOS prop ON cm.ID_PROPIETARIO = prop.ID_PROPIETARIO
                JOIN PERSONAS per ON prop.ID_PERSONA = per.ID_PERSONA
            """

            conditions = []
            query_params = []

            if estado and estado != "Todos":
                if estado == "Activo":
                    conditions.append("cm.ESTADO_CONTRATO_M = 'Activo'")
                elif estado == "Cancelado":
                    conditions.append("cm.ESTADO_CONTRATO_M != 'Activo'")
                else:
                    conditions.append(f"cm.ESTADO_CONTRATO_M = {placeholder}")
                    query_params.append(estado)

            if busqueda:
                conditions.append(
                    f"(p.DIRECCION_PROPIEDAD LIKE {placeholder} OR "
                    f"per.NOMBRE_COMPLETO LIKE {placeholder} OR "
                    f"per.NUMERO_DOCUMENTO LIKE {placeholder})"
                )
                term = f"%{busqueda}%"
                query_params.extend([term, term, term])

            if id_asesor:
                conditions.append(f"cm.ID_ASESOR = {placeholder}")
                query_params.append(int(id_asesor))

            where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""

            # 1. Count
            count_query = f"SELECT COUNT(*) as TOTAL {base_from} {where_clause}"
            cursor.execute(count_query, query_params)
            total = cursor.fetchone()["TOTAL"]

            # 2. Data
            data_query = f"""
                SELECT 
                    cm.ID_CONTRATO_M,
                    cm.ESTADO_CONTRATO_M,
                    cm.CANON_MANDATO,
                    cm.FECHA_INICIO_CONTRATO_M,
                    cm.FECHA_FIN_CONTRATO_M,
                    p.DIRECCION_PROPIEDAD,
                    p.TIPO_PROPIEDAD,
                    per.NOMBRE_COMPLETO as PROPIETARIO,
                    per.NUMERO_DOCUMENTO
                {base_from}
                {where_clause}
                ORDER BY cm.ID_CONTRATO_M DESC
                LIMIT {placeholder} OFFSET {placeholder}
            """

            cursor.execute(data_query, query_params + [params.page_size, params.offset])

            items = [
                {
                    "id": row["ID_CONTRATO_M"],
                    "estado": row["ESTADO_CONTRATO_M"],
                    "canon": row["CANON_MANDATO"],
                    "fecha_inicio": row["FECHA_INICIO_CONTRATO_M"],
                    "fecha_fin": row["FECHA_FIN_CONTRATO_M"],
                    "propiedad": row["DIRECCION_PROPIEDAD"],
                    "tipo_propiedad": row["TIPO_PROPIEDAD"],
                    "propietario": row["PROPIETARIO"],
                    "documento_propietario": row["NUMERO_DOCUMENTO"],
                }
                for row in cursor.fetchall()
            ]

            return PaginatedResult(
                items=items, total=total, page=params.page, page_size=params.page_size
            )

    def actualizar(self, contrato: ContratoMandato, usuario: str) -> None:
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        placeholder = self.db.get_placeholder()

        cursor.execute(
            f"""
        UPDATE CONTRATOS_MANDATOS SET
            ID_PROPIEDAD = {placeholder},
            ID_PROPIETARIO = {placeholder},
            ID_ASESOR = {placeholder},
            FECHA_INICIO_CONTRATO_M = {placeholder},
            FECHA_FIN_CONTRATO_M = {placeholder},
            DURACION_CONTRATO_M = {placeholder},
            CANON_MANDATO = {placeholder},
            COMISION_PORCENTAJE_CONTRATO_M = {placeholder},
            IVA_CONTRATO_M = {placeholder},
            ESTADO_CONTRATO_M = {placeholder},
            MOTIVO_CANCELACION = {placeholder},
            ALERTA_VENCIMINETO_CONTRATO_M = {placeholder},
            FECHA_RENOVACION_CONTRATO_M = {placeholder},
            UPDATED_AT = {placeholder},
            UPDATED_BY = {placeholder}
        WHERE ID_CONTRATO_M = {placeholder}
        """,
            (
                contrato.id_propiedad,
                contrato.id_propietario,
                contrato.id_asesor,
                contrato.fecha_inicio_contrato_m,
                contrato.fecha_fin_contrato_m,
                contrato.duracion_contrato_m,
                contrato.canon_mandato,
                contrato.comision_porcentaje_contrato_m,
                contrato.iva_contrato_m,
                contrato.estado_contrato_m,
                contrato.motivo_cancelacion,
                contrato.alerta_vencimiento_contrato_m,
                contrato.fecha_renovacion_contrato_m,
                datetime.now().replace(microsecond=0).isoformat(),
                usuario,
                contrato.id_contrato_m,
            ),
        )

        conn.commit()

    def _row_to_entity(self, row) -> ContratoMandato:
        if row is None:
            return None

        if hasattr(row, "keys"):
            row_dict = dict(row)
        else:
            row_dict = row

        return ContratoMandato(
            id_contrato_m=(row_dict.get("id_contrato_m") or row_dict.get("ID_CONTRATO_M")),
            id_propiedad=(row_dict.get("id_propiedad") or row_dict.get("ID_PROPIEDAD")),
            id_propietario=(row_dict.get("id_propietario") or row_dict.get("ID_PROPIETARIO")),
            id_asesor=(row_dict.get("id_asesor") or row_dict.get("ID_ASESOR")),
            fecha_inicio_contrato_m=(
                row_dict.get("fecha_inicio_contrato_m") or row_dict.get("FECHA_INICIO_CONTRATO_M")
            ),
            fecha_fin_contrato_m=(
                row_dict.get("fecha_fin_contrato_m") or row_dict.get("FECHA_FIN_CONTRATO_M")
            ),
            duracion_contrato_m=(
                row_dict.get("duracion_contrato_m") or row_dict.get("DURACION_CONTRATO_M")
            ),
            canon_mandato=(row_dict.get("canon_mandato") or row_dict.get("CANON_MANDATO")),
            comision_porcentaje_contrato_m=(
                row_dict.get("comision_porcentaje_contrato_m")
                or row_dict.get("COMISION_PORCENTAJE_CONTRATO_M")
            ),
            iva_contrato_m=(row_dict.get("iva_contrato_m") or row_dict.get("IVA_CONTRATO_M")),
            estado_contrato_m=(
                row_dict.get("estado_contrato_m") or row_dict.get("ESTADO_CONTRATO_M")
            ),
            motivo_cancelacion=(
                row_dict.get("motivo_cancelacion") or row_dict.get("MOTIVO_CANCELACION")
            ),
            # Typo in DB column name potentially? ALERTA_VENCIMINETO vs ALERTA_VENCIMIENTO
            # The original code had ALERTA_VENCIMINETO_CONTRATO_M in SQL insert/update and map.
            # We preserve it.
            alerta_vencimiento_contrato_m=(
                row_dict.get("alerta_vencimineto_contrato_m")
                or row_dict.get("ALERTA_VENCIMINETO_CONTRATO_M")
            ),
            fecha_renovacion_contrato_m=(
                row_dict.get("fecha_renovacion_contrato_m")
                or row_dict.get("FECHA_RENOVACION_CONTRATO_M")
            ),
            created_at=(row_dict.get("created_at") or row_dict.get("CREATED_AT")),
            created_by=(row_dict.get("created_by") or row_dict.get("CREATED_BY")),
            updated_at=(row_dict.get("updated_at") or row_dict.get("UPDATED_AT")),
            updated_by=(row_dict.get("updated_by") or row_dict.get("UPDATED_BY")),
        )
