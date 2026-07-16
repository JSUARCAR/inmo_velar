"""
Repositorio Postgres: ContratoArrendamiento
"""

from datetime import datetime
from typing import Dict, List, Optional

from src.dominio.entidades.contrato_arrendamiento import ContratoArrendamiento
from src.dominio.constantes.estados_contrato import EstadoContrato
from src.dominio.modelos.pagination import PaginatedResult, PaginationParams
from src.infraestructura.persistencia.database import DatabaseManager


class RepositorioContratoArrendamientoPostgres:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def crear(
        self, contrato: ContratoArrendamiento, usuario_sistema: str
    ) -> ContratoArrendamiento:
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()

        query = """
                INSERT INTO CONTRATOS_ARRENDAMIENTOS (
                    ID_PROPIEDAD, ID_ARRENDATARIO, ID_CODEUDOR,
                    FECHA_INICIO_CONTRATO_A, FECHA_FIN_CONTRATO_A,
                    DURACION_CONTRATO_A, CANON_ARRENDAMIENTO,
                    DEPOSITO, FECHA_PAGO, GRUPO_OPERATIVO,
                    ESTADO_CONTRATO_A, ALERTA_VENCIMIENTO_CONTRATO_A,
                    ALERTA_IPC, FECHA_RENOVACION_CONTRATO_A,
                    FECHA_INCREMENTO_IPC, FECHA_ULTIMO_INCREMENTO_IPC,
                    ENLACE_VIDEO, RESPONSABLE_DEPOSITO_ID,
                    CREATED_BY, UPDATED_BY
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                ) RETURNING ID_CONTRATO_A
            """
        valores = (
            contrato.id_propiedad,
            contrato.id_arrendatario,
            contrato.id_codeudor,
            contrato.fecha_inicio_contrato_a,
            contrato.fecha_fin_contrato_a,
            contrato.duracion_contrato_a,
            contrato.canon_arrendamiento,
            contrato.deposito,
            contrato.fecha_pago,
            contrato.grupo_operativo,
            (
                contrato.estado_contrato_a.value
                if hasattr(contrato.estado_contrato_a, "value")
                else contrato.estado_contrato_a
            ),
            contrato.alerta_vencimiento_contrato_a,
            contrato.alerta_ipc,
            contrato.fecha_renovacion_contrato_a,
            contrato.fecha_incremento_ipc,
            contrato.fecha_ultimo_incremento_ipc,
            contrato.enlace_video,
            contrato.responsable_deposito_id,
            usuario_sistema,
            usuario_sistema,
        )

        cursor.execute(query, valores)

        row = cursor.fetchone()

        if row:
            if hasattr(row, "values"):
                contrato.id_contrato_a = list(row.values())[0]
            elif isinstance(row, dict):
                contrato.id_contrato_a = list(row.values())[0]
            else:
                contrato.id_contrato_a = row[0]

        return contrato

    def obtener_por_id(self, id_contrato: int) -> Optional[ContratoArrendamiento]:
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        placeholder = self.db.get_placeholder()
        cursor.execute(
            f"SELECT * FROM CONTRATOS_ARRENDAMIENTOS WHERE ID_CONTRATO_A = {placeholder}",
            (id_contrato,),
        )
        row = cursor.fetchone()
        return self._row_to_entity(row) if row else None

    def obtener_activo_por_propiedad(
        self, id_propiedad: int
    ) -> Optional[ContratoArrendamiento]:
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        placeholder = self.db.get_placeholder()
        cursor.execute(
            f"""
        SELECT * FROM CONTRATOS_ARRENDAMIENTOS 
        WHERE ID_PROPIEDAD = {placeholder} AND ESTADO_CONTRATO_A = 'ACTIVO'
        """,
            (id_propiedad,),
        )
        row = cursor.fetchone()
        return self._row_to_entity(row) if row else None

    def obtener_activos_por_asesor(self, id_asesor: int) -> List[ContratoArrendamiento]:
        """
        Obtiene los contratos de arrendamiento ACTIVOs asociados a un asesor ACTIVO.
        Realiza JOIN con CONTRATOS_MANDATOS, ARRENDATARIOS y SEGUROS.
        """
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        placeholder = self.db.get_placeholder()

        query = f"""
            SELECT DISTINCT ON (ca.ID_CONTRATO_A)
                   ca.*, cm.COMISION_PORCENTAJE_CONTRATO_M, cm.ID_CONTRATO_M,
                   p.DIRECCION_PROPIEDAD,
                   arr.ID_SEGURO, seg.NOMBRE_SEGURO, seg.PORCENTAJE_SEGURO
            FROM CONTRATOS_ARRENDAMIENTOS ca
            JOIN PROPIEDADES p ON ca.ID_PROPIEDAD = p.ID_PROPIEDAD
            JOIN CONTRATOS_MANDATOS cm ON ca.ID_PROPIEDAD = cm.ID_PROPIEDAD
                AND cm.ESTADO_CONTRATO_M = 'ACTIVO'
                AND cm.ID_ASESOR = {placeholder}
            LEFT JOIN ARRENDATARIOS arr ON ca.ID_ARRENDATARIO = arr.ID_ARRENDATARIO
            LEFT JOIN SEGUROS seg ON arr.ID_SEGURO = seg.ID_SEGURO
            WHERE ca.ESTADO_CONTRATO_A = 'ACTIVO'
            ORDER BY ca.ID_CONTRATO_A, cm.ID_CONTRATO_M DESC
        """

        cursor.execute(query, (id_asesor,))
        rows = cursor.fetchall()

        return [self._row_to_entity(row) for row in rows]

    def obtener_activos_todos_agrupados(self) -> Dict[int, List[ContratoArrendamiento]]:
        """
        Obtiene TODOS los contratos ACTIVOs de TODOS los asesores,
        agrupados por ID_ASESOR en un diccionario.
        OPTIMIZACIÓN ÉLITE: Resuelve el problema N+1 queries.
        """
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)

        query = """
            SELECT DISTINCT ON (ca.ID_CONTRATO_A)
                   ca.*, cm.ID_ASESOR as asesor_id_agrupacion, 
                   cm.COMISION_PORCENTAJE_CONTRATO_M, cm.ID_CONTRATO_M,
                   p.DIRECCION_PROPIEDAD,
                   arr.ID_SEGURO, seg.NOMBRE_SEGURO, seg.PORCENTAJE_SEGURO
            FROM CONTRATOS_ARRENDAMIENTOS ca
            JOIN PROPIEDADES p ON ca.ID_PROPIEDAD = p.ID_PROPIEDAD
            JOIN CONTRATOS_MANDATOS cm ON ca.ID_PROPIEDAD = cm.ID_PROPIEDAD
                AND cm.ESTADO_CONTRATO_M = 'ACTIVO'
                AND cm.ID_ASESOR IS NOT NULL
            LEFT JOIN ARRENDATARIOS arr ON ca.ID_ARRENDATARIO = arr.ID_ARRENDATARIO
            LEFT JOIN SEGUROS seg ON arr.ID_SEGURO = seg.ID_SEGURO
            WHERE ca.ESTADO_CONTRATO_A = 'ACTIVO'
            ORDER BY ca.ID_CONTRATO_A, cm.ID_CONTRATO_M DESC
        """

        cursor.execute(query)
        rows = cursor.fetchall()

        agrupados = {}
        for row in rows:
            row_dict = dict(row)
            id_asesor = row_dict.get("asesor_id_agrupacion") or row_dict.get(
                "ASESOR_ID_AGRUPACION"
            )

            entidad = self._row_to_entity(row)
            if id_asesor not in agrupados:
                agrupados[id_asesor] = []
            agrupados[id_asesor].append(entidad)

        return agrupados

    def obtener_detalle_contratos_asesor(self, id_asesor: int) -> List[dict]:
        """
        Obtiene detalles de contratos ACTIVOs (incluyendo dirección) para UI.
        Retorna lista de diccionarios.
        """
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        placeholder = self.db.get_placeholder()

        query = f"""
            SELECT DISTINCT ON (ca.ID_CONTRATO_A)
                ca.ID_CONTRATO_A,
                ca.CANON_ARRENDAMIENTO,
                ca.FECHA_INICIO_CONTRATO_A,
                p.DIRECCION_PROPIEDAD,
                p.MATRICULA_INMOBILIARIA,
                cm.COMISION_PORCENTAJE_CONTRATO_M
            FROM CONTRATOS_ARRENDAMIENTOS ca
            JOIN PROPIEDADES p ON ca.ID_PROPIEDAD = p.ID_PROPIEDAD
            JOIN CONTRATOS_MANDATOS cm ON ca.ID_PROPIEDAD = cm.ID_PROPIEDAD
                AND cm.ESTADO_CONTRATO_M = 'ACTIVO'
                AND cm.ID_ASESOR = {placeholder}
            WHERE ca.ESTADO_CONTRATO_A = 'ACTIVO'
            ORDER BY ca.ID_CONTRATO_A, cm.ID_CONTRATO_M DESC
        """

        cursor.execute(query, (id_asesor,))
        return [dict(row) for row in cursor.fetchall()]

    def listar_todos(self) -> List[ContratoArrendamiento]:
        """Lista todos los contratos."""
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        self.db.get_placeholder()

        cursor.execute(
            "SELECT * FROM CONTRATOS_ARRENDAMIENTOS ORDER BY ID_CONTRATO_A DESC"
        )

        return [self._row_to_entity(row) for row in cursor.fetchall()]

    def listar_paginado(
        self,
        page: int = 1,
        page_size: int = 25,
        estado: Optional[str] = None,
        busqueda: Optional[str] = None,
        id_asesor: Optional[str] = None,
        sort_by: str = "ID_CONTRATO_A",
        sort_order: str = "desc",
    ) -> PaginatedResult:
        """Lista contratos de arrendamiento con paginación y filtros."""
        params = PaginationParams(page=page, page_size=page_size)

        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            placeholder = self.db.get_placeholder()

            base_from = """
                FROM CONTRATOS_ARRENDAMIENTOS ca
                JOIN PROPIEDADES p ON ca.ID_PROPIEDAD = p.ID_PROPIEDAD
                JOIN ARRENDATARIOS arr ON ca.ID_ARRENDATARIO = arr.ID_ARRENDATARIO
                JOIN PERSONAS per ON arr.ID_PERSONA = per.ID_PERSONA
                LEFT JOIN CONTRATOS_MANDATOS cm ON ca.ID_PROPIEDAD = cm.ID_PROPIEDAD AND cm.ESTADO_CONTRATO_M = 'ACTIVO'
                LEFT JOIN ASESORES am ON cm.ID_ASESOR = am.ID_ASESOR
                LEFT JOIN PERSONAS per_asesor ON am.ID_PERSONA = per_asesor.ID_PERSONA
            """

            conditions = []
            query_params = []

            if estado and estado != "Todos":
                conditions.append(f"ca.ESTADO_CONTRATO_A = {placeholder}")
                query_params.append(estado)

            if busqueda:
                cols = [
                    "p.DIRECCION_PROPIEDAD",
                    "per.NOMBRE_COMPLETO",
                    "per.NUMERO_DOCUMENTO",
                ]
                cond = self.db.get_search_condition(cols)
                conditions.append(f"({cond})")

                term_norm = f"%{self.db.normalize_search_term(busqueda)}%"
                query_params.extend([term_norm] * len(cols))

            if id_asesor:
                # Arrendamientos no tienen ID_ASESOR directo, se filtra por el mandato asociado
                conditions.append(
                    f"EXISTS (SELECT 1 FROM CONTRATOS_MANDATOS cm WHERE cm.ID_PROPIEDAD = ca.ID_PROPIEDAD AND cm.ID_ASESOR = {placeholder})"
                )
                query_params.append(int(id_asesor))

            where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""

            # Whitelist de columnas permitidas para ORDER BY
            SORT_COLUMNS = {
                "ID_CONTRATO_A": "ca.ID_CONTRATO_A",
                "FECHA_INICIO_CONTRATO_A": "ca.FECHA_INICIO_CONTRATO_A",
                "FECHA_FIN_CONTRATO_A": "ca.FECHA_FIN_CONTRATO_A",
                "CANON_ARRENDAMIENTO": "ca.CANON_ARRENDAMIENTO",
                "ARRENDATARIO": "per.NOMBRE_COMPLETO",
                "DIRECCION": "p.DIRECCION_PROPIEDAD",
                "ASESOR": "per_asesor.NOMBRE_COMPLETO",
                "PROPIETARIO": "prop_per.NOMBRE_COMPLETO",
            }
            sort_column = SORT_COLUMNS.get(sort_by, "ca.ID_CONTRATO_A")
            sort_order_valid = (
                sort_order.lower() if sort_order.lower() in ("asc", "desc") else "desc"
            )

            # 1. Count
            count_query = f"SELECT COUNT(*) as TOTAL {base_from} {where_clause}"
            print(
                f"[SQL_DEBUG_ARRENDAMIENTOS] Conteo Query: {count_query} | Params: {query_params}"
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

            print(f"[SQL_DEBUG_ARRENDAMIENTOS] Total encontrado: {total}")

            # 2. Data
            data_query = f"""
                SELECT 
                    ca.ID_CONTRATO_A,
                    ca.ESTADO_CONTRATO_A,
                    ca.CANON_ARRENDAMIENTO,
                    ca.FECHA_INICIO_CONTRATO_A,
                    ca.FECHA_FIN_CONTRATO_A,
                    p.DIRECCION_PROPIEDAD,
                    p.MATRICULA_INMOBILIARIA,
                    p.TIPO_PROPIEDAD,
                    per.NOMBRE_COMPLETO as ARRENDATARIO,
                    per.NUMERO_DOCUMENTO,
                    per_asesor.NOMBRE_COMPLETO as ASESOR,
                    arr.NOMBRE_HABITANTE as HABITANTE,
                    COALESCE(prop_per.NOMBRE_COMPLETO, 'N/A') as PROPIETARIO,
                    COALESCE(prop_per.NUMERO_DOCUMENTO, 'N/A') as PROPIETARIO_DOC,
                    ca.FECHA_PAGO,
                    ca.GRUPO_OPERATIVO
                {base_from}
                LEFT JOIN PROPIETARIOS prop_ent ON cm.ID_PROPIETARIO = prop_ent.ID_PROPIETARIO
                LEFT JOIN PERSONAS prop_per ON prop_ent.ID_PERSONA = prop_per.ID_PERSONA
                {where_clause}
                ORDER BY {sort_column} {sort_order_valid}
                LIMIT {placeholder} OFFSET {placeholder}
            """

            data_params = query_params + [params.page_size, params.offset]
            print(
                f"[SQL_DEBUG_ARRENDAMIENTOS] Data Query: {data_query} | Params: {data_params}"
            )
            cursor.execute(data_query, data_params)
            rows = cursor.fetchall()
            print(f"[SQL_DEBUG_ARRENDAMIENTOS] Filas recuperadas: {len(rows)}")

            items = []
            for row in rows:
                # Helper para obtener valor insensible a mayúsculas
                def gv(k):
                    return row.get(k) or row.get(k.upper()) or row.get(k.lower())

                items.append(
                    {
                        "id_contrato": gv("ID_CONTRATO_A"),
                        "estado_contrato": gv("ESTADO_CONTRATO_A"),
                        "valor_canon": gv("CANON_ARRENDAMIENTO"),
                        "valor_administracion": 0,
                        "fecha_inicio": gv("FECHA_INICIO_CONTRATO_A"),
                        "fecha_fin": gv("FECHA_FIN_CONTRATO_A"),
                        "propiedad_direccion": gv("DIRECCION_PROPIEDAD"),
                        "propiedad_matricula": gv("MATRICULA_INMOBILIARIA"),
                        "propiedad_tipo": gv("TIPO_PROPIEDAD"),
                        "arrendatario_nombre": gv("ARRENDATARIO"),
                        "arrendatario_documento": gv("NUMERO_DOCUMENTO"),
                        "propietario_nombre": gv("PROPIETARIO"),
                        "propietario_documento": gv("PROPIETARIO_DOC"),
                        "habitante_nombre": gv("HABITANTE") or "",
                        "asesor_nombre": gv("ASESOR") or "Sin asesor",
                        "fecha_pago": gv("FECHA_PAGO") or "",
                        "grupo_operativo": gv("GRUPO_OPERATIVO") or 0,
                    }
                )

            return PaginatedResult(
                items=items, total=total, page=params.page, page_size=params.page_size
            )

    def actualizar(self, contrato: ContratoArrendamiento, usuario_sistema: str) -> bool:
        conn = self.db.obtener_conexion()
        cursor = conn.cursor()

        query = """
                UPDATE CONTRATOS_ARRENDAMIENTOS SET
                    ID_PROPIEDAD = %s,
                    ID_ARRENDATARIO = %s,
                    ID_CODEUDOR = %s,
                    FECHA_INICIO_CONTRATO_A = %s,
                    FECHA_FIN_CONTRATO_A = %s,
                    DURACION_CONTRATO_A = %s,
                    CANON_ARRENDAMIENTO = %s,
                    DEPOSITO = %s,
                    FECHA_PAGO = %s,
                    GRUPO_OPERATIVO = %s,
                    ESTADO_CONTRATO_A = %s,
                    ALERTA_VENCIMIENTO_CONTRATO_A = %s,
                    ALERTA_IPC = %s,
                    FECHA_RENOVACION_CONTRATO_A = %s,
                    FECHA_INCREMENTO_IPC = %s,
                    FECHA_ULTIMO_INCREMENTO_IPC = %s,
                    MOTIVO_CANCELACION = %s,
                    ENLACE_VIDEO = %s,
                    RESPONSABLE_DEPOSITO_ID = %s,
                    UPDATED_BY = %s,
                    UPDATED_AT = CURRENT_TIMESTAMP
                WHERE ID_CONTRATO_A = %s
            """
        valores = (
            contrato.id_propiedad,
            contrato.id_arrendatario,
            contrato.id_codeudor,
            contrato.fecha_inicio_contrato_a,
            contrato.fecha_fin_contrato_a,
            contrato.duracion_contrato_a,
            contrato.canon_arrendamiento,
            contrato.deposito,
            contrato.fecha_pago,
            contrato.grupo_operativo,
            (
                contrato.estado_contrato_a.value
                if hasattr(contrato.estado_contrato_a, "value")
                else contrato.estado_contrato_a
            ),
            contrato.alerta_vencimiento_contrato_a,
            contrato.alerta_ipc,
            contrato.fecha_renovacion_contrato_a,
            contrato.fecha_incremento_ipc,
            contrato.fecha_ultimo_incremento_ipc,
            contrato.motivo_cancelacion,
            contrato.enlace_video,
            contrato.responsable_deposito_id,
            usuario_sistema,
            contrato.id_contrato_a,
        )

        cursor.execute(query, valores)

        return cursor.rowcount > 0

    def _row_to_entity(self, row) -> ContratoArrendamiento:
        if row is None:
            return None

        if hasattr(row, "keys"):
            row_dict = dict(row)
        else:
            row_dict = row

        # Helper para manejar nombres de columnas (Automatización LIQ-AUTO-001)
        def gv(k):
            return row_dict.get(k) or row_dict.get(k.upper()) or row_dict.get(k.lower())

        contrato = ContratoArrendamiento(
            id_contrato_a=(
                row_dict.get("id_contrato_a") or row_dict.get("ID_CONTRATO_A")
            ),
            id_propiedad=(row_dict.get("id_propiedad") or row_dict.get("ID_PROPIEDAD")),
            id_arrendatario=(
                row_dict.get("id_arrendatario") or row_dict.get("ID_ARRENDATARIO")
            ),
            id_codeudor=(row_dict.get("id_codeudor") or row_dict.get("ID_CODEUDOR")),
            fecha_inicio_contrato_a=(
                row_dict.get("fecha_inicio_contrato_a")
                or row_dict.get("FECHA_INICIO_CONTRATO_A")
            ),
            fecha_fin_contrato_a=(
                row_dict.get("fecha_fin_contrato_a")
                or row_dict.get("FECHA_FIN_CONTRATO_A")
            ),
            duracion_contrato_a=(
                row_dict.get("duracion_contrato_a")
                or row_dict.get("DURACION_CONTRATO_A")
            ),
            canon_arrendamiento=(
                row_dict.get("canon_arrendamiento")
                or row_dict.get("CANON_ARRENDAMIENTO")
            ),
            deposito=(row_dict.get("deposito") or row_dict.get("DEPOSITO")),
            fecha_pago=(row_dict.get("fecha_pago") or row_dict.get("FECHA_PAGO")),
            estado_contrato_a=self._map_estado(
                row_dict.get("estado_contrato_a") or row_dict.get("ESTADO_CONTRATO_A")
            ),
            motivo_cancelacion=(
                row_dict.get("motivo_cancelacion") or row_dict.get("MOTIVO_CANCELACION")
            ),
            alerta_vencimiento_contrato_a=(
                row_dict.get("alerta_vencimiento_contrato_a")
                or row_dict.get("ALERTA_VENCIMIENTO_CONTRATO_A")
            ),
            alerta_ipc=(row_dict.get("alerta_ipc") or row_dict.get("ALERTA_IPC")),
            fecha_renovacion_contrato_a=(
                row_dict.get("fecha_renovacion_contrato_a")
                or row_dict.get("FECHA_RENOVACION_CONTRATO_A")
            ),
            fecha_incremento_ipc=(
                row_dict.get("fecha_incremento_ipc")
                or row_dict.get("FECHA_INCREMENTO_IPC")
            ),
            fecha_ultimo_incremento_ipc=str(
                row_dict.get("fecha_ultimo_incremento_ipc", "")
            ),
            enlace_video=row_dict.get("enlace_video"),
            responsable_deposito_id=row_dict.get("responsable_deposito_id") or row_dict.get("RESPONSABLE_DEPOSITO_ID"),
            created_at=str(row_dict.get("created_at") or row_dict.get("CREATED_AT", "")),
            created_by=(row_dict.get("created_by") or row_dict.get("CREATED_BY")),
            updated_at=(row_dict.get("updated_at") or row_dict.get("UPDATED_AT")),
            updated_by=(row_dict.get("updated_by") or row_dict.get("UPDATED_BY")),
            # Datos de Seguros y Campos Extendidos (Automatización LIQ-AUTO-001)
            id_seguro=gv("ID_SEGURO"),
            nombre_seguro=gv("NOMBRE_SEGURO"),
            porcentaje_seguro=gv("PORCENTAJE_SEGURO") or 0,
            comision_porcentaje_contrato_m=gv("COMISION_PORCENTAJE_CONTRATO_M") or 0,
            id_contrato_m=gv("ID_CONTRATO_M") or 0,
            direccion_propiedad=gv("DIRECCION_PROPIEDAD") or "Sin Dirección",
        )
        return contrato

    def _map_estado(self, estado_str: str) -> EstadoContrato:
        if not estado_str:
            return EstadoContrato.ACTIVO
        try:
            return EstadoContrato(estado_str.upper())
        except ValueError:
            return EstadoContrato.ACTIVO
