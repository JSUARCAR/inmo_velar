from datetime import datetime
from typing import Any, Dict, List

from src.aplicacion.servicios.servicio_contratos import ServicioContratos
from src.aplicacion.servicios.servicio_recibos_publicos import ServicioRecibosPublicos
from src.aplicacion.servicios.servicio_configuracion import ServicioConfiguracion
from src.infraestructura.persistencia.database import DatabaseManager
from src.infraestructura.persistencia.repositorio_propiedad_sqlite import RepositorioPropiedadSQLite
from src.infraestructura.persistencia.repositorio_contrato_mandato_sqlite import RepositorioContratoMandatoSQLite
from src.infraestructura.persistencia.repositorio_contrato_arrendamiento_sqlite import RepositorioContratoArrendamientoSQLite
from src.infraestructura.persistencia.repositorio_renovacion_sqlite import RepositorioRenovacionSQLite
from src.infraestructura.persistencia.repositorio_ipc_sqlite import RepositorioIPCSQLite
from src.infraestructura.persistencia.repositorio_arrendatario_sqlite import RepositorioArrendatarioSQLite
from src.infraestructura.persistencia.repositorio_codeudor_sqlite import RepositorioCodeudorSQLite
from src.infraestructura.repositorios.repositorio_recibo_publico_sqlite import (
    RepositorioReciboPublicoSQLite,
)


class ServicioAlertas:
    """
    Servicio de agregación de alertas del sistema.
    Centraliza notificaciones de vencimientos y eventos críticos.
    """

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        
        # Instanciar Repositorios
        repo_propiedad = RepositorioPropiedadSQLite(db_manager)
        repo_mandato = RepositorioContratoMandatoSQLite(db_manager)
        repo_arriendo = RepositorioContratoArrendamientoSQLite(db_manager)
        repo_renovacion = RepositorioRenovacionSQLite(db_manager)
        repo_ipc = RepositorioIPCSQLite(db_manager)
        repo_arrendatario = RepositorioArrendatarioSQLite(db_manager)
        repo_codeudor = RepositorioCodeudorSQLite(db_manager)
        repo_recibos = RepositorioReciboPublicoSQLite(db_manager)

        # Servicio de Configuración para parámetros globales
        self.servicio_config = ServicioConfiguracion(db_manager)

        # Inicializar Servicios con dependencias
        self.servicio_contratos = ServicioContratos(
            db_manager,
            repo_mandato=repo_mandato,
            repo_arriendo=repo_arriendo,
            repo_propiedad=repo_propiedad,
            repo_renovacion=repo_renovacion,
            repo_ipc=repo_ipc,
            repo_arrendatario=repo_arrendatario,
            repo_codeudor=repo_codeudor
        )

        self.servicio_recibos = ServicioRecibosPublicos(repo_recibos, repo_propiedad)

    def obtener_alertas(self) -> List[Dict[str, Any]]:
        """
        Consulta y consolida todas las alertas del sistema.
        Retorna lista de diccionarios:
        {
            "id": unique_str,
            "tipo": "Contrato" | "Recibo" | "Sistema",
            "mensaje": str,
            "fecha": str (YYYY-MM-DD),
            "nivel": "warning" | "danger" | "info"
        }
        """
        alertas = []

        # 1. Contratos próximos a vencer (según parámetro o 90 días def)
        dias_cnt = self.servicio_config.obtener_valor_parametro("DIAS_ALERTA_ARRENDAMIENTO", 90)
        contratos_vencen = self.servicio_contratos.listar_arrendamientos_por_vencer(
            dias_antelacion=dias_cnt
        )
        for c in contratos_vencen:
            dias = c["dias_restantes"]
            nivel = "danger" if dias < 30 else "warning"
            alertas.append(
                {
                    "id": f"cnt_{c['id']}",
                    "tipo": "Contrato Arriendo",
                    "mensaje": f"Arriendo vence en {dias} días: {c['propiedad']}",
                    "fecha": c["fecha_fin"],
                    "nivel": nivel,
                    "link": "/contratos",
                }
            )

        # 1.1 Contratos Mandato próximos a vencer (según parámetro o 90 días def)
        # Forzamos mínimo 90 días para asegurar visibilidad alineada con Dashboard
        dias_mand_config = self.servicio_config.obtener_valor_parametro("DIAS_ALERTA_MANDATO", 90)
        dias_mand = max(90, int(dias_mand_config or 90))
        
        mandatos_vencen = self.servicio_contratos.listar_mandatos_por_vencer(
            dias_antelacion=dias_mand
        )
        for m in mandatos_vencen:
            dias = m["dias_restantes"]
            nivel = "danger" if dias < 30 else "warning"
            alertas.append(
                {
                    "id": f"mand_{m['id']}",
                    "tipo": "Contrato Mandato",
                    "mensaje": f"Mandato vence en {dias} días: {m['propiedad']}",
                    "fecha": m["fecha_fin"],
                    "nivel": nivel,
                    "link": "/contratos",
                }
            )

        # 2. Recibos Vencidos (Overdue)
        recibos_vencidos = self.servicio_recibos.obtener_recibos_vencidos()
        for r in recibos_vencidos:
            alertas.append(
                {
                    "id": f"rcb_v_{r.id_recibo_publico}",
                    "tipo": "Recibo",
                    "mensaje": f"Recibo VENCIDO ({r.tipo_servicio}): {r.periodo_recibo}",
                    "fecha": r.fecha_vencimiento,
                    "nivel": "danger",
                    "link": "/recibos-publicos",
                }
            )

        # 3. Recibos Próximos a Vencer (según parámetro o 5 días def)
        dias_rcb = self.servicio_config.obtener_valor_parametro("DIAS_VENCIMIENTO_PAGO", 5)
        recibos_proximos = self.servicio_recibos.listar_recibos_proximos_vencer(dias=dias_rcb)
        for r in recibos_proximos:
            # Calcular días
            try:
                vence = datetime.strptime(r.fecha_vencimiento, "%Y-%m-%d")
                hoy = datetime.now()
                dias = (vence - hoy).days + 1
            except:
                dias = 0

            alertas.append(
                {
                    "id": f"rcb_p_{r.id_recibo_publico}",
                    "tipo": "Recibo",
                    "mensaje": f"Recibo vence pronto ({dias} días): {r.tipo_servicio}",
                    "fecha": r.fecha_vencimiento,
                    "nivel": "warning",
                    "link": "/recibos-publicos",
                }
            )

        return alertas
