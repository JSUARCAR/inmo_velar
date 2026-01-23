"""
Servicio de Dashboard - Inmobiliaria Velar
Proporciona datos agregados para widgets del dashboard ejecutivo.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta

from src.infraestructura.persistencia.database import DatabaseManager

# Integración Fase 3: CacheManager para dashboard
from src.infraestructura.cache.cache_manager import cache_manager


class ServicioDashboard:
    """
    Servicio de aplicacion para metricas del dashboard.
    Consolida datos de multiples tablas y vistas.
    """
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    @cache_manager.cached('dashboard:cartera_mora', level=1, ttl=60)
    def obtener_cartera_mora(self) -> Dict:
        """
        Obtiene resumen de cartera en mora.
        
        Returns:
            Dict con monto_total, cantidad_contratos, top_morosos (lista)
        """
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            
            # Consultar vista VW_ALERTA_MORA_DIARIA
            cursor.execute("""
                SELECT 
                    COUNT(*) AS CANTIDAD,
                    SUM(VALOR_RECAUDO) AS MONTO_TOTAL
                FROM VW_ALERTA_MORA_DIARIA
            """)
            
            resumen = cursor.fetchone()
            
            # Top 5 morosos
            cursor.execute("""
                SELECT 
                    ARRENDATARIO,
                    DIAS_RETRASO,
                    VALOR_RECAUDO
                FROM VW_ALERTA_MORA_DIARIA
                ORDER BY DIAS_RETRASO DESC, VALOR_RECAUDO DESC
                LIMIT 5
            """)
            
            top_morosos = [
                {
                    "nombre": row['ARRENDATARIO'],
                    "dias_retraso": row['DIAS_RETRASO'],
                    "monto": row['VALOR_RECAUDO']
                }
                for row in cursor.fetchall()
            ]
            
            return {
                "monto_total": resumen['MONTO_TOTAL'] or 0,
                "cantidad_contratos": resumen['CANTIDAD'] or 0,
                "top_morosos": top_morosos
            }
    
    @cache_manager.cached('dashboard:flujo_caja', level=1, ttl=60) 
    def obtener_flujo_caja_mes(self, mes: int = None, anio: int = None, id_asesor: int = None) -> Dict:
        """
        Obtiene flujo de caja filtrado por mes, año y asesor.
        """
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            placeholder = self.db.get_placeholder()
            
            # 1. Definir Mes y Año
            hoy = datetime.now()
            mes_actual = mes if mes else hoy.month
            anio_actual = anio if anio else hoy.year
            
            # 2. Construir Query de RECAUDO (Aplicado)
            params = [f"{mes_actual:02d}", str(anio_actual)]
            query_recaudo = """
                SELECT SUM(r.VALOR_TOTAL) AS TOTAL_RECAUDO
                FROM RECAUDOS r
                JOIN CONTRATOS_ARRENDAMIENTOS ca ON r.ID_CONTRATO_A = ca.ID_CONTRATO_A
            """
            
            if id_asesor:
                # Join con Mandatos para filtrar por Asesor
                query_recaudo += """
                    JOIN CONTRATOS_MANDATOS cm ON ca.ID_PROPIEDAD = cm.ID_PROPIEDAD
                """
                
                query_recaudo += f"""
                    WHERE TO_CHAR(r.FECHA_PAGO::DATE, 'MM') = {placeholder}
                      AND TO_CHAR(r.FECHA_PAGO::DATE, 'YYYY') = {placeholder}
                      AND r.ESTADO_RECAUDO = 'Aplicado'
                      AND cm.ID_ASESOR = {placeholder}
                      AND cm.ESTADO_CONTRATO_M = 'Activo'
                """
                params.append(id_asesor)
            else:
                query_recaudo += f"""
                    WHERE TO_CHAR(r.FECHA_PAGO::DATE, 'MM') = {placeholder}
                      AND TO_CHAR(r.FECHA_PAGO::DATE, 'YYYY') = {placeholder}
                      AND r.ESTADO_RECAUDO = 'Aplicado'
                """
            
            cursor.execute(query_recaudo, params)
            recaudado_res = cursor.fetchone()
            recaudado = recaudado_res['TOTAL_RECAUDO'] if recaudado_res and recaudado_res['TOTAL_RECAUDO'] else 0
            
            # 3. Construir Query de ESPERADO (Contratos Activos)
            query_esperado = """
                SELECT SUM(ca.CANON_ARRENDAMIENTO) AS TOTAL_ESPERADO
                FROM CONTRATOS_ARRENDAMIENTOS ca
            """
            params_esp = []
            
            if id_asesor:
                query_esperado += " JOIN CONTRATOS_MANDATOS cm ON ca.ID_PROPIEDAD = cm.ID_PROPIEDAD "
                query_esperado += f" WHERE ca.ESTADO_CONTRATO_A = 'Activo' AND cm.ID_ASESOR = {placeholder} AND cm.ESTADO_CONTRATO_M = 'Activo' "
                params_esp.append(id_asesor)
            else:
                query_esperado += " WHERE ca.ESTADO_CONTRATO_A = 'Activo' "
                
            cursor.execute(query_esperado, params_esp)
            esperado_res = cursor.fetchone()
            esperado = esperado_res['TOTAL_ESPERADO'] if esperado_res and esperado_res['TOTAL_ESPERADO'] else 0
            
            # 4. Calcular porcentaje
            if esperado > 0:
                porcentaje = (recaudado / esperado * 100)
            else:
                porcentaje = 0
            
            return {
                "recaudado": recaudado,
                "esperado": esperado,
                "porcentaje": round(porcentaje, 1),
                "diferencia": esperado - recaudado
            }
    
    @cache_manager.cached('dashboard:contratos_vencer', level=1, ttl=60)
    def obtener_contratos_por_vencer(self) -> Dict:
        """
        Obtiene contratos proximos a vencer agrupados por rango.
        
        Returns:
            Dict con conteos por rango (30d, 60d, 90d)
        """
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            
            # Usar vista VW_ALERTA_VENCIMIENTO_CONTRATOS
            cursor.execute("""
                SELECT 
                    SUM(CASE WHEN DIAS_RESTANTES <= 30 THEN 1 ELSE 0 END) AS VENCE_30,
                    SUM(CASE WHEN DIAS_RESTANTES > 30 AND DIAS_RESTANTES <= 60 THEN 1 ELSE 0 END) AS VENCE_60,
                    SUM(CASE WHEN DIAS_RESTANTES > 60 AND DIAS_RESTANTES <= 90 THEN 1 ELSE 0 END) AS VENCE_90
                FROM VW_ALERTA_VENCIMIENTO_CONTRATOS
            """)
            
            resultado = cursor.fetchone()
            
            vence_30 = resultado['VENCE_30'] or 0
            vence_60 = resultado['VENCE_60'] or 0
            vence_90 = resultado['VENCE_90'] or 0
            
            return {
                "vence_30_dias": vence_30,
                "vence_60_dias": vence_60,
                "vence_90_dias": vence_90,
                "total": vence_30 + vence_60 + vence_90
            }
    
    def obtener_contratos_proximos_vencer(self, dias_limite: int = 30) -> List[Dict[str, Any]]:
        """
        Obtiene lista detallada de contratos próximos a vencer.
        
        Args:
            dias_limite: Número de días para considerar "próximo a vencer" (default: 30)
            
        Returns:
            Lista de diccionarios con detalles de cada contrato
        """
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            placeholder = self.db.get_placeholder()
            
            cursor.execute(f"""
                SELECT 
                    TIPO_CONTRATO,
                    ID_PROPIEDAD,
                    DIRECCION,
                    INQUILINO_PROPIETARIO as PARTE_CONTRATANTE,
                    FECHA_FIN,
                    DIAS_RESTANTES
                FROM VW_ALERTA_VENCIMIENTO_CONTRATOS
                WHERE DIAS_RESTANTES <= {placeholder}
                ORDER BY DIAS_RESTANTES ASC
            """, (dias_limite,))
            
            contratos = []
            for row in cursor.fetchall():
                contratos.append({
                    'tipo_contrato': row['TIPO_CONTRATO'],
                    'id_propiedad': row['ID_PROPIEDAD'],
                    'direccion': row['DIRECCION'],
                    'parte_contratante': row['PARTE_CONTRATANTE'],
                    'fecha_fin': row['FECHA_FIN'],
                    'dias_restantes': row['DIAS_RESTANTES']
                })
            
            return contratos
    
    def obtener_contratos_elegibles_ipc(self, dias_anticipacion: int = 30) -> List[Dict[str, Any]]:
        """
        Obtiene contratos de arrendamiento elegibles para ajuste de IPC.
        
        Un contrato es elegible si:
        - Está activo
        - Ha cumplido al menos 1 año desde inicio
        - Se acerca a aniversario (dentro de dias_anticipacion)
        - Existe IPC del año anterior disponible
        
        Args:
            dias_anticipacion: Días antes del aniversario para alertar (default: 30)
            
        Returns:
            Lista de dict con información del contrato y datos de IPC
        """
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            placeholder = self.db.get_placeholder()
            
            cursor.execute(f"""
                WITH ProximosAniversarios AS (
                    SELECT 
                        ca.ID_CONTRATO_A,
                        p.DIRECCION_PROPIEDAD,
                        arr_p.NOMBRE_COMPLETO AS INQUILINO,
                        ca.FECHA_INICIO_CONTRATO_A,
                        ca.CANON_ARRENDAMIENTO,
                        -- Calcular años activos
                        CAST((julianday('now') - julianday(ca.FECHA_INICIO_CONTRATO_A)) / 365.25 AS INTEGER) AS ANIOS_ACTIVOS,
                        -- Calcular próximo aniversario
                        date(ca.FECHA_INICIO_CONTRATO_A, 
                             '+' || CAST((julianday('now') - julianday(ca.FECHA_INICIO_CONTRATO_A)) / 365.25 AS INTEGER) + 1 || ' years'
                        ) AS PROXIMO_ANIVERSARIO,
                        -- Días hasta el aniversario
                        CAST(
                            julianday(
                                date(ca.FECHA_INICIO_CONTRATO_A, 
                                     '+' || CAST((julianday('now') - julianday(ca.FECHA_INICIO_CONTRATO_A)) / 365.25 AS INTEGER) + 1 || ' years')
                            ) - julianday('now')
                        AS INTEGER) AS DIAS_HASTA_ANIVERSARIO,
                        -- IPC del año anterior
                        ipc.VALOR_IPC,
                        ipc.ANIO
                    FROM CONTRATOS_ARRENDAMIENTOS ca
                    JOIN PROPIEDADES p ON ca.ID_PROPIEDAD = p.ID_PROPIEDAD
                    JOIN ARRENDATARIOS arr ON ca.ID_ARRENDATARIO = arr.ID_ARRENDATARIO
                    JOIN PERSONAS arr_p ON arr.ID_PERSONA = arr_p.ID_PERSONA
                    LEFT JOIN IPC ipc ON ipc.ANIO = CAST(strftime('%Y', 'now') AS INTEGER) - 1
                    WHERE ca.ESTADO_CONTRATO_A = 'Activo'
                    -- Al menos 1 año de antigüedad
                    AND julianday('now') - julianday(ca.FECHA_INICIO_CONTRATO_A) >= 365
                    -- IPC disponible
                    AND ipc.VALOR_IPC IS NOT NULL
                )
                SELECT * FROM ProximosAniversarios
                WHERE DIAS_HASTA_ANIVERSARIO BETWEEN 0 AND {placeholder}
                ORDER BY DIAS_HASTA_ANIVERSARIO ASC
            """, (dias_anticipacion,))
            
            contratos = []
            contratos = []
            for row in cursor.fetchall():
                contratos.append({
                    'id_contrato': row['ID_CONTRATO_A'],
                    'direccion': row['DIRECCION_PROPIEDAD'],
                    'inquilino': row['INQUILINO'],
                    'fecha_inicio': row['FECHA_INICIO_CONTRATO_A'],
                    'canon_actual': row['CANON_ARRENDAMIENTO'],
                    'anios_activos': row['ANIOS_ACTIVOS'],
                    'proximo_aniversario': row['PROXIMO_ANIVERSARIO'],
                    'dias_hasta_aniversario': row['DIAS_HASTA_ANIVERSARIO'],
                    'ipc_porcentaje': row['VALOR_IPC'],
                    'ipc_anio': row['ANIO']
                })
            
            return contratos
    
    @cache_manager.cached('dashboard:comisiones_pendientes', level=1, ttl=60)
    def obtener_comisiones_pendientes(self, id_asesor: int = None) -> Dict:
        """
        Obtiene total de comisiones pendientes de pago.
        """
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            placeholder = self.db.get_placeholder()
            
            query = """
                SELECT 
                    COUNT(*) AS CANTIDAD,
                    SUM(VALOR_NETO_ASESOR) AS MONTO_TOTAL
                FROM LIQUIDACIONES_ASESORES
                WHERE ESTADO_LIQUIDACION = 'Pendiente'
            """
            params = []
            
            if id_asesor:
                query += f" AND ID_ASESOR = {placeholder}"
                params.append(id_asesor)
            
            cursor.execute(query, params)
            
            resultado = cursor.fetchone()
            
            return {
                "monto_total": resultado['MONTO_TOTAL'] or 0,
                "cantidad_liquidaciones": resultado['CANTIDAD'] or 0
            }
    
    @cache_manager.cached('dashboard:tasa_ocupacion', level=1, ttl=60)
    def obtener_tasa_ocupacion(self, id_asesor: int = None) -> Dict:
        """
        Calcula tasa de ocupación de propiedades.
        """
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            placeholder = self.db.get_placeholder()
            
            if id_asesor:
                # Filtrar propiedades gestionadas por el asesor (via Mandato Activo)
                cursor.execute(f"""
                    SELECT 
                        SUM(CASE WHEN p.DISPONIBILIDAD_PROPIEDAD = TRUE THEN 1 ELSE 0 END) AS DISPONIBLES,
                        SUM(CASE WHEN p.DISPONIBILIDAD_PROPIEDAD = FALSE THEN 1 ELSE 0 END) AS OCUPADAS
                    FROM PROPIEDADES p
                    JOIN CONTRATOS_MANDATOS cm ON p.ID_PROPIEDAD = cm.ID_PROPIEDAD
                    WHERE cm.ID_ASESOR = {placeholder}
                      AND cm.ESTADO_CONTRATO_M = 'Activo'
                      AND p.ESTADO_REGISTRO = TRUE
                """, (id_asesor,))
            else:
                cursor.execute("""
                    SELECT 
                        SUM(CASE WHEN DISPONIBILIDAD_PROPIEDAD = TRUE THEN 1 ELSE 0 END) AS DISPONIBLES,
                        SUM(CASE WHEN DISPONIBILIDAD_PROPIEDAD = FALSE THEN 1 ELSE 0 END) AS OCUPADAS
                    FROM PROPIEDADES
                    WHERE ESTADO_REGISTRO = TRUE
                """)
            
            resultado = cursor.fetchone()
            disponibles = resultado['DISPONIBLES'] or 0
            ocupadas = resultado['OCUPADAS'] or 0
            total = disponibles + ocupadas
            
            porcentaje = (ocupadas / total * 100) if total > 0 else 0
            
            return {
                "ocupadas": ocupadas,
                "disponibles": disponibles,
                "total": total,
                "porcentaje_ocupacion": round(porcentaje, 1)
            }

    @cache_manager.cached('dashboard:propiedades_tipo', level=1, ttl=60)
    def obtener_propiedades_por_tipo(self, id_asesor: int = None) -> Dict[str, int]:
        """
        Obtiene cantidad de propiedades agrupadas por tipo.
        """
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            placeholder = self.db.get_placeholder()
            
            if id_asesor:
                cursor.execute(f"""
                    SELECT p.TIPO_PROPIEDAD, COUNT(*) as CONTAR
                    FROM PROPIEDADES p
                    JOIN CONTRATOS_MANDATOS cm ON p.ID_PROPIEDAD = cm.ID_PROPIEDAD
                    WHERE cm.ID_ASESOR = {placeholder}
                      AND cm.ESTADO_CONTRATO_M = 'Activo'
                      AND p.ESTADO_REGISTRO = TRUE
                    GROUP BY p.TIPO_PROPIEDAD
                """, (id_asesor,))
            else:
                cursor.execute("""
                    SELECT TIPO_PROPIEDAD, COUNT(*) as CONTAR
                    FROM PROPIEDADES
                    WHERE ESTADO_REGISTRO = TRUE
                    GROUP BY TIPO_PROPIEDAD
                """)
            
            return {row['TIPO_PROPIEDAD']: row['CONTAR'] for row in cursor.fetchall()}

    @cache_manager.cached('dashboard:metricas_expertas', level=1, ttl=60)
    def obtener_metricas_expertas(self, id_asesor: int = None) -> Dict[str, float]:
        """
        Calcula KPIs estratégicos: Ocupación Financiera y Eficiencia de Recaudo.
        """
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            placeholder = self.db.get_placeholder()
            
            # 1. Tasa de Ocupación Financiera
            # (Suma Canon Contratos Activos / Suma Canon Estimado Todas Propiedades)
            query_potencial = "SELECT SUM(CANON_ARRENDAMIENTO_ESTIMADO) as total FROM PROPIEDADES WHERE ESTADO_REGISTRO = TRUE"
            query_real = "SELECT SUM(CANON_ARRENDAMIENTO) as total FROM CONTRATOS_ARRENDAMIENTOS WHERE ESTADO_CONTRATO_A = 'Activo'"
            
            if id_asesor:
                # Filtrar por propiedades del asesor
                query_potencial += f" AND ID_PROPIEDAD IN (SELECT ID_PROPIEDAD FROM CONTRATOS_MANDATOS WHERE ID_ASESOR = {placeholder} AND ESTADO_CONTRATO_M = 'Activo')"
                query_real += f" AND ID_PROPIEDAD IN (SELECT ID_PROPIEDAD FROM CONTRATOS_MANDATOS WHERE ID_ASESOR = {placeholder} AND ESTADO_CONTRATO_M = 'Activo')"
                params = (id_asesor, id_asesor)
            else:
                params = ()
                
            cursor.execute(query_potencial, params[:1] if id_asesor else ())
            row_potencial = cursor.fetchone()
            potencial = row_potencial['TOTAL'] if row_potencial and row_potencial['TOTAL'] else 0
            
            cursor.execute(query_real, params[1:] if id_asesor else ())
            row_real = cursor.fetchone()
            real = row_real['TOTAL'] if row_real and row_real['TOTAL'] else 0
            
            ocupacion_financiera = round((real / potencial * 100), 1) if potencial > 0 else 0
            
            # 2. Eficiencia de Recaudo (Mes Actual)
            # (Recaudado Real Mes / Esperado Mes)
            # Esperado: Suma de canones activos
            # Real: Suma de recaudos aplicados este mes
            
            # Nota: Para simplificar, el esperado es el canon total activo actual.
            # Una implementación más estricta sumaría las facturas generadas en el mes.
            esperado = real # Usamos el real calculado arriba como proxy de lo esperado mensual
            
            if self.db.use_postgresql:
                query_recaudos = """
                    SELECT SUM(VALOR_TOTAL) as total 
                    FROM RECAUDOS 
                    WHERE DATE_TRUNC('month', TO_DATE(FECHA_PAGO, 'YYYY-MM-DD')) = DATE_TRUNC('month', CURRENT_DATE)
                    AND ESTADO_RECAUDO = 'Aplicado'
                """
            else:
                query_recaudos = """
                    SELECT SUM(VALOR_TOTAL) as total 
                    FROM RECAUDOS 
                    WHERE strftime('%Y-%m', FECHA_PAGO) = strftime('%Y-%m', 'now')
                    AND ESTADO_RECAUDO = 'Aplicado'
                """
                
            if id_asesor:
                 query_recaudos += f" AND ID_CONTRATO_A IN (SELECT ID_CONTRATO_A FROM CONTRATOS_ARRENDAMIENTOS ca JOIN CONTRATOS_MANDATOS cm ON ca.ID_PROPIEDAD = cm.ID_PROPIEDAD WHERE cm.ID_ASESOR = {placeholder})"
                 cursor.execute(query_recaudos, (id_asesor,))
            else:
                 cursor.execute(query_recaudos)
                 
            row_recaudado = cursor.fetchone()
            recaudado = row_recaudado['TOTAL'] if row_recaudado and row_recaudado['TOTAL'] else 0
            
            eficiencia = round((recaudado / esperado * 100), 1) if esperado > 0 else 0
            
            return {
                "ocupacion_financiera": float(ocupacion_financiera),
                "eficiencia_recaudo": float(eficiencia),
                "potencial_total": float(potencial),
                "recaudo_real": float(recaudado)
            }

    @cache_manager.cached('dashboard:top_asesores', level=1, ttl=60)
    def obtener_top_asesores_revenue(self) -> List[Dict]:
        """
        Obtiene top asesores por revenue estimado (comisiones).
        """
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            
            query = """
                SELECT 
                    p.NOMBRE_COMPLETO as nombre,
                    COUNT(cm.ID_CONTRATO_M) as contratos,
                    SUM(cm.CANON_MANDATO * (cm.COMISION_PORCENTAJE_CONTRATO_M / 100.0)) as revenue
                FROM CONTRATOS_MANDATOS cm
                JOIN ASESORES a ON cm.ID_ASESOR = a.ID_ASESOR
                JOIN PERSONAS p ON a.ID_PERSONA = p.ID_PERSONA
                WHERE cm.ESTADO_CONTRATO_M = 'Activo'
                GROUP BY p.NOMBRE_COMPLETO
                ORDER BY revenue DESC
                LIMIT 5
            """
            cursor.execute(query)
            rows = cursor.fetchall()
            return [
                {
                    'nombre': row['NOMBRE'],
                    'contratos': int(row['CONTRATOS']),
                    'revenue': float(row['REVENUE'])
                }
                for row in rows
            ]

    @cache_manager.cached('dashboard:tunel_vencimientos', level=1, ttl=60)
    def obtener_tunel_vencimientos(self) -> List[Dict]:
        """
        Proyección de vencimientos de contratos a 12 meses.
        """
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            
            # Esta lógica agrupa por mes de vencimiento los contratos activos
            # Retorna una lista de dicts: {'mes': '2024-02', 'valor': 1500000}
            
            if self.db.use_postgresql:
                query = """
                    SELECT 
                        TO_CHAR(TO_DATE(FECHA_FIN_CONTRATO_A, 'YYYY-MM-DD'), 'YYYY-MM') as mes,
                        SUM(CANON_ARRENDAMIENTO) as valor_riesgo
                    FROM CONTRATOS_ARRENDAMIENTOS
                    WHERE ESTADO_CONTRATO_A = 'Activo'
                    AND TO_DATE(FECHA_FIN_CONTRATO_A, 'YYYY-MM-DD') BETWEEN CURRENT_DATE AND (CURRENT_DATE + INTERVAL '12 months')
                    GROUP BY mes
                    ORDER BY mes
                """
            else:
                 query = """
                    SELECT 
                        strftime('%Y-%m', FECHA_FIN_CONTRATO_A) as mes,
                        SUM(CANON_ARRENDAMIENTO) as valor_riesgo
                    FROM CONTRATOS_ARRENDAMIENTOS
                    WHERE ESTADO_CONTRATO_A = 'Activo'
                    AND FECHA_FIN_CONTRATO_A BETWEEN date('now') AND date('now', '+12 months')
                    GROUP BY mes
                    ORDER BY mes
                """
            
            cursor.execute(query)
            rows = cursor.fetchall()
            return [
                {
                    'mes': row['MES'],
                    'valor_riesgo': float(row['VALOR_RIESGO'])
                }
                for row in rows
            ]
    def obtener_metricas_incidentes(self) -> Dict:
        """
        Obtiene metricas de incidentes por estado.
        
        Returns:
            Dict con total y desglose por estado
        """
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            
            cursor.execute("""
                SELECT ESTADO, COUNT(*) AS COUNT
                FROM INCIDENTES
                GROUP BY ESTADO
            """)
            
            resultados = {row['ESTADO']: row['COUNT'] for row in cursor.fetchall()}
            total = sum(resultados.values())
            
            return {
                "total": total,
                "por_estado": {
                    "Reportado": resultados.get("Reportado", 0),
                    "Cotizado": resultados.get("Cotizado", 0),
                    "Aprobado": resultados.get("Aprobado", 0),
                    "En Reparación": resultados.get("En Reparacion", 0),
                    "Finalizado": resultados.get("Finalizado", 0)
                }
            }

    def obtener_evolucion_recaudo(self, meses: int = 6, mes_fin: int = None, anio_fin: int = None) -> Dict:
        """
        Obtiene historico de recaudos de los ultimos N meses.
        Permite especificar fecha de corte (mes_fin, anio_fin).
        """
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            placeholder = self.db.get_placeholder()
            
            hoy = datetime.now()
            # Si no se define fecha fin, usar actual
            fecha_corte = hoy
            if anio_fin and mes_fin:
                 fecha_corte = datetime(anio_fin, mes_fin, 1)
            elif anio_fin:
                 # Si solo anio, usar Diciembre de ese anio (o mes actual si es anio actual?)
                 fecha_corte = datetime(anio_fin, 12, 1) if anio_fin < hoy.year else hoy

            fechas = []
            valores = []
            
            # Generar los últimos N meses desde fecha_corte hacia atrás
            # Nota: fecha_corte es el mes "0" (el más reciente)
            for i in range(meses - 1, -1, -1):
                # Calculo de mes/año
                mes_calc = fecha_corte.month - i
                anio_calc = fecha_corte.year
                
                while mes_calc <= 0:
                    mes_calc += 12
                    anio_calc -= 1
                    
                cursor.execute(f"""
                    SELECT SUM(VALOR_TOTAL) AS TOTAL_RECAUDO
                    FROM RECAUDOS
                    WHERE TO_CHAR(FECHA_PAGO::DATE, 'MM') = {placeholder}
                      AND TO_CHAR(FECHA_PAGO::DATE, 'YYYY') = {placeholder}
                      AND ESTADO_RECAUDO = 'Aplicado'
                """, (f"{mes_calc:02d}", str(anio_calc)))
                
                res = cursor.fetchone()
                total = res['TOTAL_RECAUDO'] if res and res['TOTAL_RECAUDO'] else 0
                
                fechas.append(f"{mes_calc:02d}/{anio_calc}")
                valores.append(total)
                
            return {
                "etiquetas": fechas,
                "valores": valores
            }

    def obtener_total_contratos_activos(self, id_asesor: int = None) -> int:
        """
        Obtiene conteo de contratos activos, opcionalmente filtrado por asesor.
        """
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            placeholder = self.db.get_placeholder()
            
            if id_asesor:
                query = f"""
                    SELECT COUNT(*) AS COUNT
                    FROM CONTRATOS_ARRENDAMIENTOS ca
                    JOIN CONTRATOS_MANDATOS cm ON ca.ID_PROPIEDAD = cm.ID_PROPIEDAD
                    WHERE ca.ESTADO_CONTRATO_A = 'Activo'
                      AND cm.ID_ASESOR = {placeholder}
                      AND cm.ESTADO_CONTRATO_M = 'Activo'
                """
                cursor.execute(query, (id_asesor,))
            else:
                query = """
                    SELECT COUNT(*) AS COUNT FROM CONTRATOS_ARRENDAMIENTOS 
                    WHERE ESTADO_CONTRATO_A = 'Activo'
                """
                cursor.execute(query)
                
            res = cursor.fetchone()
            return res['COUNT'] if res else 0

    def obtener_morosidad_por_zona(self) -> Dict:
        """
        Analiza la morosidad agrupada por municipio/zona.
        
        Returns:
            Dict con zonas y sus respectivos montos en mora
        """
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            
            cursor.execute("""
                SELECT 
                    m.NOMBRE_MUNICIPIO,
                    COUNT(DISTINCT vm.ID_CONTRATO_A) AS CONTRATOS_MORA,
                    SUM(vm.VALOR_RECAUDO) AS MONTO_TOTAL
                FROM VW_ALERTA_MORA_DIARIA vm
                JOIN CONTRATOS_ARRENDAMIENTOS ca ON vm.ID_CONTRATO_A = ca.ID_CONTRATO_A
                JOIN PROPIEDADES p ON ca.ID_PROPIEDAD = p.ID_PROPIEDAD
                JOIN MUNICIPIOS m ON p.ID_MUNICIPIO = m.ID_MUNICIPIO
                GROUP BY m.NOMBRE_MUNICIPIO
                ORDER BY monto_total DESC
                LIMIT 10
            """)
            
            resultados = cursor.fetchall()
            
            return {
                "zonas": [row['NOMBRE_MUNICIPIO'] for row in resultados],
                "contratos": [row['CONTRATOS_MORA'] for row in resultados],
                "montos": [row['MONTO_TOTAL'] for row in resultados]
            }

    def obtener_desempeno_asesores(self) -> Dict:
        """
        Obtiene métricas de desempeño de asesores.
        
        Returns:
            Dict con ranking de asesores por contratos activos y comisiones generadas
        """
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            placeholder = self.db.get_placeholder()
            
            # Top asesores por contratos activos
            cursor.execute("""
                SELECT 
                    p.NOMBRE_COMPLETO,
                    COUNT(ca.ID_CONTRATO_A) AS CONTRATOS_ACTIVOS,
                    SUM(ca.CANON_ARRENDAMIENTO) AS VALOR_CARTERA
                FROM CONTRATOS_ARRENDAMIENTOS ca
                JOIN ASESORES a ON ca.ID_ASESOR = a.ID_ASESOR
                JOIN PERSONAS p ON a.ID_PERSONA = p.ID_PERSONA
                WHERE ca.ESTADO_CONTRATO_A = 'Activo'
                GROUP BY p.NOMBRE_COMPLETO
                ORDER BY contratos_activos DESC
                LIMIT 5
            """)
            
            top_asesores = [
                {
                    "nombre": row['NOMBRE_COMPLETO'],
                    "contratos": row['CONTRATOS_ACTIVOS'],
                    "cartera": row['VALOR_CARTERA']
                }
                for row in cursor.fetchall()
            ]
            
            # Comisiones del mes actual
            hoy = datetime.now()
            mes_actual = hoy.month
            anio_actual = hoy.year
            
            cursor.execute(f"""
                SELECT 
                    p.NOMBRE_COMPLETO,
                    SUM(la.VALOR_NETO_ASESOR) AS COMISIONES_MES
                FROM LIQUIDACIONES_ASESORES la
                JOIN ASESORES a ON la.ID_ASESOR = a.ID_ASESOR
                JOIN PERSONAS p ON a.ID_PERSONA = p.ID_PERSONA
                WHERE TO_CHAR(la.FECHA_LIQUIDACION::DATE, 'MM') = {placeholder}
                  AND TO_CHAR(la.FECHA_LIQUIDACION::DATE, 'YYYY') = {placeholder}
                GROUP BY p.NOMBRE_COMPLETO
                ORDER BY comisiones_mes DESC
                LIMIT 5
            """, (f"{mes_actual:02d}", str(anio_actual)))
            
            top_comisiones = [
                {
                    "nombre": row['NOMBRE_COMPLETO'],
                    "comisiones": row['COMISIONES_MES']
                }
                for row in cursor.fetchall()
            ]
            
            return {
                "top_contratos": top_asesores,
                "top_comisiones": top_comisiones
            }
            
    def obtener_recibos_vencidos_resumen(self) -> Dict:
        """
        Obtiene resumen de recibos públicos vencidos.
        
        Returns:
            Dict con cantidad y monto total
        """
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            
            cursor.execute("""
                SELECT 
                    COUNT(*) AS CANTIDAD,
                    SUM(VALOR_RECIBO) AS MONTO_TOTAL
                FROM RECIBOS_PUBLICOS
                WHERE DATE(FECHA_VENCIMIENTO) < DATE('now')
                  AND ESTADO != 'Pagado'
            """)
            
            resultado = cursor.fetchone()
            
            return {
                "cantidad": resultado['CANTIDAD'] or 0,
                "monto_total": resultado['MONTO_TOTAL'] or 0
            }
