"""
Servicio de Aplicación para la gestión de Recaudos (cobros a arrendatarios).
Coordina la lógica de negocio, validaciones y persistencia de pagos.

Centraliza toda la lógica que antes estaba dispersa entre el State Reflex
y el ServicioFinanciero, siguiendo Clean Architecture.
"""

import logging
from datetime import datetime, date
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

from src.dominio.constantes.recaudo import MetodoPago, EstadoRecaudo, TipoConcepto
from src.dominio.entidades.recaudo import Recaudo
from src.dominio.entidades.recaudo_concepto import RecaudoConcepto
from src.dominio.interfaces.repositorio_recaudo import (
    IRepositorioRecaudo,
    FiltrosRecaudo,
    ResultadoPaginado,
)
from src.dominio.interfaces.repositorio_idempotencia import IRepositorioIdempotencia
from src.aplicacion.decorators.idempotent import idempotent
from src.aplicacion.esquemas.recaudo import (
    ComandoRegistrarPago,
    ComandoActualizarPago,
    RecaudoDTO,
    RecaudoDetalleDTO,
    ConceptoDTO,
    EmpresaDTO,
    RecaudoMapper,
    ResultadoGeneracionMasiva,
    ResultadoOperacion,
)
from src.aplicacion.utils.formatters import format_currency
from src.infraestructura.persistencia.database import DatabaseManager
from src.infraestructura.cache.cache_manager import cache_manager


class ServicioRecaudo:
    """
    Servicio de aplicación para gestionar pagos de arrendatarios.

    Orquesta las operaciones CRUD, cambios de estado y generación masiva,
    delegando la persistencia al repositorio y las validaciones al dominio.
    """

    def __init__(
        self,
        repo_recaudo: IRepositorioRecaudo,
        db_manager: DatabaseManager,
        repo_idempotencia: Optional[IRepositorioIdempotencia] = None,
    ) -> None:
        self.repo = repo_recaudo
        self.db = db_manager
        self.repo_idempotencia = repo_idempotencia

    # ==================== REGISTRO ====================

    @idempotent(key_prefix="recaudo:registrar")
    @cache_manager.invalidates("dashboard")
    def registrar_pago(
        self,
        comando: ComandoRegistrarPago,
        usuario: str,
        idempotency_key: Optional[str] = None,
        _idempotency_full_key: Optional[str] = None,
    ) -> Recaudo:
        """
        Registra un nuevo pago.

        Args:
            comando: Datos validados del pago a registrar
            usuario: Usuario que realiza la operación
            idempotency_key: Clave opcional de idempotencia para la operación
            _idempotency_full_key: Inyectado por @idempotent (no usar directamente)
        """
        recaudo = Recaudo(
            id_recaudo=None,
            id_contrato_a=comando.id_contrato_a,
            fecha_pago=comando.fecha_pago.isoformat(),
            valor_total=comando.valor_total,
            metodo_pago=comando.metodo_pago,
            referencia_bancaria=comando.referencia_bancaria,
            estado_recaudo=EstadoRecaudo.PENDIENTE,
            observaciones=comando.observaciones,
            created_by=usuario,
        )

        concepto = RecaudoConcepto(
            id_recaudo=0,
            tipo_concepto=comando.tipo_concepto,
            periodo=comando.periodo,
            valor=comando.valor_total,
        )

        resultado = self.repo.crear(recaudo, [concepto], usuario)

        if self.repo_idempotencia and _idempotency_full_key:
            try:
                u_id = usuario_id = 1
                user_data = self.db.execute_query_one(
                    "SELECT id_usuario FROM usuarios WHERE nombre_usuario = %s",
                    (usuario,),
                )
                if user_data:
                    u_id = user_data.get("ID_USUARIO", 1)

                self.repo_idempotencia.registrar_evento(
                    entidad_tipo="Recaudo",
                    entidad_id=resultado.id_recaudo,
                    tipo_evento="CREATED",
                    idempotency_key=_idempotency_full_key,
                    payload=(
                        resultado.__dict__
                        if hasattr(resultado, "__dict__")
                        else {"id": resultado.id_recaudo}
                    ),
                    usuario_id=u_id,
                )
            except Exception as e:
                logger.error(f"Error al registrar evento de idempotencia: {e}")

        return resultado

    # ==================== CAMBIOS DE ESTADO ====================

    @cache_manager.invalidates("dashboard")
    def aplicar_pago(self, id_recaudo: int, usuario: str) -> ResultadoOperacion:
        """
        Aplica un pago pendiente.

        Args:
            id_recaudo: ID del recaudo a aplicar
            usuario: Usuario que realiza la operación

        Returns:
            ResultadoOperacion con el resultado
        """
        recaudo = self.repo.obtener_por_id(id_recaudo)

        if not recaudo:
            return ResultadoOperacion(
                exito=False,
                mensaje=f"Recaudo {id_recaudo} no encontrado",
            )

        if not recaudo.estado_recaudo.puede_aplicarse():
            return ResultadoOperacion(
                exito=False,
                mensaje=(
                    f"Solo se pueden aplicar pagos en estado Pendiente. "
                    f"Estado actual: {recaudo.estado_recaudo.value}"
                ),
            )

        self.repo.cambiar_estado(id_recaudo, EstadoRecaudo.APLICADO.value, usuario)

        return ResultadoOperacion(
            exito=True,
            mensaje=f"Pago #{id_recaudo} aplicado exitosamente",
            id_recaudo=id_recaudo,
        )

    @cache_manager.invalidates("dashboard")
    def reversar_pago(self, id_recaudo: int, usuario: str) -> ResultadoOperacion:
        """
        Revierte un pago aplicado.

        Args:
            id_recaudo: ID del recaudo a reversar
            usuario: Usuario que realiza la operación

        Returns:
            ResultadoOperacion con el resultado
        """
        recaudo = self.repo.obtener_por_id(id_recaudo)

        if not recaudo:
            return ResultadoOperacion(
                exito=False,
                mensaje=f"Recaudo {id_recaudo} no encontrado",
            )

        if not recaudo.estado_recaudo.puede_reversarse():
            return ResultadoOperacion(
                exito=False,
                mensaje=(
                    f"Solo se pueden reversar pagos en estado Aplicado. "
                    f"Estado actual: {recaudo.estado_recaudo.value}"
                ),
            )

        self.repo.cambiar_estado(id_recaudo, EstadoRecaudo.REVERSADO.value, usuario)

        return ResultadoOperacion(
            exito=True,
            mensaje=f"Pago #{id_recaudo} reversado",
            id_recaudo=id_recaudo,
        )

    # ==================== ELIMINACIÓN ====================

    @cache_manager.invalidates("dashboard")
    def eliminar_pago(self, id_recaudo: int, usuario: str) -> ResultadoOperacion:
        """
        Elimina un pago pendiente.

        Args:
            id_recaudo: ID del recaudo a eliminar
            usuario: Usuario que realiza la operación

        Returns:
            ResultadoOperacion con el resultado
        """
        recaudo = self.repo.obtener_por_id(id_recaudo)

        if not recaudo:
            return ResultadoOperacion(
                exito=False,
                mensaje=f"Recaudo {id_recaudo} no encontrado",
            )

        if not recaudo.estado_recaudo.puede_eliminarse():
            return ResultadoOperacion(
                exito=False,
                mensaje=(
                    f"Solo se pueden eliminar recaudos en estado Pendiente. "
                    f"Estado actual: {recaudo.estado_recaudo.value}"
                ),
            )

        self.repo.eliminar(id_recaudo, usuario)

        return ResultadoOperacion(
            exito=True,
            mensaje=f"Recaudo #{id_recaudo} eliminado",
            id_recaudo=id_recaudo,
        )

    # ==================== ACTUALIZACIÓN ====================

    @cache_manager.invalidates("dashboard")
    def actualizar_pago(
        self, id_recaudo: int, comando: ComandoActualizarPago, usuario: str
    ) -> ResultadoOperacion:
        """
        Actualiza un pago existente.

        Args:
            id_recaudo: ID del recaudo a actualizar
            comando: Datos validados para la actualización
            usuario: Usuario que realiza la operación
        """
        recaudo_existente = self.repo.obtener_por_id(id_recaudo)

        if not recaudo_existente:
            return ResultadoOperacion(
                exito=False,
                mensaje=f"Recaudo {id_recaudo} no encontrado",
            )

        if not recaudo_existente.estado_recaudo.puede_editarse():
            return ResultadoOperacion(
                exito=False,
                mensaje=(
                    f"No se puede editar el recaudo en estado {recaudo_existente.estado_recaudo.value}"
                ),
            )

        # Actualizar campos de la entidad principal preservando el estado original
        recaudo_actualizado = Recaudo(
            id_recaudo=id_recaudo,
            id_contrato_a=recaudo_existente.id_contrato_a,
            fecha_pago=comando.fecha_pago.isoformat(),
            valor_total=comando.valor_total,
            metodo_pago=comando.metodo_pago,
            referencia_bancaria=comando.referencia_bancaria,
            estado_recaudo=recaudo_existente.estado_recaudo,  # Preservar estado (Pendiente o Vencido)
            observaciones=comando.observaciones,
            created_by=recaudo_existente.created_by,
            created_at=recaudo_existente.created_at,
        )

        # Preparar el nuevo concepto único
        concepto = RecaudoConcepto(
            id_recaudo=id_recaudo,
            tipo_concepto=comando.tipo_concepto,
            periodo=comando.periodo,
            valor=comando.valor_total,
        )

        try:
            self.repo.actualizar(recaudo_actualizado, usuario, [concepto])
            return ResultadoOperacion(
                exito=True,
                mensaje=f"Pago #{id_recaudo} actualizado exitosamente",
                id_recaudo=id_recaudo,
            )
        except Exception as e:
            logger.error(f"Error al actualizar pago #{id_recaudo}: {e}")
            return ResultadoOperacion(
                exito=False,
                mensaje=f"Error interno al actualizar: {str(e)}",
            )

    # ==================== CONSULTAS ====================

    def listar_paginado(self, filtros: FiltrosRecaudo) -> ResultadoPaginado[RecaudoDTO]:
        """
        Lista recaudos con filtros y paginación.

        Args:
            filtros: Filtros tipados para la consulta

        Returns:
            ResultadoPaginado con los items DTO y metadata
        """
        estado_str = filtros.estado.value if filtros.estado else None

        total = self.repo.contar_con_filtros(
            estado=estado_str,
            fecha_desde=filtros.fecha_desde,
            fecha_hasta=filtros.fecha_hasta,
            busqueda=filtros.busqueda,
            dia_pago=filtros.dia_pago,
        )

        rows = self.repo.listar_paginado(
            limit=filtros.page_size,
            offset=filtros.offset,
            estado=estado_str,
            fecha_desde=filtros.fecha_desde,
            fecha_hasta=filtros.fecha_hasta,
            busqueda=filtros.busqueda,
            dia_pago=filtros.dia_pago,
            sort_by=filtros.sort_by,
            sort_order=filtros.sort_order,
        )

        items = [RecaudoMapper.map_to_dto(row) for row in rows]

        return ResultadoPaginado(
            items=items,
            total=total,
            page=filtros.page,
            page_size=filtros.page_size,
        )

    def obtener_detalle(self, id_recaudo: int) -> Optional[RecaudoDetalleDTO]:
        """
        Obtiene el detalle completo de un recaudo.

        Args:
            id_recaudo: ID del recaudo

        Returns:
            RecaudoDetalleDTO con datos del recaudo y conceptos, o None
        """
        recaudo = self.repo.obtener_por_id(id_recaudo)
        if not recaudo:
            return None

        conceptos_entities = self.repo.obtener_conceptos_por_recaudo(id_recaudo)

        info_contrato = self.obtener_info_contrato(recaudo.id_contrato_a)

        conceptos_dto = [
            ConceptoDTO(
                tipo=c.tipo_concepto,
                periodo=c.periodo,
                valor=c.valor,
                valor_view=format_currency(c.valor),
            )
            for c in conceptos_entities
        ]

        return RecaudoDetalleDTO(
            id_recaudo=recaudo.id_recaudo or 0,
            id_contrato=recaudo.id_contrato_a,
            direccion=info_contrato.get("direccion", ""),
            matricula=info_contrato.get("matricula", ""),
            arrendatario=info_contrato.get("arrendatario", ""),
            telefono_arrendatario=info_contrato.get("telefono_arrendatario", ""),
            habitante=info_contrato.get("habitante", ""),
            telefono_habitante=info_contrato.get("telefono_habitante", ""),
            fecha_pago=recaudo.fecha_pago,
            valor_total=recaudo.valor_total,
            valor_total_view=format_currency(recaudo.valor_total),
            metodo_pago=(
                recaudo.metodo_pago.value
                if hasattr(recaudo.metodo_pago, "value")
                else str(recaudo.metodo_pago)
            ),
            referencia=recaudo.referencia_bancaria or "",
            estado=(
                recaudo.estado_recaudo.value
                if hasattr(recaudo.estado_recaudo, "value")
                else str(recaudo.estado_recaudo)
            ),
            observaciones=recaudo.observaciones or "",
            created_at=recaudo.created_at or "",
            created_by=recaudo.created_by or "",
            conceptos=conceptos_dto,
        )

    def obtener_contratos_activos(self) -> List[Dict[str, Any]]:
        """
        Obtiene los contratos activos con info de propiedad y arrendatario.
        Usado para poblar filtros y combobox en la UI.

        Returns:
            Lista de diccionarios con id, texto y canon del contrato
        """
        query = """
            SELECT 
                ca.ID_CONTRATO_A,
                p.DIRECCION_PROPIEDAD,
                per.NOMBRE_COMPLETO,
                ca.CANON_ARRENDAMIENTO
            FROM CONTRATOS_ARRENDAMIENTOS ca
            INNER JOIN PROPIEDADES p ON ca.ID_PROPIEDAD = p.ID_PROPIEDAD
            INNER JOIN ARRENDATARIOS arr ON ca.ID_ARRENDATARIO = arr.ID_ARRENDATARIO
            INNER JOIN PERSONAS per ON arr.ID_PERSONA = per.ID_PERSONA
            WHERE ca.ESTADO_CONTRATO_A = 'ACTIVO'
            ORDER BY p.DIRECCION_PROPIEDAD
        """

        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            cursor.execute(query)
            rows = cursor.fetchall()

        return [
            {
                "id": str(row["ID_CONTRATO_A"]),
                "texto": f"ID:{row['ID_CONTRATO_A']} - {row['DIRECCION_PROPIEDAD']} ({row['NOMBRE_COMPLETO']})",
                "canon": row["CANON_ARRENDAMIENTO"],
            }
            for row in rows
        ]

    def obtener_info_contrato(self, id_contrato: int) -> Dict[str, str]:
        """
        Obtiene información de un contrato específico para el detalle.

        Args:
            id_contrato: ID del contrato de arrendamiento

        Returns:
            Dict con direccion, matricula, arrendatario y datos de contacto
        """
        placeholder = self.db.get_placeholder()
        query = f"""
            SELECT 
                p.DIRECCION_PROPIEDAD,
                p.MATRICULA_INMOBILIARIA,
                per.NOMBRE_COMPLETO as ARRENDATARIO,
                per.TELEFONO_PRINCIPAL as TELEFONO_ARRENDATARIO,
                arr.NOMBRE_HABITANTE,
                arr.TELEFONO_HABITANTE
            FROM CONTRATOS_ARRENDAMIENTOS ca
            INNER JOIN PROPIEDADES p ON ca.ID_PROPIEDAD = p.ID_PROPIEDAD
            INNER JOIN ARRENDATARIOS arr ON ca.ID_ARRENDATARIO = arr.ID_ARRENDATARIO
            INNER JOIN PERSONAS per ON arr.ID_PERSONA = per.ID_PERSONA
            WHERE ca.ID_CONTRATO_A = {placeholder}
        """

        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            cursor.execute(query, (id_contrato,))
            row = cursor.fetchone()

        return {
            "direccion": (row["DIRECCION_PROPIEDAD"] or "") if row else "",
            "matricula": (row["MATRICULA_INMOBILIARIA"] or "") if row else "",
            "arrendatario": (row["ARRENDATARIO"] or "") if row else "",
            "telefono_arrendatario": (
                (row["TELEFONO_ARRENDATARIO"] or "") if row else ""
            ),
            "habitante": (row["NOMBRE_HABITANTE"] or "") if row else "",
            "telefono_habitante": (row["TELEFONO_HABITANTE"] or "") if row else "",
        }

    # ==================== GENERACIÓN MASIVA ====================

    @cache_manager.invalidates("dashboard")
    def generar_recaudos_mes_actual(
        self, usuario_sistema: str
    ) -> ResultadoGeneracionMasiva:
        """
        Genera masivamente los recaudos de canon para todos los contratos
        activos que aún no tengan un recaudo generado en el mes actual.

        Args:
            usuario_sistema: Usuario que genera los pagos

        Returns:
            ResultadoGeneracionMasiva con el resumen de la operación
        """
        ahora = datetime.now()
        periodo_bd = ahora.strftime("%Y-%m")
        fecha_hoy = ahora.date()

        meses_espanol = [
            "enero",
            "febrero",
            "marzo",
            "abril",
            "mayo",
            "junio",
            "julio",
            "agosto",
            "septiembre",
            "octubre",
            "noviembre",
            "diciembre",
        ]
        periodo_display = f"{meses_espanol[ahora.month - 1]} de {ahora.year}"

        # 1. Obtener contratos activos con fecha de inicio
        query_contratos = """
            SELECT ID_CONTRATO_A, CANON_ARRENDAMIENTO, FECHA_INICIO_CONTRATO_A
            FROM CONTRATOS_ARRENDAMIENTOS
            WHERE ESTADO_CONTRATO_A = 'ACTIVO'
        """

        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            cursor.execute(query_contratos)
            contratos_activos = cursor.fetchall()

        if not contratos_activos:
            return ResultadoGeneracionMasiva(
                generados=0,
                omitidos_por_duplicidad=0,
                periodo=periodo_bd,
            )

        # 2. Obtener IDs de contratos que ya tienen recaudo este mes
        ids_ya_facturados = set(self.repo.obtener_ids_contratos_con_recaudo(periodo_bd))

        recaudos_a_crear: List[tuple[Recaudo, List[RecaudoConcepto]]] = []
        omitidos = 0

        # 3. Filtrar y preparar entidades
        for contrato in contratos_activos:
            id_contrato = contrato["ID_CONTRATO_A"]
            canon = contrato["CANON_ARRENDAMIENTO"]

            if id_contrato in ids_ya_facturados:
                omitidos += 1
                continue

            if not canon or canon <= 0:
                continue

            fecha_inicio_str = contrato.get("FECHA_INICIO_CONTRATO_A")
            if not fecha_inicio_str:
                continue

            try:
                fecha_inicio = datetime.strptime(fecha_inicio_str, "%Y-%m-%d").date()
            except (ValueError, TypeError):
                continue

            dia_pago = fecha_inicio.day

            try:
                fecha_pago_calculada = date(ahora.year, ahora.month, dia_pago)
            except ValueError:
                fecha_pago_calculada = date(ahora.year, ahora.month, 1)

            if fecha_pago_calculada < fecha_hoy:
                estado_recaudo = EstadoRecaudo.VENCIDO
            else:
                estado_recaudo = EstadoRecaudo.PENDIENTE

            recaudo = Recaudo(
                id_recaudo=None,
                id_contrato_a=id_contrato,
                fecha_pago=fecha_pago_calculada.isoformat(),
                valor_total=canon,
                metodo_pago=MetodoPago.EFECTIVO,
                referencia_bancaria=None,
                estado_recaudo=estado_recaudo,
                observaciones=f"Generación masiva - {periodo_display}",
                created_by=usuario_sistema,
            )

            concepto = RecaudoConcepto(
                id_recaudo=0,
                tipo_concepto=TipoConcepto.CANON,
                periodo=periodo_bd,
                valor=canon,
            )

            recaudos_a_crear.append((recaudo, [concepto]))

        # 4. Persistir masivamente
        generados = self.repo.crear_masivo(recaudos_a_crear, usuario_sistema)

        return ResultadoGeneracionMasiva(
            generados=generados,
            omitidos_por_duplicidad=omitidos,
            periodo=periodo_bd,
        )

    # ==================== EXPORTACIÓN MASIVA PDF ====================

    def generar_recibos_masivos_pdf(self, periodo: str) -> str:
        """Genera todos los recibos de recaudo de un período como archivo ZIP.

        Orquesta:
        1. Consulta al repositorio para obtener recaudos enriquecidos.
        2. Transformación de datos al formato PDF élite mediante Mapper.
        3. Delegación a la facade para generación paralela y empaquetado ZIP.

        Args:
            periodo: Período en formato YYYY-MM.

        Returns:
            Ruta absoluta del archivo ZIP generado.

        Raises:
            ValueError: Si no hay recaudos en el período.
        """
        import re

        if not re.match(r"^\d{4}-\d{2}$", periodo):
            raise ValueError(f"Formato de período inválido: {periodo}. Use YYYY-MM.")

        logger.info(f"Iniciando generación masiva de recibos para período: {periodo}")

        # 1. Obtener datos enriquecidos del repositorio
        recaudos = self.repo.obtener_recaudos_por_periodo(periodo)

        if not recaudos:
            raise ValueError(f"No se encontraron recaudos para el período {periodo}")

        logger.info(f"Se encontraron {len(recaudos)} recaudos en el período {periodo}")

        # 2. Inyectar datos de empresa (logo)
        empresa_dto = None
        try:
            from src.aplicacion.servicios.servicio_configuracion import (
                ServicioConfiguracion,
            )

            servicio_config = ServicioConfiguracion(self.db)
            config_emp = servicio_config.obtener_configuracion_empresa()
            if config_emp:
                empresa_dto = EmpresaDTO(
                    nombre=config_emp.nombre_empresa,
                    nit=config_emp.nit,
                    direccion=config_emp.direccion,
                    telefono=config_emp.telefono,
                    email=config_emp.email,
                    logo_base64=config_emp.logo_base64,
                    website=config_emp.website,
                )
        except Exception as e:
            logger.warning(f"No se pudo cargar configuración de empresa: {e}")

        # 3. Transformar datos al formato PDF élite mediante Mapper
        lista_datos_pdf = [
            RecaudoMapper.map_to_pdf_dto(
                rec, empresa=empresa_dto, periodo_fallback=periodo
            ).model_dump()
            for rec in recaudos
        ]

        # 4. Generar ZIP con la facade
        from src.infraestructura.servicios.servicio_pdf_facade import ServicioPDFFacade

        facade = ServicioPDFFacade()
        zip_path = facade.generar_lote_recibos_recaudo_zip(
            lista_datos=lista_datos_pdf,
            filename_prefix=f"recibos_recaudo_{periodo}",
        )

        logger.info(f"ZIP generado exitosamente: {zip_path}")
        return zip_path
