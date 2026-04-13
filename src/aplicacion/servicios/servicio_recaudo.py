"""
Servicio de Aplicación para la gestión de Recaudos (cobros a arrendatarios).
Coordina la lógica de negocio, validaciones y persistencia de pagos.

Centraliza toda la lógica que antes estaba dispersa entre el State Reflex
y el ServicioFinanciero, siguiendo Clean Architecture.
"""

from datetime import datetime, date
from typing import Any, Dict, List, Optional

from src.dominio.constantes.recaudo import MetodoPago, EstadoRecaudo, TipoConcepto
from src.dominio.entidades.recaudo import Recaudo
from src.dominio.entidades.recaudo_concepto import RecaudoConcepto
from src.dominio.interfaces.repositorio_recaudo import (
    IRepositorioRecaudo,
    FiltrosRecaudo,
    ResultadoPaginado,
)
from src.aplicacion.esquemas.recaudo import (
    ComandoRegistrarPago,
    RecaudoDTO,
    RecaudoDetalleDTO,
    ConceptoDTO,
    ResultadoGeneracionMasiva,
    ResultadoOperacion,
)
from src.infraestructura.persistencia.database import DatabaseManager


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
    ) -> None:
        self.repo = repo_recaudo
        self.db = db_manager

    # ==================== REGISTRO ====================

    def registrar_pago(self, comando: ComandoRegistrarPago, usuario: str) -> Recaudo:
        """
        Registra un nuevo pago.

        Args:
            comando: Datos validados del pago a registrar
            usuario: Usuario que realiza la operación

        Returns:
            Entidad Recaudo creada con ID asignado

        Raises:
            ValueError: Si los datos son inválidos
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

        return self.repo.crear(recaudo, [concepto], usuario)

    # ==================== CAMBIOS DE ESTADO ====================

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

    # ==================== CONSULTAS ====================

    def listar_paginado(
        self, filtros: FiltrosRecaudo
    ) -> ResultadoPaginado[Dict[str, Any]]:
        """
        Lista recaudos con filtros y paginación.

        Args:
            filtros: Filtros tipados para la consulta

        Returns:
            ResultadoPaginado con los items y metadata
        """
        estado_str = filtros.estado.value if filtros.estado else None

        total = self.repo.contar_con_filtros(
            estado=estado_str,
            fecha_desde=filtros.fecha_desde,
            fecha_hasta=filtros.fecha_hasta,
            busqueda=filtros.busqueda,
        )

        items = self.repo.listar_paginado(
            limit=filtros.page_size,
            offset=filtros.offset,
            estado=estado_str,
            fecha_desde=filtros.fecha_desde,
            fecha_hasta=filtros.fecha_hasta,
            busqueda=filtros.busqueda,
        )

        return ResultadoPaginado(
            items=items,
            total=total,
            page=filtros.page,
            page_size=filtros.page_size,
        )

    def obtener_detalle(self, id_recaudo: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene el detalle completo de un recaudo.

        Args:
            id_recaudo: ID del recaudo

        Returns:
            Dict con datos del recaudo, contrato y conceptos, o None
        """
        recaudo = self.repo.obtener_por_id(id_recaudo)
        if not recaudo:
            return None

        conceptos = self.repo.obtener_conceptos_por_recaudo(id_recaudo)

        return {
            "recaudo": recaudo,
            "conceptos": conceptos,
        }

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
            WHERE ca.ESTADO_CONTRATO_A = 'Activo'
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
            Dict con direccion, matricula y arrendatario
        """
        placeholder = self.db.get_placeholder()
        query = f"""
            SELECT 
                p.DIRECCION_PROPIEDAD,
                p.MATRICULA_INMOBILIARIA,
                per.NOMBRE_COMPLETO as ARRENDATARIO
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
            "direccion": row["DIRECCION_PROPIEDAD"] if row else "",
            "matricula": row["MATRICULA_INMOBILIARIA"] if row else "",
            "arrendatario": row["ARRENDATARIO"] if row else "",
        }

    # ==================== GENERACIÓN MASIVA ====================

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
        fecha_hoy = ahora.date().isoformat()

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
            WHERE ESTADO_CONTRATO_A = 'Activo'
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
