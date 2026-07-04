"""
Servicio de Dashboard - Inmobiliaria Velar
Proporciona datos agregados para widgets del dashboard ejecutivo.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from src.dominio.interfaces.repositorio_dashboard import IRepositorioDashboard
from src.infraestructura.cache.cache_manager import cache_manager


from src.dominio.interfaces.repositorio_alerta import IRepositorioAlerta


class ServicioDashboard:
    """
    Servicio de aplicacion para metricas del dashboard.
    Consolida datos de multiples tablas y vistas.
    """

    def __init__(
        self,
        repo_dashboard: IRepositorioDashboard,
        repo_alerta: Optional[IRepositorioAlerta] = None,
    ):
        self.repo = repo_dashboard
        self.repo_alerta = repo_alerta

    @cache_manager.cached("dashboard:alertas_conteo", level=1, ttl=60)
    def obtener_conteo_alertas_pendientes(self) -> int:
        """Obtiene el total de alertas en estado Pendiente o En Proceso."""
        if not self.repo_alerta:
            return 0
        return self.repo_alerta.contar_todas(
            estado="Pendiente"
        ) + self.repo_alerta.contar_todas(estado="En Proceso")

    @cache_manager.cached("dashboard:cartera_mora", level=1, ttl=60)
    def obtener_cartera_mora(self) -> Dict:
        """Obtiene resumen de cartera en mora."""
        try:
            resumen = self.repo.obtener_resumen_mora()
            top_morosos = self.repo.obtener_top_morosos(5)
            return {
                "monto_total": resumen["monto_total"],
                "cantidad_contratos": resumen["cantidad_contratos"],
                "top_morosos": top_morosos,
            }
        except Exception as e:
            import logging

            logging.error(f"Error en obtener_cartera_mora: {e}")
            return {"monto_total": 0, "cantidad_contratos": 0, "top_morosos": []}

    @cache_manager.cached("dashboard:flujo_caja", level=1, ttl=60)
    def obtener_flujo_caja_mes(
        self, mes: int = None, anio: int = None, id_asesor: int = None
    ) -> Dict:
        """Obtiene flujo de caja filtrado."""
        try:
            hoy = datetime.now()
            mes_actual = f"{mes:02d}" if mes else f"{hoy.month:02d}"
            anio_actual = str(anio) if anio else str(hoy.year)

            recaudado = self.repo.obtener_total_recaudado(
                mes_actual, anio_actual, id_asesor
            )
            esperado = self.repo.obtener_total_esperado(id_asesor)

            porcentaje = (recaudado / esperado * 100) if esperado > 0 else 0

            return {
                "recaudado": recaudado,
                "esperado": esperado,
                "porcentaje": round(porcentaje, 1),
                "diferencia": esperado - recaudado,
            }
        except Exception as e:
            import logging

            logging.error(f"Error en obtener_flujo_caja_mes: {e}")
            return {"recaudado": 0, "esperado": 0, "porcentaje": 0, "diferencia": 0}

    @cache_manager.cached("dashboard:contratos_vencer", level=1, ttl=60)
    def obtener_contratos_por_vencer(self) -> Dict:
        """Contratos proximos a vencer por rango."""
        try:
            rangos = self.repo.obtener_conteo_vencimientos_rangos()
            total = sum(rangos.values())
            return {**rangos, "total": total}
        except Exception as e:
            import logging

            logging.error(f"Error en obtener_contratos_por_vencer: {e}")
            return {
                "vence_30_dias": 0,
                "vence_60_dias": 0,
                "vence_90_dias": 0,
                "total": 0,
            }

    def obtener_contratos_proximos_vencer(
        self, dias_limite: int = 30
    ) -> List[Dict[str, Any]]:
        try:
            return self.repo.obtener_lista_vencimientos(dias_limite)
        except Exception as e:
            import logging

            logging.error(f"Error en obtener_contratos_proximos_vencer: {e}")
            return []

    def obtener_contratos_elegibles_ipc(
        self, dias_anticipacion: int = 30
    ) -> List[Dict[str, Any]]:
        return self.repo.obtener_contratos_elegibles_ipc(dias_anticipacion)

    @cache_manager.cached("dashboard:comisiones_pendientes", level=1, ttl=60)
    def obtener_comisiones_pendientes(self, id_asesor: int = None) -> Dict:
        return self.repo.obtener_comisiones_pendientes(id_asesor)

    @cache_manager.cached("dashboard:tasa_ocupacion", level=1, ttl=60)
    def obtener_tasa_ocupacion(self, id_asesor: int = None) -> Dict:
        try:
            return self.repo.obtener_metricas_ocupacion(id_asesor)
        except Exception as e:
            import logging

            logging.error(f"Error en obtener_tasa_ocupacion: {e}")
            return {
                "ocupadas": 0,
                "disponibles": 0,
                "total": 0,
                "porcentaje_ocupacion": 0,
            }

    @cache_manager.cached("dashboard:propiedades_tipo", level=1, ttl=60)
    def obtener_propiedades_por_tipo(self, id_asesor: int = None) -> Dict[str, int]:
        return self.repo.obtener_propiedades_por_tipo(id_asesor)

    @cache_manager.cached("dashboard:metricas_expertas", level=1, ttl=60)
    def obtener_metricas_expertas(self, id_asesor: int = None) -> Dict[str, float]:
        try:
            data = self.repo.obtener_metricas_expertas(id_asesor)
            # Asegurar que los valores sean float para evitar errores de tipo en Reflex
            return {k: float(v) for k, v in data.items()}
        except Exception as e:
            import logging

            logging.error(f"Error en obtener_metricas_expertas: {e}")
            return {
                "ocupacion_financiera": 0.0,
                "eficiencia_recaudo": 0.0,
                "potencial_total": 0.0,
                "recaudo_real": 0.0,
            }

    @cache_manager.cached("dashboard:top_asesores", level=1, ttl=60)
    def obtener_top_asesores_revenue(self) -> List[Dict]:
        return self.repo.obtener_top_asesores_revenue()

    @cache_manager.cached("dashboard:tunel_vencimientos", level=1, ttl=60)
    def obtener_tunel_vencimientos(self) -> List[Dict]:
        try:
            return self.repo.obtener_tunel_vencimientos()
        except Exception as e:
            import logging

            logging.error(f"Error en obtener_tunel_vencimientos: {e}")
            return []

    def obtener_metricas_incidentes(self) -> Dict:
        return self.repo.obtener_metricas_incidentes()

    def obtener_total_contratos_activos(self, id_asesor: int = None) -> int:
        return self.repo.obtener_total_contratos_activos(id_asesor)

    def obtener_recibos_vencidos_resumen(self) -> Dict:
        return self.repo.obtener_recibos_vencidos_resumen()

    def obtener_evolucion_recaudo(
        self,
        meses: int = 6,
        mes_fin: int = None,
        anio_fin: int = None,
        id_asesor: Optional[int] = None,
    ) -> Dict:
        """Obtiene la evolución del recaudo histórico utilizando una única consulta optimizada (Fase 3)."""
        hoy = datetime.now()
        mes_fin = mes_fin or hoy.month
        anio_fin = anio_fin or hoy.year
        fecha_corte = datetime(anio_fin, mes_fin, 1)

        etiquetas = []
        valores = []

        try:
            # Obtener datos optimizados (1 sola query)
            historico = self.repo.obtener_historico_recaudos(
                meses, mes_fin, anio_fin, id_asesor
            )

            # Reconstruir la serie asegurando que los meses sin recaudo aparezcan como 0
            for i in range(meses - 1, -1, -1):
                m = (fecha_corte.month - i - 1) % 12 + 1
                a = fecha_corte.year + (fecha_corte.month - i - 1) // 12
                mes_str = f"{m:02d}/{a}"

                etiquetas.append(mes_str)
                valores.append(historico.get(mes_str, 0.0))

        except Exception as e:
            # Fallback en caso de error o si el repositorio falla
            import logging

            logging.error(f"Error al obtener evolución recaudo: {e}")
            etiquetas = [f"Mes {-i}" for i in range(meses - 1, -1, -1)]
            valores = [0.0] * meses

        return {"etiquetas": etiquetas, "valores": valores}
