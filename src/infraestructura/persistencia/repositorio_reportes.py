from typing import List, Dict, Any, Tuple, Optional
from src.infraestructura.persistencia.database import db_manager


class RepositorioReportes:
    """Repositorio especializado en consultas analíticas y generación de reportes para PostgreSQL."""

    def __init__(self):
        self.db = db_manager

    def _ejecutar_query_paginada(
        self, query: str, params: List[Any], page: int, limit: int
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Ejecuta una consulta con paginación y retorna los datos y el conteo total.
        
        Realiza rollback previo para garantizar lectura fresca bajo READ COMMITTED.
        """
        offset = (page - 1) * limit

        # 1. Obtener el total de registros (Count)
        count_query = f"SELECT COUNT(*) as total FROM ({query}) AS subquery"

        # 2. Agregar LIMIT y OFFSET
        paginated_query = f"{query} LIMIT %s OFFSET %s"
        paginated_params = params + [limit, offset]

        with self.db.obtener_conexion() as conn:
            # Rollback preventivo: limpia cualquier transacción pendiente
            # para garantizar que READ COMMITTED vea datos frescos
            try:
                conn.rollback()
            except Exception:
                pass  # Silenciar si no hay transacción activa

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
            # Rollback preventivo para lectura fresca
            try:
                conn.rollback()
            except Exception:
                pass
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
                    COALESCE(p.DIRECCION_PROPIEDAD, 'N/A') AS "DIRECCION_INMUEBLE",
                    COALESCE(p.MATRICULA_INMOBILIARIA, 'N/A') AS "MATRICULA",
                    COALESCE(per.NOMBRE_COMPLETO, 'N/A') AS "NOMBRE_ARRENDATARIO",
                    COALESCE(per.TELEFONO_PRINCIPAL, 'N/A') AS "TELEFONO_ARRENDATARIO",
                    COALESCE(per.CORREO_ELECTRONICO, 'N/A') AS "EMAIL_ARRENDATARIO",
                    r.FECHA_PAGO AS "FECHA_PAGO",
                    r.VALOR_TOTAL AS "VALOR_TOTAL",
                    r.METODO_PAGO AS "METODO_PAGO",
                    COALESCE(r.REFERENCIA_BANCARIA, 'N/A') AS "REFERENCIA_BANCARIA",
                    r.ESTADO_RECAUDO AS "ESTADO_RECAUDO",
                    MIN(rc.PERIODO) AS "PERIODO_FACTURADO",
                    COALESCE(r.OBSERVACIONES, '') AS "OBSERVACIONES",
                    r.CREATED_AT AS "CREATED_AT"
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
                    COALESCE(p.DIRECCION_PROPIEDAD, 'N/A') AS "DIRECCION_INMUEBLE",
                    COALESCE(p.MATRICULA_INMOBILIARIA, 'N/A') AS "MATRICULA",
                    COALESCE(per.NOMBRE_COMPLETO, 'N/A') AS "NOMBRE_ARRENDATARIO",
                    COALESCE(per.TELEFONO_PRINCIPAL, 'N/A') AS "TELEFONO_ARRENDATARIO",
                    COALESCE(per.CORREO_ELECTRONICO, 'N/A') AS "EMAIL_ARRENDATARIO",
                    r.FECHA_PAGO AS "FECHA_PAGO",
                    r.VALOR_TOTAL AS "VALOR_TOTAL",
                    r.METODO_PAGO AS "METODO_PAGO",
                    COALESCE(r.REFERENCIA_BANCARIA, 'N/A') AS "REFERENCIA_BANCARIA",
                    r.ESTADO_RECAUDO AS "ESTADO_RECAUDO",
                    (SELECT MIN(rc2.PERIODO) FROM RECAUDO_CONCEPTOS rc2 WHERE rc2.ID_RECAUDO = r.ID_RECAUDO) AS "PERIODO_FACTURADO",
                    COALESCE(r.OBSERVACIONES, '') AS "OBSERVACIONES",
                    r.CREATED_AT AS "CREATED_AT"
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

    def obtener_reporte_incidentes_enriquecido(
        self,
        estado: Optional[str] = None,
        busqueda: Optional[str] = None,
        page: int = 1,
        limit: int = 20,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Reporte especializado de incidentes con metadata del propietario y la propiedad."""
        query = """
            SELECT 
                i.ID_INCIDENTE AS "ID",
                i.FECHA_INCIDENTE AS "Fecha Reporte",
                i.ID_PROPIEDAD AS "ID Propiedad",
                COALESCE(p.DIRECCION_PROPIEDAD, 'N/A') AS "Dirección Propiedad",
                i.ID_CONTRATO_M AS "ID Contrato Mandato",
                COALESCE(per.NOMBRE_COMPLETO, 'N/A') AS "Nombre Propietario",
                i.DESCRIPCION_INCIDENTE AS "Descripción",
                i.ESTADO AS "Estado"
            FROM INCIDENTES i
            LEFT JOIN PROPIEDADES p ON i.ID_PROPIEDAD = p.ID_PROPIEDAD
            LEFT JOIN CONTRATOS_MANDATOS cm ON i.ID_CONTRATO_M = cm.ID_CONTRATO_M OR p.ID_PROPIEDAD = cm.ID_PROPIEDAD
            LEFT JOIN PROPIETARIOS pr ON cm.ID_PROPIETARIO = pr.ID_PROPIETARIO
            LEFT JOIN PERSONAS per ON pr.ID_PERSONA = per.ID_PERSONA
        """

        conditions = []
        params = []

        if estado and estado != "Todos":
            conditions.append("i.ESTADO = %s")
            params.append(estado)

        if busqueda:
            conditions.append("""(
                COALESCE(per.NOMBRE_COMPLETO, '') ILIKE %s OR 
                COALESCE(p.DIRECCION_PROPIEDAD, '') ILIKE %s OR
                i.DESCRIPCION_INCIDENTE ILIKE %s OR
                CAST(i.ID_INCIDENTE AS TEXT) ILIKE %s
            )""")
            params.extend([f"%{busqueda}%"] * 4)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY i.FECHA_INCIDENTE DESC, i.ID_INCIDENTE DESC"

        return self._ejecutar_query_paginada(query, params, page, limit)

    def obtener_reporte_consolidado(
        self,
        fecha_pago_inicio: Optional[str] = None,
        fecha_pago_fin: Optional[str] = None,
        periodo_inicio: Optional[str] = None,
        periodo_fin: Optional[str] = None,
        estado_contrato: Optional[str] = None,
        estado_liquidacion: Optional[str] = None,
        asesor_id: Optional[int] = None,
        propietario_buscar: Optional[str] = None,
        busqueda: Optional[str] = None,
        page: int = 1,
        limit: int = 20,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Reporte consolidado unificado de información financiera y contractual.
        Consolida: Propietario, Arrendatario, Contrato, Recaudos, Liquidaciones.
        """
        query = """
            SELECT
                -- Información del Propietario
                per_prop.TIPO_DOCUMENTO AS "TIPO_DOCUMENTO_PROPIETARIO",
                per_prop.NUMERO_DOCUMENTO AS "NUMERO_DOCUMENTO_PROPIETARIO",
                per_prop.NOMBRE_COMPLETO AS "NOMBRE_COMPLETO_PROPIETARIO",
                prop.BANCO_PROPIETARIO AS "BANCO_PROPIETARIO",
                prop.NUMERO_CUENTA_PROPIETARIO AS "NUMERO_CUENTA_PROPIETARIO",
                prop.TIPO_CUENTA AS "TIPO_CUENTA_PROPIETARIO",
                COALESCE(prop.CONSIGNATARIO, '') AS "CONSIGNATARIO_PROPIETARIO",
                COALESCE(prop.DOCUMENTO_CONSIGNATARIO, '') AS "DOCUMENTO_CONSIGNATARIO_PROPIETARIO",

                -- Información del Arrendatario
                per_arr.TIPO_DOCUMENTO AS "TIPO_DOCUMENTO_ARRENDATARIO",
                per_arr.NUMERO_DOCUMENTO AS "NUMERO_DOCUMENTO_ARRENDATARIO",
                per_arr.NOMBRE_COMPLETO AS "NOMBRE_COMPLETO_ARRENDATARIO",

                -- Información del Contrato
                cm.FECHA_INICIO_CONTRATO_M AS "FECHA_INICIO_CONTRATO",
                cm.ESTADO_CONTRATO_M AS "ESTADO_CONTRATO",
                p.DIRECCION_PROPIEDAD AS "DIRECCION_PROPIEDAD",

                -- Información de Recaudos (del recaudo relacionado a la liquidación)
                COALESCE(r.METODO_PAGO, '') AS "METODO_PAGO_RECAUDOS",
                COALESCE(r.ESTADO_RECAUDO, '') AS "ESTADO_RECAUDO",
                l.PERIODO AS "PERIODO_FACTURADO",

                -- Información Comercial
                per_ase.NOMBRE_COMPLETO AS "NOMBRE_ASESOR",
                cm.CANON_MANDATO AS "CANON_ARRENDAMIENTO",

                -- Ingresos (Liquidaciones)
                COALESCE(l.OTROS_INGRESOS, 0) AS "OTROS_INGRESOS",
                l.TOTAL_INGRESOS AS "TOTAL_INGRESOS",

                -- Comisiones
                l.COMISION_PORCENTAJE AS "COMISION_PORCENTAJE_ASESOR",
                l.COMISION_MONTO AS "COMISION_MONTO_ASESOR",
                COALESCE(l.IVA_COMISION, 0) AS "IVA_COMISION",
                COALESCE(l.IMPUESTO_4X1000, 0) AS "IMPUESTO_4X1000",

                -- Egresos
                COALESCE(l.GASTOS_ADMINISTRACION, 0) AS "VALOR_ADMINISTRACION_PROPIEDAD",
                CASE WHEN l.GASTOS_ADMINISTRACION > 0 AND l.ESTADO_LIQUIDACION = 'Pagada'
                     THEN 'Pagado'
                     WHEN l.GASTOS_ADMINISTRACION > 0 THEN 'Pendiente'
                     ELSE 'N/A'
                END AS "ESTADO_PAGO_ADMINISTRACION",
                COALESCE(l.GASTOS_SERVICIOS, 0) AS "GASTOS_SERVICIOS",
                COALESCE(l.GASTOS_REPARACIONES, 0) AS "GASTOS_REPARACIONES",
                COALESCE(l.PAGO_PREDIAL, 0) AS "PAGO_PREDIAL",
                COALESCE(l.OTROS_EGRESOS, 0) AS "OTROS_EGRESOS",
                l.TOTAL_EGRESOS AS "TOTAL_EGRESOS",

                -- Resultado Financiero
                l.NETO_A_PAGAR AS "NETO_A_PAGAR",

                -- Estado y Fechas
                l.ESTADO_LIQUIDACION AS "ESTADO_LIQUIDACION",
                l.FECHA_PAGO AS "FECHA_PAGO",

                -- IDs para relaciones
                l.ID_LIQUIDACION AS "ID_LIQUIDACION",
                cm.ID_CONTRATO_M AS "ID_CONTRATO_M",
                p.ID_PROPIEDAD AS "ID_PROPIEDAD"
            FROM liquidaciones l
            LEFT JOIN CONTRATOS_MANDATOS cm ON l.ID_CONTRATO_M = cm.ID_CONTRATO_M
            LEFT JOIN PROPIEDADES p ON cm.ID_PROPIEDAD = p.ID_PROPIEDAD
            LEFT JOIN PROPIETARIOS prop ON cm.ID_PROPIETARIO = prop.ID_PROPIETARIO
            LEFT JOIN PERSONAS per_prop ON prop.ID_PERSONA = per_prop.ID_PERSONA
            LEFT JOIN ASESORES a ON cm.ID_ASESOR = a.ID_ASESOR
            LEFT JOIN PERSONAS per_ase ON a.ID_PERSONA = per_ase.ID_PERSONA
            LEFT JOIN (
                SELECT DISTINCT ON (ca_inner.ID_PROPIEDAD)
                    ca_inner.ID_CONTRATO_A,
                    ca_inner.ID_PROPIEDAD,
                    ca_inner.ID_ARRENDATARIO
                FROM CONTRATOS_ARRENDAMIENTOS ca_inner
                ORDER BY ca_inner.ID_PROPIEDAD,
                         CASE WHEN ca_inner.ESTADO_CONTRATO_A = 'Activo' THEN 0 ELSE 1 END,
                         ca_inner.FECHA_INICIO_CONTRATO_A DESC
            ) ca ON cm.ID_PROPIEDAD = ca.ID_PROPIEDAD
            LEFT JOIN ARRENDATARIOS arr ON ca.ID_ARRENDATARIO = arr.ID_ARRENDATARIO
            LEFT JOIN PERSONAS per_arr ON arr.ID_PERSONA = per_arr.ID_PERSONA
            LEFT JOIN (
                SELECT r.ID_RECAUDO, r.ID_CONTRATO_A, r.METODO_PAGO, r.ESTADO_RECAUDO
                FROM RECAUDOS r
                INNER JOIN (
                    SELECT ID_CONTRATO_A, MAX(FECHA_PAGO) AS ultima_fecha
                    FROM RECAUDOS
                    WHERE ESTADO_RECAUDO = 'Aplicado'
                    GROUP BY ID_CONTRATO_A
                ) max_r ON r.ID_CONTRATO_A = max_r.ID_CONTRATO_A AND r.FECHA_PAGO = max_r.ultima_fecha
            ) r ON ca.ID_CONTRATO_A = r.ID_CONTRATO_A
        """

        conditions = []
        params = []

        # Filtro: Estado del Contrato
        if estado_contrato and estado_contrato != "Todos":
            conditions.append("cm.ESTADO_CONTRATO_M = %s")
            params.append(estado_contrato)

        # Filtro: Estado de Liquidación
        if estado_liquidacion and estado_liquidacion != "Todos":
            conditions.append("l.ESTADO_LIQUIDACION = %s")
            params.append(estado_liquidacion)

        # Filtro: Asesor
        if asesor_id:
            conditions.append("cm.ID_ASESOR = %s")
            params.append(asesor_id)

        # Filtro: Propietario (búsqueda por nombre o documento)
        if propietario_buscar:
            conditions.append("""(
                per_prop.NOMBRE_COMPLETO ILIKE %s OR
                per_prop.NUMERO_DOCUMENTO ILIKE %s
            )""")
            params.extend([f"%{propietario_buscar}%", f"%{propietario_buscar}%"])

        # Filtro: Rango de fechas de pago (FECHA_PAGO)
        if fecha_pago_inicio:
            conditions.append("l.FECHA_PAGO >= %s")
            params.append(fecha_pago_inicio)

        if fecha_pago_fin:
            conditions.append("l.FECHA_PAGO <= %s")
            params.append(fecha_pago_fin)

        # Filtro: Período facturado
        if periodo_inicio:
            conditions.append("l.PERIODO >= %s")
            params.append(periodo_inicio)

        if periodo_fin:
            conditions.append("l.PERIODO <= %s")
            params.append(periodo_fin)

        # Búsqueda general
        if busqueda:
            conditions.append("""(
                per_prop.NOMBRE_COMPLETO ILIKE %s OR
                per_arr.NOMBRE_COMPLETO ILIKE %s OR
                p.DIRECCION_PROPIEDAD ILIKE %s OR
                per_ase.NOMBRE_COMPLETO ILIKE %s OR
                CAST(l.ID_LIQUIDACION AS TEXT) ILIKE %s
            )""")
            params.extend([f"%{busqueda}%"] * 5)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY l.FECHA_PAGO DESC, l.ID_LIQUIDACION DESC"

        return self._ejecutar_query_paginada(query, params, page, limit)
