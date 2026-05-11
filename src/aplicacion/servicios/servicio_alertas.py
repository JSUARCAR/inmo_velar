from datetime import datetime
from typing import Any, Dict, List, Optional

from src.aplicacion.servicios.servicio_configuracion import ServicioConfiguracion
from src.aplicacion.servicios.servicio_contratos import ServicioContratos
from src.aplicacion.servicios.servicio_recibos_publicos import ServicioRecibosPublicos
from src.dominio.entidades.alerta import Alerta
from src.dominio.interfaces.repositorio_alerta import IRepositorioAlerta
from src.infraestructura.persistencia.database import DatabaseManager
from src.infraestructura.persistencia.repositorio_arrendatario_sqlite import (
    RepositorioArrendatarioSQLite,
)
from src.infraestructura.persistencia.repositorio_asistencia_postgres import (
    RepositorioAsistenciaPostgres,
)
from src.infraestructura.persistencia.repositorio_codeudor_sqlite import (
    RepositorioCodeudorSQLite,
)
from src.infraestructura.persistencia.repositorio_contrato_arrendamiento_sqlite import (
    RepositorioContratoArrendamientoSQLite,
)
from src.infraestructura.persistencia.repositorio_contrato_mandato_sqlite import (
    RepositorioContratoMandatoSQLite,
)
from src.infraestructura.persistencia.repositorio_ipc_sqlite import RepositorioIPCSQLite
from src.infraestructura.persistencia.repositorio_pagos_admin_postgres import (
    RepositorioPagosAdminPostgres,
)
from src.infraestructura.persistencia.repositorio_propiedad_sqlite import (
    RepositorioPropiedadSQLite,
)
from src.infraestructura.persistencia.repositorio_renovacion_sqlite import (
    RepositorioRenovacionSQLite,
)
from src.infraestructura.repositorios.repositorio_recibo_publico import (
    RepositorioReciboPublico,
)
from src.infraestructura.persistencia.repositorio_dashboard import (
    RepositorioDashboard,
)


import logging
logger = logging.getLogger(__name__)

class ServicioAlertas:
    """
    Servicio de gestión y sincronización de alertas del sistema.
    Centraliza la detección de vencimientos y eventos críticos persistiendo
    los resultados en la tabla ALERTAS para su gestión en el Dashboard.
    """

    def __init__(self, db_manager: DatabaseManager, repo_alerta: IRepositorioAlerta):
        self.db = db_manager
        self.repo_alerta = repo_alerta

        # Instanciar Repositorios Auxiliares
        repo_propiedad = RepositorioPropiedadSQLite(db_manager)
        repo_mandato = RepositorioContratoMandatoSQLite(db_manager)
        repo_arriendo = RepositorioContratoArrendamientoSQLite(db_manager)
        repo_renovacion = RepositorioRenovacionSQLite(db_manager)
        repo_ipc = RepositorioIPCSQLite(db_manager)
        repo_arrendatario = RepositorioArrendatarioSQLite(db_manager)
        repo_codeudor = RepositorioCodeudorSQLite(db_manager)
        repo_recibos = RepositorioReciboPublico(db_manager)

        # Repositorios PH
        self.repo_asistencia = RepositorioAsistenciaPostgres(db_manager)
        self.repo_pagos_admin = RepositorioPagosAdminPostgres(db_manager)

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
            repo_codeudor=repo_codeudor,
        )

        self.servicio_recibos = ServicioRecibosPublicos(repo_recibos, repo_propiedad)

        # Repositorio Dashboard (para consultas IPC elegibles)
        self.repo_dashboard = RepositorioDashboard(db_manager)

    def sincronizar_alertas(self, usuario_sistema: str = "sistema", forzar: bool = False) -> int:
        """
        Escanea el sistema en busca de eventos que requieran alertas y las persiste.
        Implementa guard global para evitar DDOS y validación de historial para idempotencia.
        """
        from src.infraestructura.cache.cache_manager import cache_manager

        # 1. Guard Global (Evitar DDOS por múltiples sesiones)
        if not forzar:
            last_global_sync = cache_manager.l1.get("alertas:last_global_sync")
            if last_global_sync:
                logger.debug("Sincronización global omitida (Guard de 30 min activo)")
                return 0

        logger.info(f"Iniciando sincronización proactiva de alertas (Usuario: {usuario_sistema})...")
        nuevas = 0
        alertas_calculadas = self.obtener_alertas_calculadas()

        for ac in alertas_calculadas:
            try:
                # Extraer ID de entidad
                partes = ac["id"].split("_")
                id_entidad = int(partes[-1]) if len(partes) > 1 else None
                
                # 2. Idempotencia Avanzada (Bug Recreación Fix)
                # Buscamos si existe una alerta PENDIENTE
                existente = self.repo_alerta.obtener_por_entidad_y_tipo(
                    id_entidad=id_entidad,
                    tipo_entidad=ac.get("tipo_entidad", "Otros"),
                    tipo_alerta=ac["tipo"],
                    solo_pendientes=True,
                )

                if not existente:
                    # Verificamos si se resolvió recientemente (ej: hoy) para no molestar
                    # Esto evita el bucle infinito si el usuario resuelve pero no corrige el origen
                    reciente = self.repo_alerta.obtener_por_entidad_y_tipo(
                        id_entidad=id_entidad,
                        tipo_entidad=ac.get("tipo_entidad", "Otros"),
                        tipo_alerta=ac["tipo"],
                        solo_pendientes=False,
                    )
                    
                    # Si existe una resuelta hoy, no recrear
                    if reciente and reciente.fecha_resolucion:
                        if reciente.fecha_resolucion[:10] == datetime.now().isoformat()[:10]:
                            continue

                    nueva_alerta = Alerta(
                        tipo_alerta=ac["tipo"],
                        descripcion_alerta=ac["mensaje"],
                        prioridad=ac["prioridad"],
                        fecha_generacion_alerta=datetime.now().isoformat(),
                        fecha_vencimiento_alerta=ac.get("fecha"),
                        estado_alerta="Pendiente",
                        id_entidad_relacionada=id_entidad,
                        tipo_entidad=ac.get("tipo_entidad", "Otros"),
                    )
                    self.repo_alerta.guardar(nueva_alerta, usuario_sistema)
                    nuevas += 1
            except Exception as e:
                logger.error(f"Error procesando alerta individual {ac.get('id')}: {e}")

        # 3. Finalización y Caché
        if nuevas > 0:
            cache_manager.invalidate("dashboard", level=1)
            logger.info(f"Sincronización completa: {nuevas} nuevas alertas registradas.")
        
        # Establecer timestamp global de sincronización (30 min)
        cache_manager.l1.set("alertas:last_global_sync", datetime.now().isoformat())

        return nuevas

    def obtener_alertas(
        self,
        estado: Optional[str] = None,
        prioridad: Optional[str] = None,
        tipo: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        formato_notificacion: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Retorna las alertas persistidas en la base de datos con filtros opcionales.
        """
        entidades = self.repo_alerta.obtener_todas(
            estado=estado, prioridad=prioridad, tipo=tipo, limit=limit, offset=offset
        )

        if not formato_notificacion:
            return [vars(e) for e in entidades]

        # Formato compatible con la campana de notificaciones UI
        return [
            {
                "id": str(e.id_alertas),
                "tipo": e.tipo_alerta,
                "mensaje": e.descripcion_alerta,
                "fecha": e.fecha_vencimiento_alerta or e.fecha_generacion_alerta[:10],
                "nivel": "danger" if e.prioridad == "Alta" else "warning",
                "link": self._obtener_link_por_tipo(e.tipo_alerta),
            }
            for e in entidades
        ]

    def contar_todas(
        self,
        estado: Optional[str] = None,
        prioridad: Optional[str] = None,
        tipo: Optional[str] = None,
    ) -> int:
        """Cuenta el total de alertas según filtros."""
        return self.repo_alerta.contar_todas(estado=estado, prioridad=prioridad, tipo=tipo)

    def marcar_como_resuelta(self, id_alerta: int, usuario: str, accion: str) -> bool:
        """Marcar una alerta como resuelta."""
        result = self.repo_alerta.marcar_resuelta(id_alerta, usuario, accion)
        if result:
            from src.infraestructura.cache.cache_manager import cache_manager
            cache_manager.invalidate("dashboard")
        return result

    def exportar_alertas_csv(
        self,
        estado: Optional[str] = None,
        prioridad: Optional[str] = None,
        tipo: Optional[str] = None,
    ) -> str:
        """Genera un contenido CSV con las alertas filtradas."""
        import csv
        import io

        entidades = self.repo_alerta.obtener_todas(
            estado=estado, prioridad=prioridad, tipo=tipo, limit=1000
        )

        output = io.StringIO()
        writer = csv.writer(output, delimiter=";", quoting=csv.QUOTE_MINIMAL)

        # Header
        writer.writerow(
            [
                "ID",
                "Tipo",
                "Prioridad",
                "Estado",
                "Descripción",
                "Vencimiento",
                "Generación",
                "Entidad Relacionada",
            ]
        )

        # Data
        for e in entidades:
            writer.writerow(
                [
                    e.id_alertas,
                    e.tipo_alerta,
                    e.prioridad,
                    e.estado_alerta,
                    e.descripcion_alerta,
                    e.fecha_vencimiento_alerta or "N/A",
                    e.fecha_generacion_alerta[:10],
                    f"{e.tipo_entidad or ''} #{e.id_entidad_relacionada or ''}",
                ]
            )

        return output.getvalue()

    def obtener_alertas_calculadas(self) -> List[Dict[str, Any]]:
        """
        Realiza el cálculo lógico de lo que DEBERÍA ser una alerta hoy.
        """
        alertas = []

        # 1. Contratos próximos a vencer
        dias_cnt = self.servicio_config.obtener_valor_parametro("DIAS_ALERTA_ARRENDAMIENTO", 90)
        contratos_vencen = self.servicio_contratos.listar_arrendamientos_por_vencer(
            dias_antelacion=dias_cnt
        )
        for c in contratos_vencen:
            dias = c["dias_restantes"]
            prioridad = "Alta" if dias < 30 else "Media"

            if dias < 0:
                mensaje = f"Arriendo VENCIDO hace {abs(dias)} días: {c['propiedad']}"
            elif dias == 0:
                mensaje = f"Arriendo vence HOY: {c['propiedad']}"
            else:
                mensaje = f"Arriendo vence en {dias} días: {c['propiedad']}"

            alertas.append(
                {
                    "id": f"cnt_{c['id']}",
                    "tipo": "Vencimiento Contrato Arrendamiento",
                    "tipo_entidad": "Contrato",
                    "mensaje": mensaje,
                    "fecha": c["fecha_fin"],
                    "prioridad": prioridad,
                }
            )

        # 1.1 Contratos Mandato
        dias_mand_config = self.servicio_config.obtener_valor_parametro("DIAS_ALERTA_MANDATO", 90)
        dias_mand = max(90, int(dias_mand_config or 90))

        mandatos_vencen = self.servicio_contratos.listar_mandatos_por_vencer(
            dias_antelacion=dias_mand
        )
        for m in mandatos_vencen:
            dias = m["dias_restantes"]
            prioridad = "Alta" if dias < 30 else "Media"

            if dias < 0:
                mensaje = f"Mandato VENCIDO hace {abs(dias)} días: {m['propiedad']}"
            elif dias == 0:
                mensaje = f"Mandato vence HOY: {m['propiedad']}"
            else:
                mensaje = f"Mandato vence en {dias} días: {m['propiedad']}"

            alertas.append(
                {
                    "id": f"mand_{m['id']}",
                    "tipo": "Vencimiento Contrato Mandato",
                    "tipo_entidad": "Contrato",
                    "mensaje": mensaje,
                    "fecha": m["fecha_fin"],
                    "prioridad": prioridad,
                }
            )

        # 1.2 Incrementos IPC
        dias_ipc = self.servicio_config.obtener_valor_parametro("DIAS_ALERTA_IPC", 30)
        contratos_ipc = self.repo_dashboard.obtener_contratos_elegibles_ipc(
            dias=int(dias_ipc)
        )
        for c in contratos_ipc:
            alertas.append(
                {
                    "id": f"ipc_{c['id_contrato']}",
                    "tipo": "Incremento IPC",
                    "tipo_entidad": "Contrato",
                    "mensaje": f"Incremento IPC pendiente: {c['direccion']}",
                    "fecha": c.get("proximo_aniversario"),
                    "prioridad": "Media",
                }
            )

        # 2. Recibos
        recibos_vencidos = self.servicio_recibos.obtener_recibos_vencidos()
        for r in recibos_vencidos:
            alertas.append(
                {
                    "id": f"rcb_v_{r.id_recibo_publico}",
                    "tipo": "Mora Recaudo",
                    "tipo_entidad": "Recibo",
                    "mensaje": f"Recibo VENCIDO ({r.tipo_servicio}): {r.periodo_recibo}",
                    "fecha": r.fecha_vencimiento,
                    "prioridad": "Alta",
                }
            )

        # 3. Alertas PH
        alertas.extend(self._obtener_alertas_asambleas_raw())
        alertas.extend(self._obtener_alertas_pagos_admin_raw())

        return alertas

    def _obtener_link_por_tipo(self, tipo: str) -> str:
        """Helper para navegación."""
        if "Contrato" in tipo:
            return "/contratos"
        if "IPC" in tipo:
            return "/incrementos"
        if "Recibo" in tipo or "Mora" in tipo:
            return "/recibos-publicos"
        if "PH" in tipo or "Asamblea" in tipo:
            return "/propiedad-horizontal"
        return "/dashboard"

    def _obtener_alertas_asambleas_raw(self) -> List[Dict[str, Any]]:
        alertas = []
        try:
            # 1. Asambleas de HOY
            asambleas_hoy = self.repo_asistencia.listar_asambleas_hoy()
            for reg in asambleas_hoy:
                a = reg["entidad"]
                alertas.append(
                    {
                        "id": f"asm_hoy_{a.id_asistencia}",
                        "tipo": "Otros",
                        "tipo_entidad": "Asistencia",
                        "mensaje": f"Asamblea HOY: {reg.get('direccion_propiedad')}",
                        "fecha": str(a.fecha_asistencia),
                        "prioridad": "Alta",
                    }
                )
            
            # 2. Asambleas PRÓXIMAS
            dias_alerta = self.servicio_config.obtener_valor_parametro("DIAS_ALERTA_ASAMBLEA", 3)
            asambleas_prox = self.repo_asistencia.listar_asambleas_proximas(int(dias_alerta))
            for reg in asambleas_prox:
                a = reg["entidad"]
                alertas.append(
                    {
                        "id": f"asm_prox_{a.id_asistencia}",
                        "tipo": "Otros",
                        "tipo_entidad": "Asistencia",
                        "mensaje": f"Asamblea en {a.dias_hasta_asamblea} días: {reg.get('direccion_propiedad')}",
                        "fecha": str(a.fecha_asistencia),
                        "prioridad": "Media",
                    }
                )
        except Exception as e:
            logger.warning(f"Error en _obtener_alertas_asambleas_raw: {e}")
        return alertas

    def _obtener_alertas_pagos_admin_raw(self) -> List[Dict[str, Any]]:
        alertas = []
        try:
            # 1. Pagos VENCIDOS
            vencidos = self.repo_pagos_admin.listar_pagos_vencidos()
            for p in vencidos:
                alertas.append(
                    {
                        "id": f"pago_v_{p.id_pago_admin}",
                        "tipo": "Mora Recaudo",
                        "tipo_entidad": "Pago Administración",
                        "mensaje": f"Administración VENCIDA ({p.periodo_pago}): {p.direccion_propiedad}",
                        "fecha": str(p.created_at)[:10] if p.created_at else None,
                        "prioridad": "Alta",
                    }
                )
            
            # 2. Pagos PRÓXIMOS
            dias_pago = self.servicio_config.obtener_valor_parametro("DIAS_ALERTA_PAGO_ADMIN", 5)
            proximos = self.repo_pagos_admin.listar_pagos_proximos_vencer(int(dias_pago))
            for p in proximos:
                alertas.append(
                    {
                        "id": f"pago_p_{p.id_pago_admin}",
                        "tipo": "Mora Recaudo",
                        "tipo_entidad": "Pago Administración",
                        "mensaje": f"Administración vence en {p.dias_vencimiento} días: {p.direccion_propiedad}",
                        "fecha": p.periodo_pago,
                        "prioridad": "Media",
                    }
                )
        except Exception as e:
            logger.warning(f"Error en _obtener_alertas_pagos_admin_raw: {e}")
        return alertas

