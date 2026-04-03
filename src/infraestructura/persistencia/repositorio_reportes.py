from typing import List, Dict, Any, Tuple, Optional
from src.infraestructura.persistencia.database import db_manager


class RepositorioReportes:
    """Repositorio especializado en consultas analíticas y generación de reportes para PostgreSQL."""

    def __init__(self):
        self.db = db_manager

    def _ejecutar_query_paginada(
        self, query: str, params: List[Any], page: int, limit: int
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Ejecuta una consulta con paginación y retorna los datos y el conteo total."""
        offset = (page - 1) * limit

        # 1. Obtener el total de registros (Count)
        count_query = f"SELECT COUNT(*) as total FROM ({query}) AS subquery"

        # 2. Agregar LIMIT y OFFSET
        paginated_query = f"{query} LIMIT %s OFFSET %s"
        paginated_params = params + [limit, offset]

        with self.db.obtener_conexion() as conn:
            # Count
            cursor = self.db.get_dict_cursor(conn)
            try:
                cursor.execute(count_query, params)
                res = cursor.fetchone()
                total = res.get("TOTAL", res.get("total", 0)) if res else 0
            finally:
                cursor.close()

            # Data
            cursor = self.db.get_dict_cursor(conn)
            try:
                cursor.execute(paginated_query, paginated_params)
                rows = cursor.fetchall()
            finally:
                cursor.close()

        return rows, total

    def obtener_reporte_roles(
        self,
        role_table: str,
        busqueda: Optional[str] = None,
        solo_activos: bool = True,
        page: int = 1,
        limit: int = 20,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Obtiene datos de personas con un rol específico (Propietarios, Arrendatarios, etc)."""
        query = f"""
            SELECT p.TIPO_DOCUMENTO, p.NUMERO_DOCUMENTO, p.NOMBRE_COMPLETO, 
                   p.TELEFONO_PRINCIPAL, p.CORREO_ELECTRONICO, p.DIRECCION_PRINCIPAL,
                   r.* 
            FROM PERSONAS p
            INNER JOIN {role_table} r ON p.ID_PERSONA = r.ID_PERSONA
        """
        conditions = []
        params = []

        if busqueda:
            conditions.append(
                "(p.NOMBRE_COMPLETO ILIKE %s OR p.NUMERO_DOCUMENTO ILIKE %s)"
            )
            params.extend([f"%{busqueda}%", f"%{busqueda}%"])

        if solo_activos:
            conditions.append("p.ESTADO_REGISTRO = %s")
            params.append(True)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        return self._ejecutar_query_paginada(query, params, page, limit)

    def obtener_reporte_liquidaciones(
        self,
        asesor_id: Optional[int] = None,
        busqueda: Optional[str] = None,
        page: int = 1,
        limit: int = 20,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Reporte especializado de liquidaciones con datos de contrato, propiedad y asesor."""
        query = """
            SELECT 
                l.ID_LIQUIDACION, l.ID_CONTRATO_M,
                p.DIRECCION_PROPIEDAD AS "Direccion_Predio",
                per_prop.NOMBRE_COMPLETO AS "Nombre_Propietario",
                per_ase.NOMBRE_COMPLETO AS "Nombre_Asesor",
                l.PERIODO, l.FECHA_GENERACION, l.CANON_BRUTO, l.OTROS_INGRESOS,
                l.TOTAL_INGRESOS, l.COMISION_PORCENTAJE, l.COMISION_MONTO,
                l.IVA_COMISION, l.IMPUESTO_4X1000, l.GASTOS_ADMINISTRACION,
                l.GASTOS_SERVICIOS, l.GASTOS_REPARACIONES, l.PAGO_PREDIAL,
                l.OTROS_EGRESOS, l.TOTAL_EGRESOS, l.NETO_A_PAGAR,
                l.ESTADO_LIQUIDACION, l.FECHA_PAGO, l.METODO_PAGO,
                l.REFERENCIA_PAGO, l.OBSERVACIONES
            FROM liquidaciones l
            LEFT JOIN CONTRATOS_MANDATOS cm ON l.ID_CONTRATO_M = cm.ID_CONTRATO_M
            LEFT JOIN PROPIEDADES p ON cm.ID_PROPIEDAD = p.ID_PROPIEDAD
            LEFT JOIN PROPIETARIOS prop ON cm.ID_PROPIETARIO = prop.ID_PROPIETARIO
            LEFT JOIN PERSONAS per_prop ON prop.ID_PERSONA = per_prop.ID_PERSONA
            LEFT JOIN ASESORES a ON cm.ID_ASESOR = a.ID_ASESOR
            LEFT JOIN PERSONAS per_ase ON a.ID_PERSONA = per_ase.ID_PERSONA
        """
        conditions = []
        params = []

        if asesor_id:
            conditions.append("cm.ID_ASESOR = %s")
            params.append(asesor_id)

        if busqueda:
            conditions.append("""(
                per_prop.NOMBRE_COMPLETO ILIKE %s OR 
                per_ase.NOMBRE_COMPLETO ILIKE %s OR 
                p.DIRECCION_PROPIEDAD ILIKE %s OR
                CAST(l.ID_LIQUIDACION AS TEXT) ILIKE %s
            )""")
            params.extend([f"%{busqueda}%"] * 4)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        return self._ejecutar_query_paginada(query, params, page, limit)

    def obtener_reporte_generico(
        self, tabla: str, busqueda: Optional[str] = None, page: int = 1, limit: int = 20
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Obtiene todos los registros de una tabla con búsqueda simple y paginación."""
        query = f"SELECT * FROM {tabla}"
        params = []

        if busqueda:
            # En PostgreSQL necesitamos saber las columnas para ILIKE o usar un truco con cast a text
            # Para reportes genéricos, buscaremos en todas las columnas convirtiendo la fila a texto (simple pero efectivo)
            query = f"SELECT * FROM ({query}) AS t WHERE CAST(ROW_TO_JSON(t) AS TEXT) ILIKE %s"
            params.append(f"%{busqueda}%")

        return self._ejecutar_query_paginada(query, params, page, limit)

    def obtener_lista_asesores(self) -> List[Dict[str, Any]]:
        """Obtiene la lista de asesores activos para los filtros."""
        query = """
            SELECT a.ID_ASESOR, p.NOMBRE_COMPLETO 
            FROM ASESORES a 
            JOIN PERSONAS p ON a.ID_PERSONA = p.ID_PERSONA 
            WHERE p.ESTADO_REGISTRO IS TRUE
            ORDER BY p.NOMBRE_COMPLETO
        """
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            try:
                cursor.execute(query)
                return cursor.fetchall()
            finally:
                cursor.close()

    def obtener_reporte_recaudos(
        self,
        estado: Optional[str] = None,
        metodo_pago: Optional[str] = None,
        periodo_inicio: Optional[str] = None,
        periodo_fin: Optional[str] = None,
        busqueda: Optional[str] = None,
        page: int = 1,
        limit: int = 20,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Reporte especializado de recaudos con JOINs a contratos, propiedades y arrendatarios."""

        necesita_filtro_periodo = periodo_inicio or periodo_fin

        if necesita_filtro_periodo:
            query = """
                SELECT DISTINCT
                    r.ID_RECAUDO,
                    r.ID_CONTRATO_A,
                    COALESCE(p.DIRECCION_PROPIEDAD, 'N/A') AS "Direccion_Inmueble",
                    COALESCE(p.MATRICULA_INMOBILIARIA, 'N/A') AS "Matricula",
                    COALESCE(per.NOMBRE_COMPLETO, 'N/A') AS "Nombre_Arrendatario",
                    COALESCE(per.TELEFONO_PRINCIPAL, 'N/A') AS "Telefono_Arrendatario",
                    COALESCE(per.CORREO_ELECTRONICO, 'N/A') AS "Email_Arrendatario",
                    r.FECHA_PAGO,
                    r.VALOR_TOTAL,
                    r.METODO_PAGO,
                    COALESCE(r.REFERENCIA_BANCARIA, 'N/A') AS "Referencia_Bancaria",
                    r.ESTADO_RECAUDO,
                    MIN(rc.PERIODO) AS "Periodo_Facturado",
                    COALESCE(r.OBSERVACIONES, '') AS "Observaciones",
                    r.CREATED_AT
                FROM RECAUDOS r
                LEFT JOIN CONTRATOS_ARRENDAMIENTOS ca ON r.ID_CONTRATO_A = ca.ID_CONTRATO_A
                LEFT JOIN PROPIEDADES p ON ca.ID_PROPIEDAD = p.ID_PROPIEDAD
                LEFT JOIN ARRENDATARIOS arr ON ca.ID_ARRENDATARIO = arr.ID_ARRENDATARIO
                LEFT JOIN PERSONAS per ON arr.ID_PERSONA = per.ID_PERSONA
                LEFT JOIN RECAUDO_CONCEPTOS rc ON r.ID_RECAUDO = rc.ID_RECAUDO
                GROUP BY r.ID_RECAUDO, r.ID_CONTRATO_A, p.DIRECCION_PROPIEDAD, p.MATRICULA_INMOBILIARIA,
                         per.NOMBRE_COMPLETO, per.TELEFONO_PRINCIPAL, per.CORREO_ELECTRONICO,
                         r.FECHA_PAGO, r.VALOR_TOTAL, r.METODO_PAGO, r.REFERENCIA_BANCARIA,
                         r.ESTADO_RECAUDO, r.OBSERVACIONES, r.CREATED_AT
            """
        else:
            query = """
                SELECT 
                    r.ID_RECAUDO,
                    r.ID_CONTRATO_A,
                    COALESCE(p.DIRECCION_PROPIEDAD, 'N/A') AS "Direccion_Inmueble",
                    COALESCE(p.MATRICULA_INMOBILIARIA, 'N/A') AS "Matricula",
                    COALESCE(per.NOMBRE_COMPLETO, 'N/A') AS "Nombre_Arrendatario",
                    COALESCE(per.TELEFONO_PRINCIPAL, 'N/A') AS "Telefono_Arrendatario",
                    COALESCE(per.CORREO_ELECTRONICO, 'N/A') AS "Email_Arrendatario",
                    r.FECHA_PAGO,
                    r.VALOR_TOTAL,
                    r.METODO_PAGO,
                    COALESCE(r.REFERENCIA_BANCARIA, 'N/A') AS "Referencia_Bancaria",
                    r.ESTADO_RECAUDO,
                    (SELECT MIN(rc2.PERIODO) FROM RECAUDO_CONCEPTOS rc2 WHERE rc2.ID_RECAUDO = r.ID_RECAUDO) AS "Periodo_Facturado",
                    COALESCE(r.OBSERVACIONES, '') AS "Observaciones",
                    r.CREATED_AT
                FROM RECAUDOS r
                LEFT JOIN CONTRATOS_ARRENDAMIENTOS ca ON r.ID_CONTRATO_A = ca.ID_CONTRATO_A
                LEFT JOIN PROPIEDADES p ON ca.ID_PROPIEDAD = p.ID_PROPIEDAD
                LEFT JOIN ARRENDATARIOS arr ON ca.ID_ARRENDATARIO = arr.ID_ARRENDATARIO
                LEFT JOIN PERSONAS per ON arr.ID_PERSONA = per.ID_PERSONA
            """

        conditions = []
        params = []

        if estado and estado != "Todos":
            conditions.append("r.ESTADO_RECAUDO = %s")
            params.append(estado)

        if metodo_pago and metodo_pago != "Todos":
            conditions.append("r.METODO_PAGO = %s")
            params.append(metodo_pago)

        if necesita_filtro_periodo:
            if periodo_inicio:
                conditions.append(
                    "EXISTS (SELECT 1 FROM RECAUDO_CONCEPTOS rc3 WHERE rc3.ID_RECAUDO = r.ID_RECAUDO AND rc3.PERIODO >= %s)"
                )
                params.append(periodo_inicio)

            if periodo_fin:
                conditions.append(
                    "EXISTS (SELECT 1 FROM RECAUDO_CONCEPTOS rc4 WHERE rc4.ID_RECAUDO = r.ID_RECAUDO AND rc4.PERIODO <= %s)"
                )
                params.append(periodo_fin)

        if busqueda:
            conditions.append("""(
                COALESCE(per.NOMBRE_COMPLETO, '') ILIKE %s OR 
                COALESCE(p.DIRECCION_PROPIEDAD, '') ILIKE %s OR
                COALESCE(r.REFERENCIA_BANCARIA, '') ILIKE %s OR
                CAST(r.ID_RECAUDO AS TEXT) ILIKE %s
            )""")
            params.extend([f"%{busqueda}%"] * 4)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY r.FECHA_PAGO DESC, r.ID_RECAUDO DESC"

        return self._ejecutar_query_paginada(query, params, page, limit)
