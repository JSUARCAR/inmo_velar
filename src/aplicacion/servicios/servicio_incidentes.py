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
from src.infraestructura.persistencia.repositorio_orden_trabajo_sqlite import (
    RepositorioOrdenTrabajoSQLite,
)
from src.infraestructura.persistencia.repositorio_propiedad_sqlite import (
    RepositorioPropiedadSQLite,
)
from src.infraestructura.persistencia.repositorio_proveedores_sqlite import (
    RepositorioProveedoresSQLite,
)


class ServicioIncidentes:
    def __init__(
        self, db_manager: DatabaseManager, repo_incidentes: RepositorioIncidentes = None
    ):
        self.db_manager = db_manager
        self.repo_incidentes = (
            repo_incidentes
            if repo_incidentes
            else RepositorioIncidentesPostgres(db_manager)
        )
        self.repo_proveedores = RepositorioProveedoresSQLite(db_manager)
        self.repo_propiedades = RepositorioPropiedadSQLite(db_manager)
        self.repo_ordenes = RepositorioOrdenTrabajoSQLite(db_manager)

    def reportar_incidente(
        self, datos: Dict[str, Any], usuario_sistema: str
    ) -> Incidente:
        """
        Reporta un nuevo incidente.
        Estado inicial: Reportado.
        """
        with self.db_manager.transaccion() as conn:
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
            return replace(incidente, id_incidente=id_new)

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
        """Lista incidentes delegando filtros al repositorio PostgreSQL.

        Args:
            busqueda: Texto de búsqueda (descripción o ID).
            id_propiedad: Filtro por propiedad.
            prioridad: Filtro por prioridad.
            estado: Filtro por estado (SQL nativo).
            fecha_desde: Fecha mínima ISO 8601.
            fecha_hasta: Fecha máxima ISO 8601.
            id_proveedor: Filtro por proveedor asignado.
            dias_min: Días mínimos sin resolver.
            page: Página (None = sin paginación).
            page_size: Tamaño de página (None = sin paginación).

        Returns:
            Dict con 'items' (List[Incidente]) y 'total' (int).
        """
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

    def obtener_datos_propietario_incidente(
        self, id_contrato_m: Optional[int], id_propiedad: int
    ) -> Optional[tuple[str, str]]:
        """Obtiene (nombre, telefono) del propietario."""
        query = """
            SELECT per.NOMBRE_COMPLETO, per.TELEFONO_PRINCIPAL
            FROM contratos_mandatos cm
            JOIN propietarios p ON cm.id_propietario = p.id_propietario
            JOIN personas per ON p.id_persona = per.id_persona
            WHERE cm.id_contrato_m = %s OR cm.id_propiedad = %s
            LIMIT 1
        """
        with self.db_manager.obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (id_contrato_m, id_propiedad))
            res = cursor.fetchone()
            if res:
                nombre = (
                    res[0] if isinstance(res, tuple) else res.get("NOMBRE_COMPLETO")
                )
                telefono = (
                    res[1] if isinstance(res, tuple) else res.get("TELEFONO_PRINCIPAL")
                )
                if nombre:
                    return (nombre, telefono or "")
        return None

    def obtener_datos_inquilino_incidente(
        self, id_propiedad: int
    ) -> Optional[tuple[str, str]]:
        """Obtiene (nombre, telefono) del inquilino."""
        query = """
            SELECT per.NOMBRE_COMPLETO, per.TELEFONO_PRINCIPAL
            FROM contratos_arrendamientos ca
            JOIN arrendatarios arr ON ca.id_arrendatario = arr.id_arrendatario
            JOIN personas per ON arr.id_persona = per.id_persona
            WHERE ca.id_propiedad = %s AND ca.estado_contrato_a = 'Activo'
            LIMIT 1
        """
        with self.db_manager.obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (id_propiedad,))
            res = cursor.fetchone()
            if res:
                nombre = (
                    res[0] if isinstance(res, tuple) else res.get("NOMBRE_COMPLETO")
                )
                telefono = (
                    res[1] if isinstance(res, tuple) else res.get("TELEFONO_PRINCIPAL")
                )
                if nombre:
                    return (nombre, telefono or "")
        return None

    def obtener_datos_habitante_incidente(
        self, id_propiedad: int
    ) -> Optional[tuple[str, str]]:
        """Obtiene (nombre, telefono) del habitante."""
        query = """
            SELECT arr.NOMBRE_HABITANTE, arr.TELEFONO_HABITANTE
            FROM contratos_arrendamientos ca
            JOIN arrendatarios arr ON ca.id_arrendatario = arr.id_arrendatario
            WHERE ca.id_propiedad = %s AND ca.estado_contrato_a = 'Activo'
              AND arr.NOMBRE_HABITANTE IS NOT NULL AND arr.NOMBRE_HABITANTE != ''
            LIMIT 1
        """
        with self.db_manager.obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (id_propiedad,))
            res = cursor.fetchone()
            if res:
                nombre = (
                    res[0] if isinstance(res, tuple) else res.get("NOMBRE_HABITANTE")
                )
                telefono = (
                    res[1] if isinstance(res, tuple) else res.get("TELEFONO_HABITANTE")
                )
                if nombre:
                    return (nombre, telefono or "")
        return None

    # M�todos legacy para compatibilidad
    def obtener_nombre_propietario_incidente(
        self, id_contrato_m: Optional[int], id_propiedad: int
    ) -> Optional[str]:
        datos = self.obtener_datos_propietario_incidente(id_contrato_m, id_propiedad)
        return datos[0] if datos else None

    def obtener_nombre_inquilino_incidente(self, id_propiedad: int) -> Optional[str]:
        datos = self.obtener_datos_inquilino_incidente(id_propiedad)
        return datos[0] if datos else None

    def obtener_nombre_habitante_incidente(self, id_propiedad: int) -> Optional[str]:
        datos = self.obtener_datos_habitante_incidente(id_propiedad)
        return datos[0] if datos else None

    def cambiar_estado(
        self,
        id_incidente: int,
        nuevo_estado: str,
        usuario_sistema: str,
        datos_extra: Optional[Dict[str, Any]] = None,
    ) -> Incidente:
        """
        Gestiona transiciones de estado.
        """
        with self.db_manager.transaccion() as conn:
            incidente = self.repo_incidentes.obtener_por_id(id_incidente)
            if not incidente:
                raise ValueError(f"Incidente {id_incidente} no encontrado")

            incidente = incidente.avanzar_estado(nuevo_estado, usuario_sistema)

            # Lógica específica por estado
            if nuevo_estado == "Aprobado" and datos_extra:
                cambios = {}
                # Si se aprueba manualmente sin cotización formal (ej: emergencia menor)
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

    def registrar_cotizacion(
        self, id_incidente: int, datos_cotizacion: Dict[str, Any], usuario_sistema: str
    ) -> Cotizacion:
        """
        Registra una cotización y pasa el incidente a 'Cotizado'.
        """
        with self.db_manager.transaccion() as conn:
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

            cotizacion = (
                cotizacion.con_total_calculado()
            )  # Suma materiales + mano de obra

            new_id = self.repo_incidentes.guardar_cotizacion(cotizacion)
            cotizacion = replace(cotizacion, id_cotizacion=new_id)

            # Actualizar estado incidente si estaba en Reportado o En Revision
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

        pass  # print("DEBUG SERVICIO: registrar_cotizacion COMPLETADO") [OpSec Removed]
        pass  # print("="*80 + "\n") [OpSec Removed]
        return cotizacion

    def iniciar_reparacion(self, id_incidente: int, usuario_sistema: str) -> None:
        """
        Inicia la reparación, cambiando el estado de Aprobado a En Reparacion.
        """
        with self.db_manager.transaccion() as conn:
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

    def aprobar_cotizacion(
        self,
        id_incidente: int,
        id_cotizacion: int,
        usuario_sistema: str,
        responsable_pago: str,
    ) -> None:
        """
        Aprueba una cotización, asigna el proveedor y costo, y pasa a 'Aprobado'.
        """
        with self.db_manager.transaccion() as conn:
            incidente = self.repo_incidentes.obtener_por_id(id_incidente)
            cotizaciones = self.repo_incidentes.obtener_cotizaciones(id_incidente)

            cotizacion_aprobada = next(
                (c for c in cotizaciones if c.id_cotizacion == id_cotizacion), None
            )
            if not cotizacion_aprobada:
                raise ValueError("Cotización no encontrada")

            # Actualizar todas las cotizaciones
            for c in cotizaciones:
                nuevo_est = (
                    "Aprobada" if c.id_cotizacion == id_cotizacion else "Rechazada"
                )
                c_update = replace(c, estado_cotizacion=nuevo_est)
                self.repo_incidentes.actualizar_cotizacion(c_update)

            # Actualizar Incidente
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

        # Crear Orden de Trabajo automáticamente (DISABLED PER USER REQUEST)
        # orden = OrdenTrabajo(
        #     id_incidente=id_incidente,
        #     id_proveedor=cotizacion_aprobada.id_proveedor,
        #     costo_mano_obra=cotizacion_aprobada.valor_mano_obra,
        #     costo_materiales=cotizacion_aprobada.valor_materiales,
        #     descripcion_trabajo=cotizacion_aprobada.descripcion_trabajo,
        #     # dias_estimados no está en OrdenTrabajo, calculamos fecha fin
        #     estado="Pendiente"
        # )
        # self.repo_ordenes.guardar(orden)

    def obtener_costos_reparaciones_periodo(
        self, id_contrato_m: int, mes_anio: str
    ) -> int:
        """
        Retorna la suma de costos de incidentes Aprobados/Finalizados en un mes dado,
        cuyo responsable de pago sea el Propietario.
        Útil para integración financiera.
        """
        # Esto requeriría un método en repositorio más específico.
        # Por ahora implementamos lógica en memoria o query raw si repo lo permite.
        # Simplificación: Listar todos y filtrar.
        # TODO: Optimizar con query SQL específica.
        incidentes = self.repo_incidentes.listar()  # Ojo: performance. Mejorar repo.

        total = 0
        for inc in incidentes:
            if (
                inc.id_contrato_m == id_contrato_m
                and inc.responsable_pago == "Propietario"
            ):
                # Verificar fecha. Usamos fecha_arreglo o fecha_incidente?
                # Usualmente fecha_arreglo o fecha de aprobación determina cuando se cobra.
                # Usaremos updated_at como proxy de aprobación/finalización si fecha_arreglo es nula.
                fecha_ref = inc.fecha_arreglo or inc.updated_at
                if fecha_ref:
                    if isinstance(fecha_ref, str):
                        fecha_ref = datetime.fromisoformat(fecha_ref)
                    if fecha_ref.strftime("%Y-%m") == mes_anio:
                        total += inc.costo_incidente
        return total

    # ==================== NUEVOS MÉTODOS FASE 6.5 ====================

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
        """
        Método interno para registrar cambios en el historial del incidente.
        """
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

        # Inyección a tabla Global de Auditoría (FASE 3)
        query_audit = """
            INSERT INTO AUDITORIA_CAMBIOS 
            (TABLA, ID_REGISTRO, TIPO_OPERACION, VALOR_ANTERIOR, VALOR_NUEVO, USUARIO, MOTIVO_CAMBIO)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        params_audit = (
            "incidentes",
            id_incidente,
            "ESTADO_CHANGE" if estado_anterior != estado_nuevo else "UPDATE",
            estado_anterior,
            estado_nuevo,
            usuario,
            f"Acción: {tipo_accion} | Comentario: {comentario or 'N/A'}",
        )
        with self.db_manager.obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute(query_audit, params_audit)

    def rechazar_cotizacion(
        self,
        id_incidente: int,
        id_cotizacion: int,
        usuario_sistema: str,
        motivo: str = None,
    ) -> None:
        """
        Rechaza una cotización específica sin afectar el estado del incidente.
        Permite solicitar nuevas cotizaciones.
        """
        with self.db_manager.transaccion() as conn:
            # Obtener incidente para saber su estado actual
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

            # Actualizar estado de la cotización
            cotizacion = replace(cotizacion, estado_cotizacion="Rechazada")
            self.repo_incidentes.actualizar_cotizacion(cotizacion)

            # Registrar en historial (estado del incidente no cambia)
            self._registrar_historial(
                id_incidente=id_incidente,
                estado_anterior=incidente.estado,
                estado_nuevo=incidente.estado,  # No hay cambio de estado
                usuario=usuario_sistema,
                tipo_accion="COTIZACION_RECHAZADA",
                comentario=motivo,
                datos_extra={
                    "id_cotizacion": id_cotizacion,
                    "id_proveedor": cotizacion.id_proveedor,
                    "valor_total": cotizacion.valor_total,
                },
            )

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
        """
        Finaliza un incidente desde cualquier estado editable.

        Args:
            id_incidente: ID del incidente
            usuario_sistema: Usuario que realiza la acción
            costo_final: Costo real de la reparación (opcional)
            comentario: Observaciones de cierre
            fecha_arreglo: Fecha de reparación
            es_finalizacion_directa: Si True, indica finalización fuera del flujo normal
            id_proveedor: ID del proveedor asignado (opcional)

        Estados desde los que se puede finalizar:
            Reportado, En Revision, Cotizado, Aprobado, En Reparacion
        """
        estados_finalizables = [
            "Reportado",
            "En Revision",
            "Cotizado",
            "Aprobado",
            "En Reparacion",
        ]

        with self.db_manager.transaccion() as conn:
            incidente = self.repo_incidentes.obtener_por_id(id_incidente)
            if not incidente:
                raise ValueError(f"Incidente {id_incidente} no encontrado")

            if incidente.estado not in estados_finalizables:
                raise ValueError(
                    f"No se puede finalizar un incidente en estado {incidente.estado}. "
                    f"Estados permitidos: {', '.join(estados_finalizables)}"
                )

            estado_anterior = incidente.estado
            costo_anterior = incidente.costo_incidente

            # Actualizar costo si se proporciona uno diferente
            if costo_final is not None and costo_final != incidente.costo_incidente:
                incidente = replace(incidente, costo_incidente=costo_final)

            # Asignar proveedor si se proporciona (antes de cambiar estado)
            if id_proveedor:
                incidente = replace(incidente, id_proveedor_asignado=id_proveedor)

            # Cambiar estado
            incidente = incidente.avanzar_estado("Finalizado", usuario_sistema)

            # Establecer fecha de arreglo (usar la provista o now)
            if fecha_arreglo:
                incidente = replace(incidente, fecha_arreglo=fecha_arreglo)

            self.repo_incidentes.actualizar(incidente)

            # Determinar tipo de acción
            tipo_accion = (
                "FINALIZACION_DIRECTA" if es_finalizacion_directa else "CAMBIO_ESTADO"
            )

            # Registrar en historial
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

    def cancelar_incidente(
        self, id_incidente: int, usuario_sistema: str, motivo: str
    ) -> Incidente:
        """
        Cancela un incidente. Requiere un motivo obligatorio.
        Solo se puede cancelar si no está Finalizado o ya Cancelado.
        """
        if not motivo or not motivo.strip():
            raise ValueError("Se requiere un motivo para cancelar el incidente")

        with self.db_manager.transaccion() as conn:
            incidente = self.repo_incidentes.obtener_por_id(id_incidente)
            if not incidente:
                raise ValueError(f"Incidente {id_incidente} no encontrado")

            if incidente.estado in ["Finalizado", "Cancelado"]:
                raise ValueError(
                    f"No se puede cancelar un incidente {incidente.estado}"
                )

            estado_anterior = incidente.estado

            # Cambiar estado
            incidente = replace(
                incidente,
                estado="Cancelado",
                motivo_cancelacion=motivo,
                updated_by=usuario_sistema,
                updated_at=datetime.now(),
            )

            self.repo_incidentes.actualizar(incidente)

            # Registrar en historial
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
        """
        Obtiene el historial completo de cambios de un incidente.
        """
        return self.repo_incidentes.obtener_historial(id_incidente)

    def obtener_cotizaciones_rechazadas(self, id_incidente: int) -> List[Cotizacion]:
        """
        Obtiene solo las cotizaciones rechazadas de un incidente.
        """
        cotizaciones = self.repo_incidentes.obtener_cotizaciones(id_incidente)
        return [c for c in cotizaciones if c.estado_cotizacion == "Rechazada"]

    def editar_incidente(
        self,
        id_incidente: int,
        datos_actualizacion: Dict[str, Any],
        usuario_sistema: str,
    ) -> Incidente:
        """
        Edita los atributos de un incidente sin cambiar de estado.

        Campos editables por estado:
        - Reportado: cualquier campo
        - En Revision: cualquier campo
        - Cotizado: descripcion, prioridad, responsable_pago, costo
        - Aprobado: costo, responsable_pago, comentarios
        - En Reparacion: costo_final, comentarios
        - Finalizado: solo lectura (no editable)

        Args:
            id_incidente: ID del incidente a editar
            datos_actualizacion: Dict con campos a actualizar
            usuario_sistema: Usuario que realiza la edición

        Returns:
            Incidente actualizado

        Raises:
            ValueError: Si el incidente no existe o no es editable en el estado actual
        """
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
            "Finalizado": ["*"],  # Todos bloqueados
            "Cancelado": ["*"],  # Todos bloqueados
        }

        with self.db_manager.transaccion() as conn:
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
