"""
Servicio de Dashboard - Inmobiliaria Velar
Proporciona datos agregados para widgets del dashboard ejecutivo.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from src.dominio.interfaces.repositorio_dashboard import IRepositorioDashboard
from src.infraestructura.cache.cache_manager import cache_manager


class ServicioDashboard:
    """
    Servicio de aplicacion para metricas del dashboard.
    Consolida datos de multiples tablas y vistas.
    """

    def __init__(self, repo_dashboard: IRepositorioDashboard):
        self.repo = repo_dashboard

    @cache_manager.cached("dashboard:cartera_mora", level=1, ttl=60)
    def obtener_cartera_mora(self) -> Dict:
        """Obtiene resumen de cartera en mora."""
        resumen = self.repo.obtener_resumen_mora()
        top_morosos = self.repo.obtener_top_morosos(5)
        return {
            "monto_total": resumen["monto_total"],
            "cantidad_contratos": resumen["cantidad_contratos"],
            "top_morosos": top_morosos,
        }

    @cache_manager.cached("dashboard:flujo_caja", level=1, ttl=60)
    def obtener_flujo_caja_mes(
        self, mes: int = None, anio: int = None, id_asesor: int = None
    ) -> Dict:
        """Obtiene flujo de caja filtrado."""
        hoy = datetime.now()
        mes_actual = f"{mes:02d}" if mes else f"{hoy.month:02d}"
        anio_actual = str(anio) if anio else str(hoy.year)

        recaudado = self.repo.obtener_total_recaudado(mes_actual, anio_actual, id_asesor)
        esperado = self.repo.obtener_total_esperado(id_asesor)

        porcentaje = (recaudado / esperado * 100) if esperado > 0 else 0

        return {
            "recaudado": recaudado,
            "esperado": esperado,
            "porcentaje": round(porcentaje, 1),
            "diferencia": esperado - recaudado,
        }

    @cache_manager.cached("dashboard:contratos_vencer", level=1, ttl=60)
    def obtener_contratos_por_vencer(self) -> Dict:
        """Contratos proximos a vencer por rango."""
        rangos = self.repo.obtener_conteo_vencimientos_rangos()
        total = sum(rangos.values())
        return {**rangos, "total": total}

    def obtener_contratos_proximos_vencer(self, dias_limite: int = 30) -> List[Dict[str, Any]]:
        return self.repo.obtener_lista_vencimientos(dias_limite)

    def obtener_contratos_elegibles_ipc(self, dias_anticipacion: int = 30) -> List[Dict[str, Any]]:
        return self.repo.obtener_contratos_elegibles_ipc(dias_anticipacion)

    @cache_manager.cached("dashboard:comisiones_pendientes", level=1, ttl=60)
    def obtener_comisiones_pendientes(self, id_asesor: int = None) -> Dict:
        return self.repo.obtener_comisiones_pendientes(id_asesor)

    @cache_manager.cached("dashboard:tasa_ocupacion", level=1, ttl=60)
    def obtener_tasa_ocupacion(self, id_asesor: int = None) -> Dict:
        return self.repo.obtener_metricas_ocupacion(id_asesor)

    @cache_manager.cached("dashboard:propiedades_tipo", level=1, ttl=60)
    def obtener_propiedades_por_tipo(self, id_asesor: int = None) -> Dict[str, int]:
        return self.repo.obtener_propiedades_por_tipo(id_asesor)

    @cache_manager.cached("dashboard:metricas_expertas", level=1, ttl=60)
    def obtener_metricas_expertas(self, id_asesor: int = None) -> Dict[str, float]:
        data = self.repo.obtener_metricas_expertas(id_asesor)
        # Asegurar que los valores sean float para evitar errores de tipo en Reflex
        return {k: float(v) for k, v in data.items()}

    @cache_manager.cached("dashboard:top_asesores", level=1, ttl=60)
    def obtener_top_asesores_revenue(self) -> List[Dict]:
        return self.repo.obtener_top_asesores_revenue()

    @cache_manager.cached("dashboard:tunel_vencimientos", level=1, ttl=60)
    def obtener_tunel_vencimientos(self) -> List[Dict]:
        return self.repo.obtener_tunel_vencimientos()

    def obtener_metricas_incidentes(self) -> Dict:
        return self.repo.obtener_metricas_incidentes()

    def obtener_total_contratos_activos(self, id_asesor: int = None) -> int:
        return self.repo.obtener_total_contratos_activos(id_asesor)

    def obtener_morosidad_por_zona(self) -> Dict:
        return self.repo.obtener_morosidad_por_zona()

    def obtener_desempeno_asesores(self) -> Dict:
        return self.repo.obtener_desempeno_asesores()

    def obtener_recibos_vencidos_resumen(self) -> Dict:
        return self.repo.obtener_recibos_vencidos_resumen()

    def obtener_evolucion_recaudo(self, meses: int = 6, mes_fin: int = None, anio_fin: int = None) -> Dict:
        """Pendiente migrar lógica secuencial a repo o mantenerla aquí llamando al repo mes a mes."""
        # Para cumplir Fase 3, lo ideal es que el repo lo haga en una sola consulta o el servicio llame al repo.
        etiquetas = []
        valores = []
        hoy = datetime.now()
        fecha_corte = datetime(anio_fin, mes_fin, 1) if anio_fin and mes_fin else hoy

        for i in range(meses - 1, -1, -1):
            # Lógica de desplazamiento de meses (simplificada para el ejemplo)
            m = (fecha_corte.month - i - 1) % 12 + 1
            a = fecha_corte.year + (fecha_corte.month - i - 1) // 12
            mes_str = f"{m:02d}"
            anio_str = str(a)
            val = self.repo.obtener_total_recaudado(mes_str, anio_str)
            etiquetas.append(f"{mes_str}/{anio_str}")
            valores.append(val)
        return {"etiquetas": etiquetas, "valores": valores}
