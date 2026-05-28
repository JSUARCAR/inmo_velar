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

        # Calcular Ciclo de Pago y Grupo Operativo
        dia_pago = CalculadoraContratos.calcular_dia_pago_arrendamiento(datos["fecha_inicio"])
        fecha_pago_str = str(dia_pago)
        grupo, _ = CalculadoraContratos.calcular_ciclo_pago_mandato(datos["fecha_inicio"])

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
            estado_contrato_a=EstadoContrato.ACTIVO,
            alerta_vencimiento_contrato_a=True,
            alerta_ipc=True,
        )

        contrato_creado = self.repo_arriendo.crear(contrato, usuario_sistema)

        # Marcar la propiedad como OCUPADA usando el método unificado
        self._sincronizar_disponibilidad_por_estado(contrato_creado, EstadoContrato.BORRADOR, EstadoContrato.ACTIVO, usuario_sistema)

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
            self._ejecutar_actualizacion_arrendamiento(id_contrato, datos, usuario_sistema)
            return

        with db.transaccion():
            self._ejecutar_actualizacion_arrendamiento(id_contrato, datos, usuario_sistema)

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

            coherente, mensaje = CalculadoraContratos.validar_coherencia(f_inicio, f_fin, d_reg)
            if not coherente:
                raise ValueError(f"Error de Integridad Contractual: {mensaje}")

        # Guardar valores anteriores para detectar cambios que requieren cascada
        canon_anterior = int(arriendo.canon_arrendamiento or 0)
        fecha_inicio_anterior = arriendo.fecha_inicio_contrato_a
        fecha_fin_anterior = arriendo.fecha_fin_contrato_a
        estado_anterior = arriendo.estado_contrato_a

        # Actualización de llaves foráneas y datos básicos
        arriendo.id_propiedad = datos.get("id_propiedad", arriendo.id_propiedad)
        arriendo.id_arrendatario = datos.get("id_arrendatario", arriendo.id_arrendatario)
        arriendo.id_codeudor = datos.get("id_codeudor", arriendo.id_codeudor)

        # Actualización de fechas y duración
        if "fecha_inicio" in datos:
            arriendo.fecha_inicio_contrato_a = datos["fecha_inicio"]
            # Recalcular Ciclo de Pago para Arrendamiento (mismo día de inicio)
            dia_pago = CalculadoraContratos.calcular_dia_pago_arrendamiento(datos["fecha_inicio"])
            arriendo.fecha_pago = str(dia_pago)
            # Para mantener coherencia en la DB, calculamos el grupo operativo
            grupo, _ = CalculadoraContratos.calcular_ciclo_pago_mandato(datos["fecha_inicio"])
            if hasattr(arriendo, 'grupo_operativo'):
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

        arriendo.deposito = int(datos.get("deposito", arriendo.deposito))

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
            self._sincronizar_disponibilidad_por_estado(arriendo, estado_anterior, estado_nuevo, usuario_sistema)

        # 2. Sincronización en Cascada (Integridad Contractual Élite)
        logger = logging.getLogger(__name__)
        nuevo_canon = int(arriendo.canon_arrendamiento or 0)

        # Sincronización Consolidada y Atómica en Cascada
        cambio_canon = nuevo_canon != canon_anterior
        cambio_fechas = (
            arriendo.fecha_inicio_contrato_a != fecha_inicio_anterior or 
            arriendo.fecha_fin_contrato_a != fecha_fin_anterior
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
                mandato = self.repo_mandato.obtener_activo_por_propiedad(arriendo.id_propiedad)
                if mandato:
                    if cambio_canon:
                        mandato.canon_mandato = nuevo_canon
                    if cambio_fechas:
                        mandato.fecha_inicio_contrato_m = arriendo.fecha_inicio_contrato_a
                        mandato.fecha_fin_contrato_m = arriendo.fecha_fin_contrato_a
                        dia_pago = CalculadoraContratos.calcular_dia_pago_mandato(mandato.fecha_inicio_contrato_m)
                        mandato.fecha_pago = str(dia_pago)
                        grupo_op = CalculadoraContratos.calcular_ciclo_pago_mandato(mandato.fecha_inicio_contrato_m)
                        mandato.grupo_operativo = grupo_op[0]
                    
                    self.repo_mandato.actualizar(mandato, usuario_sistema)
                    logger.info(f"Mandato {mandato.id_contrato_m} sincronizado exitosamente")
                else:
                    logger.info(f"No existe mandato activo para la propiedad {arriendo.id_propiedad}")

            # Sincronizar Propiedad
            if cambio_canon:
                if self.repo_propiedad is None:
                    logger.error("CASCADA PROPIEDAD ABORTADA: repo_propiedad es None")
                else:
                    propiedad = self.repo_propiedad.obtener_por_id(arriendo.id_propiedad)
                    if propiedad:
                        propiedad.canon_arrendamiento_estimado = nuevo_canon
                        self.repo_propiedad.actualizar(propiedad, usuario_sistema)
                        self._invalidar_cache_propiedad(arriendo.id_propiedad)
                        logger.info(f"Propiedad {arriendo.id_propiedad} sincronizada: canon_estimado={nuevo_canon}")
                    else:
                        logger.warning(f"Propiedad {arriendo.id_propiedad} no encontrada para cascada")

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
        nueva_fecha_fin_dt = CalculadoraContratos.sumar_meses(fecha_fin_actual, meses_duracion)
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
            return self._ejecutar_renovacion_arrendamiento(id_contrato, usuario_sistema, nueva_fecha_fin)
            
        with db.transaccion():
            return self._ejecutar_renovacion_arrendamiento(id_contrato, usuario_sistema, nueva_fecha_fin)

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
        nueva_fecha_fin_dt = CalculadoraContratos.sumar_meses(fecha_fin_actual, meses_duracion)
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
            mandato.fecha_fin_contrato_m = nueva_fecha_fin_str # Sincronizar fecha fin en renovación
            mandato.updated_by = usuario_sistema
            mandato.updated_at = datetime.now().isoformat()
            self.repo_mandato.actualizar(mandato, usuario_sistema)

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
        self, id_contrato: int, motivo: str, usuario_sistema: str, estado_destino: EstadoContrato = EstadoContrato.CANCELADO
    ) -> None:
        db = getattr(self.repo_arriendo, "db", None)
        if db is None:
            self._ejecutar_terminacion_arrendamiento(id_contrato, motivo, usuario_sistema, estado_destino)
            return
        with db.transaccion():
            self._ejecutar_terminacion_arrendamiento(id_contrato, motivo, usuario_sistema, estado_destino)

    def _ejecutar_terminacion_arrendamiento(
        self, id_contrato: int, motivo: str, usuario_sistema: str, estado_destino: EstadoContrato
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
        self._sincronizar_disponibilidad_por_estado(arriendo, estado_anterior, arriendo.estado_contrato_a, usuario_sistema)

    def _sincronizar_disponibilidad_por_estado(
        self,
        contrato: ContratoArrendamiento,
        estado_anterior: EstadoContrato,
        estado_nuevo: EstadoContrato,
        usuario: str
    ) -> None:
        """
        Único punto de sincronización de disponibilidad.
        Detecta transiciones de estado y actualiza propiedad atómicamente.
        """
        ESTADOS_TERMINALES = {EstadoContrato.FINALIZADO, EstadoContrato.CANCELADO}

        # Transición: Activo → Terminal → Liberar propiedad
        if estado_anterior == EstadoContrato.ACTIVO and estado_nuevo in ESTADOS_TERMINALES:
            propiedad = self.repo_propiedad.obtener_por_id(contrato.id_propiedad)
            if propiedad and getattr(propiedad, 'disponibilidad_propiedad', None) != 1:
                propiedad.disponibilidad_propiedad = 1  # DISPONIBLE
                self.repo_propiedad.actualizar(propiedad, usuario)
                self._invalidar_cache_propiedad(contrato.id_propiedad)

        # Transición: Terminal/Borrador → Activo → Ocupar propiedad (re-activación)
        elif estado_anterior != EstadoContrato.ACTIVO and estado_nuevo == EstadoContrato.ACTIVO:
            propiedad = self.repo_propiedad.obtener_por_id(contrato.id_propiedad)
            if propiedad and getattr(propiedad, 'disponibilidad_propiedad', None) != 0:
                propiedad.disponibilidad_propiedad = 0  # OCUPADA
                self.repo_propiedad.actualizar(propiedad, usuario)
                self._invalidar_cache_propiedad(contrato.id_propiedad)

    def _invalidar_cache_propiedad(self, id_propiedad: int):
        """Invalida caché relacionada a propiedades"""
        cache_manager.invalidate(CacheKeys.PROPIEDADES_BASE_LIST)
        cache_manager.invalidate(CacheKeys.PROPIEDADES_LIST)
        cache_manager.invalidate(CacheKeys.propiedad(id_propiedad))
        cache_manager.invalidate(CacheKeys.DASHBOARD_PROPIEDADES_TIPO)
