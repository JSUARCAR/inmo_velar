"""
Repositorio PostgreSQL para entidad LiquidacionAsesor.
Implementa operaciones CRUD y consultas especializadas bajo estándares Élite.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple

from src.dominio.entidades.liquidacion_asesor import LiquidacionAsesor
from src.infraestructura.persistencia.database import DatabaseManager


class RepositorioLiquidacionAsesor:
    """Repositorio para gestión de liquidaciones de asesores en PostgreSQL"""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def crear(self, liquidacion: LiquidacionAsesor, usuario: str) -> LiquidacionAsesor:
        """
        Crea una nueva liquidación de asesor con PostgreSQL Native.
        """
        query = """
            INSERT INTO LIQUIDACIONES_ASESORES (
                ID_CONTRATO_A, ID_ASESOR, PERIODO_LIQUIDACION, 
                CANON_ARRENDAMIENTO_LIQUIDADO, PORCENTAJE_COMISION, COMISION_BRUTA, 
                TOTAL_DESCUENTOS, TOTAL_BONIFICACIONES, VALOR_NETO_ASESOR, 
                ESTADO_LIQUIDACION, MODO_COMISION, OBSERVACIONES_LIQUIDACION, 
                USUARIO_CREADOR, CREATED_BY, UPDATED_BY
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
            RETURNING ID_LIQUIDACION_ASESOR
        """

        params = (
            liquidacion.id_contrato_a,
            liquidacion.id_asesor,
            liquidacion.periodo_liquidacion,
            liquidacion.canon_arrendamiento_liquidado,
            liquidacion.porcentaje_comision,
            liquidacion.comision_bruta,
            liquidacion.total_descuentos,
            liquidacion.total_bonificaciones,
            liquidacion.valor_neto_asesor,
            liquidacion.estado_liquidacion,
            liquidacion.modo_comision,
            liquidacion.observaciones_liquidacion,
            usuario,
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
                        liquidacion.id_liquidacion_asesor = row.get("ID_LIQUIDACION_ASESOR") or row.get("id_liquidacion_asesor")
                    else:
                        liquidacion.id_liquidacion_asesor = row[0]

                liquidacion.usuario_creador = usuario
                liquidacion.created_by = usuario
                liquidacion.updated_by = usuario
                return liquidacion
        except Exception as e:
            if "unique" in str(e).lower() or "duplicada" in str(e).lower():
                raise ValueError(
                    f"Ya existe una liquidación para el contrato {liquidacion.id_contrato_a} "
                    f"en el período {liquidacion.periodo_liquidacion}"
                )
            raise

    def actualizar(
        self, liquidacion: LiquidacionAsesor, usuario: str
    ) -> LiquidacionAsesor:
        """
        Actualiza una liquidación existente.
        """
        query = """
            UPDATE LIQUIDACIONES_ASESORES SET 
                PORCENTAJE_COMISION = %s, COMISION_BRUTA = %s, TOTAL_DESCUENTOS = %s, 
                TOTAL_BONIFICACIONES = %s, VALOR_NETO_ASESOR = %s, ESTADO_LIQUIDACION = %s, 
                FECHA_APROBACION = %s, USUARIO_APROBADOR = %s, OBSERVACIONES_LIQUIDACION = %s, 
                MOTIVO_ANULACION = %s, UPDATED_AT = %s, UPDATED_BY = %s 
            WHERE ID_LIQUIDACION_ASESOR = %s
        """

        params = (
            liquidacion.porcentaje_comision,
            liquidacion.comision_bruta,
            liquidacion.total_descuentos,
            liquidacion.total_bonificaciones,
            liquidacion.valor_neto_asesor,
            liquidacion.estado_liquidacion,
            liquidacion.fecha_aprobacion,
            liquidacion.usuario_aprobador,
            liquidacion.observaciones_liquidacion,
            liquidacion.motivo_anulacion,
            datetime.now(),
            usuario,
            liquidacion.id_liquidacion_asesor,
        )

        with self.db_manager.transaccion() as conn:
            cursor = self.db_manager.get_dict_cursor(conn)
            cursor.execute(query, params)
            if cursor.rowcount == 0:
                raise ValueError(
                    f"No se encontró la liquidación con ID {liquidacion.id_liquidacion_asesor}"
                )

        liquidacion.updated_by = usuario
        liquidacion.updated_at = datetime.now().isoformat()
        return liquidacion

    def obtener_por_id(self, id_liquidacion: int) -> Optional[LiquidacionAsesor]:
        """Obtiene una liquidación por su ID."""
        query = """
            SELECT 
                la.*,
                p.NOMBRE_COMPLETO as NOMBRE_ASESOR
            FROM LIQUIDACIONES_ASESORES la
            LEFT JOIN ASESORES a ON la.ID_ASESOR = a.ID_ASESOR
            LEFT JOIN PERSONAS p ON a.ID_PERSONA = p.ID_PERSONA
            WHERE la.ID_LIQUIDACION_ASESOR = %s
        """

        with self.db_manager.obtener_conexion() as conn:
            cursor = self.db_manager.get_dict_cursor(conn)
            cursor.execute(query, (id_liquidacion,))
            row = cursor.fetchone()
            return self._row_to_entity(row) if row else None

    def listar_con_filtros(
        self,
        id_asesor: Optional[int] = None,
        periodo: Optional[str] = None,
        estado: Optional[str] = None,
    ) -> List[LiquidacionAsesor]:
        """Lista liquidaciones con múltiples filtros."""
        query = "SELECT * FROM LIQUIDACIONES_ASESORES WHERE 1=1"
        params = []

        if id_asesor is not None:
            query += " AND ID_ASESOR = %s"
            params.append(id_asesor)

        if periodo:
            query += " AND PERIODO_LIQUIDACION = %s"
            params.append(periodo)

        if estado:
            query += " AND ESTADO_LIQUIDACION = %s"
            params.append(estado)

        query += " ORDER BY PERIODO_LIQUIDACION DESC, ID_ASESOR"

        with self.db_manager.obtener_conexion() as conn:
            cursor = self.db_manager.get_dict_cursor(conn)
            cursor.execute(query, tuple(params))
            rows = cursor.fetchall()
            return [self._row_to_entity(row) for row in rows]

    def listar_paginado(
        self,
        page: int,
        page_size: int,
        id_asesor: Optional[int] = None,
        periodo: Optional[str] = None,
        estado: Optional[str] = None,
        busqueda: Optional[str] = None,
        sort_by: str = "periodo_liquidacion",
        sort_order: str = "desc",
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Lista liquidaciones con paginación y filtros (Migrado de Capa de Aplicación).
        """
        offset = (page - 1) * page_size

        with self.db_manager.obtener_conexion() as conn:
            cursor = self.db_manager.get_dict_cursor(conn)

            base_from = """
                FROM LIQUIDACIONES_ASESORES l
                JOIN ASESORES a ON l.ID_ASESOR = a.ID_ASESOR
                JOIN PERSONAS per ON a.ID_PERSONA = per.ID_PERSONA
            """

            conditions = []
            query_params = []

            if estado and estado != "Todos":
                conditions.append("l.ESTADO_LIQUIDACION = %s")
                query_params.append(estado)

            if periodo:
                conditions.append("l.PERIODO_LIQUIDACION LIKE %s")
                query_params.append(f"%{periodo}%")

            if id_asesor:
                conditions.append("l.ID_ASESOR = %s")
                query_params.append(id_asesor)

            if busqueda:
                term = f"%{self.db_manager.normalize_search_term(busqueda)}%"
                search_cond = self.db_manager.get_search_condition(
                    ["per.NOMBRE_COMPLETO", "per.NUMERO_DOCUMENTO"]
                )
                conditions.append(f"({search_cond} OR CAST(l.ID_LIQUIDACION_ASESOR AS TEXT) LIKE %s)")
                query_params.extend([term, term, term])

            where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""

            # Whitelist de ordenamiento
            SORT_COLUMNS = {
                "periodo_liquidacion": "l.PERIODO_LIQUIDACION",
                "comision_bruta": "l.COMISION_BRUTA",
                "valor_neto_asesor": "l.VALOR_NETO_ASESOR",
                "estado_liquidacion": "l.ESTADO_LIQUIDACION",
                "nombre_asesor": "per.NOMBRE_COMPLETO",
                "id_liquidacion_asesor": "l.ID_LIQUIDACION_ASESOR",
            }
            sort_column = SORT_COLUMNS.get(sort_by, "l.PERIODO_LIQUIDACION")
            sort_order_valid = "DESC" if sort_order.lower() == "desc" else "ASC"

            # Contar total
            cursor.execute(f"SELECT COUNT(*) as total {base_from} {where_clause}", query_params)
            count_res = cursor.fetchone()
            total = count_res["TOTAL"] if count_res and "TOTAL" in count_res else (count_res["total"] if count_res and "total" in count_res else 0)

            # Datos
            data_query = f"""
                SELECT 
                    l.*, per.NOMBRE_COMPLETO
                {base_from}
                {where_clause}
                ORDER BY {sort_column} {sort_order_valid}
                LIMIT %s OFFSET %s
            """
            cursor.execute(data_query, query_params + [page_size, offset])
            rows = cursor.fetchall()

            items = []
            for row in rows:
                def gv(k): return row.get(k) or row.get(k.upper()) or row.get(k.lower())
                pct = float(gv("PORCENTAJE_COMISION") or 0) / 100.0
                estado_val = gv("ESTADO_LIQUIDACION")
                
                items.append({
                    "id_liquidacion_asesor": gv("ID_LIQUIDACION_ASESOR"),
                    "periodo_liquidacion": gv("PERIODO_LIQUIDACION"),
                    "estado_liquidacion": estado_val,
                    "comision_bruta": gv("COMISION_BRUTA"),
                    "total_descuentos": gv("TOTAL_DESCUENTOS"),
                    "total_bonificaciones": gv("TOTAL_BONIFICACIONES") or 0,
                    "valor_neto_asesor": gv("VALOR_NETO_ASESOR"),
                    "porcentaje_real": pct,
                    "id_contrato_a": gv("ID_CONTRATO_A"),
                    "id_asesor": gv("ID_ASESOR"),
                    "nombre_asesor": gv("NOMBRE_COMPLETO"),
                    "puede_editarse": estado_val == "Pendiente",
                    "puede_aprobarse": estado_val == "Pendiente",
                    "puede_anularse": estado_val not in ["Anulada", "Pagada"],
                })

            return items, total

    def obtener_metricas_por_filtros(
        self,
        estado: Optional[str] = None,
        periodo: Optional[str] = None,
        busqueda: Optional[str] = None,
        id_asesor: Optional[int] = None,
    ) -> Dict[str, int]:
        """Calcula totales monetarios por estado (Migrado de Capa de Aplicación)."""
        with self.db_manager.obtener_conexion() as conn:
            cursor = self.db_manager.get_dict_cursor(conn)

            query = """
                SELECT l.ESTADO_LIQUIDACION, SUM(l.VALOR_NETO_ASESOR) as total
                FROM LIQUIDACIONES_ASESORES l
                JOIN ASESORES a ON l.ID_ASESOR = a.ID_ASESOR
                JOIN PERSONAS per ON a.ID_PERSONA = per.ID_PERSONA
            """

            conditions = []
            query_params = []

            if estado and estado != "Todos":
                conditions.append("l.ESTADO_LIQUIDACION = %s")
                query_params.append(estado)
            if periodo:
                conditions.append("l.PERIODO_LIQUIDACION LIKE %s")
                query_params.append(f"%{periodo}%")
            if id_asesor:
                conditions.append("l.ID_ASESOR = %s")
                query_params.append(id_asesor)
            if busqueda:
                term = f"%{self.db_manager.normalize_search_term(busqueda)}%"
                search_cond = self.db_manager.get_search_condition(["per.NOMBRE_COMPLETO"])
                conditions.append(f"({search_cond} OR CAST(l.ID_LIQUIDACION_ASESOR AS TEXT) LIKE %s)")
                query_params.extend([term, term])

            where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
            cursor.execute(f"{query} {where_clause} GROUP BY l.ESTADO_LIQUIDACION", query_params)

            resultados = {"Pendiente": 0, "Aprobada": 0, "Pagada": 0, "Anulada": 0}
            for row in cursor.fetchall():
                e = row.get("estado_liquidacion") or row.get("ESTADO_LIQUIDACION")
                t = row.get("total") or row.get("TOTAL") or 0
                if e in resultados:
                    resultados[e] = int(t)

            return resultados

    def obtener_por_asesor_periodo(
        self, id_asesor: int, periodo: str
    ) -> Optional[LiquidacionAsesor]:
        """Obtiene una liquidación por asesor y período."""
        query = "SELECT * FROM LIQUIDACIONES_ASESORES WHERE ID_ASESOR = %s AND PERIODO_LIQUIDACION = %s"
        with self.db_manager.obtener_conexion() as conn:
            cursor = self.db_manager.get_dict_cursor(conn)
            cursor.execute(query, (id_asesor, periodo))
            row = cursor.fetchone()
            return self._row_to_entity(row) if row else None

    def guardar_contratos_liquidacion(
        self, id_liquidacion: int, contratos_ids_canones: List[Tuple], usuario: str
    ):
        """
        Guarda contratos asociados en tabla intermedia con desglose de comisión.
        contratos_ids_canones: List[Tuple(id, canon, pct, comision)]
        """
        query = """
            INSERT INTO LIQUIDACIONES_CONTRATOS (
                ID_LIQUIDACION_ASESOR, ID_CONTRATO_A, CANON_INCLUIDO, 
                COMISION_PORCENTAJE_CONTRATO, COMISION_MONTO_CONTRATO, CREATED_BY
            ) VALUES (%s, %s, %s, %s, %s, %s)
        """
        with self.db_manager.transaccion() as conn:
            cursor = self.db_manager.get_dict_cursor(conn)
            for id_contrato, canon, pct, comision in contratos_ids_canones:
                cursor.execute(query, (id_liquidacion, id_contrato, canon, pct, comision, usuario))

    def obtener_contratos_de_liquidacion(self, id_liquidacion: int) -> List[Dict]:
        """
        Obtiene lista de contratos asociados con desglose de comisión.
        Implementa FALLBACK ÉLITE: Si la comisión histórica es 0, intenta obtenerla del Mandato actual.
        """
        query = """
            SELECT lc.ID_CONTRATO_A, lc.CANON_INCLUIDO, 
                   lc.COMISION_PORCENTAJE_CONTRATO, lc.COMISION_MONTO_CONTRATO,
                   ca.CANON_ARRENDAMIENTO, 
                   p.DIRECCION_PROPIEDAD, per.NOMBRE_COMPLETO as ARRENDATARIO,
                   cm.COMISION_PORCENTAJE_CONTRATO_M as PCT_MANDATO_ACTUAL
            FROM LIQUIDACIONES_CONTRATOS lc 
            JOIN CONTRATOS_ARRENDAMIENTOS ca ON lc.ID_CONTRATO_A = ca.ID_CONTRATO_A 
            JOIN PROPIEDADES p ON ca.ID_PROPIEDAD = p.ID_PROPIEDAD 
            JOIN ARRENDATARIOS arr ON ca.ID_ARRENDATARIO = arr.ID_ARRENDATARIO 
            JOIN PERSONAS per ON arr.ID_PERSONA = per.ID_PERSONA 
            LEFT JOIN CONTRATOS_MANDATOS cm ON ca.ID_PROPIEDAD = cm.ID_PROPIEDAD AND cm.ESTADO_CONTRATO_M = 'Activo'
            WHERE lc.ID_LIQUIDACION_ASESOR = %s
        """
        with self.db_manager.obtener_conexion() as conn:
            cursor = self.db_manager.get_dict_cursor(conn)
            cursor.execute(query, (id_liquidacion,))
            rows = cursor.fetchall()
            
            result = []
            for row in rows:
                def gv(k): return row.get(k) or row.get(k.upper()) or row.get(k.lower())
                
                # Lógica de Fallback
                pct_db = gv("COMISION_PORCENTAJE_CONTRATO") or 0
                monto_db = gv("COMISION_MONTO_CONTRATO") or 0
                
                if pct_db == 0:
                    pct_final = gv("PCT_MANDATO_ACTUAL") or 0
                    monto_final = int(gv("CANON_INCLUIDO") * pct_final / 10000)
                else:
                    pct_final = pct_db
                    monto_final = monto_db

                result.append({
                    "id_contrato": gv("ID_CONTRATO_A"),
                    "canon_incluido": gv("CANON_INCLUIDO"),
                    "comision_porcentaje_contrato": pct_final,
                    "comision_monto_contrato": monto_final,
                    "direccion": gv("DIRECCION_PROPIEDAD"),
                    "arrendatario": gv("ARRENDATARIO"),
                })
            return result

    def _row_to_entity(self, row: Dict[str, Any]) -> LiquidacionAsesor:
        """Helper para mapeo de fila a entidad."""
        def gv(k): return row.get(k) or row.get(k.upper()) or row.get(k.lower())
        return LiquidacionAsesor(
            id_liquidacion_asesor=gv("ID_LIQUIDACION_ASESOR"),
            id_contrato_a=gv("ID_CONTRATO_A"),
            id_asesor=gv("ID_ASESOR"),
            periodo_liquidacion=gv("PERIODO_LIQUIDACION"),
            canon_arrendamiento_liquidado=gv("CANON_ARRENDAMIENTO_LIQUIDADO") or 0,
            porcentaje_comision=gv("PORCENTAJE_COMISION") or 0,
            comision_bruta=gv("COMISION_BRUTA") or 0,
            total_descuentos=gv("TOTAL_DESCUENTOS") or 0,
            total_bonificaciones=gv("TOTAL_BONIFICACIONES") or 0,
            valor_neto_asesor=gv("VALOR_NETO_ASESOR") or 0,
            estado_liquidacion=gv("ESTADO_LIQUIDACION"),
            modo_comision=gv("MODO_COMISION") or "ASESOR",
            fecha_creacion=gv("FECHA_CREACION"),
            fecha_aprobacion=gv("FECHA_APROBACION"),
            usuario_creador=gv("USUARIO_CREADOR"),
            usuario_aprobador=gv("USUARIO_APROBADOR"),
            observaciones_liquidacion=gv("OBSERVACIONES_LIQUIDACION"),
            motivo_anulacion=gv("MOTIVO_ANULACION"),
            nombre_asesor=gv("NOMBRE_ASESOR"),
        )
