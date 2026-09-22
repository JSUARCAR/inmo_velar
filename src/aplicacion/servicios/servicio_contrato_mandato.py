from datetime import datetime
import logging
from typing import Any, Dict, List, Optional

from src.dominio.constantes.estados_contrato import EstadoContrato
from src.dominio.entidades.contrato_mandato import ContratoMandato
from src.dominio.entidades.renovacion_contrato import RenovacionContrato
from src.dominio.servicios.calculadora_contratos import CalculadoraContratos
from src.dominio.repositorios.interfaces import (
    RepositorioContratoMandato,
    RepositorioPropiedad,
    RepositorioRenovacion,
)
from src.dominio.interfaces.repositorio_idempotencia import IRepositorioIdempotencia
from src.aplicacion.decorators.idempotent import idempotent
from src.infraestructura.cache.cache_manager import cache_manager, invalidate_cache
from src.dominio.constantes.cache_keys import CacheKeys
from src.dominio.excepciones.excepciones_base import ContratoNoRenovableError
from src.aplicacion.utils.validadores import validar_canon

logger = logging.getLogger(__name__)


class ServicioContratoMandato:
    """
    Servicio especializado en la gestión de contratos de Mandato (Propietarios).
    Sigue el Principio de Responsabilidad Única (SRP).
    """

    def __init__(
        self,
        repo_mandato: RepositorioContratoMandato,
        repo_propiedad: RepositorioPropiedad,
        repo_renovacion: RepositorioRenovacion,
        repo_idempotencia: Optional[IRepositorioIdempotencia] = None,
    ):
        self.repo_mandato = repo_mandato
        self.repo_propiedad = repo_propiedad
        self.repo_renovacion = repo_renovacion
        self.repo_idempotencia = repo_idempotencia

    # =========================================================================
    # HELPERS UI / DROPDOWNS
    # =========================================================================

    def obtener_propiedades_sin_mandato_activo(self) -> List[Dict[str, Any]]:
        """Retorna propiedades elegibles para nuevos mandatos."""
        rows = self.repo_propiedad.listar_sin_mandato()
        return [
            {
                "id": row["ID_PROPIEDAD"],
                "texto": f"{row['MATRICULA_INMOBILIARIA']} - {row['DIRECCION_PROPIEDAD']}",
                "canon": row["CANON_ARRENDAMIENTO_ESTIMADO"],
            }
            for row in rows
        ]

    @cache_manager.invalidates(CacheKeys.MANDATOS_LIST)
    def crear_mandato(self, datos: Dict, usuario_sistema: str) -> ContratoMandato:
        """Crea un nuevo contrato de mandato con validaciones de negocio."""
        db = getattr(self.repo_mandato, "db", None)
        if db is None:
            return self._ejecutar_creacion_mandato(datos, usuario_sistema)

        with db.transaccion():
            return self._ejecutar_creacion_mandato(datos, usuario_sistema)

    def _ejecutar_creacion_mandato(
        self, datos: Dict, usuario_sistema: str
    ) -> ContratoMandato:
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

        # 1. Validar que no exista otro mandato activo
        existente = self.repo_mandato.obtener_activo_por_propiedad(id_propiedad)
        if existente:
            raise ValueError(
                f"La propiedad ya tiene un contrato de mandato activo (ID: {existente.id_contrato_m})"
            )

        # Calcular Ciclo de Pago y Grupo Operativo
        grupo, _ = CalculadoraContratos.calcular_ciclo_pago_mandato(
            datos["fecha_inicio"]
        )
        dia_pago = CalculadoraContratos.calcular_dia_pago_mandato(datos["fecha_inicio"])
        fecha_pago_str = str(dia_pago)

        # 2. Crear Entidad
        contrato = ContratoMandato(
            id_propiedad=datos["id_propiedad"],
            id_propietario=datos["id_propietario"],
            id_asesor=datos["id_asesor"],
            fecha_inicio_contrato_m=datos["fecha_inicio"],
            fecha_fin_contrato_m=datos["fecha_fin"],
            duracion_contrato_m=datos["duracion_meses"],
            canon_mandato=datos["canon"],
            comision_porcentaje_contrato_m=datos["comision_porcentaje"],
            iva_contrato_m=datos.get("iva_porcentaje", 1900),
            estado_contrato_m=EstadoContrato.ACTIVO,
            alerta_vencimiento_contrato_m=True,
            fecha_pago=fecha_pago_str,
            grupo_operativo=grupo,
            # Campos bancarios migrados
            banco_propietario=datos.get("banco_propietario"),
            numero_cuenta_propietario=datos.get("numero_cuenta_propietario"),
            tipo_cuenta=datos.get("tipo_cuenta"),
            consignatario=datos.get("consignatario"),
            documento_consignatario=datos.get("documento_consignatario"),
            enlace_video=datos.get("enlace_video"),
        )

        return self.repo_mandato.crear(contrato, usuario_sistema)

    def obtener_mandato(self, id_contrato: int) -> Optional[ContratoMandato]:
        return self.repo_mandato.obtener_por_id(id_contrato)

    @cache_manager.invalidates(CacheKeys.MANDATOS_LIST)
    def actualizar_mandato(
        self, id_contrato: int, datos: Dict, usuario_sistema: str
    ) -> None:
        """Actualiza condiciones de un mandato."""
        db = getattr(self.repo_mandato, "db", None)
        if db is None:
            self._ejecutar_actualizacion_mandato(id_contrato, datos, usuario_sistema)
            return

        with db.transaccion():
            self._ejecutar_actualizacion_mandato(id_contrato, datos, usuario_sistema)

    def _ejecutar_actualizacion_mandato(
        self, id_contrato: int, datos: Dict, usuario_sistema: str
    ) -> None:
        mandato = self.repo_mandato.obtener_por_id(id_contrato)
        if not mandato:
            raise ValueError(f"No existe el contrato de mandato con ID {id_contrato}")

        # 0. Validar Coherencia si se están modificando fechas o duración
        if "fecha_inicio" in datos or "fecha_fin" in datos or "duracion_meses" in datos:
            f_inicio = datos.get("fecha_inicio", mandato.fecha_inicio_contrato_m)
            f_fin = datos.get("fecha_fin", mandato.fecha_fin_contrato_m)
            d_reg = int(datos.get("duracion_meses", mandato.duracion_contrato_m))

            coherente, mensaje = CalculadoraContratos.validar_coherencia(
                f_inicio, f_fin, d_reg
            )
            if not coherente:
                raise ValueError(f"Error de Integridad Contractual: {mensaje}")

        # Update fields
        mandato.id_propiedad = datos.get("id_propiedad", mandato.id_propiedad)
        mandato.id_propietario = datos.get("id_propietario", mandato.id_propietario)
        mandato.id_asesor = datos.get("id_asesor", mandato.id_asesor)

        if "fecha_inicio" in datos:
            mandato.fecha_inicio_contrato_m = datos["fecha_inicio"]
            # Recalcular Ciclo de Pago y Grupo Operativo
            grupo, _ = CalculadoraContratos.calcular_ciclo_pago_mandato(
                datos["fecha_inicio"]
            )
            dia_pago = CalculadoraContratos.calcular_dia_pago_mandato(
                datos["fecha_inicio"]
            )
            mandato.fecha_pago = str(dia_pago)
            mandato.grupo_operativo = grupo

        mandato.fecha_fin_contrato_m = datos.get(
            "fecha_fin", mandato.fecha_fin_contrato_m
        )
        mandato.duracion_contrato_m = datos.get(
            "duracion_meses", mandato.duracion_contrato_m
        )
        mandato.canon_mandato = datos.get("canon", mandato.canon_mandato)
        mandato.comision_porcentaje_contrato_m = datos.get(
            "comision_porcentaje", mandato.comision_porcentaje_contrato_m
        )
        mandato.iva_contrato_m = datos.get("iva_porcentaje", mandato.iva_contrato_m)

        # Solo actualizar fecha_pago si no fue recalculada por un cambio en fecha_inicio
        if "fecha_inicio" not in datos:
            mandato.fecha_pago = datos.get("fecha_pago", mandato.fecha_pago)

        # Actualizar campos bancarios
        if "banco_propietario" in datos:
            mandato.banco_propietario = datos["banco_propietario"]
        if "numero_cuenta_propietario" in datos:
            mandato.numero_cuenta_propietario = datos["numero_cuenta_propietario"]
        if "tipo_cuenta" in datos:
            mandato.tipo_cuenta = datos["tipo_cuenta"]
        if "consignatario" in datos:
            mandato.consignatario = datos.get("consignatario", mandato.consignatario)
        mandato.documento_consignatario = datos.get(
            "documento_consignatario", mandato.documento_consignatario
        )

        if "enlace_video" in datos:
            mandato.enlace_video = datos["enlace_video"]

        mandato.updated_by = usuario_sistema
        mandato.updated_at = datetime.now().isoformat()

        self.repo_mandato.actualizar(mandato, usuario_sistema)

    def listar_mandatos_paginado(self, **kwargs) -> Any:
        """Delega el listado al repositorio (Inyección de Infraestructura).

        Acepta sin_arrendamiento como kwarg opcional para filtrar mandatos
        cuya propiedad no tenga arrendamiento activo.
        """
        return self.repo_mandato.listar_paginado(**kwargs)

    def calcular_proyeccion_renovacion(self, id_contrato: int) -> dict:
        """
        Calcula la proyección de renovación de mandato SIN guardar nada en la BD.
        El mandato no aplica IPC, solo se extienden las fechas.
        """
        mandato = self.repo_mandato.obtener_por_id(id_contrato)
        if not mandato or mandato.estado_contrato_m != EstadoContrato.ACTIVO:
            raise ValueError("Contrato no válido para proyección de renovación")

        fecha_fin_actual = datetime.strptime(mandato.fecha_fin_contrato_m, "%Y-%m-%d")
        meses_duracion = mandato.duracion_contrato_m

        # Calcular nueva fecha fin sumando los meses de duración
        nueva_fecha_fin_dt = CalculadoraContratos.sumar_meses(
            fecha_fin_actual, meses_duracion
        )
        nueva_fecha_fin_str = nueva_fecha_fin_dt.strftime("%Y-%m-%d")

        return {
            "tipo": "Mandato",
            "fecha_fin_actual": mandato.fecha_fin_contrato_m,
            "nueva_fecha_fin": nueva_fecha_fin_str,
            "duracion_meses": meses_duracion,
            "canon_actual": mandato.canon_mandato,
            "canon_nuevo": mandato.canon_mandato,  # Sin cambio en mandato
            "porcentaje_ipc": 0.0,
            "aplica_ipc": False,
        }

    @idempotent(key_prefix="mandato:renovar")
    @cache_manager.invalidates(CacheKeys.MANDATOS_LIST)
    def renovar_mandato(
        self,
        id_contrato: int,
        usuario_sistema: str,
        nueva_fecha_fin: Optional[str] = None,
        **kwargs,
    ) -> "ContratoMandato":
        """Renueva un contrato de mandato extendiendo su fecha de fin. Acepta fecha personalizada."""
        db = getattr(self.repo_mandato, "db", None)

        if db is None:
            resultado = self._ejecutar_renovacion_mandato(
                id_contrato, usuario_sistema, nueva_fecha_fin
            )
        else:
            with db.transaccion():
                resultado = self._ejecutar_renovacion_mandato(
                    id_contrato, usuario_sistema, nueva_fecha_fin
                )

        self._invalidar_cache_estado_cartera()
        return resultado

    def _ejecutar_renovacion_mandato(
        self,
        id_contrato: int,
        usuario_sistema: str,
        nueva_fecha_fin: Optional[str] = None,
    ) -> "ContratoMandato":
        mandato = self.repo_mandato.obtener_por_id(id_contrato)
        if not mandato or mandato.estado_contrato_m != EstadoContrato.ACTIVO:
            raise ContratoNoRenovableError(
                f"Contrato de mandato {id_contrato} no válido para renovación"
            )

        # FR-009 (spec 073): mismo estándar de validación que arrendamiento.
        validar_canon(int(mandato.canon_mandato or 0))

        fecha_fin_actual = datetime.strptime(mandato.fecha_fin_contrato_m, "%Y-%m-%d")
        meses_duracion = mandato.duracion_contrato_m

        # Calcular nueva fecha fin automática
        nueva_fecha_fin_dt = CalculadoraContratos.sumar_meses(
            fecha_fin_actual, meses_duracion
        )

        nueva_fecha_fin_str = (
            nueva_fecha_fin
            if nueva_fecha_fin
            else nueva_fecha_fin_dt.strftime("%Y-%m-%d")
        )

        # Registrar historial de renovación (Spec §FR-001, §FR-006)
        fecha_inicio_ren = CalculadoraContratos.calcular_fecha_inicio_renovacion(
            mandato.fecha_fin_contrato_m
        )
        renovacion = RenovacionContrato(
            id_contrato_m=mandato.id_contrato_m,
            tipo_contrato="Mandato",
            fecha_inicio_original=mandato.fecha_inicio_contrato_m,
            fecha_fin_original=mandato.fecha_fin_contrato_m,
            fecha_inicio_renovacion=fecha_inicio_ren,
            fecha_fin_renovacion=nueva_fecha_fin_str,
            canon_anterior=mandato.canon_mandato,
            canon_nuevo=mandato.canon_mandato,
            porcentaje_incremento=0,
            motivo_renovacion="Prórroga Automática de Mandato",
            fecha_renovacion=datetime.now().date().isoformat(),
        )
        self.repo_renovacion.crear(renovacion, usuario_sistema)

        # Actualizar contrato (recalcular grupo y fecha_pago, Spec §FR-006)
        mandato.fecha_fin_contrato_m = nueva_fecha_fin_str
        mandato.fecha_renovacion_contrato_m = datetime.now().date().isoformat()
        grupo_m, dia_m = CalculadoraContratos.calcular_ciclo_pago_mandato(
            fecha_inicio_ren
        )
        mandato.grupo_operativo = grupo_m
        mandato.fecha_pago = str(dia_m)
        mandato.updated_by = usuario_sistema
        mandato.updated_at = datetime.now().isoformat()

        self.repo_mandato.actualizar(mandato, usuario_sistema)

        # Actualizar canon estimado en propiedad
        propiedad = self.repo_propiedad.obtener_por_id(mandato.id_propiedad)
        if propiedad:
            propiedad.canon_arrendamiento_estimado = mandato.canon_mandato
            self.repo_propiedad.actualizar(propiedad, usuario_sistema)

        return mandato

    def _invalidar_cache_estado_cartera(self) -> None:
        """Invalida la caché de estado de cartera post-commit (FR-012).

        El fallo de invalidación nunca debe abortar ni hacer rollback de la
        operación de renovación ya confirmada.
        """
        try:
            invalidate_cache("cache_estado_cartera")
        except Exception as ex:  # pragma: no cover
            logger.warning("No se pudo invalidar caché 'cache_estado_cartera': %s", ex)

    @cache_manager.invalidates(CacheKeys.MANDATOS_LIST)
    def terminar_mandato(
        self, id_contrato: int, motivo: str, usuario_sistema: str
    ) -> None:
        """Finaliza un contrato de mandato."""
        if not motivo:
            raise ValueError("El motivo de terminación es obligatorio")

        mandato = self.repo_mandato.obtener_por_id(id_contrato)
        if not mandato:
            raise ValueError(f"Contrato {id_contrato} no existe")

        mandato.estado_contrato_m = EstadoContrato.CANCELADO
        mandato.motivo_cancelacion = motivo
        mandato.fecha_fin_contrato_m = datetime.now().strftime("%Y-%m-%d")
        mandato.updated_by = usuario_sistema
        mandato.updated_at = datetime.now().isoformat()

        self.repo_mandato.actualizar(mandato, usuario_sistema)
