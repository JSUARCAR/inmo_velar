"""
Repositorio PostgreSQL para Dashboard.
Implementa consultas agregadas para métricas.
"""

from typing import List, Optional, Dict
from src.infraestructura.persistencia.database import DatabaseManager
from src.dominio.interfaces.repositorio_dashboard import IRepositorioDashboard


class RepositorioDashboard(IRepositorioDashboard):
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def _get_sql_mora_diaria(self) -> str:
        if self.db.use_postgresql:
            return """
                SELECT 
                    ca.ID_CONTRATO_A,
                    per.NOMBRE_COMPLETO AS ARRENDATARIO,
                    p.DIRECCION_PROPIEDAD AS PROPIEDAD,
                    ca.CANON_ARRENDAMIENTO AS VALOR_RECAUDO,
                    '' AS BARRIO,
                    m.NOMBRE_MUNICIPIO AS MUNICIPIO,
                    (CURRENT_DATE - (
                        TO_CHAR(CURRENT_DATE, 'YYYY-MM') || '-' || LPAD(ca.FECHA_PAGO::TEXT, 2, '0')
                    )::DATE)::INTEGER AS DIAS_RETRASO
                FROM CONTRATOS_ARRENDAMIENTOS ca
                JOIN PROPIEDADES p ON ca.ID_PROPIEDAD = p.ID_PROPIEDAD
                JOIN MUNICIPIOS m ON p.ID_MUNICIPIO = m.ID_MUNICIPIO
                JOIN ARRENDATARIOS a ON ca.ID_ARRENDATARIO = a.ID_ARRENDATARIO
                JOIN PERSONAS per ON a.ID_PERSONA = per.ID_PERSONA
                WHERE ca.ESTADO_CONTRATO_A = 'ACTIVO'
                AND EXTRACT(DAY FROM CURRENT_DATE) > ca.FECHA_PAGO::INTEGER
                AND NOT EXISTS (
                    SELECT 1 
                    FROM RECAUDOS r 
                    WHERE r.ID_CONTRATO_A = ca.ID_CONTRATO_A 
                    AND EXTRACT(MONTH FROM r.FECHA_PAGO::DATE) = EXTRACT(MONTH FROM CURRENT_DATE)
                    AND EXTRACT(YEAR FROM r.FECHA_PAGO::DATE) = EXTRACT(YEAR FROM CURRENT_DATE)
                    AND r.ESTADO_RECAUDO = 'Aplicado'
                )
            """
        else:
            return """
                SELECT 
                    ca.ID_CONTRATO_A,
                    per.NOMBRE_COMPLETO AS ARRENDATARIO,
                    p.DIRECCION_PROPIEDAD AS PROPIEDAD,
                    ca.CANON_ARRENDAMIENTO AS VALOR_RECAUDO,
                    '' AS BARRIO,
                    m.NOMBRE_MUNICIPIO AS MUNICIPIO,
                    CAST(julianday('now') - julianday(strftime('%Y-%m', 'now') || '-' || substr('0' || ca.FECHA_PAGO, -2, 2)) AS INTEGER) AS DIAS_RETRASO
                FROM CONTRATOS_ARRENDAMIENTOS ca
                JOIN PROPIEDADES p ON ca.ID_PROPIEDAD = p.ID_PROPIEDAD
                JOIN MUNICIPIOS m ON p.ID_MUNICIPIO = m.ID_MUNICIPIO
                JOIN ARRENDATARIOS a ON ca.ID_ARRENDATARIO = a.ID_ARRENDATARIO
                JOIN PERSONAS per ON a.ID_PERSONA = per.ID_PERSONA
                WHERE ca.ESTADO_CONTRATO_A = 'ACTIVO'
                AND CAST(strftime('%d', 'now') AS INTEGER) > CAST(ca.FECHA_PAGO AS INTEGER)
                AND NOT EXISTS (
                    SELECT 1 
                    FROM RECAUDOS r 
                    WHERE r.ID_CONTRATO_A = ca.ID_CONTRATO_A 
                    AND strftime('%m', r.FECHA_PAGO) = strftime('%m', 'now')
                    AND strftime('%Y', r.FECHA_PAGO) = strftime('%Y', 'now')
                    AND r.ESTADO_RECAUDO = 'Aplicado'
                )
            """

    def obtener_resumen_mora(self) -> Dict:
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            query = f"WITH mora AS ({self._get_sql_mora_diaria()}) SELECT COUNT(*) AS CANTIDAD, SUM(VALOR_RECAUDO) AS MONTO_TOTAL FROM mora"
            cursor.execute(query)
            resumen = cursor.fetchone()
            return {
                "monto_total": resumen["MONTO_TOTAL"] or 0,
                "cantidad_contratos": resumen["CANTIDAD"] or 0,
            }

    def obtener_top_morosos(self, limit: int = 5) -> List[Dict]:
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            placeholder = self.db.get_placeholder()
            query = f"WITH mora AS ({self._get_sql_mora_diaria()}) SELECT ARRENDATARIO, DIAS_RETRASO, VALOR_RECAUDO FROM mora ORDER BY DIAS_RETRASO DESC, VALOR_RECAUDO DESC LIMIT {placeholder}"
            cursor.execute(query, (limit,))
            return [
                {
                    "nombre": row["ARRENDATARIO"],
                    "dias_retraso": row["DIAS_RETRASO"],
                    "monto": row["VALOR_RECAUDO"],
                }
                for row in cursor.fetchall()
            ]

    def obtener_morosidad_por_zona(self) -> Dict:
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            query = f"WITH mora AS ({self._get_sql_mora_diaria()}) SELECT MUNICIPIO, BARRIO, SUM(VALOR_RECAUDO) AS TOTAL FROM mora GROUP BY MUNICIPIO, BARRIO ORDER BY TOTAL DESC"
            cursor.execute(query)
            return {
                f"{row['MUNICIPIO']} - {row['BARRIO']}": row["TOTAL"]
                for row in cursor.fetchall()
                if row["BARRIO"] and row["MUNICIPIO"]
            }

    def obtener_desempeno_asesores(self) -> Dict:
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            query = """
                SELECT 
                    per.NOMBRE_COMPLETO AS ASESOR,
                    COUNT(cm.ID_CONTRATO_M) AS TOTAL_CONTRATOS,
                    SUM(CASE WHEN ca.ESTADO_CONTRATO_A = 'ACTIVO' THEN 1 ELSE 0 END) AS CONTRATOS_ACTIVOS
                FROM ASESORES a
                JOIN PERSONAS per ON a.ID_PERSONA = per.ID_PERSONA
                LEFT JOIN CONTRATOS_MANDATOS cm ON a.ID_ASESOR = cm.ID_ASESOR
                LEFT JOIN CONTRATOS_ARRENDAMIENTOS ca ON cm.ID_PROPIEDAD = ca.ID_PROPIEDAD
                GROUP BY per.NOMBRE_COMPLETO
            """
            cursor.execute(query)
            return [
                {
                    "asesor": row["ASESOR"],
                    "total_contratos": row["TOTAL_CONTRATOS"],
                    "contratos_activos": row["CONTRATOS_ACTIVOS"],
                }
                for row in cursor.fetchall()
            ]

    def obtener_total_recaudado(
        self, mes: str, anio: str, id_asesor: Optional[int] = None
    ) -> float:
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            placeholder = self.db.get_placeholder()
            params = [mes, anio]

            query = """
                SELECT SUM(r.VALOR_TOTAL) AS TOTAL_RECAUDO
                FROM RECAUDOS r
                JOIN CONTRATOS_ARRENDAMIENTOS ca ON r.ID_CONTRATO_A = ca.ID_CONTRATO_A
            """

            if self.db.use_postgresql:
                where_date = f"TO_CHAR(r.FECHA_PAGO::DATE, 'MM') = {placeholder} AND TO_CHAR(r.FECHA_PAGO::DATE, 'YYYY') = {placeholder}"
            else:
                where_date = f"strftime('%m', r.FECHA_PAGO) = {placeholder} AND strftime('%Y', r.FECHA_PAGO) = {placeholder}"

            if id_asesor:
                query += (
                    " JOIN CONTRATOS_MANDATOS cm ON ca.ID_PROPIEDAD = cm.ID_PROPIEDAD "
                )
                where = f" WHERE {where_date} AND r.ESTADO_RECAUDO = 'Aplicado' AND cm.ID_ASESOR = {placeholder} AND cm.ESTADO_CONTRATO_M = 'ACTIVO'"
                params.append(id_asesor)
            else:
                where = f" WHERE {where_date} AND r.ESTADO_RECAUDO = 'Aplicado'"

            cursor.execute(query + where, params)
            res = cursor.fetchone()
            return res["TOTAL_RECAUDO"] if res and res["TOTAL_RECAUDO"] else 0

    def obtener_historico_recaudos(
        self, meses: int, mes_fin: int, anio_fin: int, id_asesor: Optional[int] = None
    ) -> Dict[str, float]:
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            placeholder = self.db.get_placeholder()

            asesor_join = ""
            asesor_where = ""
            if id_asesor:
                asesor_join = " JOIN CONTRATOS_ARRENDAMIENTOS ca ON r.ID_CONTRATO_A = ca.ID_CONTRATO_A JOIN CONTRATOS_MANDATOS cm ON ca.ID_PROPIEDAD = cm.ID_PROPIEDAD "
                asesor_where = f" AND cm.ID_ASESOR = {placeholder} "

            if self.db.use_postgresql:
                query = f"""
                    SELECT 
                        TO_CHAR(r.FECHA_PAGO::DATE, 'MM/YYYY') AS MES_ANIO,
                        SUM(r.VALOR_TOTAL) AS TOTAL_RECAUDO
                    FROM RECAUDOS r
                    {asesor_join}
                    WHERE r.ESTADO_RECAUDO = 'Aplicado'
                    {asesor_where}
                    AND r.FECHA_PAGO::DATE >= DATE_TRUNC('month', TO_DATE(%(fin)s, 'YYYY-MM-DD') - INTERVAL %(intervalo)s)
                    AND r.FECHA_PAGO::DATE < DATE_TRUNC('month', TO_DATE(%(fin)s, 'YYYY-MM-DD') + INTERVAL '1 month')
                    GROUP BY TO_CHAR(r.FECHA_PAGO::DATE, 'MM/YYYY')
                """
                fecha_fin = f"{anio_fin}-{mes_fin:02d}-01"
                intervalo = f"{meses - 1} months"
                params = {"fin": fecha_fin, "intervalo": intervalo}
                if id_asesor:
                    # Mezclamos named params y positional params, psycopg2 no permite mezclar así, mejor usar named param
                    # Ya que placeholder es %s, para postgres es preferible named o todo positional
                    # Como ya usábamos named, vamos a cambiar todo a positional para PG
                    query = query.replace("%(fin)s", "%s").replace(
                        "%(intervalo)s", "%s"
                    )
                    cursor.execute(query, (id_asesor, fecha_fin, intervalo, fecha_fin))
                else:
                    query = query.replace("%(fin)s", "%s").replace(
                        "%(intervalo)s", "%s"
                    )
                    cursor.execute(query, (fecha_fin, intervalo, fecha_fin))
            else:
                query = f"""
                    SELECT 
                        strftime('%m/%Y', r.FECHA_PAGO) AS MES_ANIO,
                        SUM(r.VALOR_TOTAL) AS TOTAL_RECAUDO
                    FROM RECAUDOS r
                    {asesor_join}
                    WHERE r.ESTADO_RECAUDO = 'Aplicado'
                    {asesor_where}
                    AND date(r.FECHA_PAGO) >= date(?, 'start of month', '-' || ? || ' months')
                    AND date(r.FECHA_PAGO) < date(?, 'start of month', '+1 month')
                    GROUP BY strftime('%m/%Y', r.FECHA_PAGO)
                """
                fecha_fin = f"{anio_fin}-{mes_fin:02d}-01"
                intervalo_str = str(meses - 1)

                params = []
                if id_asesor:
                    params.append(id_asesor)
                params.extend([fecha_fin, intervalo_str, fecha_fin])
                cursor.execute(query, tuple(params))

            resultados = cursor.fetchall()
            return {
                row["MES_ANIO"]: float(row["TOTAL_RECAUDO"] or 0) for row in resultados
            }

    def obtener_total_esperado(self, id_asesor: Optional[int] = None) -> float:
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            placeholder = self.db.get_placeholder()

            query = "SELECT SUM(ca.CANON_ARRENDAMIENTO) AS TOTAL_ESPERADO FROM CONTRATOS_ARRENDAMIENTOS ca "
            params = []
            if id_asesor:
                query += f" JOIN CONTRATOS_MANDATOS cm ON ca.ID_PROPIEDAD = cm.ID_PROPIEDAD WHERE ca.ESTADO_CONTRATO_A = 'ACTIVO' AND cm.ID_ASESOR = {placeholder} AND cm.ESTADO_CONTRATO_M = 'ACTIVO' "
                params.append(id_asesor)
            else:
                query += " WHERE ca.ESTADO_CONTRATO_A = 'ACTIVO' "

            cursor.execute(query, tuple(params))
            res = cursor.fetchone()
            return float(res["TOTAL_ESPERADO"] or 0) if res else 0.0

    def _get_sql_vencimientos(self) -> str:
        if self.db.use_postgresql:
            return """
                SELECT 
                    'ARRENDAMIENTO' AS TIPO_CONTRATO,
                    ca.ID_CONTRATO_A AS ID_CONTRATO,
                    ca.ID_PROPIEDAD,
                    p.DIRECCION_PROPIEDAD AS DIRECCION,
                    per.NOMBRE_COMPLETO AS INQUILINO_PROPIETARIO,
                    ca.FECHA_FIN_CONTRATO_A AS FECHA_FIN,
                    (ca.FECHA_FIN_CONTRATO_A::DATE - CURRENT_DATE)::INTEGER AS DIAS_RESTANTES
                FROM CONTRATOS_ARRENDAMIENTOS ca
                JOIN PROPIEDADES p ON ca.ID_PROPIEDAD = p.ID_PROPIEDAD
                JOIN ARRENDATARIOS a ON ca.ID_ARRENDATARIO = a.ID_ARRENDATARIO
                JOIN PERSONAS per ON a.ID_PERSONA = per.ID_PERSONA
                WHERE ca.ESTADO_CONTRATO_A = 'ACTIVO' AND ca.FECHA_FIN_CONTRATO_A IS NOT NULL
            """
        else:
            return """
                SELECT 
                    'ARRENDAMIENTO' AS TIPO_CONTRATO,
                    ca.ID_CONTRATO_A AS ID_CONTRATO,
                    ca.ID_PROPIEDAD,
                    p.DIRECCION_PROPIEDAD AS DIRECCION,
                    per.NOMBRE_COMPLETO AS INQUILINO_PROPIETARIO,
                    ca.FECHA_FIN_CONTRATO_A AS FECHA_FIN,
                    CAST(julianday(ca.FECHA_FIN_CONTRATO_A) - julianday('now', 'localtime') AS INTEGER) AS DIAS_RESTANTES
                FROM CONTRATOS_ARRENDAMIENTOS ca
                JOIN PROPIEDADES p ON ca.ID_PROPIEDAD = p.ID_PROPIEDAD
                JOIN ARRENDATARIOS a ON ca.ID_ARRENDATARIO = a.ID_ARRENDATARIO
                JOIN PERSONAS per ON a.ID_PERSONA = per.ID_PERSONA
                WHERE ca.ESTADO_CONTRATO_A = 'ACTIVO' AND ca.FECHA_FIN_CONTRATO_A IS NOT NULL
            """

    def obtener_conteo_vencimientos_rangos(self) -> Dict:
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            query = f"""
                WITH vencimientos AS ({self._get_sql_vencimientos()})
                SELECT 
                    SUM(CASE WHEN DIAS_RESTANTES >= 0 AND DIAS_RESTANTES <= 30 THEN 1 ELSE 0 END) AS VENCE_30,
                    SUM(CASE WHEN DIAS_RESTANTES > 30 AND DIAS_RESTANTES <= 60 THEN 1 ELSE 0 END) AS VENCE_60,
                    SUM(CASE WHEN DIAS_RESTANTES > 60 AND DIAS_RESTANTES <= 90 THEN 1 ELSE 0 END) AS VENCE_90
                FROM vencimientos
                WHERE DIAS_RESTANTES >= 0 AND DIAS_RESTANTES <= 90
            """
            cursor.execute(query)
            r = cursor.fetchone()
            return {
                "vence_30_dias": r["VENCE_30"] or 0,
                "vence_60_dias": r["VENCE_60"] or 0,
                "vence_90_dias": r["VENCE_90"] or 0,
            }

    def obtener_lista_vencimientos(self, dias: int) -> List[Dict]:
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            placeholder = self.db.get_placeholder()
            query = f"WITH vencimientos AS ({self._get_sql_vencimientos()}) SELECT TIPO_CONTRATO, ID_PROPIEDAD, DIRECCION, INQUILINO_PROPIETARIO, FECHA_FIN, DIAS_RESTANTES FROM vencimientos WHERE DIAS_RESTANTES >= 0 AND DIAS_RESTANTES <= {placeholder} ORDER BY DIAS_RESTANTES ASC"
            cursor.execute(query, (dias,))
            return [
                {
                    "tipo_contrato": r["TIPO_CONTRATO"],
                    "id_propiedad": r["ID_PROPIEDAD"],
                    "direccion": r["DIRECCION"],
                    "parte_contratante": r["INQUILINO_PROPIETARIO"],
                    "fecha_fin": r["FECHA_FIN"],
                    "dias_restantes": r["DIAS_RESTANTES"],
                }
                for r in cursor.fetchall()
            ]

    def obtener_contratos_elegibles_ipc(self, dias: int) -> List[Dict]:
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            placeholder = self.db.get_placeholder()

            # Versión PostgreSQL: usa AGE, EXTRACT e intervalos
            if self.db.use_postgresql:
                query = f"""
                    WITH ProximosAniversarios AS (
                        SELECT 
                            ca.ID_CONTRATO_A, p.DIRECCION_PROPIEDAD, per.NOMBRE_COMPLETO AS INQUILINO,
                            ca.FECHA_INICIO_CONTRATO_A, ca.CANON_ARRENDAMIENTO,
                            -- NOTA: AGE() aquí es correcto: extraemos YEAR (años completos),
                            -- no DAY (días totales). Ver ADR-0010.
                            EXTRACT(YEAR FROM AGE(CURRENT_DATE, ca.FECHA_INICIO_CONTRATO_A::DATE))::INTEGER AS ANIOS_ACTIVOS,
                            (ca.FECHA_INICIO_CONTRATO_A::DATE + (EXTRACT(YEAR FROM AGE(CURRENT_DATE, ca.FECHA_INICIO_CONTRATO_A::DATE))::INTEGER + 1 || ' years')::INTERVAL)::DATE AS PROXIMO_ANIVERSARIO,
                            ((ca.FECHA_INICIO_CONTRATO_A::DATE + (EXTRACT(YEAR FROM AGE(CURRENT_DATE, ca.FECHA_INICIO_CONTRATO_A::DATE))::INTEGER + 1 || ' years')::INTERVAL)::DATE - CURRENT_DATE) AS DIAS_HASTA_ANIVERSARIO,
                            ipc.VALOR_IPC, ipc.ANIO
                        FROM CONTRATOS_ARRENDAMIENTOS ca
                        JOIN PROPIEDADES p ON ca.ID_PROPIEDAD = p.ID_PROPIEDAD
                        JOIN ARRENDATARIOS arr ON ca.ID_ARRENDATARIO = arr.ID_ARRENDATARIO
                        JOIN PERSONAS per ON arr.ID_PERSONA = per.ID_PERSONA
                        LEFT JOIN IPC ipc ON ipc.ANIO = EXTRACT(YEAR FROM CURRENT_DATE)::INTEGER - 1
                        WHERE ca.ESTADO_CONTRATO_A = 'ACTIVO' 
                        AND CURRENT_DATE - ca.FECHA_INICIO_CONTRATO_A::DATE >= 365 
                        AND ipc.VALOR_IPC IS NOT NULL
                    )
                    SELECT * FROM ProximosAniversarios 
                    WHERE DIAS_HASTA_ANIVERSARIO BETWEEN 0 AND {placeholder} 
                    ORDER BY DIAS_HASTA_ANIVERSARIO ASC
                """
            else:
                query = f"""
                    WITH ProximosAniversarios AS (
                        SELECT 
                            ca.ID_CONTRATO_A, p.DIRECCION_PROPIEDAD, per.NOMBRE_COMPLETO AS INQUILINO,
                            ca.FECHA_INICIO_CONTRATO_A, ca.CANON_ARRENDAMIENTO,
                            (strftime('%Y', 'now') - strftime('%Y', ca.FECHA_INICIO_CONTRATO_A)) - 
                            (strftime('%m-%d', 'now') < strftime('%m-%d', ca.FECHA_INICIO_CONTRATO_A)) AS ANIOS_ACTIVOS,
                            date(ca.FECHA_INICIO_CONTRATO_A, '+' || ((strftime('%Y', 'now') - strftime('%Y', ca.FECHA_INICIO_CONTRATO_A)) - 
                            (strftime('%m-%d', 'now') < strftime('%m-%d', ca.FECHA_INICIO_CONTRATO_A)) + 1) || ' years') AS PROXIMO_ANIVERSARIO,
                            CAST(julianday(date(ca.FECHA_INICIO_CONTRATO_A, '+' || ((strftime('%Y', 'now') - strftime('%Y', ca.FECHA_INICIO_CONTRATO_A)) - 
                            (strftime('%m-%d', 'now') < strftime('%m-%d', ca.FECHA_INICIO_CONTRATO_A)) + 1) || ' years')) - julianday('now') AS INTEGER) AS DIAS_HASTA_ANIVERSARIO,
                            ipc.VALOR_IPC, ipc.ANIO
                        FROM CONTRATOS_ARRENDAMIENTOS ca
                        JOIN PROPIEDADES p ON ca.ID_PROPIEDAD = p.ID_PROPIEDAD
                        JOIN ARRENDATARIOS arr ON ca.ID_ARRENDATARIO = arr.ID_ARRENDATARIO
                        JOIN PERSONAS per ON arr.ID_PERSONA = per.ID_PERSONA
                        LEFT JOIN IPC ipc ON ipc.ANIO = CAST(strftime('%Y', 'now') AS INTEGER) - 1
                        WHERE ca.ESTADO_CONTRATO_A = 'ACTIVO' 
                        AND CAST(julianday('now') - julianday(ca.FECHA_INICIO_CONTRATO_A) AS INTEGER) >= 365 
                        AND ipc.VALOR_IPC IS NOT NULL
                    )
                    SELECT * FROM ProximosAniversarios 
                    WHERE DIAS_HASTA_ANIVERSARIO BETWEEN 0 AND {placeholder} 
                    ORDER BY DIAS_HASTA_ANIVERSARIO ASC
                """
            cursor.execute(query, (dias,))
            return [
                {
                    "id_contrato": r["ID_CONTRATO_A"],
                    "direccion": r["DIRECCION_PROPIEDAD"],
                    "inquilino": r["INQUILINO"],
                    "fecha_inicio": r["FECHA_INICIO_CONTRATO_A"],
                    "canon_actual": r["CANON_ARRENDAMIENTO"],
                    "anios_activos": r["ANIOS_ACTIVOS"],
                    "proximo_aniversario": r["PROXIMO_ANIVERSARIO"],
                    "dias_hasta_aniversario": r["DIAS_HASTA_ANIVERSARIO"],
                    "ipc_porcentaje": r["VALOR_IPC"],
                    "ipc_anio": r["ANIO"],
                }
                for r in cursor.fetchall()
            ]

    def obtener_comisiones_pendientes(self, id_asesor: Optional[int] = None) -> Dict:
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            placeholder = self.db.get_placeholder()
            query = "SELECT COUNT(*) AS CANTIDAD, SUM(VALOR_NETO_ASESOR) AS MONTO_TOTAL FROM LIQUIDACIONES_ASESORES WHERE ESTADO_LIQUIDACION = 'Pendiente'"
            params = []
            if id_asesor:
                query += f" AND ID_ASESOR = {placeholder}"
                params.append(id_asesor)
            cursor.execute(query, params)
            r = cursor.fetchone()
            return {
                "monto_total": r["MONTO_TOTAL"] or 0,
                "cantidad_liquidaciones": r["CANTIDAD"] or 0,
            }

    def obtener_metricas_ocupacion(self, id_asesor: Optional[int] = None) -> Dict:
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            placeholder = self.db.get_placeholder()
            if id_asesor:
                query = f"SELECT SUM(CASE WHEN p.DISPONIBILIDAD_PROPIEDAD IS TRUE THEN 1 ELSE 0 END) AS DISPONIBLES, SUM(CASE WHEN p.DISPONIBILIDAD_PROPIEDAD IS FALSE THEN 1 ELSE 0 END) AS OCUPADAS FROM PROPIEDADES p JOIN CONTRATOS_MANDATOS cm ON p.ID_PROPIEDAD = cm.ID_PROPIEDAD WHERE cm.ID_ASESOR = {placeholder} AND cm.ESTADO_CONTRATO_M = 'ACTIVO' AND p.ESTADO_REGISTRO IS TRUE"
                cursor.execute(query, (id_asesor,))
            else:
                query = "SELECT SUM(CASE WHEN DISPONIBILIDAD_PROPIEDAD IS TRUE THEN 1 ELSE 0 END) AS DISPONIBLES, SUM(CASE WHEN DISPONIBILIDAD_PROPIEDAD IS FALSE THEN 1 ELSE 0 END) AS OCUPADAS FROM PROPIEDADES WHERE ESTADO_REGISTRO IS TRUE"
                cursor.execute(query)
            r = cursor.fetchone()
            disp, ocup = r["DISPONIBLES"] or 0, r["OCUPADAS"] or 0
            total = disp + ocup
            return {
                "ocupadas": ocup,
                "disponibles": disp,
                "total": total,
                "porcentaje_ocupacion": (
                    round((ocup / total * 100), 1) if total > 0 else 0
                ),
            }

    def obtener_propiedades_por_tipo(
        self, id_asesor: Optional[int] = None
    ) -> Dict[str, int]:
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            placeholder = self.db.get_placeholder()
            if id_asesor:
                query = f"SELECT p.TIPO_PROPIEDAD, COUNT(*) as CONTAR FROM PROPIEDADES p JOIN CONTRATOS_MANDATOS cm ON p.ID_PROPIEDAD = cm.ID_PROPIEDAD WHERE cm.ID_ASESOR = {placeholder} AND cm.ESTADO_CONTRATO_M = 'ACTIVO' AND p.ESTADO_REGISTRO IS TRUE GROUP BY p.TIPO_PROPIEDAD"
                cursor.execute(query, (id_asesor,))
            else:
                query = "SELECT TIPO_PROPIEDAD, COUNT(*) as CONTAR FROM PROPIEDADES WHERE ESTADO_REGISTRO IS TRUE GROUP BY TIPO_PROPIEDAD"
                cursor.execute(query)
            return {row["TIPO_PROPIEDAD"]: row["CONTAR"] for row in cursor.fetchall()}

    def obtener_metricas_expertas(
        self, id_asesor: Optional[int] = None
    ) -> Dict[str, float]:
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            placeholder = self.db.get_placeholder()

            asesor_cond = (
                f" AND ID_PROPIEDAD IN (SELECT ID_PROPIEDAD FROM CONTRATOS_MANDATOS WHERE ID_ASESOR = {placeholder} AND ESTADO_CONTRATO_M = 'ACTIVO')"
                if id_asesor
                else ""
            )

            if self.db.use_postgresql:
                q_rec = "SELECT SUM(VALOR_TOTAL) FROM RECAUDOS WHERE DATE_TRUNC('month', TO_DATE(FECHA_PAGO, 'YYYY-MM-DD')) = DATE_TRUNC('month', CURRENT_DATE) AND ESTADO_RECAUDO = 'Aplicado'"
            else:
                q_rec = "SELECT SUM(VALOR_TOTAL) FROM RECAUDOS WHERE strftime('%Y-%m', FECHA_PAGO) = strftime('%Y-%m', 'now') AND ESTADO_RECAUDO = 'Aplicado'"

            q_rec += (
                f" AND ID_CONTRATO_A IN (SELECT ID_CONTRATO_A FROM CONTRATOS_ARRENDAMIENTOS ca JOIN CONTRATOS_MANDATOS cm ON ca.ID_PROPIEDAD = cm.ID_PROPIEDAD WHERE cm.ID_ASESOR = {placeholder})"
                if id_asesor
                else ""
            )

            query = f"""
                SELECT 
                    (SELECT SUM(CANON_ARRENDAMIENTO_ESTIMADO) FROM PROPIEDADES WHERE ESTADO_REGISTRO IS TRUE {asesor_cond}) as potencial,
                    (SELECT SUM(CANON_ARRENDAMIENTO) FROM CONTRATOS_ARRENDAMIENTOS WHERE ESTADO_CONTRATO_A = 'ACTIVO' {asesor_cond}) as real,
                    ({q_rec}) as recaudado
            """

            params = []
            if id_asesor:
                params.extend([id_asesor, id_asesor, id_asesor])

            cursor.execute(query, tuple(params))
            row = cursor.fetchone()

            potencial = row["POTENCIAL"] or 0
            real = row["REAL"] or 0
            recaudado = row["RECAUDADO"] or 0

            return {
                "ocupacion_financiera": (
                    round((real / potencial * 100), 1) if potencial > 0 else 0
                ),
                "eficiencia_recaudo": (
                    round((recaudado / real * 100), 1) if real > 0 else 0
                ),
                "potencial_total": float(potencial),
                "recaudo_real": float(recaudado),
            }

    def obtener_top_asesores_revenue(self) -> List[Dict]:
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            query = "SELECT p.NOMBRE_COMPLETO as nombre, COUNT(cm.ID_CONTRATO_M) as contratos, SUM(cm.CANON_MANDATO * (cm.COMISION_PORCENTAJE_CONTRATO_M / 10000.0)) as revenue FROM CONTRATOS_MANDATOS cm JOIN ASESORES a ON cm.ID_ASESOR = a.ID_ASESOR JOIN PERSONAS p ON a.ID_PERSONA = p.ID_PERSONA WHERE cm.ESTADO_CONTRATO_M = 'ACTIVO' GROUP BY p.NOMBRE_COMPLETO ORDER BY revenue DESC LIMIT 5"
            cursor.execute(query)
            return [
                {
                    "nombre": r["NOMBRE"],
                    "contratos": int(r["CONTRATOS"]),
                    "revenue": float(r["REVENUE"]),
                }
                for r in cursor.fetchall()
            ]

    def obtener_tunel_vencimientos(self) -> List[Dict]:
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            if self.db.use_postgresql:
                query = "SELECT TO_CHAR(TO_DATE(FECHA_FIN_CONTRATO_A, 'YYYY-MM-DD'), 'YYYY-MM') as mes, SUM(CANON_ARRENDAMIENTO) as valor_riesgo FROM CONTRATOS_ARRENDAMIENTOS WHERE ESTADO_CONTRATO_A = 'ACTIVO' AND TO_DATE(FECHA_FIN_CONTRATO_A, 'YYYY-MM-DD') BETWEEN CURRENT_DATE AND (CURRENT_DATE + INTERVAL '12 months') GROUP BY mes ORDER BY mes"
            else:
                query = "SELECT strftime('%Y-%m', FECHA_FIN_CONTRATO_A) as mes, SUM(CANON_ARRENDAMIENTO) as valor_riesgo FROM CONTRATOS_ARRENDAMIENTOS WHERE ESTADO_CONTRATO_A = 'ACTIVO' AND date(FECHA_FIN_CONTRATO_A) BETWEEN date('now') AND date('now', '+12 months') GROUP BY mes ORDER BY mes"

            cursor.execute(query)
            return [
                {"mes": r["MES"], "valor_riesgo": float(r["VALOR_RIESGO"])}
                for r in cursor.fetchall()
            ]

    def obtener_metricas_incidentes(self) -> Dict:
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            cursor.execute(
                "SELECT ESTADO, COUNT(*) AS COUNT FROM INCIDENTES GROUP BY ESTADO"
            )
            res = {row["ESTADO"]: row["COUNT"] for row in cursor.fetchall()}
            return {"total": sum(res.values()), "por_estado": res}

    def obtener_total_contratos_activos(self, id_asesor: Optional[int] = None) -> int:
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            placeholder = self.db.get_placeholder()
            if id_asesor:
                query = f"SELECT COUNT(*) AS COUNT FROM CONTRATOS_ARRENDAMIENTOS ca JOIN CONTRATOS_MANDATOS cm ON ca.ID_PROPIEDAD = cm.ID_PROPIEDAD WHERE ca.ESTADO_CONTRATO_A = 'ACTIVO' AND cm.ID_ASESOR = {placeholder} AND cm.ESTADO_CONTRATO_M = 'ACTIVO'"
                cursor.execute(query, (id_asesor,))
            else:
                query = "SELECT COUNT(*) AS COUNT FROM CONTRATOS_ARRENDAMIENTOS WHERE ESTADO_CONTRATO_A = 'ACTIVO'"
                cursor.execute(query)
            r = cursor.fetchone()
            return r["COUNT"] if r else 0

    def obtener_recibos_vencidos_resumen(self) -> Dict:
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)

            if self.db.use_postgresql:
                query = """
                    SELECT COUNT(*) AS CANTIDAD, SUM(VALOR_RECIBO) AS MONTO_TOTAL 
                    FROM RECIBOS_PUBLICOS 
                    WHERE ESTADO != 'Pagado' AND CAST(FECHA_VENCIMIENTO AS DATE) < CURRENT_DATE
                """
            else:
                query = """
                    SELECT COUNT(*) AS CANTIDAD, SUM(VALOR_RECIBO) AS MONTO_TOTAL 
                    FROM RECIBOS_PUBLICOS 
                    WHERE ESTADO != 'Pagado' AND date(FECHA_VENCIMIENTO) < date('now')
                """

            cursor.execute(query)
            res = cursor.fetchone()
            return {
                "monto_total": res["MONTO_TOTAL"] or 0,
                "cantidad": res["CANTIDAD"] or 0,
            }
