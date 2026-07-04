import json
from dataclasses import replace
from datetime import datetime
from typing import Any, Dict, List, Optional

from src.dominio.entidades.cotizacion import Cotizacion
from src.dominio.entidades.historial_incidente import HistorialIncidente
from src.dominio.entidades.incidente import Incidente
from src.dominio.interfaces.repositorio_incidentes import RepositorioIncidentes
from src.infraestructura.persistencia.database import DatabaseManager
from src.infraestructura.persistencia.repositorio_incidentes_postgres import (
    RepositorioIncidentesPostgres,
)
from src.infraestructura.persistencia.repositorio_orden_trabajo_postgres import (
    RepositorioOrdenTrabajoPostgres,
)
from src.infraestructura.persistencia.repositorio_propiedad_postgres import (
    RepositorioPropiedadPostgres,
)
from src.infraestructura.persistencia.repositorio_proveedores_postgres import (
    RepositorioProveedoresPostgres,
)


from src.dominio.interfaces.repositorio_idempotencia import IRepositorioIdempotencia
from src.aplicacion.decorators.idempotent import idempotent
from src.infraestructura.cache.cache_manager import cache_manager


class ServicioIncidentes:
    def __init__(
        self,
        db_manager: DatabaseManager,
        repo_incidentes: RepositorioIncidentes = None,
        repo_idempotencia: Optional[IRepositorioIdempotencia] = None,
    ):
        self.db_manager = db_manager
        self.repo_incidentes = (
            repo_incidentes
            if repo_incidentes
            else RepositorioIncidentesPostgres(db_manager)
        )
        self.repo_proveedores = RepositorioProveedoresPostgres(db_manager)
        self.repo_propiedades = RepositorioPropiedadPostgres(db_manager)
        self.repo_ordenes = RepositorioOrdenTrabajoPostgres(db_manager)

        from src.infraestructura.persistencia.repositorio_plan_pago_postgres import (
            RepositorioPlanPagoPostgres,
        )
        from src.infraestructura.persistencia.repositorio_cuota_postgres import (
            RepositorioCuotaPostgres,
        )
        from src.infraestructura.persistencia.repositorio_bloqueos import (
            RepositorioBloqueos,
        )

        self.repo_plan_pago = RepositorioPlanPagoPostgres(db_manager)
        self.repo_cuota = RepositorioCuotaPostgres(db_manager)
        self.repo_bloqueos = RepositorioBloqueos(db_manager)
        self.repo_idempotencia = repo_idempotencia

    @idempotent(key_prefix="incidentes:reportar")
    @cache_manager.invalidates("dashboard")
    def reportar_incidente(
        self,
        datos: Dict[str, Any],
        usuario_sistema: str,
        idempotency_key: Optional[str] = None,
    ) -> Incidente:
        """
        Reporta un nuevo incidente.
        Estado inicial: Reportado.
        """
        with self.db_manager.transaccion():
            incidente = Incidente(
                id_propiedad=datos["id_propiedad"],
                id_contrato_m=datos.get("id_contrato_m"),
                descripcion_incidente=datos["descripcion"],
                fecha_incidente=datos.get(
                    "fecha_incidente", datetime.now().isoformat()
                ),
                prioridad=datos.get("prioridad", "Media"),
                origen_reporte=datos.get("origen_reporte", "Inquilino"),
                created_by=usuario_sistema,
            )
            id_new = self.repo_incidentes.guardar(incidente)
            resultado = replace(incidente, id_incidente=id_new)

        # Auditoría Elite
        if self.repo_idempotencia and idempotency_key:
            try:
                # Intentar obtener ID de usuario
                user_data = self.db_manager.execute_query_one(
                    "SELECT id_usuario FROM usuarios WHERE nombre_usuario = %s",
                    (usuario_sistema,),
                )
                u_id = user_data.get("ID_USUARIO") if user_data else 1

                self.repo_idempotencia.registrar_evento(
                    entidad_tipo="Incidente",
                    entidad_id=resultado.id_incidente,
                    tipo_evento="CREATED",
                    idempotency_key=(
                        f"incidentes:reportar:{idempotency_key}"
                        if not idempotency_key.startswith("incidentes")
                        else idempotency_key
                    ),
                    payload=(
                        resultado.__dict__
                        if hasattr(resultado, "__dict__")
                        else {"id": resultado.id_incidente}
                    ),
                    usuario_id=u_id,
                )
            except Exception:
                pass

        return resultado

    def listar_incidentes(
        self, id_propiedad: Optional[int] = None, estado: Optional[str] = None
    ) -> List[Incidente]:
        return self.repo_incidentes.listar(id_propiedad, estado)

    def listar_con_filtros(
        self,
        busqueda: Optional[str] = None,
        id_propiedad: Optional[int] = None,
        prioridad: Optional[str] = None,
        estado: Optional[str] = None,
        fecha_desde: Optional[str] = None,
        fecha_hasta: Optional[str] = None,
        id_proveedor: Optional[int] = None,
        dias_min: Optional[int] = None,
        page: Optional[int] = None,
        page_size: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Lista incidentes delegando filtros al repositorio PostgreSQL."""
        return self.repo_incidentes.listar_con_filtros(
            busqueda=busqueda,
            id_propiedad=id_propiedad,
            prioridad=prioridad,
            estado=estado,
            fecha_desde=fecha_desde,
            fecha_hasta=fecha_hasta,
            id_proveedor=id_proveedor,
            dias_min=dias_min,
            page=page,
            page_size=page_size,
        )

    def obtener_detalle(self, id_incidente: int) -> Optional[Dict[str, Any]]:
        incidente = self.repo_incidentes.obtener_por_id(id_incidente)
        if not incidente:
            return None

        cotizaciones = self.repo_incidentes.obtener_cotizaciones(id_incidente)
        proveedor_asignado = None
        if incidente.id_proveedor_asignado:
            proveedor_asignado = self.repo_proveedores.obtener_por_id(
                incidente.id_proveedor_asignado
            )

        propiedad = self.repo_propiedades.obtener_por_id(incidente.id_propiedad)

        return {
            "incidente": incidente,
            "cotizaciones": cotizaciones,
            "proveedor_asignado": proveedor_asignado,
            "propiedad": propiedad,
        }

    # Los métodos obtener_datos_* han sido removidos. La data ahora se obtiene
    # mediante JOINs en el Repositorio (Fase 1 del Refactor Maestro).

    @cache_manager.invalidates("dashboard")
    def cambiar_estado(
        self,
        id_incidente: int,
        nuevo_estado: str,
        usuario_sistema: str,
        datos_extra: Optional[Dict[str, Any]] = None,
    ) -> Incidente:
        """Gestiona transiciones de estado."""
        with self.db_manager.transaccion():
            incidente = self.repo_incidentes.obtener_por_id(id_incidente)
            if not incidente:
                raise ValueError(f"Incidente {id_incidente} no encontrado")

            incidente = incidente.avanzar_estado(nuevo_estado, usuario_sistema)

            if nuevo_estado == "Aprobado" and datos_extra:
                cambios = {}
                if "costo" in datos_extra:
                    cambios["costo_incidente"] = datos_extra["costo"]
                if "id_proveedor" in datos_extra:
                    cambios["id_proveedor_asignado"] = datos_extra["id_proveedor"]
                if "responsable_pago" in datos_extra:
                    cambios["responsable_pago"] = datos_extra["responsable_pago"]
                if cambios:
                    incidente = replace(incidente, **cambios)

            self.repo_incidentes.actualizar(incidente)
            return incidente

    @cache_manager.invalidates("dashboard")
    def registrar_cotizacion(
        self, id_incidente: int, datos_cotizacion: Dict[str, Any], usuario_sistema: str
    ) -> Cotizacion:
        """Registra una cotización y pasa el incidente a 'Cotizado'."""
        with self.db_manager.transaccion():
            incidente = self.repo_incidentes.obtener_por_id(id_incidente)

            if not incidente:
                raise ValueError("Incidente no encontrado")

            cotizacion = Cotizacion(
                id_incidente=id_incidente,
                id_proveedor=datos_cotizacion["id_proveedor"],
                valor_materiales=datos_cotizacion.get("materiales", 0),
                valor_mano_obra=datos_cotizacion.get("mano_obra", 0),
                descripcion_trabajo=datos_cotizacion.get("descripcion"),
                dias_estimados=datos_cotizacion.get("dias", 1),
                created_by=usuario_sistema,
            )

            cotizacion = cotizacion.con_total_calculado()
            new_id = self.repo_incidentes.guardar_cotizacion(cotizacion)
            cotizacion = replace(cotizacion, id_cotizacion=new_id)

            if incidente.estado == "Reportado":
                estado_anterior = incidente.estado
                incidente = incidente.avanzar_estado("En Revision", usuario_sistema)
                self.repo_incidentes.actualizar(incidente)
                self._registrar_historial(
                    id_incidente=id_incidente,
                    estado_anterior=estado_anterior,
                    estado_nuevo="En Revision",
                    usuario=usuario_sistema,
                    tipo_accion="CAMBIO_ESTADO",
                )

            return cotizacion

    @cache_manager.invalidates("dashboard")
    def iniciar_reparacion(self, id_incidente: int, usuario_sistema: str) -> None:
        """Inicia la reparación, cambiando el estado de Aprobado a En Reparacion."""
        with self.db_manager.transaccion():
            incidente = self.repo_incidentes.obtener_por_id(id_incidente)
            if not incidente:
                raise ValueError(f"Incidente {id_incidente} no encontrado")

            if incidente.estado != "Aprobado":
                raise ValueError(
                    f"Solo se puede iniciar reparación desde estado Aprobado. Estado actual: {incidente.estado}"
                )

            estado_anterior = incidente.estado
            incidente = incidente.avanzar_estado("En Reparacion", usuario_sistema)
            self.repo_incidentes.actualizar(incidente)

            self._registrar_historial(
                id_incidente=id_incidente,
                estado_anterior=estado_anterior,
                estado_nuevo="En Reparacion",
                usuario=usuario_sistema,
                tipo_accion="INICIAR_REPARACION",
            )

    @cache_manager.invalidates("dashboard")
    def aprobar_cotizacion(
        self,
        id_incidente: int,
        id_cotizacion: int,
        usuario_sistema: str,
        responsable_pago: str,
    ) -> None:
        """Aprueba una cotización, asigna el proveedor y costo, y pasa a 'Aprobado'."""
        with self.db_manager.transaccion():
            incidente = self.repo_incidentes.obtener_por_id(id_incidente)
            cotizaciones = self.repo_incidentes.obtener_cotizaciones(id_incidente)

            cotizacion_aprobada = next(
                (c for c in cotizaciones if c.id_cotizacion == id_cotizacion), None
            )
            if not cotizacion_aprobada:
                raise ValueError("Cotización no encontrada")

            for c in cotizaciones:
                nuevo_est = (
                    "Aprobada" if c.id_cotizacion == id_cotizacion else "Rechazada"
                )
                c_update = replace(c, estado_cotizacion=nuevo_est)
                self.repo_incidentes.actualizar_cotizacion(c_update)

            incidente = replace(
                incidente,
                id_cotizacion_aprobada=id_cotizacion,
                id_proveedor_asignado=cotizacion_aprobada.id_proveedor,
                costo_incidente=cotizacion_aprobada.valor_total,
                responsable_pago=responsable_pago,
            )
            estado_anterior = incidente.estado
            incidente = incidente.avanzar_estado("Aprobado", usuario_sistema)

            self.repo_incidentes.actualizar(incidente)

            # Crear plan de pago automáticamente con 1 cuota
            from src.aplicacion.servicios.servicio_plan_pago import (
                ServicioPlanPagoIncidente,
            )

            servicio_plan = ServicioPlanPagoIncidente(
                repositorio_plan=self.repo_plan_pago,
                repositorio_cuota=self.repo_cuota,
                repositorio_incidentes=self.repo_incidentes,
                repositorio_bloqueos=self.repo_bloqueos,
            )

            # Solo si el responsable de pago es Propietario (o Inquilino, pero esto impacta Liquidaciones de Propietario)
            if cotizacion_aprobada.valor_total > 0:
                res = servicio_plan.crear_plan(
                    id_incidente=id_incidente,
                    num_cuotas=1,
                    valor_cuota=cotizacion_aprobada.valor_total,
                    creado_por=usuario_sistema,
                )
                if not res.get("success"):
                    _log.warning(
                        f"No se pudo crear el plan de pago automáticamente: {res.get('message')}"
                    )

            self._registrar_historial(
                id_incidente=id_incidente,
                estado_anterior=estado_anterior,
                estado_nuevo="Aprobado",
                usuario=usuario_sistema,
                tipo_accion="APROBAR_COTIZACION",
                datos_extra={
                    "id_cotizacion_aprobada": id_cotizacion,
                    "costo": cotizacion_aprobada.valor_total,
                },
            )

    def obtener_costos_reparaciones_periodo(
        self, id_contrato_m: int, mes_anio: str
    ) -> int:
        """Retorna la suma de costos de incidentes Aprobados/Finalizados en un mes dado."""
        incidentes = self.repo_incidentes.listar()

        total = 0
        for inc in incidentes:
            if (
                inc.id_contrato_m == id_contrato_m
                and inc.responsable_pago == "Propietario"
            ):
                fecha_ref = inc.fecha_arreglo or inc.updated_at
                if fecha_ref:
                    if isinstance(fecha_ref, str):
                        fecha_ref = datetime.fromisoformat(fecha_ref)
                    if fecha_ref.strftime("%Y-%m") == mes_anio:
                        total += inc.costo_incidente
        return total

    def _registrar_historial(
        self,
        id_incidente: int,
        estado_anterior: str,
        estado_nuevo: str,
        usuario: str,
        tipo_accion: str,
        comentario: str = None,
        datos_extra: Dict = None,
    ) -> None:
        """Método interno para registrar cambios en el historial del incidente."""
        historial = HistorialIncidente(
            id_incidente=id_incidente,
            estado_anterior=estado_anterior,
            estado_nuevo=estado_nuevo,
            usuario=usuario,
            comentario=comentario,
            tipo_accion=tipo_accion,
            datos_adicionales=json.dumps(datos_extra) if datos_extra else None,
        )
        self.repo_incidentes.guardar_historial(historial)

        # Auditoría Global vía Repositorio (Clean Architecture)
        self.repo_incidentes.guardar_auditoria(
            tabla="incidentes",
            id_registro=id_incidente,
            tipo_operacion=(
                "ESTADO_CHANGE" if estado_anterior != estado_nuevo else "UPDATE"
            ),
            valor_anterior=estado_anterior,
            valor_nuevo=estado_nuevo,
            usuario=usuario,
            motivo=f"Acción: {tipo_accion} | Comentario: {comentario or 'N/A'}",
        )

    @cache_manager.invalidates("dashboard")
    def rechazar_cotizacion(
        self,
        id_incidente: int,
        id_cotizacion: int,
        usuario_sistema: str,
        motivo: str = None,
    ) -> None:
        """Rechaza una cotización específica."""
        with self.db_manager.transaccion():
            incidente = self.repo_incidentes.obtener_por_id(id_incidente)
            if not incidente:
                raise ValueError(f"Incidente {id_incidente} no encontrado")

            cotizaciones = self.repo_incidentes.obtener_cotizaciones(id_incidente)
            cotizacion = next(
                (c for c in cotizaciones if c.id_cotizacion == id_cotizacion), None
            )

            if not cotizacion:
                raise ValueError("Cotización no encontrada")

            if cotizacion.estado_cotizacion != "Pendiente":
                raise ValueError(
                    f"Solo se pueden rechazar cotizaciones pendientes. Estado actual: {cotizacion.estado_cotizacion}"
                )

            cotizacion = replace(cotizacion, estado_cotizacion="Rechazada")
            self.repo_incidentes.actualizar_cotizacion(cotizacion)

            self._registrar_historial(
                id_incidente=id_incidente,
                estado_anterior=incidente.estado,
                estado_nuevo=incidente.estado,
                usuario=usuario_sistema,
                tipo_accion="COTIZACION_RECHAZADA",
                comentario=motivo,
                datos_extra={
                    "id_cotizacion": id_cotizacion,
                    "id_proveedor": cotizacion.id_proveedor,
                    "valor_total": cotizacion.valor_total,
                },
            )

    @cache_manager.invalidates("dashboard")
    def finalizar_incidente(
        self,
        id_incidente: int,
        usuario_sistema: str,
        costo_final: int = None,
        comentario: str = None,
        fecha_arreglo: datetime = None,
        es_finalizacion_directa: bool = False,
        id_proveedor: int = None,
    ) -> Incidente:
        """Finaliza un incidente desde cualquier estado editable."""
        estados_finalizables = [
            "Reportado",
            "En Revision",
            "Cotizado",
            "Aprobado",
            "En Reparacion",
        ]

        with self.db_manager.transaccion():
            incidente = self.repo_incidentes.obtener_por_id(id_incidente)
            if not incidente:
                raise ValueError(f"Incidente {id_incidente} no encontrado")

            if incidente.estado not in estados_finalizables:
                raise ValueError(
                    f"No se puede finalizar un incidente en estado {incidente.estado}."
                )

            estado_anterior = incidente.estado
            costo_anterior = incidente.costo_incidente

            if costo_final is not None and costo_final != incidente.costo_incidente:
                incidente = replace(incidente, costo_incidente=costo_final)

            if id_proveedor:
                incidente = replace(incidente, id_proveedor_asignado=id_proveedor)

            incidente = incidente.avanzar_estado("Finalizado", usuario_sistema)

            if fecha_arreglo:
                incidente = replace(incidente, fecha_arreglo=fecha_arreglo)

            self.repo_incidentes.actualizar(incidente)

            tipo_accion = (
                "FINALIZACION_DIRECTA" if es_finalizacion_directa else "CAMBIO_ESTADO"
            )

            self._registrar_historial(
                id_incidente=id_incidente,
                estado_anterior=estado_anterior,
                estado_nuevo="Finalizado",
                usuario=usuario_sistema,
                tipo_accion=tipo_accion,
                comentario=comentario,
                datos_extra={
                    "costo_presupuestado": costo_anterior,
                    "costo_final": incidente.costo_incidente,
                    "es_finalizacion_directa": es_finalizacion_directa,
                },
            )

            return incidente

    @cache_manager.invalidates("dashboard")
    def cancelar_incidente(
        self, id_incidente: int, usuario_sistema: str, motivo: str
    ) -> Incidente:
        """Cancela un incidente."""
        if not motivo or not motivo.strip():
            raise ValueError("Se requiere un motivo para cancelar el incidente")

        with self.db_manager.transaccion():
            incidente = self.repo_incidentes.obtener_por_id(id_incidente)
            if not incidente:
                raise ValueError(f"Incidente {id_incidente} no encontrado")

            if incidente.estado in ["Finalizado", "Cancelado"]:
                raise ValueError(
                    f"No se puede cancelar un incidente {incidente.estado}"
                )

            estado_anterior = incidente.estado

            incidente = replace(
                incidente,
                estado="Cancelado",
                motivo_cancelacion=motivo,
                updated_by=usuario_sistema,
                updated_at=datetime.now(),
            )

            self.repo_incidentes.actualizar(incidente)

            self._registrar_historial(
                id_incidente=id_incidente,
                estado_anterior=estado_anterior,
                estado_nuevo="Cancelado",
                usuario=usuario_sistema,
                tipo_accion="CANCELACION",
                comentario=motivo,
            )

            return incidente

    def obtener_historial(self, id_incidente: int) -> List[HistorialIncidente]:
        """Obtiene el historial completo de cambios de un incidente."""
        return self.repo_incidentes.obtener_historial(id_incidente)

    def obtener_cotizaciones_rechazadas(self, id_incidente: int) -> List[Cotizacion]:
        """Obtiene solo las cotizaciones rechazadas de un incidente."""
        cotizaciones = self.repo_incidentes.obtener_cotizaciones(id_incidente)
        return [c for c in cotizaciones if c.estado_cotizacion == "Rechazada"]

    @cache_manager.invalidates("dashboard")
    def editar_incidente(
        self,
        id_incidente: int,
        datos_actualizacion: Dict[str, Any],
        usuario_sistema: str,
    ) -> Incidente:
        """Edita los atributos de un incidente sin cambiar de estado."""
        campos_bloqueados_por_estado = {
            "Reportado": [],
            "En Revision": [],
            "Cotizado": ["id_propiedad", "id_contrato_m", "origen_reporte"],
            "Aprobado": [
                "id_propiedad",
                "id_contrato_m",
                "origen_reporte",
                "prioridad",
            ],
            "En Reparacion": [
                "id_propiedad",
                "id_contrato_m",
                "origen_reporte",
                "prioridad",
                "descripcion_incidente",
            ],
            "Finalizado": ["*"],
            "Cancelado": ["*"],
        }

        with self.db_manager.transaccion():
            incidente = self.repo_incidentes.obtener_por_id(id_incidente)
            if not incidente:
                raise ValueError(f"Incidente {id_incidente} no encontrado")

            estado_actual = incidente.estado

            if estado_actual in ["Finalizado", "Cancelado"]:
                raise ValueError(
                    f"No se puede editar un incidente en estado {estado_actual}"
                )

            campos_bloqueados = campos_bloqueados_por_estado.get(estado_actual, [])

            cambios_validos = {}
            cambios_rechazados = []

            for campo, valor in datos_actualizacion.items():
                if campo in [
                    "updated_by",
                    "updated_at",
                    "created_by",
                    "created_at",
                    "id_incidente",
                    "estado",
                ]:
                    continue
                if campo == "*" in campos_bloqueados:
                    cambios_rechazados.append(campo)
                    continue
                if campo in campos_bloqueados:
                    cambios_rechazados.append(campo)
                    continue

                cambios_validos[campo] = valor

            if cambios_rechazados:
                raise ValueError(
                    f"Campos no editables en estado {estado_actual}: {', '.join(cambios_rechazados)}"
                )

            if not cambios_validos:
                raise ValueError("No hay campos válidos para actualizar")

            cambios_validos["updated_by"] = usuario_sistema
            cambios_validos["updated_at"] = datetime.now()

            incidente_actualizado = replace(incidente, **cambios_validos)
            self.repo_incidentes.actualizar(incidente_actualizado)

            self._registrar_historial(
                id_incidente=id_incidente,
                estado_anterior=estado_actual,
                estado_nuevo=estado_actual,
                usuario=usuario_sistema,
                tipo_accion="EDICION",
                comentario=f"Campos editados: {', '.join(cambios_validos.keys())}",
                datos_extra=cambios_validos,
            )

            return incidente_actualizado
