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

        # Utilizamos una Window Function para obtener el count total y los datos en un solo viaje
        paginated_query = f"""
            SELECT subquery.*, COUNT(*) OVER() as _total_count
            FROM ({query}) AS subquery
            LIMIT %s OFFSET %s
        """
        paginated_params = params + [limit, offset]

        with self.db.obtener_conexion() as conn:
            # Limpiar estado transaccional para asegurar READ COMMITTED con datos frescos.
            # En PostgreSQL, si la conexión fue usada previamente y no se hizo commit/rollback,
            # podríamos leer datos estancados (stale snapshot).
            try:
                conn.rollback()
            except getattr(conn, "OperationalError", Exception) as e:
                # Fallar si la conexión está severamente dañada, en lugar de silenciar todo
                pass

            cursor = self.db.get_dict_cursor(conn)
            try:
                cursor.execute(paginated_query, paginated_params)
                rows = cursor.fetchall()
                
                # Extraer el total_count de la primera fila si existen resultados (Blindaje Élite)
                total = 0
                if rows is not None and len(rows) > 0:
                    first_row = rows[0]
                    if hasattr(first_row, "get"):
                        total = (first_row.get("_total_count") or 
                                 first_row.get("_TOTAL_COUNT") or 
                                 0)
                
                # Limpiar la columna auxiliar de los resultados de forma segura
                if rows:
                    for row in rows:
                        if hasattr(row, "pop"):
                            row.pop("_total_count", None)
                            row.pop("_TOTAL_COUNT", None)
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
        _TABLAS_PERMITIDAS = {"PROPIETARIOS", "ARRENDATARIOS", "CODEUDORES", "ASESORES", "TERCEROS"}
        if role_table.upper() not in _TABLAS_PERMITIDAS:
            raise ValueError(f"Tabla no permitida para reporte de roles: {role_table}")
            
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

    def obtener_reporte_personas(
        self,
        busqueda: Optional[str] = None,
        solo_activos: Optional[bool] = None,
        filtro_rol: Optional[str] = None,
        page: int = 1,
        limit: int = 20,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Reporte de personas con paginación real en PostgreSQL.

        Reemplaza la carga en memoria del RepositorioPersonaSQLite.

        Args:
            busqueda: Texto libre sobre nombre completo o número de documento.
            solo_activos: True=solo activos, False=solo inactivos, None=todos.
            filtro_rol: Nombre del rol (PROPIETARIOS, ARRENDATARIOS, etc.) para filtrar por tabla de rol.
            page: Página actual (1-indexed).
            limit: Registros por página.

        Returns:
            Tupla (lista de registros, total de registros).
        """
        # Mapa de nombres de rol de dominio a tablas de DB
        _MAPA_ROLES: Dict[str, str] = {
            "Propietario": "PROPIETARIOS",
            "Arrendatario": "ARRENDATARIOS",
            "Codeudor": "CODEUDORES",
            "Asesor": "ASESORES",
        }

        rol_tabla = _MAPA_ROLES.get(filtro_rol) if filtro_rol else None

        if rol_tabla:
            # Filtro por rol: JOIN a tabla específica
            query = f"""
                SELECT
                    p.ID_PERSONA,
                    p.TIPO_DOCUMENTO,
                    p.NUMERO_DOCUMENTO,
                    p.NOMBRE_COMPLETO,
                    p.TELEFONO_PRINCIPAL,
                    p.CORREO_ELECTRONICO,
                    p.DIRECCION_PRINCIPAL,
                    p.ESTADO_REGISTRO
                FROM PERSONAS p
                INNER JOIN {rol_tabla} r ON p.ID_PERSONA = r.ID_PERSONA
            """
        else:
            query = """
                SELECT
                    p.ID_PERSONA,
                    p.TIPO_DOCUMENTO,
                    p.NUMERO_DOCUMENTO,
                    p.NOMBRE_COMPLETO,
                    p.TELEFONO_PRINCIPAL,
                    p.CORREO_ELECTRONICO,
                    p.DIRECCION_PRINCIPAL,
                    p.ESTADO_REGISTRO
                FROM PERSONAS p
            """

        conditions = []
        params = []

        if busqueda:
            conditions.append(
                "(p.NOMBRE_COMPLETO ILIKE %s OR p.NUMERO_DOCUMENTO ILIKE %s)"
            )
            params.extend([f"%{busqueda}%", f"%{busqueda}%"])

        if solo_activos is True:
            conditions.append("p.ESTADO_REGISTRO = %s")
            params.append(True)
        elif solo_activos is False:
            conditions.append("p.ESTADO_REGISTRO = %s")
            params.append(False)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY p.NOMBRE_COMPLETO"

        return self._ejecutar_query_paginada(query, params, page, limit)

    def obtener_reporte_propiedades(
        self,
        busqueda: Optional[str] = None,
        solo_activas: Optional[bool] = None,
        page: int = 1,
        limit: int = 20,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Reporte de propiedades con paginación real en PostgreSQL.

        Reemplaza la carga en memoria del RepositorioPropiedadSQLite.

        Args:
            busqueda: Texto libre sobre dirección o matrícula inmobiliaria.
            solo_activas: True=solo activas, False=solo inactivas, None=todas.
            page: Página actual (1-indexed).
            limit: Registros por página.

        Returns:
            Tupla (lista de registros, total de registros).
        """
        query = """
            SELECT
                p.ID_PROPIEDAD,
                p.MATRICULA_INMOBILIARIA,
                p.DIRECCION_PROPIEDAD,
                p.TIPO_PROPIEDAD,
                p.AREA_M2,
                p.HABITACIONES,
                p.ESTRATO,
                p.VALOR_ADMINISTRACION,
                p.CANON_ARRENDAMIENTO_ESTIMADO,
                p.DISPONIBILIDAD_PROPIEDAD,
                p.ESTADO_REGISTRO
            FROM PROPIEDADES p
        """
        conditions = []
        params = []

        if busqueda:
            conditions.append(
                "(p.DIRECCION_PROPIEDAD ILIKE %s OR p.MATRICULA_INMOBILIARIA ILIKE %s)"
            )
            params.extend([f"%{busqueda}%", f"%{busqueda}%"])

        if solo_activas is True:
            conditions.append("p.ESTADO_REGISTRO = %s")
            params.append(True)
        elif solo_activas is False:
            conditions.append("p.ESTADO_REGISTRO = %s")
            params.append(False)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY p.MATRICULA_INMOBILIARIA"

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
                l.IVA_COMISION, l.IMPUESTO_4X1000, l.SEGURO_MONTO as "Seguro_Arrendamiento",
                l.GASTOS_ADMINISTRACION, l.GASTOS_SERVICIOS, l.GASTOS_REPARACIONES, l.PAGO_PREDIAL,
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

    def obtener_reporte_liquidaciones_asesores(
        self,
        asesor_id: Optional[int] = None,
        busqueda: Optional[str] = None,
        page: int = 1,
        limit: int = 20,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Reporte especializado de liquidaciones de asesores con pivoteo de descuentos sistémicos."""
        query = """
            SELECT 
                la.ID_LIQUIDACION_ASESOR AS "ID",
                p.NOMBRE_COMPLETO AS "Nombre_Asesor",
                la.PERIODO_LIQUIDACION AS "Periodo",
                la.CANON_ARRENDAMIENTO_LIQUIDADO AS "Canon_Liquidado",
                la.PORCENTAJE_COMISION AS "%%_Comision",
                la.COMISION_BRUTA AS "Comision_Bruta",
                COALESCE(la.TOTAL_BONIFICACIONES, 0) AS "Bonificaciones",
                la.TOTAL_DESCUENTOS AS "Total_Descuentos",
                (SELECT COALESCE(SUM(VALOR_DESCUENTO), 0) FROM DESCUENTOS_ASESORES WHERE ID_LIQUIDACION_ASESOR = la.ID_LIQUIDACION_ASESOR AND DESCRIPCION_DESCUENTO ILIKE '%%4x1000%%') AS "Descuento_4x1000",
                (SELECT COALESCE(SUM(VALOR_DESCUENTO), 0) FROM DESCUENTOS_ASESORES WHERE ID_LIQUIDACION_ASESOR = la.ID_LIQUIDACION_ASESOR AND DESCRIPCION_DESCUENTO ILIKE '%%Seguro%%') AS "Descuento_Seguro",
                la.VALOR_NETO_ASESOR AS "Neto_Asesor",
                la.ESTADO_LIQUIDACION AS "Estado",
                la.FECHA_CREACION AS "Fecha_Creacion",
                la.USUARIO_CREADOR AS "Usuario"
            FROM LIQUIDACIONES_ASESORES la
            JOIN ASESORES a ON la.ID_ASESOR = a.ID_ASESOR
            JOIN PERSONAS p ON a.ID_PERSONA = p.ID_PERSONA
        """
        conditions = []
        params = []

        if asesor_id:
            conditions.append("la.ID_ASESOR = %s")
            params.append(asesor_id)

        if busqueda:
            conditions.append("""(
                p.NOMBRE_COMPLETO ILIKE %s OR 
                la.PERIODO_LIQUIDACION ILIKE %s OR
                CAST(la.ID_LIQUIDACION_ASESOR AS TEXT) ILIKE %s
            )""")
            params.extend([f"%{busqueda}%"] * 3)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY la.ID_LIQUIDACION_ASESOR DESC"

        return self._ejecutar_query_paginada(query, params, page, limit)

    def obtener_reporte_generico(
        self, tabla: str, busqueda: Optional[str] = None, page: int = 1, limit: int = 20
    ) -> Tuple[List[Dict[str, Any]], int]:
        """Obtiene todos los registros de una tabla con búsqueda simple y paginación."""
        _TABLAS_PERMITIDAS = {
            "PERSONAS", "PROPIETARIOS", "ARRENDATARIOS", "CODEUDORES", "ASESORES", "TERCEROS",
            "PROPIEDADES", "CONTRATOS_MANDATOS", "CONTRATOS_ARRENDAMIENTOS", "RECAUDOS", "LIQUIDACIONES", "INCIDENTES"
        }
        if tabla.upper() not in _TABLAS_PERMITIDAS:
            raise ValueError(f"Tabla genérica no permitida: {tabla}")
            
        query = f"SELECT * FROM {tabla.upper()}"
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
        ESTRATEGIA ÉLITE: Vinculación histórica por ID_PROPIEDAD para evitar pérdida de datos por renovaciones.
        SANITIZACIÓN: Uso de CHR(10)/CHR(13) para limpiar saltos de línea que rompen el CSV.
        """
        # Preparar filtros de liquidación dinámicos para el JOIN interno
        liq_filter_clauses = []
        liq_params = []
        
        if fecha_pago_inicio:
            liq_filter_clauses.append("l_inner.FECHA_PAGO >= %s")
            liq_params.append(fecha_pago_inicio)
        if fecha_pago_fin:
            liq_filter_clauses.append("l_inner.FECHA_PAGO <= %s")
            liq_params.append(fecha_pago_fin)
        if periodo_inicio:
            liq_filter_clauses.append("l_inner.PERIODO >= %s")
            liq_params.append(periodo_inicio)
        if periodo_fin:
            liq_filter_clauses.append("l_inner.PERIODO <= %s")
            liq_params.append(periodo_fin)
            
        liq_where = ""
        if liq_filter_clauses:
            liq_where = " WHERE " + " AND ".join(liq_filter_clauses)

        query = f"""
            SELECT
                -- 1. Claves e IDs
                cm.ID_CONTRATO_M AS "ID_CONTRATO_M",
                p.ID_PROPIEDAD AS "ID_PROPIEDAD",
                COALESCE(l.ID_LIQUIDACION, 0) AS "ID_LIQUIDACION",

                -- 2. Información del Propietario
                per_prop.TIPO_DOCUMENTO AS "TIPO_DOCUMENTO_PROPIETARIO",
                per_prop.NUMERO_DOCUMENTO AS "NUMERO_DOCUMENTO_PROPIETARIO",
                per_prop.NOMBRE_COMPLETO AS "NOMBRE_COMPLETO_PROPIETARIO",
                cm.BANCO_PROPIETARIO AS "BANCO_PROPIETARIO",
                cm.NUMERO_CUENTA_PROPIETARIO AS "NUMERO_CUENTA_PROPIETARIO",
                cm.TIPO_CUENTA AS "TIPO_CUENTA_PROPIETARIO",
                COALESCE(cm.CONSIGNATARIO, '') AS "CONSIGNATARIO_PROPIETARIO",
                COALESCE(cm.DOCUMENTO_CONSIGNATARIO, '') AS "DOCUMENTO_CONSIGNATARIO_PROPIETARIO",

                -- 3. Información del Inmueble (Sanitizada para CSV)
                REPLACE(REPLACE(p.DIRECCION_PROPIEDAD, CHR(10), ' '), CHR(13), '') AS "DIRECCION_PROPIEDAD",
                cm.ESTADO_CONTRATO_M AS "ESTADO_CONTRATO",
                cm.FECHA_INICIO_CONTRATO_M AS "FECHA_INICIO_CONTRATO",
                cm.FECHA_FIN_CONTRATO_M AS "FECHA_FIN_CONTRATO",
                cm.FECHA_PAGO AS "FECHA_PAGO_CONTRATO",
                cm.CANON_MANDATO AS "CANON_MANDATO",

                -- 4. Información de la Propiedad Horizontal
                COALESCE(p.VALOR_ADMINISTRACION, 0)          AS "VALOR_ADMIN_PROPIEDAD_BASE",
                p.FECHA_PAGO_ADMINISTRACION                  AS "DIA_PAGO_ADMIN",
                COALESCE(p.LINK_PAGO_ADMINISTRACION, '')     AS "LINK_PAGO_ADMIN",
                COALESCE(p.CUOTA_EXTRA_ORDINARIA, 0)         AS "CUOTA_EXTRA",
                REPLACE(REPLACE(COALESCE(p.OBSERVACIONES_ADMIN_PH, ''), CHR(10), ' '), CHR(13), '') AS "OBSERVACIONES_ADMIN_PH",
                CASE WHEN l.GASTOS_ADMINISTRACION > 0 AND l.ESTADO_LIQUIDACION = 'Pagada'
                     THEN 'Pagado'
                     WHEN l.GASTOS_ADMINISTRACION > 0 THEN 'Pendiente'
                     ELSE 'N/A'
                END AS "ESTADO_PAGO_ADMINISTRACION",

                -- 5. Información del Arrendatario
                COALESCE(ca.ESTADO_CONTRATO_A, 'N/A') AS "ESTADO_ARRIENDO",
                per_arr.NUMERO_DOCUMENTO AS "NUMERO_DOCUMENTO_ARRENDATARIO",
                per_arr.NOMBRE_COMPLETO AS "NOMBRE_COMPLETO_ARRENDATARIO",
                COALESCE(arr.NOMBRE_HABITANTE, '') AS "NOMBRE_COMPLETO_HABITANTE",

                -- 6. Recaudos y Gestión Comercial
                COALESCE(r.METODO_PAGO, 'N/A') AS "METODO_PAGO_RECAUDOS",
                COALESCE(l.PERIODO, 'N/A') AS "PERIODO_FACTURADO",
                COALESCE(per_ase.NOMBRE_COMPLETO, 'No asignado') AS "NOMBRE_ASESOR",

                -- 7. Composición Financiera (Ingresos)
                COALESCE(l.OTROS_INGRESOS, 0) AS "OTROS_INGRESOS",
                COALESCE(l.TOTAL_INGRESOS, 0) AS "TOTAL_INGRESOS",

                -- 8. Composición Financiera (Egresos y Retenciones)
                COALESCE(l.COMISION_PORCENTAJE, 0) AS "COMISION_PORCENTAJE_ASESOR",
                COALESCE(l.COMISION_MONTO, 0) AS "COMISION_MONTO_ASESOR",
                COALESCE(l.IVA_COMISION, 0) AS "IVA_COMISION",
                COALESCE(l.GASTOS_ADMINISTRACION, 0) AS "GASTOS_ADMINISTRACION",
                COALESCE(l.GASTOS_SERVICIOS, 0) AS "GASTOS_SERVICIOS",
                COALESCE(l.GASTOS_REPARACIONES, 0) AS "GASTOS_REPARACIONES",
                COALESCE(l.PAGO_PREDIAL, 0) AS "PAGO_PREDIAL",
                COALESCE(l.OTROS_EGRESOS, 0) AS "OTROS_EGRESOS",
                (COALESCE(l.COMISION_MONTO, 0) + 
                 COALESCE(l.IVA_COMISION, 0) + 
                 COALESCE(l.GASTOS_ADMINISTRACION, 0) + 
                 COALESCE(l.GASTOS_SERVICIOS, 0) + 
                 COALESCE(l.GASTOS_REPARACIONES, 0) + 
                 COALESCE(l.PAGO_PREDIAL, 0) + 
                 COALESCE(l.OTROS_EGRESOS, 0)) AS "TOTAL_EGRESOS",

                -- 9. Cierre Financiero (Liquidación)
                (COALESCE(l.TOTAL_INGRESOS, 0) - 
                 (COALESCE(l.COMISION_MONTO, 0) + 
                  COALESCE(l.IVA_COMISION, 0) + 
                  COALESCE(l.GASTOS_ADMINISTRACION, 0) + 
                  COALESCE(l.GASTOS_SERVICIOS, 0) + 
                  COALESCE(l.GASTOS_REPARACIONES, 0) + 
                  COALESCE(l.PAGO_PREDIAL, 0) + 
                  COALESCE(l.OTROS_EGRESOS, 0))) AS "NETO_A_PAGAR",
                COALESCE(l.ESTADO_LIQUIDACION, 'Sin Liquidar') AS "ESTADO_LIQUIDACION",
                l.FECHA_PAGO AS "FECHA_PAGO",
                l.PERIODO AS "PERIODO",
                COALESCE(r.ESTADO_RECAUDO, 'N/A') AS "ESTADO_RECAUDO"

            FROM CONTRATOS_MANDATOS cm
            LEFT JOIN PROPIEDADES p ON cm.ID_PROPIEDAD = p.ID_PROPIEDAD
            LEFT JOIN PROPIETARIOS prop ON cm.ID_PROPIETARIO = prop.ID_PROPIETARIO
            LEFT JOIN PERSONAS per_prop ON prop.ID_PERSONA = per_prop.ID_PERSONA
            LEFT JOIN ASESORES a ON cm.ID_ASESOR = a.ID_ASESOR
            LEFT JOIN PERSONAS per_ase ON a.ID_PERSONA = per_ase.ID_PERSONA
            
            -- JOIN Liquidaciones histórico vinculado por propiedad para sobrevivir a renovaciones
            LEFT JOIN (
                SELECT l_inner.*, cm_inner.ID_PROPIEDAD 
                FROM liquidaciones l_inner
                JOIN CONTRATOS_MANDATOS cm_inner ON l_inner.ID_CONTRATO_M = cm_inner.ID_CONTRATO_M
                {liq_where}
            ) l ON p.ID_PROPIEDAD = l.ID_PROPIEDAD
            
            -- JOIN Arrendamientos flexibilizado (Inquilino actual)
            LEFT JOIN (
                SELECT DISTINCT ON (ca_inner.ID_PROPIEDAD)
                    ca_inner.ID_CONTRATO_A,
                    ca_inner.ID_PROPIEDAD,
                    ca_inner.ID_ARRENDATARIO,
                    ca_inner.ESTADO_CONTRATO_A,
                    ca_inner.FECHA_INICIO_CONTRATO_A
                FROM CONTRATOS_ARRENDAMIENTOS ca_inner
                WHERE ca_inner.ESTADO_CONTRATO_A IN ('ACTIVO', 'En Mora', 'Renovado')
                ORDER BY ca_inner.ID_PROPIEDAD, ca_inner.FECHA_INICIO_CONTRATO_A DESC
            ) ca ON p.ID_PROPIEDAD = ca.ID_PROPIEDAD
            
            LEFT JOIN ARRENDATARIOS arr ON ca.ID_ARRENDATARIO = arr.ID_ARRENDATARIO
            LEFT JOIN PERSONAS per_arr ON arr.ID_PERSONA = per_arr.ID_PERSONA
            
            -- JOIN Recaudos histórico sincronizado por propiedad y periodo financiero
            LEFT JOIN (
                SELECT DISTINCT ON (ca_inner2.ID_PROPIEDAD, rc_inner.PERIODO)
                    r_inner.ID_RECAUDO, r_inner.METODO_PAGO, r_inner.ESTADO_RECAUDO, r_inner.FECHA_PAGO, rc_inner.PERIODO, ca_inner2.ID_PROPIEDAD
                FROM RECAUDOS r_inner
                JOIN RECAUDO_CONCEPTOS rc_inner ON r_inner.ID_RECAUDO = rc_inner.ID_RECAUDO
                JOIN CONTRATOS_ARRENDAMIENTOS ca_inner2 ON r_inner.ID_CONTRATO_A = ca_inner2.ID_CONTRATO_A
                ORDER BY ca_inner2.ID_PROPIEDAD, rc_inner.PERIODO, r_inner.FECHA_PAGO DESC, r_inner.ID_RECAUDO DESC
            ) r ON p.ID_PROPIEDAD = r.ID_PROPIEDAD AND l.PERIODO = r.PERIODO
        """

        conditions = []
        # Parámetros: primero los de liquidación (inyectados en el FROM), luego los de conditions
        params = list(liq_params)

        # REGLA FUNCIONAL: Mandato Activo + Arrendamiento Activo/Mora
        conditions.append("cm.ESTADO_CONTRATO_M = 'ACTIVO'")
        conditions.append("ca.ID_CONTRATO_A IS NOT NULL")

        # Filtro: Estado de Liquidación (ahora filtrado sobre el resultado del JOIN)
        if estado_liquidacion and estado_liquidacion != "Todos":
            if estado_liquidacion == "Sin Liquidar":
                conditions.append("l.ID_LIQUIDACION IS NULL")
            else:
                conditions.append("l.ESTADO_LIQUIDACION = %s")
                params.append(estado_liquidacion)

        # Filtro: Asesor
        if asesor_id:
            conditions.append("cm.ID_ASESOR = %s")
            params.append(asesor_id)

        # Filtro: Propietario
        if propietario_buscar:
            conditions.append("""(
                per_prop.NOMBRE_COMPLETO ILIKE %s OR
                per_prop.NUMERO_DOCUMENTO ILIKE %s
            )""")
            params.extend([f"%{propietario_buscar}%", f"%{propietario_buscar}%"])

        # Búsqueda general
        if busqueda:
            conditions.append("""(
                per_prop.NOMBRE_COMPLETO ILIKE %s OR
                per_arr.NOMBRE_COMPLETO ILIKE %s OR
                p.DIRECCION_PROPIEDAD ILIKE %s OR
                per_ase.NOMBRE_COMPLETO ILIKE %s OR
                cm.ID_CONTRATO_M::TEXT ILIKE %s OR
                p.MATRICULA_INMOBILIARIA ILIKE %s
            )""")
            params.extend([f"%{busqueda}%"] * 6)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        # Order by
        query += " ORDER BY l.FECHA_PAGO DESC NULLS LAST, cm.FECHA_INICIO_CONTRATO_M DESC, cm.ID_CONTRATO_M DESC"

        return self._ejecutar_query_paginada(query, params, page, limit)
