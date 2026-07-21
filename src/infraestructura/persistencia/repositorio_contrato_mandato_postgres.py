"""
Repositorio Postgres: ContratoMandato
"""

from datetime import datetime
from typing import List, Optional

from src.dominio.entidades.contrato_mandato import ContratoMandato
from src.dominio.modelos.pagination import PaginatedResult, PaginationParams
from src.infraestructura.persistencia.database import DatabaseManager


class RepositorioContratoMandatoPostgres:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def crear(self, contrato: ContratoMandato, usuario: str) -> ContratoMandato:
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()
        query = """
            INSERT INTO CONTRATOS_MANDATOS (
                ID_PROPIEDAD, ID_PROPIETARIO, ID_ASESOR,
                FECHA_INICIO_CONTRATO_M, FECHA_FIN_CONTRATO_M,
                DURACION_CONTRATO_M, CANON_MANDATO,
                COMISION_PORCENTAJE_CONTRATO_M, IVA_CONTRATO_M,
                ESTADO_CONTRATO_M, ALERTA_VENCIMIENTO_CONTRATO_M,
                FECHA_RENOVACION_CONTRATO_M, FECHA_PAGO, GRUPO_OPERATIVO,
                BANCO_PROPIETARIO, NUMERO_CUENTA_PROPIETARIO, TIPO_CUENTA,
                CONSIGNATARIO, DOCUMENTO_CONSIGNATARIO,
                ENLACE_VIDEO,
                CREATED_BY, UPDATED_BY
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            ) RETURNING ID_CONTRATO_M
        """
        valores = (
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
            contrato.fecha_pago,
            contrato.grupo_operativo,
            contrato.banco_propietario,
            contrato.numero_cuenta_propietario,
            contrato.tipo_cuenta,
            contrato.consignatario,
            contrato.documento_consignatario,
            contrato.enlace_video,
            usuario,
            usuario,
        )
        cursor.execute(query, valores)

        row = cursor.fetchone()

        if row:
            if hasattr(row, "values"):
                contrato.id_contrato_m = list(row.values())[0]
            elif isinstance(row, dict):
                contrato.id_contrato_m = list(row.values())[0]
            else:
                contrato.id_contrato_m = row[0]

        return contrato

    def obtener_por_id(self, id_contrato: int) -> Optional[ContratoMandato]:
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        placeholder = self.db.get_placeholder()
        cursor.execute(
            f"SELECT * FROM CONTRATOS_MANDATOS WHERE ID_CONTRATO_M = {placeholder}",
            (id_contrato,),
        )
        row = cursor.fetchone()
        return self._row_to_entity(row) if row else None

    def obtener_activo_por_propiedad(
        self, id_propiedad: int
    ) -> Optional[ContratoMandato]:
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        placeholder = self.db.get_placeholder()
        cursor.execute(
            f"""
        SELECT * FROM CONTRATOS_MANDATOS 
        WHERE ID_PROPIEDAD = {placeholder} AND ESTADO_CONTRATO_M = 'ACTIVO'
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
        sin_arrendamiento: bool = False,
        sort_by: str = "ID_CONTRATO_M",
        sort_order: str = "desc",
    ) -> PaginatedResult:
        """Lista contratos de mandato con paginación y filtros.

        Args:
            page: Número de página.
            page_size: Tamaño de página.
            estado: Filtro de estado (ACTIVO, Cancelado, Todos).
            busqueda: Texto de búsqueda libre.
            id_asesor: ID del asesor para filtrar.
            sin_arrendamiento: Si True, retorna solo mandatos cuya propiedad
                NO tiene un contrato de arrendamiento ACTIVO.
            sort_by: Columna para ordenar.
            sort_order: Orden (asc/desc).
        """
        params = PaginationParams(page=page, page_size=page_size)

        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            placeholder = self.db.get_placeholder()

            base_from = """
                FROM CONTRATOS_MANDATOS cm
                LEFT JOIN PROPIEDADES p ON cm.ID_PROPIEDAD = p.ID_PROPIEDAD
                LEFT JOIN PROPIETARIOS prop ON cm.ID_PROPIETARIO = prop.ID_PROPIETARIO
                LEFT JOIN PERSONAS per ON prop.ID_PERSONA = per.ID_PERSONA
                LEFT JOIN ASESORES am ON cm.ID_ASESOR = am.ID_ASESOR
                LEFT JOIN PERSONAS per_asesor ON am.ID_PERSONA = per_asesor.ID_PERSONA
            """

            conditions = []
            query_params = []

            if estado and estado != "Todos":
                conditions.append(f"cm.ESTADO_CONTRATO_M = {placeholder}")
                query_params.append(estado)

            if busqueda:
                cols = [
                    "COALESCE(p.DIRECCION_PROPIEDAD, '')",
                    "COALESCE(per.NOMBRE_COMPLETO, '')",
                    "COALESCE(per.NUMERO_DOCUMENTO, '')",
                ]
                cond = self.db.get_search_condition(cols)
                conditions.append(f"({cond})")

                term_norm = f"%{self.db.normalize_search_term(busqueda)}%"
                query_params.extend([term_norm] * len(cols))

            if id_asesor:
                conditions.append(f"cm.ID_ASESOR = {placeholder}")
                query_params.append(int(id_asesor))

            if sin_arrendamiento:
                conditions.append("""NOT EXISTS (
                        SELECT 1 FROM CONTRATOS_ARRENDAMIENTOS ca
                        WHERE ca.ID_PROPIEDAD = cm.ID_PROPIEDAD
                          AND ca.ESTADO_CONTRATO_A = 'ACTIVO'
                    )""")

            where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""

            # Whitelist de columnas permitidas para ORDER BY
            SORT_COLUMNS = {
                "ID_CONTRATO_M": "cm.ID_CONTRATO_M",
                "FECHA_INICIO_CONTRATO_M": "cm.FECHA_INICIO_CONTRATO_M",
                "FECHA_FIN_CONTRATO_M": "cm.FECHA_FIN_CONTRATO_M",
                "CANON_MANDATO": "cm.CANON_MANDATO",
                "PROPIETARIO": "per.NOMBRE_COMPLETO",
                "DIRECCION": "p.DIRECCION_PROPIEDAD",
            }
            sort_column = SORT_COLUMNS.get(sort_by, "cm.ID_CONTRATO_M")
            sort_order_valid = (
                sort_order.lower() if sort_order.lower() in ("asc", "desc") else "desc"
            )

            # 1. Count
            count_query = f"SELECT COUNT(*) as TOTAL {base_from} {where_clause}"
            print(
                f"[SQL_DEBUG_MANDATOS] Conteo Query: {count_query} | Params: {query_params}"
            )
            cursor.execute(count_query, query_params)
            row = cursor.fetchone()
            total = 0
            if row:
                # Acceso robusto al total (soporta TOTAL, total o índice 0)
                try:
                    total = row["TOTAL"]
                except (KeyError, TypeError):
                    total = row.get("total") or list(row.values())[0] if row else 0

            print(f"[SQL_DEBUG_MANDATOS] Total encontrado: {total}")

            # 2. Data
            data_query = f"""
                SELECT
                    cm.ID_CONTRATO_M,
                    cm.ESTADO_CONTRATO_M,
                    cm.CANON_MANDATO,
                    cm.FECHA_INICIO_CONTRATO_M,
                    cm.FECHA_FIN_CONTRATO_M,
                    COALESCE(p.DIRECCION_PROPIEDAD, 'Propiedad no encontrada') as DIRECCION_PROPIEDAD,
                    COALESCE(p.MATRICULA_INMOBILIARIA, 'N/A') as MATRICULA_INMOBILIARIA,
                    COALESCE(p.TIPO_PROPIEDAD, 'N/A') as TIPO_PROPIEDAD,
                    COALESCE(p.CANON_ARRENDAMIENTO_ESTIMADO, 0) as CANON_ARRENDAMIENTO_ESTIMADO,
                    COALESCE(per.NOMBRE_COMPLETO, 'Propietario no encontrado') as PROPIETARIO,
                    COALESCE(per.NUMERO_DOCUMENTO, 'N/A') as NUMERO_DOCUMENTO,
                    per_asesor.NOMBRE_COMPLETO as ASESOR,
                    cm.FECHA_PAGO,
                    cm.GRUPO_OPERATIVO,
                    cm.CONSIGNATARIO,
                    cm.BANCO_PROPIETARIO,
                    cm.NUMERO_CUENTA_PROPIETARIO
                {base_from}
                {where_clause}
                ORDER BY {sort_column} {sort_order_valid}
                LIMIT {placeholder} OFFSET {placeholder}
            """

            data_params = query_params + [params.page_size, params.offset]
            print(
                f"[SQL_DEBUG_MANDATOS] Data Query: {data_query} | Params: {data_params}"
            )
            cursor.execute(data_query, data_params)
            rows = cursor.fetchall()
            print(f"[SQL_DEBUG_MANDATOS] Filas recuperadas: {len(rows)}")

            items = []
            for row in rows:
                # Helper para obtener valor insensible a mayúsculas
                def gv(k):
                    return row.get(k) or row.get(k.upper()) or row.get(k.lower())

                items.append(
                    {
                        "id_contrato": gv("ID_CONTRATO_M"),
                        "estado_contrato": gv("ESTADO_CONTRATO_M"),
                        "valor_canon": gv("CANON_MANDATO") or 0,
                        "valor_administracion": 0,
                        "fecha_inicio": gv("FECHA_INICIO_CONTRATO_M"),
                        "fecha_fin": gv("FECHA_FIN_CONTRATO_M"),
                        "propiedad_direccion": gv("DIRECCION_PROPIEDAD"),
                        "propiedad_matricula": gv("MATRICULA_INMOBILIARIA"),
                        "propiedad_tipo": gv("TIPO_PROPIEDAD"),
                        "propietario_nombre": gv("PROPIETARIO"),
                        "propietario_documento": gv("NUMERO_DOCUMENTO"),
                        "arrendatario_nombre": "N/A",
                        "arrendatario_documento": "N/A",
                        "habitante_nombre": "",
                        "asesor_nombre": gv("ASESOR") or "Sin asesor",
                        "fecha_pago": gv("FECHA_PAGO") or "",
                        "grupo_operativo": gv("GRUPO_OPERATIVO") or 0,
                        "consignatario": gv("CONSIGNATARIO"),
                        "banco_propietario": gv("BANCO_PROPIETARIO"),
                        "numero_cuenta_propietario": gv("NUMERO_CUENTA_PROPIETARIO"),
                    }
                )
            return PaginatedResult(
                items=items, total=total, page=params.page, page_size=params.page_size
            )

    def actualizar(self, contrato: ContratoMandato, usuario: str) -> bool:
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
            ALERTA_VENCIMIENTO_CONTRATO_M = {placeholder},
            FECHA_RENOVACION_CONTRATO_M = {placeholder},
            FECHA_PAGO = {placeholder},
            GRUPO_OPERATIVO = {placeholder},
            BANCO_PROPIETARIO = {placeholder},
            NUMERO_CUENTA_PROPIETARIO = {placeholder},
            TIPO_CUENTA = {placeholder},
            CONSIGNATARIO = {placeholder},
            DOCUMENTO_CONSIGNATARIO = {placeholder},
            ENLACE_VIDEO = {placeholder},
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
                contrato.fecha_pago,
                contrato.grupo_operativo,
                contrato.banco_propietario,
                contrato.numero_cuenta_propietario,
                contrato.tipo_cuenta,
                contrato.consignatario,
                contrato.documento_consignatario,
                contrato.enlace_video,
                datetime.now().replace(microsecond=0).isoformat(),
                usuario,
                contrato.id_contrato_m,
            ),
        )

        return cursor.rowcount > 0

    def _row_to_entity(self, row) -> ContratoMandato:
        if row is None:
            return None

        if hasattr(row, "keys"):
            row_dict = dict(row)
        else:
            row_dict = row

        return ContratoMandato(
            id_contrato_m=(
                row_dict.get("id_contrato_m") or row_dict.get("ID_CONTRATO_M")
            ),
            id_propiedad=(row_dict.get("id_propiedad") or row_dict.get("ID_PROPIEDAD")),
            id_propietario=(
                row_dict.get("id_propietario") or row_dict.get("ID_PROPIETARIO")
            ),
            id_asesor=(row_dict.get("id_asesor") or row_dict.get("ID_ASESOR")),
            fecha_inicio_contrato_m=(
                row_dict.get("fecha_inicio_contrato_m")
                or row_dict.get("FECHA_INICIO_CONTRATO_M")
            ),
            fecha_fin_contrato_m=(
                row_dict.get("fecha_fin_contrato_m")
                or row_dict.get("FECHA_FIN_CONTRATO_M")
            ),
            duracion_contrato_m=(
                row_dict.get("duracion_contrato_m")
                or row_dict.get("DURACION_CONTRATO_M")
            ),
            canon_mandato=(
                row_dict.get("canon_mandato") or row_dict.get("CANON_MANDATO")
            ),
            comision_porcentaje_contrato_m=(
                row_dict.get("comision_porcentaje_contrato_m")
                or row_dict.get("COMISION_PORCENTAJE_CONTRATO_M")
            ),
            iva_contrato_m=(
                row_dict.get("iva_contrato_m") or row_dict.get("IVA_CONTRATO_M")
            ),
            estado_contrato_m=(
                row_dict.get("estado_contrato_m") or row_dict.get("ESTADO_CONTRATO_M")
            ),
            motivo_cancelacion=(
                row_dict.get("motivo_cancelacion") or row_dict.get("MOTIVO_CANCELACION")
            ),
            alerta_vencimiento_contrato_m=(
                row_dict.get("alerta_vencimiento_contrato_m")
                or row_dict.get("ALERTA_VENCIMIENTO_CONTRATO_M")
            ),
            fecha_renovacion_contrato_m=(
                row_dict.get("fecha_renovacion_contrato_m")
                or row_dict.get("FECHA_RENOVACION_CONTRATO_M")
            ),
            fecha_pago=(row_dict.get("fecha_pago") or row_dict.get("FECHA_PAGO")),
            grupo_operativo=(
                row_dict.get("grupo_operativo") or row_dict.get("GRUPO_OPERATIVO") or 0
            ),
            banco_propietario=(
                row_dict.get("banco_propietario") or row_dict.get("BANCO_PROPIETARIO")
            ),
            numero_cuenta_propietario=(
                row_dict.get("numero_cuenta_propietario")
                or row_dict.get("NUMERO_CUENTA_PROPIETARIO")
            ),
            tipo_cuenta=(row_dict.get("tipo_cuenta") or row_dict.get("TIPO_CUENTA")),
            consignatario=(row_dict.get("consignatario") or row_dict.get("CONSIGNATARIO")),
            documento_consignatario=(row_dict.get("documento_consignatario") or row_dict.get("DOCUMENTO_CONSIGNATARIO")),
            enlace_video=(row_dict.get("enlace_video") or row_dict.get("ENLACE_VIDEO")),
            created_at=str(row_dict.get("created_at", "")),
            created_by=(row_dict.get("created_by") or row_dict.get("CREATED_BY")),
            updated_at=(row_dict.get("updated_at") or row_dict.get("UPDATED_AT")),
            updated_by=(row_dict.get("updated_by") or row_dict.get("UPDATED_BY")),
        )
