"""
Repositorio SQLite para Dashboard.
Implementa consultas agregadas para métricas.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from src.infraestructura.persistencia.database import DatabaseManager
from src.dominio.interfaces.repositorio_dashboard import IRepositorioDashboard

class RepositorioDashboardSQLite(IRepositorioDashboard):
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def obtener_resumen_mora(self) -> Dict:
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            cursor.execute("SELECT COUNT(*) AS CANTIDAD, SUM(VALOR_RECAUDO) AS MONTO_TOTAL FROM VW_ALERTA_MORA_DIARIA")
            resumen = cursor.fetchone()
            return {"monto_total": resumen["MONTO_TOTAL"] or 0, "cantidad_contratos": resumen["CANTIDAD"] or 0}

    def obtener_top_morosos(self, limit: int = 5) -> List[Dict]:
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            cursor.execute(f"SELECT ARRENDATARIO, DIAS_RETRASO, VALOR_RECAUDO FROM VW_ALERTA_MORA_DIARIA ORDER BY DIAS_RETRASO DESC, VALOR_RECAUDO DESC LIMIT {limit}")
            return [{"nombre": row["ARRENDATARIO"], "dias_retraso": row["DIAS_RETRASO"], "monto": row["VALOR_RECAUDO"]} for row in cursor.fetchall()]

    def obtener_total_recaudado(self, mes: str, anio: str, id_asesor: Optional[int] = None) -> float:
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            placeholder = self.db.get_placeholder()
            params = [mes, anio]
            
            query = """
                SELECT SUM(r.VALOR_TOTAL) AS TOTAL_RECAUDO
                FROM RECAUDOS r
                JOIN CONTRATOS_ARRENDAMIENTOS ca ON r.ID_CONTRATO_A = ca.ID_CONTRATO_A
            """
            if id_asesor:
                query += " JOIN CONTRATOS_MANDATOS cm ON ca.ID_PROPIEDAD = cm.ID_PROPIEDAD "
                where = f" WHERE TO_CHAR(r.FECHA_PAGO::DATE, 'MM') = {placeholder} AND TO_CHAR(r.FECHA_PAGO::DATE, 'YYYY') = {placeholder} AND r.ESTADO_RECAUDO = 'Aplicado' AND cm.ID_ASESOR = {placeholder} AND cm.ESTADO_CONTRATO_M = 'Activo'"
                params.append(id_asesor)
            else:
                where = f" WHERE TO_CHAR(r.FECHA_PAGO::DATE, 'MM') = {placeholder} AND TO_CHAR(r.FECHA_PAGO::DATE, 'YYYY') = {placeholder} AND r.ESTADO_RECAUDO = 'Aplicado'"
            
            # Ajuste para SQLite si no es Postgres
            if not self.db.use_postgresql:
                where = where.replace("TO_CHAR(r.FECHA_PAGO::DATE, 'MM')", "strftime('%m', r.FECHA_PAGO)").replace("TO_CHAR(r.FECHA_PAGO::DATE, 'YYYY')", "strftime('%Y', r.FECHA_PAGO)")

            cursor.execute(query + where, params)
            res = cursor.fetchone()
            return res["TOTAL_RECAUDO"] if res and res["TOTAL_RECAUDO"] else 0

    def obtener_total_esperado(self, id_asesor: Optional[int] = None) -> float:
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            placeholder = self.db.get_placeholder()
            query = "SELECT SUM(ca.CANON_ARRENDAMIENTO) AS TOTAL_ESPERADO FROM CONTRATOS_ARRENDAMIENTOS ca"
            params = []
            if id_asesor:
                query += " JOIN CONTRATOS_MANDATOS cm ON ca.ID_PROPIEDAD = cm.ID_PROPIEDAD WHERE ca.ESTADO_CONTRATO_A = 'Activo' AND cm.ID_ASESOR = ? AND cm.ESTADO_CONTRATO_M = 'Activo' "
                params.append(id_asesor)
            else:
                query += " WHERE ca.ESTADO_CONTRATO_A = 'Activo' "
            cursor.execute(query, params)
            res = cursor.fetchone()
            return res["TOTAL_ESPERADO"] if res and res["TOTAL_ESPERADO"] else 0

    def obtener_conteo_vencimientos_rangos(self) -> Dict:
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            cursor.execute("""
                SELECT 
                    SUM(CASE WHEN DIAS_RESTANTES <= 30 THEN 1 ELSE 0 END) AS VENCE_30,
                    SUM(CASE WHEN DIAS_RESTANTES > 30 AND DIAS_RESTANTES <= 60 THEN 1 ELSE 0 END) AS VENCE_60,
                    SUM(CASE WHEN DIAS_RESTANTES > 60 AND DIAS_RESTANTES <= 90 THEN 1 ELSE 0 END) AS VENCE_90
                FROM VW_ALERTA_VENCIMIENTO_CONTRATOS
            """)
            r = cursor.fetchone()
            return {"vence_30_dias": r["VENCE_30"] or 0, "vence_60_dias": r["VENCE_60"] or 0, "vence_90_dias": r["VENCE_90"] or 0}

    def obtener_lista_vencimientos(self, dias: int) -> List[Dict]:
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            placeholder = self.db.get_placeholder()
            cursor.execute(f"SELECT TIPO_CONTRATO, ID_PROPIEDAD, DIRECCION, INQUILINO_PROPIETARIO, FECHA_FIN, DIAS_RESTANTES FROM VW_ALERTA_VENCIMIENTO_CONTRATOS WHERE DIAS_RESTANTES <= {placeholder} ORDER BY DIAS_RESTANTES ASC", (dias,))
            return [{"tipo_contrato": r["TIPO_CONTRATO"], "id_propiedad": r["ID_PROPIEDAD"], "direccion": r["DIRECCION"], "parte_contratante": r["INQUILINO_PROPIETARIO"], "fecha_fin": r["FECHA_FIN"], "dias_restantes": r["DIAS_RESTANTES"]} for r in cursor.fetchall()]

    def obtener_contratos_elegibles_ipc(self, dias: int) -> List[Dict]:
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            placeholder = self.db.get_placeholder()
            # SQL simplificado del servicio
            query = f"""
                WITH ProximosAniversarios AS (
                    SELECT 
                        ca.ID_CONTRATO_A, p.DIRECCION_PROPIEDAD, per.NOMBRE_COMPLETO AS INQUILINO,
                        ca.FECHA_INICIO_CONTRATO_A, ca.CANON_ARRENDAMIENTO,
                        CAST((julianday('now') - julianday(ca.FECHA_INICIO_CONTRATO_A)) / 365.25 AS INTEGER) AS ANIOS_ACTIVOS,
                        date(ca.FECHA_INICIO_CONTRATO_A, '+' || CAST((julianday('now') - julianday(ca.FECHA_INICIO_CONTRATO_A)) / 365.25 AS INTEGER) + 1 || ' years') AS PROXIMO_ANIVERSARIO,
                        CAST(julianday(date(ca.FECHA_INICIO_CONTRATO_A, '+' || CAST((julianday('now') - julianday(ca.FECHA_INICIO_CONTRATO_A)) / 365.25 AS INTEGER) + 1 || ' years')) - julianday('now') AS INTEGER) AS DIAS_HASTA_ANIVERSARIO,
                        ipc.VALOR_IPC, ipc.ANIO
                    FROM CONTRATOS_ARRENDAMIENTOS ca
                    JOIN PROPIEDADES p ON ca.ID_PROPIEDAD = p.ID_PROPIEDAD
                    JOIN ARRENDATARIOS arr ON ca.ID_ARRENDATARIO = arr.ID_ARRENDATARIO
                    JOIN PERSONAS per ON arr.ID_PERSONA = per.ID_PERSONA
                    LEFT JOIN IPC ipc ON ipc.ANIO = CAST(strftime('%Y', 'now') AS INTEGER) - 1
                    WHERE ca.ESTADO_CONTRATO_A = 'Activo' AND julianday('now') - julianday(ca.FECHA_INICIO_CONTRATO_A) >= 365 AND ipc.VALOR_IPC IS NOT NULL
                )
                SELECT * FROM ProximosAniversarios WHERE DIAS_HASTA_ANIVERSARIO BETWEEN 0 AND {placeholder} ORDER BY DIAS_HASTA_ANIVERSARIO ASC
            """
            cursor.execute(query, (dias,))
            return [{
                "id_contrato": r["ID_CONTRATO_A"], "direccion": r["DIRECCION_PROPIEDAD"], "inquilino": r["INQUILINO"],
                "fecha_inicio": r["FECHA_INICIO_CONTRATO_A"], "canon_actual": r["CANON_ARRENDAMIENTO"],
                "anios_activos": r["ANIOS_ACTIVOS"], "proximo_aniversario": r["PROXIMO_ANIVERSARIO"],
                "dias_hasta_aniversario": r["DIAS_HASTA_ANIVERSARIO"], "ipc_porcentaje": r["VALOR_IPC"], "ipc_anio": r["ANIO"]
            } for r in cursor.fetchall()]

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
            return {"monto_total": r["MONTO_TOTAL"] or 0, "cantidad_liquidaciones": r["CANTIDAD"] or 0}

    def obtener_metricas_ocupacion(self, id_asesor: Optional[int] = None) -> Dict:
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            placeholder = self.db.get_placeholder()
            if id_asesor:
                query = f"SELECT SUM(CASE WHEN p.DISPONIBILIDAD_PROPIEDAD IS TRUE THEN 1 ELSE 0 END) AS DISPONIBLES, SUM(CASE WHEN p.DISPONIBILIDAD_PROPIEDAD IS FALSE THEN 1 ELSE 0 END) AS OCUPADAS FROM PROPIEDADES p JOIN CONTRATOS_MANDATOS cm ON p.ID_PROPIEDAD = cm.ID_PROPIEDAD WHERE cm.ID_ASESOR = {placeholder} AND cm.ESTADO_CONTRATO_M = 'Activo' AND p.ESTADO_REGISTRO IS TRUE"
                cursor.execute(query, (id_asesor,))
            else:
                query = "SELECT SUM(CASE WHEN DISPONIBILIDAD_PROPIEDAD IS TRUE THEN 1 ELSE 0 END) AS DISPONIBLES, SUM(CASE WHEN DISPONIBILIDAD_PROPIEDAD IS FALSE THEN 1 ELSE 0 END) AS OCUPADAS FROM PROPIEDADES WHERE ESTADO_REGISTRO IS TRUE"
                cursor.execute(query)
            r = cursor.fetchone()
            disp, ocup = r["DISPONIBLES"] or 0, r["OCUPADAS"] or 0
            total = disp + ocup
            return {"ocupadas": ocup, "disponibles": disp, "total": total, "porcentaje_ocupacion": round((ocup/total*100),1) if total > 0 else 0}

    def obtener_propiedades_por_tipo(self, id_asesor: Optional[int] = None) -> Dict[str, int]:
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            placeholder = self.db.get_placeholder()
            if id_asesor:
                query = f"SELECT p.TIPO_PROPIEDAD, COUNT(*) as CONTAR FROM PROPIEDADES p JOIN CONTRATOS_MANDATOS cm ON p.ID_PROPIEDAD = cm.ID_PROPIEDAD WHERE cm.ID_ASESOR = {placeholder} AND cm.ESTADO_CONTRATO_M = 'Activo' AND p.ESTADO_REGISTRO IS TRUE GROUP BY p.TIPO_PROPIEDAD"
                cursor.execute(query, (id_asesor,))
            else:
                query = "SELECT TIPO_PROPIEDAD, COUNT(*) as CONTAR FROM PROPIEDADES WHERE ESTADO_REGISTRO IS TRUE GROUP BY TIPO_PROPIEDAD"
                cursor.execute(query)
            return {row["TIPO_PROPIEDAD"]: row["CONTAR"] for row in cursor.fetchall()}

    def obtener_metricas_expertas(self, id_asesor: Optional[int] = None) -> Dict[str, float]:
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            placeholder = self.db.get_placeholder()
            q_potencial = "SELECT SUM(CANON_ARRENDAMIENTO_ESTIMADO) as TOTAL FROM PROPIEDADES WHERE ESTADO_REGISTRO IS TRUE"
            q_real = "SELECT SUM(CANON_ARRENDAMIENTO) as TOTAL FROM CONTRATOS_ARRENDAMIENTOS WHERE ESTADO_CONTRATO_A = 'Activo'"
            if id_asesor:
                cand = f" AND ID_PROPIEDAD IN (SELECT ID_PROPIEDAD FROM CONTRATOS_MANDATOS WHERE ID_ASESOR = {placeholder} AND ESTADO_CONTRATO_M = 'Activo')"
                cursor.execute(q_potencial + cand, (id_asesor,))
                potencial = cursor.fetchone()["TOTAL"] or 0
                cursor.execute(q_real + cand, (id_asesor,))
                real = cursor.fetchone()["TOTAL"] or 0
            else:
                cursor.execute(q_potencial)
                potencial = cursor.fetchone()["TOTAL"] or 0
                cursor.execute(q_real)
                real = cursor.fetchone()["TOTAL"] or 0
            
            # Eficiencia Recaudo Mes
            if not self.db.use_postgresql:
                q_rec = "SELECT SUM(VALOR_TOTAL) as TOTAL FROM RECAUDOS WHERE strftime('%Y-%m', FECHA_PAGO) = strftime('%Y-%m', 'now') AND ESTADO_RECAUDO = 'Aplicado'"
            else:
                q_rec = "SELECT SUM(VALOR_TOTAL) as TOTAL FROM RECAUDOS WHERE DATE_TRUNC('month', TO_DATE(FECHA_PAGO, 'YYYY-MM-DD')) = DATE_TRUNC('month', CURRENT_DATE) AND ESTADO_RECAUDO = 'Aplicado'"
            
            if id_asesor:
                q_rec += f" AND ID_CONTRATO_A IN (SELECT ID_CONTRATO_A FROM CONTRATOS_ARRENDAMIENTOS ca JOIN CONTRATOS_MANDATOS cm ON ca.ID_PROPIEDAD = cm.ID_PROPIEDAD WHERE cm.ID_ASESOR = {placeholder})"
                cursor.execute(q_rec, (id_asesor,))
            else:
                cursor.execute(q_rec)
            recaudado = cursor.fetchone()["TOTAL"] or 0
            
            return {
                "ocupacion_financiera": round((real/potencial*100),1) if potencial > 0 else 0,
                "eficiencia_recaudo": round((recaudado/real*100),1) if real > 0 else 0,
                "potencial_total": float(potencial), "recaudo_real": float(recaudado)
            }

    def obtener_top_asesores_revenue(self) -> List[Dict]:
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            query = "SELECT p.NOMBRE_COMPLETO as nombre, COUNT(cm.ID_CONTRATO_M) as contratos, SUM(cm.CANON_MANDATO * (cm.COMISION_PORCENTAJE_CONTRATO_M / 10000.0)) as revenue FROM CONTRATOS_MANDATOS cm JOIN ASESORES a ON cm.ID_ASESOR = a.ID_ASESOR JOIN PERSONAS p ON a.ID_PERSONA = p.ID_PERSONA WHERE cm.ESTADO_CONTRATO_M = 'Activo' GROUP BY p.NOMBRE_COMPLETO ORDER BY revenue DESC LIMIT 5"
            cursor.execute(query)
            return [{"nombre": r["NOMBRE"], "contratos": int(r["CONTRATOS"]), "revenue": float(r["REVENUE"])} for r in cursor.fetchall()]

    def obtener_tunel_vencimientos(self) -> List[Dict]:
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            if self.db.use_postgresql:
                query = "SELECT TO_CHAR(TO_DATE(FECHA_FIN_CONTRATO_A, 'YYYY-MM-DD'), 'YYYY-MM') as mes, SUM(CANON_ARRENDAMIENTO) as valor_riesgo FROM CONTRATOS_ARRENDAMIENTOS WHERE ESTADO_CONTRATO_A = 'Activo' AND TO_DATE(FECHA_FIN_CONTRATO_A, 'YYYY-MM-DD') BETWEEN CURRENT_DATE AND (CURRENT_DATE + INTERVAL '12 months') GROUP BY mes ORDER BY mes"
            else:
                query = "SELECT strftime('%Y-%m', FECHA_FIN_CONTRATO_A) as mes, SUM(CANON_ARRENDAMIENTO) as valor_riesgo FROM CONTRATOS_ARRENDAMIENTOS WHERE ESTADO_CONTRATO_A = 'Activo' AND FECHA_FIN_CONTRATO_A BETWEEN date('now') AND date('now', '+12 months') GROUP BY mes ORDER BY mes"
            cursor.execute(query)
            return [{"mes": r["MES"], "valor_riesgo": float(r["VALOR_RIESGO"])} for r in cursor.fetchall()]

    def obtener_metricas_incidentes(self) -> Dict:
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            cursor.execute("SELECT ESTADO, COUNT(*) AS COUNT FROM INCIDENTES GROUP BY ESTADO")
            res = {row["ESTADO"]: row["COUNT"] for row in cursor.fetchall()}
            return {"total": sum(res.values()), "por_estado": res}

    def obtener_total_contratos_activos(self, id_asesor: Optional[int] = None) -> int:
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            placeholder = self.db.get_placeholder()
            if id_asesor:
                query = f"SELECT COUNT(*) AS COUNT FROM CONTRATOS_ARRENDAMIENTOS ca JOIN CONTRATOS_MANDATOS cm ON ca.ID_PROPIEDAD = cm.ID_PROPIEDAD WHERE ca.ESTADO_CONTRATO_A = 'Activo' AND cm.ID_ASESOR = {placeholder} AND cm.ESTADO_CONTRATO_M = 'Activo'"
                cursor.execute(query, (id_asesor,))
            else:
                query = "SELECT COUNT(*) AS COUNT FROM CONTRATOS_ARRENDAMIENTOS WHERE ESTADO_CONTRATO_A = 'Activo'"
                cursor.execute(query)
            r = cursor.fetchone()
            return r["COUNT"] if r else 0

    def obtener_morosidad_por_zona(self) -> Dict:
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            cursor.execute("""
                SELECT m.NOMBRE_MUNICIPIO, COUNT(DISTINCT vm.ID_CONTRATO_A) AS CONTRATOS_MORA, SUM(vm.VALOR_RECAUDO) AS MONTO_TOTAL
                FROM VW_ALERTA_MORA_DIARIA vm JOIN CONTRATOS_ARRENDAMIENTOS ca ON vm.ID_CONTRATO_A = ca.ID_CONTRATO_A
                JOIN PROPIEDADES p ON ca.ID_PROPIEDAD = p.ID_PROPIEDAD JOIN MUNICIPIOS m ON p.ID_MUNICIPIO = m.ID_MUNICIPIO
                GROUP BY m.NOMBRE_MUNICIPIO ORDER BY MONTO_TOTAL DESC LIMIT 10
            """)
            res = cursor.fetchall()
            return {"zonas": [r["NOMBRE_MUNICIPIO"] for r in res], "contratos": [r["CONTRATOS_MORA"] for r in res], "montos": [r["MONTO_TOTAL"] for r in res]}

    def obtener_desempeno_asesores(self) -> Dict:
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            placeholder = self.db.get_placeholder()
            cursor.execute("SELECT p.NOMBRE_COMPLETO, COUNT(ca.ID_CONTRATO_A) AS CONTRATOS_ACTIVOS, SUM(ca.CANON_ARRENDAMIENTO) AS VALOR_CARTERA FROM CONTRATOS_ARRENDAMIENTOS ca JOIN ASESORES a ON ca.ID_ASESOR = a.ID_ASESOR JOIN PERSONAS p ON a.ID_PERSONA = p.ID_PERSONA WHERE ca.ESTADO_CONTRATO_A = 'Activo' GROUP BY p.NOMBRE_COMPLETO ORDER BY CONTRATOS_ACTIVOS DESC LIMIT 5")
            top_contratos = [{"nombre": r["NOMBRE_COMPLETO"], "contratos": r["CONTRATOS_ACTIVOS"], "cartera": r["VALOR_CARTERA"]} for r in cursor.fetchall()]
            
            hoy = datetime.now()
            cursor.execute(f"SELECT p.NOMBRE_COMPLETO, SUM(la.VALOR_NETO_ASESOR) AS COMISIONES_MES FROM LIQUIDACIONES_ASESORES la JOIN ASESORES a ON la.ID_ASESOR = a.ID_ASESOR JOIN PERSONAS p ON a.ID_PERSONA = p.ID_PERSONA WHERE TO_CHAR(la.FECHA_LIQUIDACION::DATE, 'MM') = {placeholder} AND TO_CHAR(la.FECHA_LIQUIDACION::DATE, 'YYYY') = {placeholder} GROUP BY p.NOMBRE_COMPLETO ORDER BY COMISIONES_MES DESC LIMIT 5", (f"{hoy.month:02d}", str(hoy.year)))
            top_com = [{"nombre": r["NOMBRE_COMPLETO"], "comisiones": r["COMISIONES_MES"]} for r in cursor.fetchall()]
            return {"top_contratos": top_contratos, "top_comisiones": top_com}

    def obtener_recibos_vencidos_resumen(self) -> Dict:
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            
            # Query compatible con SQLite y PostgreSQL para vencimientos
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
                    WHERE ESTADO != 'Pagado' AND FECHA_VENCIMIENTO < date('now')
                """
                
            cursor.execute(query)
            res = cursor.fetchone()
            return {
                "monto_total": res["MONTO_TOTAL"] or 0, 
                "cantidad": res["CANTIDAD"] or 0
            }
