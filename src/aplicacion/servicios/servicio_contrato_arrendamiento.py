from datetime import datetime
import logging
from typing import Any, Dict, List, Optional

from src.dominio.entidades.contrato_arrendamiento import ContratoArrendamiento
from src.dominio.constantes.estados_contrato import EstadoContrato
from src.dominio.entidades.renovacion_contrato import RenovacionContrato
from src.dominio.servicios.calculadora_contratos import CalculadoraContratos
from src.dominio.repositorios.interfaces import (
    RepositorioContratoArrendamiento,
    RepositorioContratoMandato,
    RepositorioIPC,
    RepositorioPropiedad,
    RepositorioRenovacion,
)
from src.dominio.interfaces.repositorio_idempotencia import IRepositorioIdempotencia
from src.aplicacion.decorators.idempotent import idempotent
from src.infraestructura.cache.cache_manager import cache_manager
from src.dominio.constantes.cache_keys import CacheKeys


class ServicioContratoArrendamiento:
    """
    Servicio especializado en la gestión de contratos de Arrendamiento (Inquilinos).
    Sigue el Principio de Responsabilidad Única (SRP) y Clean Architecture.
    """

    def __init__(
        self,
        repo_arriendo: RepositorioContratoArrendamiento,
        repo_propiedad: RepositorioPropiedad,
        repo_renovacion: RepositorioRenovacion,
        repo_ipc: RepositorioIPC,
        repo_mandato: RepositorioContratoMandato,
        repo_idempotencia: Optional[IRepositorioIdempotencia] = None,
    ):
        self.repo_arriendo = repo_arriendo
        self.repo_propiedad = repo_propiedad
        self.repo_renovacion = repo_renovacion
        self.repo_ipc = repo_ipc
        self.repo_mandato = repo_mandato
        self.repo_idempotencia = repo_idempotencia

    # =========================================================================
    # HELPERS UI / DROPDOWNS
    # =========================================================================

    def obtener_propiedades_para_arrendamiento(self) -> List[Dict[str, Any]]:
        """Retorna propiedades elegibles para nuevos arrendamientos."""
        rows = self.repo_propiedad.listar_para_arrendamiento()
        return [
            {
                "id": row["ID_PROPIEDAD"],
                "texto": f"{row['MATRICULA_INMOBILIARIA']} - {row['DIRECCION_PROPIEDAD']}",
                "canon": row["CANON_ARRENDAMIENTO_ESTIMADO"],
            }
            for row in rows
        ]

    @idempotent(key_prefix="arriendo:crear")
    @cache_manager.invalidates(CacheKeys.ARRIENDOS_LIST)
    @cache_manager.invalidates("dashboard")
    def crear_arrendamiento(
        self, datos: Dict, usuario_sistema: str
    ) -> ContratoArrendamiento:
        """Crea un nuevo contrato de arrendamiento con validaciones. Uso de transacción atómica."""
        db = getattr(self.repo_arriendo, "db", None)

        if db is None:
            return self._ejecutar_creacion_arrendamiento(datos, usuario_sistema)

        with db.transaccion():
            return self._ejecutar_creacion_arrendamiento(datos, usuario_sistema)

    def _ejecutar_creacion_arrendamiento(
        self, datos: Dict, usuario_sistema: str
    ) -> ContratoArrendamiento:
        id_propiedad = datos["id_propiedad"]

        # 0. Validar Coherencia de Fechas y Duración
        fecha_inicio = datos["fecha_inicio"]
        fecha_fin = datos["fecha_fin"]
        duracion_reg = int(datos.get("duracion_meses") or 0)

        coherente, mensaje = CalculadoraContratos.validar_coherencia(
            fecha_inicio, fecha_fin, duracion_reg
        )
        if not coherente:
            raise ValueError(f"Error de Integridad Contractual: {mensaje}")

        # Validar si ya existe arriendo activo
        existente = self.repo_arriendo.obtener_activo_por_propiedad(id_propiedad)
        if existente:
            raise ValueError(
                f"La propiedad ya tiene un contrato de arrendamiento activo (ID: {existente.id_contrato_a})"
            )

        # Calcular Día de Pago (El mismo día de inicio para arrendamientos)
        dia_pago = CalculadoraContratos.calcular_dia_pago_arrendamiento(
            datos["fecha_inicio"]
        )
        fecha_pago_str = str(dia_pago)

        # En arrendamientos, el grupo operativo ya no obedece a las reglas de mandato.
        # Se establece en 0 o se deriva un grupo lógico simple según el día de pago.
        grupo = 1 if dia_pago <= 10 else (2 if dia_pago <= 20 else 3)

        contrato = ContratoArrendamiento(
            id_propiedad=datos["id_propiedad"],
            id_arrendatario=datos["id_arrendatario"],
            id_codeudor=datos.get("id_codeudor"),
            fecha_inicio_contrato_a=datos["fecha_inicio"],
            fecha_fin_contrato_a=datos["fecha_fin"],
            duracion_contrato_a=datos["duracion_meses"],
            canon_arrendamiento=datos["canon"],
            deposito=datos.get("deposito", 0),
            fecha_pago=fecha_pago_str,
            grupo_operativo=grupo,
            enlace_video=datos.get("enlace_video"),
            estado_contrato_a=EstadoContrato.ACTIVO,
            alerta_vencimiento_contrato_a=True,
            alerta_ipc=True,
            responsable_deposito_id=datos.get("responsable_deposito_id") and int(datos.get("responsable_deposito_id")),
        )

        contrato_creado = self.repo_arriendo.crear(contrato, usuario_sistema)

        # Marcar la propiedad como OCUPADA usando el método unificado
        self._sincronizar_disponibilidad_por_estado(
            contrato_creado,
            EstadoContrato.BORRADOR,
            EstadoContrato.ACTIVO,
            usuario_sistema,
        )

        return contrato_creado

    def obtener_arrendamiento(
        self, id_contrato: int
    ) -> Optional[ContratoArrendamiento]:
        return self.repo_arriendo.obtener_por_id(id_contrato)

    @cache_manager.invalidates(CacheKeys.ARRIENDOS_LIST)
    @cache_manager.invalidates("dashboard")
    def actualizar_arrendamiento(
        self, id_contrato: int, datos: Dict, usuario_sistema: str
    ) -> None:
        """
        Actualiza un contrato de arrendamiento y sincroniza en cascada con Propiedad y Mandato.
        Utiliza blindaje transaccional atómico.
        """
        # Obtenemos el db_manager desde el repositorio para el bloque transaccional
        db = getattr(self.repo_arriendo, "db", None)

        # Si no hay db_manager (caso raro o mocks), ejecutamos sin transacción explícita
        if db is None:
            self._ejecutar_actualizacion_arrendamiento(
                id_contrato, datos, usuario_sistema
            )
            return

        with db.transaccion():
            self._ejecutar_actualizacion_arrendamiento(
                id_contrato, datos, usuario_sistema
            )

    def _ejecutar_actualizacion_arrendamiento(
        self, id_contrato: int, datos: Dict, usuario_sistema: str
    ) -> None:
        arriendo = self.repo_arriendo.obtener_por_id(id_contrato)
        if not arriendo:
            raise ValueError(
                f"No existe el contrato de arrendamiento con ID {id_contrato}"
            )

        # 0. Validar Coherencia si se están modificando fechas o duración
        if "fecha_inicio" in datos or "fecha_fin" in datos or "duracion_meses" in datos:
            f_inicio = datos.get("fecha_inicio", arriendo.fecha_inicio_contrato_a)
            f_fin = datos.get("fecha_fin", arriendo.fecha_fin_contrato_a)
            d_reg = int(datos.get("duracion_meses", arriendo.duracion_contrato_a))

            coherente, mensaje = CalculadoraContratos.validar_coherencia(
                f_inicio, f_fin, d_reg
            )
            if not coherente:
                raise ValueError(f"Error de Integridad Contractual: {mensaje}")

        # Guardar valores anteriores para detectar cambios que requieren cascada
        canon_anterior = int(arriendo.canon_arrendamiento or 0)
        fecha_inicio_anterior = arriendo.fecha_inicio_contrato_a
        fecha_fin_anterior = arriendo.fecha_fin_contrato_a
        estado_anterior = arriendo.estado_contrato_a

        # Actualización de llaves foráneas y datos básicos
        arriendo.id_propiedad = datos.get("id_propiedad", arriendo.id_propiedad)
        arriendo.id_arrendatario = datos.get(
            "id_arrendatario", arriendo.id_arrendatario
        )
        arriendo.id_codeudor = datos.get("id_codeudor", arriendo.id_codeudor)

        # Actualización de fechas y duración
        if "fecha_inicio" in datos:
            arriendo.fecha_inicio_contrato_a = datos["fecha_inicio"]
            # Recalcular Ciclo de Pago para Arrendamiento (mismo día de inicio)
            dia_pago = CalculadoraContratos.calcular_dia_pago_arrendamiento(
                datos["fecha_inicio"]
            )
            arriendo.fecha_pago = str(dia_pago)
            # Para mantener coherencia en la DB, calculamos el grupo operativo
            grupo, _ = CalculadoraContratos.calcular_ciclo_pago_mandato(
                datos["fecha_inicio"]
            )
            if hasattr(arriendo, "grupo_operativo"):
                arriendo.grupo_operativo = grupo

        arriendo.fecha_fin_contrato_a = datos.get(
            "fecha_fin", arriendo.fecha_fin_contrato_a
        )
        arriendo.duracion_contrato_a = datos.get(
            "duracion_meses", arriendo.duracion_contrato_a
        )

        # Condiciones económicas
        if "canon" in datos:
            arriendo.canon_arrendamiento = int(datos["canon"])

        arriendo.deposito = datos.get("deposito", arriendo.deposito)
        
        if "enlace_video" in datos:
            arriendo.enlace_video = datos["enlace_video"]
            
        if "responsable_deposito_id" in datos:
            arriendo.responsable_deposito_id = (
                int(datos["responsable_deposito_id"]) if datos["responsable_deposito_id"] else None
            )

        # Solo actualizar fecha_pago si no fue recalculada por un cambio en fecha_inicio
        if "fecha_inicio" not in datos:
            arriendo.fecha_pago = datos.get("fecha_pago", arriendo.fecha_pago)

        # Estado y Alertas
        arriendo.estado_contrato_a = datos.get("estado", arriendo.estado_contrato_a)
        arriendo.alerta_vencimiento_contrato_a = datos.get(
            "alerta_vencimiento", arriendo.alerta_vencimiento_contrato_a
        )
        arriendo.alerta_ipc = datos.get("alerta_ipc", arriendo.alerta_ipc)

        arriendo.updated_by = usuario_sistema
        arriendo.updated_at = datetime.now().isoformat()

        # 1. Actualizar el Arrendamiento
        self.repo_arriendo.actualizar(arriendo, usuario_sistema)

        # 1.1 Sincronizar disponibilidad si hubo cambio de estado
        estado_nuevo = arriendo.estado_contrato_a
        if estado_anterior != estado_nuevo:
            self._sincronizar_disponibilidad_por_estado(
                arriendo, estado_anterior, estado_nuevo, usuario_sistema
            )

        # 2. Sincronización en Cascada (Integridad Contractual Élite)
        logger = logging.getLogger(__name__)
        nuevo_canon = int(arriendo.canon_arrendamiento or 0)

        # Sincronización Consolidada y Atómica en Cascada
        cambio_canon = nuevo_canon != canon_anterior
        cambio_fechas = (
            arriendo.fecha_inicio_contrato_a != fecha_inicio_anterior
            or arriendo.fecha_fin_contrato_a != fecha_fin_anterior
        )

        if cambio_canon or cambio_fechas:
            logger.info(
                f"Iniciando cascada de sincronización para contrato={id_contrato}. "
                f"Cambios -> Canon: {cambio_canon}, Fechas: {cambio_fechas}"
            )

            # Sincronizar Mandato en un solo fetch/update
            if self.repo_mandato is None:
                logger.error("CASCADA MANDATO ABORTADA: repo_mandato es None")
            else:
                mandato = self.repo_mandato.obtener_activo_por_propiedad(
                    arriendo.id_propiedad
                )
                if mandato:
                    if cambio_canon:
                        mandato.canon_mandato = nuevo_canon
                    if cambio_fechas:
                        mandato.fecha_inicio_contrato_m = (
                            arriendo.fecha_inicio_contrato_a
                        )
                        mandato.fecha_fin_contrato_m = arriendo.fecha_fin_contrato_a
                        dia_pago = CalculadoraContratos.calcular_dia_pago_mandato(
                            mandato.fecha_inicio_contrato_m
                        )
                        mandato.fecha_pago = str(dia_pago)
                        grupo_op = CalculadoraContratos.calcular_ciclo_pago_mandato(
                            mandato.fecha_inicio_contrato_m
                        )
                        mandato.grupo_operativo = grupo_op[0]

                    self.repo_mandato.actualizar(mandato, usuario_sistema)
                    logger.info(
                        f"Mandato {mandato.id_contrato_m} sincronizado exitosamente"
                    )
                else:
                    logger.info(
                        f"No existe mandato activo para la propiedad {arriendo.id_propiedad}"
                    )

            # Sincronizar Propiedad
            if cambio_canon:
                if self.repo_propiedad is None:
                    logger.error("CASCADA PROPIEDAD ABORTADA: repo_propiedad es None")
                else:
                    propiedad = self.repo_propiedad.obtener_por_id(
                        arriendo.id_propiedad
                    )
                    if propiedad:
                        propiedad.canon_arrendamiento_estimado = nuevo_canon
                        self.repo_propiedad.actualizar(propiedad, usuario_sistema)
                        self._invalidar_cache_propiedad(arriendo.id_propiedad)
                        logger.info(
                            f"Propiedad {arriendo.id_propiedad} sincronizada: canon_estimado={nuevo_canon}"
                        )
                    else:
                        logger.warning(
                            f"Propiedad {arriendo.id_propiedad} no encontrada para cascada"
                        )
            
            # Sincronizar Liquidaciones Futuras (Propagación Canon)
            if cambio_canon:
                fecha_renov = arriendo.fecha_renovacion_contrato_a or datetime.now().date().isoformat()
                filas_liq = self.actualizar_canon_liquidaciones_futuras(
                    arriendo.id_contrato_a, nuevo_canon, fecha_renov, usuario_sistema
                )
                logger.info(f"Liquidaciones futuras sincronizadas: {filas_liq} actualizadas")
                
            # Sincronizar Recaudos Futuros (Propagación Canon)
            if cambio_canon:
                fecha_renov = arriendo.fecha_renovacion_contrato_a or datetime.now().date().isoformat()
                filas_rec = self.actualizar_valor_recaudos_futuros(
                    arriendo.id_contrato_a, nuevo_canon, fecha_renov, usuario_sistema
                )
                logger.info(f"Recaudos futuros sincronizados: {filas_rec} actualizados")

    def listar_arrendamientos_paginado(self, **kwargs):
        return self.repo_arriendo.listar_paginado(**kwargs)

    def calcular_proyeccion_renovacion(self, id_contrato: int) -> dict:
        """
        Calcula la proyección de renovación SIN guardar nada en la BD.
        Retorna un dict con las fechas y canon proyectados para mostrar en UI.
        """
        arriendo = self.repo_arriendo.obtener_por_id(id_contrato)
        if not arriendo or arriendo.estado_contrato_a != EstadoContrato.ACTIVO:
            raise ValueError("Contrato no válido para proyección de renovación")

        fecha_fin_actual = datetime.strptime(arriendo.fecha_fin_contrato_a, "%Y-%m-%d")
        meses_duracion = arriendo.duracion_contrato_a

        # Calcular nueva fecha fin usando CalculadoraContratos
        nueva_fecha_fin_dt = CalculadoraContratos.sumar_meses(
            fecha_fin_actual, meses_duracion
        )
        nueva_fecha_fin_str = nueva_fecha_fin_dt.strftime("%Y-%m-%d")

        # Calcular IPC si aplica
        aplica_ipc = meses_duracion >= 12
        canon_nuevo = arriendo.canon_arrendamiento
        porcentaje_ipc = 0.0

        if aplica_ipc:
            ipc = self.repo_ipc.obtener_ultimo()
            if ipc:
                porcentaje_ipc = float(ipc.valor_ipc)
                incremento = arriendo.canon_arrendamiento * (porcentaje_ipc / 100)
                canon_nuevo = int(arriendo.canon_arrendamiento + incremento)

        return {
            "tipo": "Arrendamiento",
            "fecha_fin_actual": arriendo.fecha_fin_contrato_a,
            "nueva_fecha_fin": nueva_fecha_fin_str,
            "duracion_meses": meses_duracion,
            "canon_actual": arriendo.canon_arrendamiento,
            "canon_nuevo": canon_nuevo,
            "porcentaje_ipc": porcentaje_ipc,
            "aplica_ipc": aplica_ipc,
        }

    @idempotent(key_prefix="arriendo:renovar")
    @cache_manager.invalidates(CacheKeys.ARRIENDOS_LIST)
    @cache_manager.invalidates("dashboard")
    def renovar_arrendamiento(
        self, id_contrato: int, usuario_sistema: str, nueva_fecha_fin: str = None
    ) -> ContratoArrendamiento:
        """Lógica de renovación automática con incremento IPC. Acepta fecha fin personalizada."""
        db = getattr(self.repo_arriendo, "db", None)

        if db is None:
            return self._ejecutar_renovacion_arrendamiento(
                id_contrato, usuario_sistema, nueva_fecha_fin
            )

        with db.transaccion():
            return self._ejecutar_renovacion_arrendamiento(
                id_contrato, usuario_sistema, nueva_fecha_fin
            )

    def _ejecutar_renovacion_arrendamiento(
        self, id_contrato: int, usuario_sistema: str, nueva_fecha_fin: str = None
    ) -> ContratoArrendamiento:
        arriendo = self.repo_arriendo.obtener_por_id(id_contrato)
        if not arriendo or arriendo.estado_contrato_a != EstadoContrato.ACTIVO:
            raise ValueError("Contrato no válido para renovación")

        # 1. Calcular nuevas fechas
        fecha_fin_actual = datetime.strptime(arriendo.fecha_fin_contrato_a, "%Y-%m-%d")
        meses_duracion = arriendo.duracion_contrato_a

        # Calcular nueva fecha fin automática usando CalculadoraContratos
        nueva_fecha_fin_dt = CalculadoraContratos.sumar_meses(
            fecha_fin_actual, meses_duracion
        )
        nueva_fecha_fin_str = nueva_fecha_fin_dt.strftime("%Y-%m-%d")

        # Si el usuario proveyó una fecha personalizada, usarla en lugar de la calculada
        if nueva_fecha_fin:
            nueva_fecha_fin_str = nueva_fecha_fin

        # 2. Calcular incremento IPC si aplica (duración >= 12 meses)
        nuevo_canon = arriendo.canon_arrendamiento
        porcentaje_ipc = 0.0
        motivo_ren = "Prórroga Automática - Sin IPC (< 1 año)"

        if meses_duracion >= 12:
            nuevo_canon, porcentaje_ipc = self._calcular_incremento_ipc(
                arriendo.canon_arrendamiento
            )
            motivo_ren = f"Prórroga Automática - Renovación IPC ({porcentaje_ipc}%)"

        # 3. Registrar Renovación
        renovacion = RenovacionContrato(
            id_contrato_a=arriendo.id_contrato_a,
            tipo_contrato="Arrendamiento",
            fecha_inicio_original=arriendo.fecha_inicio_contrato_a,
            fecha_fin_original=arriendo.fecha_fin_contrato_a,
            fecha_fin_renovacion=nueva_fecha_fin_str,
            canon_anterior=arriendo.canon_arrendamiento,
            canon_nuevo=nuevo_canon,
            porcentaje_incremento=int(porcentaje_ipc * 100),
            motivo_renovacion=motivo_ren,
            fecha_renovacion=datetime.now().date().isoformat(),
        )

        self.repo_renovacion.crear(renovacion, usuario_sistema)

        # 4. Actualizar contrato
        arriendo.fecha_fin_contrato_a = nueva_fecha_fin_str
        arriendo.canon_arrendamiento = nuevo_canon
        arriendo.fecha_renovacion_contrato_a = datetime.now().date().isoformat()

        self.repo_arriendo.actualizar(arriendo, usuario_sistema)

        # 5. Actualizar canon estimado en propiedad
        propiedad = self.repo_propiedad.obtener_por_id(arriendo.id_propiedad)
        if propiedad:
            propiedad.canon_arrendamiento_estimado = nuevo_canon
            self.repo_propiedad.actualizar(propiedad, usuario_sistema)
            self._invalidar_cache_propiedad(arriendo.id_propiedad)

        # 6. Sincronizar canon y fecha_fin en mandato activo asociado a la misma propiedad
        mandato = self.repo_mandato.obtener_activo_por_propiedad(arriendo.id_propiedad)
        if mandato:
            mandato.canon_mandato = nuevo_canon
            mandato.fecha_fin_contrato_m = (
                nueva_fecha_fin_str  # Sincronizar fecha fin en renovación
            )
            mandato.updated_by = usuario_sistema
            mandato.updated_at = datetime.now().isoformat()
            self.repo_mandato.actualizar(mandato, usuario_sistema)

        # 7. Sincronizar Liquidaciones Futuras (Propagación Canon)
        self.actualizar_canon_liquidaciones_futuras(
            arriendo.id_contrato_a, nuevo_canon, arriendo.fecha_renovacion_contrato_a, usuario_sistema
        )
        
        # 8. Sincronizar Recaudos Futuros (Propagación Canon)
        self.actualizar_valor_recaudos_futuros(
            arriendo.id_contrato_a, nuevo_canon, arriendo.fecha_renovacion_contrato_a, usuario_sistema
        )

        return arriendo

    def _calcular_incremento_ipc(self, canon_actual: int) -> tuple[int, float]:
        ipc = self.repo_ipc.obtener_ultimo()
        if not ipc:
            return canon_actual, 0.0

        porcentaje = float(ipc.valor_ipc)
        incremento = canon_actual * (porcentaje / 100)
        return int(canon_actual + incremento), porcentaje

    @idempotent(key_prefix="arriendo:terminar")
    @cache_manager.invalidates(CacheKeys.ARRIENDOS_LIST)
    @cache_manager.invalidates("dashboard")
    def terminar_arrendamiento(
        self,
        id_contrato: int,
        motivo: str,
        usuario_sistema: str,
        estado_destino: EstadoContrato = EstadoContrato.CANCELADO,
    ) -> None:
        db = getattr(self.repo_arriendo, "db", None)
        if db is None:
            self._ejecutar_terminacion_arrendamiento(
                id_contrato, motivo, usuario_sistema, estado_destino
            )
            return
        with db.transaccion():
            self._ejecutar_terminacion_arrendamiento(
                id_contrato, motivo, usuario_sistema, estado_destino
            )

    def _ejecutar_terminacion_arrendamiento(
        self,
        id_contrato: int,
        motivo: str,
        usuario_sistema: str,
        estado_destino: EstadoContrato,
    ) -> None:
        arriendo = self.repo_arriendo.obtener_por_id(id_contrato)
        if not arriendo:
            raise ValueError(f"Contrato {id_contrato} no existe")

        estado_anterior = arriendo.estado_contrato_a
        if estado_destino not in [EstadoContrato.FINALIZADO, EstadoContrato.CANCELADO]:
            raise ValueError(f"Estado de terminación inválido: {estado_destino}")

        arriendo.estado_contrato_a = estado_destino
        arriendo.motivo_cancelacion = motivo
        arriendo.fecha_fin_contrato_a = datetime.now().strftime("%Y-%m-%d")

        self.repo_arriendo.actualizar(arriendo, usuario_sistema)
        self._sincronizar_disponibilidad_por_estado(
            arriendo, estado_anterior, arriendo.estado_contrato_a, usuario_sistema
        )

    def _sincronizar_disponibilidad_por_estado(
        self,
        contrato: ContratoArrendamiento,
        estado_anterior: EstadoContrato,
        estado_nuevo: EstadoContrato,
        usuario: str,
    ) -> None:
        """
        Único punto de sincronización de disponibilidad.
        Detecta transiciones de estado y actualiza propiedad atómicamente.
        """
        ESTADOS_TERMINALES = {EstadoContrato.FINALIZADO, EstadoContrato.CANCELADO}

        # Transición: Activo → Terminal → Liberar propiedad
        if (
            estado_anterior == EstadoContrato.ACTIVO
            and estado_nuevo in ESTADOS_TERMINALES
        ):
            propiedad = self.repo_propiedad.obtener_por_id(contrato.id_propiedad)
            if propiedad and getattr(propiedad, "disponibilidad_propiedad", None) != 1:
                propiedad.disponibilidad_propiedad = 1  # DISPONIBLE
                self.repo_propiedad.actualizar(propiedad, usuario)
                self._invalidar_cache_propiedad(contrato.id_propiedad)

        # Transición: Terminal/Borrador → Activo → Ocupar propiedad (re-activación)
        elif (
            estado_anterior != EstadoContrato.ACTIVO
            and estado_nuevo == EstadoContrato.ACTIVO
        ):
            propiedad = self.repo_propiedad.obtener_por_id(contrato.id_propiedad)
            if propiedad and getattr(propiedad, "disponibilidad_propiedad", None) != 0:
                propiedad.disponibilidad_propiedad = 0  # OCUPADA
                self.repo_propiedad.actualizar(propiedad, usuario)
                self._invalidar_cache_propiedad(contrato.id_propiedad)

    def _invalidar_cache_propiedad(self, id_propiedad: int):
        """Invalida caché relacionada a propiedades"""
        cache_manager.invalidate(CacheKeys.PROPIEDADES_BASE_LIST)
        cache_manager.invalidate(CacheKeys.PROPIEDADES_LIST)
        cache_manager.invalidate(CacheKeys.propiedad(id_propiedad))
        cache_manager.invalidate(CacheKeys.DASHBOARD_PROPIEDADES_TIPO)

    def actualizar_canon_liquidaciones_futuras(self, id_contrato_a: int, canon_nuevo: int, fecha_renovacion: str, usuario: str) -> int:
        """Propaga el nuevo canon a liquidaciones generadas con fecha posterior a la renovación."""
        db = getattr(self.repo_arriendo, "db", None)
        if db is None:
            return 0
            
        conn = db.obtener_conexion()
        cursor = db.get_dict_cursor(conn)
        
        # 1. Obtener valores anteriores para auditoría
        query_sel = """
            SELECT id_liquidacion, canon_bruto 
            FROM LIQUIDACIONES 
            WHERE id_contrato_m = (
                SELECT m.id_contrato_m 
                FROM CONTRATOS_MANDATOS m
                JOIN CONTRATOS_ARRENDAMIENTOS a ON m.id_propiedad = a.id_propiedad
                WHERE a.id_contrato_a = %s LIMIT 1
            )
            AND fecha_generacion::date >= date_trunc('month', %s::date)
        """
        cursor.execute(query_sel, (id_contrato_a, fecha_renovacion))
        records = cursor.fetchall()
        
        if not records:
            return 0
            
        # 2. Actualizar registros futuros
        query_upd = """
            UPDATE LIQUIDACIONES
            SET canon_bruto = %s
            WHERE id_contrato_m = (
                SELECT m.id_contrato_m 
                FROM CONTRATOS_MANDATOS m
                JOIN CONTRATOS_ARRENDAMIENTOS a ON m.id_propiedad = a.id_propiedad
                WHERE a.id_contrato_a = %s LIMIT 1
            )
            AND fecha_generacion::date >= date_trunc('month', %s::date);
        """
        cursor.execute(query_upd, (canon_nuevo, id_contrato_a, fecha_renovacion))
        filas = cursor.rowcount
        
        # 3. Registrar auditoría (FR-009)
        audit_query = """
            INSERT INTO AUDITORIA_PROPAGACION_CANON (
                contrato_id, tabla_afectada, registro_id,
                canon_anterior, canon_nuevo, fecha_actualizacion, usuario_sistema
            ) VALUES (%s, %s, %s, %s, %s, %s, %s);
        """
        now_str = datetime.now().isoformat()
        for r in records:
            id_liq = r.get("ID_LIQUIDACION", r.get("id_liquidacion")) if isinstance(r, dict) else r[0]
            canon_ant = r.get("CANON_BRUTO", r.get("canon_bruto")) if isinstance(r, dict) else r[1]
            cursor.execute(audit_query, (id_contrato_a, "LIQUIDACIONES", str(id_liq), canon_ant, canon_nuevo, now_str, usuario))
            
        return filas

    def actualizar_valor_recaudos_futuros(self, id_contrato_a: int, canon_nuevo: int, fecha_renovacion: str, usuario: str) -> int:
        """Propaga el nuevo canon a recaudos con fecha de pago posterior a la renovación."""
        db = getattr(self.repo_arriendo, "db", None)
        if db is None:
            return 0
            
        conn = db.obtener_conexion()
        cursor = db.get_dict_cursor(conn)
        
        # 1. Obtener valores anteriores para auditoría
        query_sel = """
            SELECT id_recaudo, valor_total
            FROM RECAUDOS
            WHERE id_contrato_a = %s
            AND fecha_pago::date >= date_trunc('month', %s::date)
        """
        cursor.execute(query_sel, (id_contrato_a, fecha_renovacion))
        records = cursor.fetchall()
        
        if not records:
            return 0
            
        # 2. Actualizar registros futuros
        query_upd = """
            UPDATE RECAUDOS
            SET valor_total = %s
            WHERE id_contrato_a = %s
            AND fecha_pago::date >= date_trunc('month', %s::date);
        """
        cursor.execute(query_upd, (canon_nuevo, id_contrato_a, fecha_renovacion))
        filas = cursor.rowcount
        
        # 3. Registrar auditoría (FR-009)
        audit_query = """
            INSERT INTO AUDITORIA_PROPAGACION_CANON (
                contrato_id, tabla_afectada, registro_id,
                canon_anterior, canon_nuevo, fecha_actualizacion, usuario_sistema
            ) VALUES (%s, %s, %s, %s, %s, %s, %s);
        """
        now_str = datetime.now().isoformat()
        for r in records:
            id_rec = r.get("ID_RECAUDO", r.get("id_recaudo")) if isinstance(r, dict) else r[0]
            canon_ant = r.get("VALOR_TOTAL", r.get("valor_total")) if isinstance(r, dict) else r[1]
            cursor.execute(audit_query, (id_contrato_a, "RECAUDOS", str(id_rec), canon_ant, canon_nuevo, now_str, usuario))
            
        return filas

    def verificar_propagacion_canon(self, id_contrato_a: int, fecha_renovacion: str) -> dict:
        """
        Verifica la integridad de la propagación del canon en liquidaciones y recaudos futuros.
        Retorna un reporte con inconsistencias clasificadas por severidad.
        """
        db = getattr(self.repo_arriendo, "db", None)
        if db is None:
            return {"inconsistencias": []}
            
        conn = db.obtener_conexion()
        cursor = db.get_dict_cursor(conn)
        inconsistencias = []
        
        # 1. Verificar Liquidaciones
        query_liq = """
            SELECT
                l.id_liquidacion,
                l.canon_bruto,
                c.canon_arrendamiento,
                l.fecha_generacion
            FROM LIQUIDACIONES l
            JOIN CONTRATOS_MANDATOS cm ON l.id_contrato_m = cm.id_contrato_m
            JOIN CONTRATOS_ARRENDAMIENTOS c ON cm.id_propiedad = c.id_propiedad
            WHERE c.id_contrato_a = %s
            AND l.canon_bruto != c.canon_arrendamiento
            AND l.fecha_generacion::date >= date_trunc('month', %s::date);
        """
        cursor.execute(query_liq, (id_contrato_a, fecha_renovacion))
        for r in cursor.fetchall():
            id_liq = r.get("ID_LIQUIDACION", r.get("id_liquidacion")) if isinstance(r, dict) else r[0]
            canon_liq = r.get("CANON_BRUTO", r.get("canon_bruto")) if isinstance(r, dict) else r[1]
            canon_arr = r.get("CANON_ARRENDAMIENTO", r.get("canon_arrendamiento")) if isinstance(r, dict) else r[2]
            fecha_gen = r.get("FECHA_GENERACION", r.get("fecha_generacion")) if isinstance(r, dict) else r[3]
            
            inconsistencias.append({
                "tipo": "LIQUIDACION",
                "id_registro": id_liq,
                "valor_actual": canon_liq,
                "valor_esperado": canon_arr,
                "fecha": fecha_gen,
                "severidad": "ALTA" if abs(canon_liq - canon_arr) > 10000 else "MEDIA"
            })
            
        # 2. Verificar Recaudos
        query_rec = """
            SELECT
                r.id_recaudo,
                r.valor_total,
                c.canon_arrendamiento,
                r.fecha_pago
            FROM RECAUDOS r
            JOIN CONTRATOS_ARRENDAMIENTOS c ON r.id_contrato_a = c.id_contrato_a
            WHERE c.id_contrato_a = %s
            AND r.valor_total != c.canon_arrendamiento
            AND r.fecha_pago::date >= date_trunc('month', %s::date);
        """
        cursor.execute(query_rec, (id_contrato_a, fecha_renovacion))
        for r in cursor.fetchall():
            id_rec = r.get("ID_RECAUDO", r.get("id_recaudo")) if isinstance(r, dict) else r[0]
            valor_rec = r.get("VALOR_TOTAL", r.get("valor_total")) if isinstance(r, dict) else r[1]
            canon_arr = r.get("CANON_ARRENDAMIENTO", r.get("canon_arrendamiento")) if isinstance(r, dict) else r[2]
            fecha_pago = r.get("FECHA_PAGO", r.get("fecha_pago")) if isinstance(r, dict) else r[3]
            
            inconsistencias.append({
                "tipo": "RECAUDO",
                "id_registro": id_rec,
                "valor_actual": valor_rec,
                "valor_esperado": canon_arr,
                "fecha": fecha_pago,
                "severidad": "ALTA" if abs(valor_rec - canon_arr) > 10000 else "MEDIA"
            })
            
        return {
            "id_contrato": id_contrato_a,
            "total_inconsistencias": len(inconsistencias),
            "inconsistencias": inconsistencias
        }

    def corregir_propagacion_canon(self, id_contrato_a: int, usuario: str) -> dict:
        """
        Corrige inconsistencias detectadas en la propagación del canon.
        Utiliza el último canon de arrendamiento y la fecha de renovación.
        """
        db = getattr(self.repo_arriendo, "db", None)
        if db is None:
            return {"corregidos": 0}
            
        arriendo = self.repo_arriendo.obtener_por_id(id_contrato_a)
        if not arriendo:
            raise ValueError(f"Contrato {id_contrato_a} no encontrado")
            
        canon_esperado = int(arriendo.canon_arrendamiento or 0)
        fecha_renovacion = arriendo.fecha_renovacion_contrato_a
        if not fecha_renovacion:
            fecha_renovacion = arriendo.fecha_inicio_contrato_a # Fallback si nunca fue renovado
            
        # Utilizamos verificar_propagacion_canon para identificar inconsistencias
        reporte = self.verificar_propagacion_canon(id_contrato_a, fecha_renovacion)
        
        if reporte["total_inconsistencias"] == 0:
            return {"corregidos": 0, "detalles": []}
            
        conn = db.obtener_conexion()
        cursor = db.get_dict_cursor(conn)
        
        detalles_corregidos = []
        
        # Iniciar bloque transaccional manualmente o asumir que será llamado dentro de db.transaccion()
        with db.transaccion():
            for inc in reporte["inconsistencias"]:
                if inc["tipo"] == "LIQUIDACION":
                    query = "UPDATE LIQUIDACIONES SET canon_bruto = %s WHERE id_liquidacion = %s"
                    cursor.execute(query, (canon_esperado, inc["id_registro"]))
                    
                    audit_query = """
                        INSERT INTO AUDITORIA_PROPAGACION_CANON (
                            contrato_id, tabla_afectada, registro_id,
                            canon_anterior, canon_nuevo, fecha_actualizacion, usuario_sistema
                        ) VALUES (%s, %s, %s, %s, %s, NOW(), %s);
                    """
                    cursor.execute(audit_query, (
                        id_contrato_a, "LIQUIDACIONES", str(inc["id_registro"]), 
                        inc["valor_actual"], canon_esperado, usuario
                    ))
                    detalles_corregidos.append(f"Liquidación {inc['id_registro']} corregida de {inc['valor_actual']} a {canon_esperado}")
                    
                elif inc["tipo"] == "RECAUDO":
                    query = "UPDATE RECAUDOS SET valor_total = %s WHERE id_recaudo = %s"
                    cursor.execute(query, (canon_esperado, inc["id_registro"]))
                    
                    audit_query = """
                        INSERT INTO AUDITORIA_PROPAGACION_CANON (
                            contrato_id, tabla_afectada, registro_id,
                            canon_anterior, canon_nuevo, fecha_actualizacion, usuario_sistema
                        ) VALUES (%s, %s, %s, %s, %s, NOW(), %s);
                    """
                    cursor.execute(audit_query, (
                        id_contrato_a, "RECAUDOS", str(inc["id_registro"]), 
                        inc["valor_actual"], canon_esperado, usuario
                    ))
                    detalles_corregidos.append(f"Recaudo {inc['id_registro']} corregido de {inc['valor_actual']} a {canon_esperado}")
        
        return {
            "corregidos": len(detalles_corregidos),
            "detalles": detalles_corregidos
        }
