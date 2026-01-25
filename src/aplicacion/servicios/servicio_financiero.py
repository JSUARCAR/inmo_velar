"""
Servicio de Aplicación: Gestión Financiera
Coordina la lógica de negocio para recaudos y liquidaciones.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from dateutil.relativedelta import relativedelta

from src.dominio.entidades.liquidacion import Liquidacion
from src.dominio.entidades.liquidacion_propietario import LiquidacionPropietario
from src.dominio.entidades.recaudo import Recaudo
from src.dominio.entidades.recaudo_concepto import RecaudoConcepto
from src.infraestructura.cache.cache_manager import cache_manager
from src.infraestructura.persistencia.database import DatabaseManager
from src.infraestructura.persistencia.repositorio_contrato_arrendamiento_sqlite import (
    RepositorioContratoArrendamientoSQLite,
)
from src.infraestructura.persistencia.repositorio_contrato_mandato_sqlite import (
    RepositorioContratoMandatoSQLite,
)
from src.infraestructura.persistencia.repositorio_liquidacion_sqlite import (
    RepositorioLiquidacionSQLite,
)
from src.infraestructura.persistencia.repositorio_recaudo_sqlite import RepositorioRecaudoSQLite
from src.infraestructura.servicios.servicio_documentos_pdf import ServicioDocumentosPDF


class ServicioFinanciero:
    """Servicio para gestión de recaudos y liquidaciones"""

    def __init__(self, db_manager: DatabaseManager):
        self.repo_recaudo = RepositorioRecaudoSQLite(db_manager)
        self.repo_liquidacion = RepositorioLiquidacionSQLite(db_manager)
        self.repo_arriendo = RepositorioContratoArrendamientoSQLite(db_manager)
        self.repo_mandato = RepositorioContratoMandatoSQLite(db_manager)
        self.pdf_service = ServicioDocumentosPDF()
        self.db = db_manager

    # =========================================================================
    # RECAUDOS
    # =========================================================================

    def registrar_recaudo(
        self, datos: Dict[str, Any], conceptos_data: List[Dict[str, Any]], usuario_sistema: str
    ) -> Recaudo:
        """
        Registra un nuevo pago del inquilino con sus conceptos.

        Args:
            datos: {
                'id_contrato_a': int,
                'fecha_pago': str (YYYY-MM-DD),
                'valor_total': int,
                'metodo_pago': str,
                'referencia_bancaria': str (opcional si es efectivo),
                'observaciones': str (opcional)
            }
            conceptos_data: [
                {
                    'tipo_concepto': str ('Canon', 'Administración', 'Mora', 'Servicios', 'Otro'),
                    'periodo': str (YYYY-MM),
                    'valor': int
                }
            ]
            usuario_sistema: str

        Returns:
            Recaudo creado con sus conceptos

        Raises:
            ValueError: Si la suma de conceptos != valor_total o validaciones fallan
        """
        # Crear entidad Recaudo
        recaudo = Recaudo(
            id_contrato_a=datos["id_contrato_a"],
            fecha_pago=datos["fecha_pago"],
            valor_total=datos["valor_total"],
            metodo_pago=datos["metodo_pago"],
            referencia_bancaria=datos.get("referencia_bancaria"),
            observaciones=datos.get("observaciones"),
        )

        # Crear entidades RecaudoConcepto
        conceptos = [
            RecaudoConcepto(
                tipo_concepto=c["tipo_concepto"], periodo=c["periodo"], valor=c["valor"]
            )
            for c in conceptos_data
        ]

        # El repositorio valida que la suma sea correcta
        return self.repo_recaudo.crear(recaudo, conceptos, usuario_sistema)

    def calcular_mora(
        self, id_contrato_a: int, fecha_limite: str, fecha_pago: str, valor_canon: int
    ) -> int:
        """
        Calcula el valor de mora automáticamente según días de retraso.
        Tasa: 6% anual (configurable desde PARAMETROS_SISTEMA en el futuro)

        Args:
            id_contrato_a: ID del contrato de arrendamiento
            fecha_limite: Fecha límite de pago (YYYY-MM-DD)
            fecha_pago: Fecha real de pago (YYYY-MM-DD)
            valor_canon: Monto del canon sobre el cual calcular la mora

        Returns:
            Valor de la mora calculado
        """
        fecha_lim = datetime.fromisoformat(fecha_limite)
        fecha_pag = datetime.fromisoformat(fecha_pago)

        # Calcular días de mora
        dias_mora = (fecha_pag - fecha_lim).days

        if dias_mora <= 0:
            return 0

        # Tasa de mora: 6% anual = 0.06 / 365
        tasa_diaria = 0.06 / 365
        valor_mora = int(valor_canon * tasa_diaria * dias_mora)

        return valor_mora

    def aplicar_pago_anticipado(
        self,
        id_contrato_a: int,
        meses_adelantados: int,
        valor_canon_mensual: int,
        fecha_pago: str,
        metodo_pago: str,
        referencia_bancaria: Optional[str],
        usuario_sistema: str,
    ) -> Recaudo:
        """
        Registra un pago anticipado de varios meses.
        Crea un recaudo con múltiples conceptos (uno por cada mes).

        Args:
            id_contrato_a: ID del contrato
            meses_adelantados: Número de meses que se están pagando
            valor_canon_mensual: Valor del canon por mes
            fecha_pago: Fecha del pago
            metodo_pago: Método usado
            referencia_bancaria: Referencia del pago
            usuario_sistema: Usuario que registra

        Returns:
            Recaudo creado con N conceptos (uno por mes)
        """
        # Calcular el valor total
        valor_total = valor_canon_mensual * meses_adelantados

        # Generar conceptos para cada mes
        conceptos_data = []
        fecha_base = datetime.fromisoformat(fecha_pago)

        for i in range(meses_adelantados):
            periodo = (fecha_base + relativedelta(months=i)).strftime("%Y-%m")
            conceptos_data.append(
                {"tipo_concepto": "Canon", "periodo": periodo, "valor": valor_canon_mensual}
            )

        # Registrar el recaudo
        return self.registrar_recaudo(
            datos={
                "id_contrato_a": id_contrato_a,
                "fecha_pago": fecha_pago,
                "valor_total": valor_total,
                "metodo_pago": metodo_pago,
                "referencia_bancaria": referencia_bancaria,
                "observaciones": f"Pago anticipado de {meses_adelantados} meses",
            },
            conceptos_data=conceptos_data,
            usuario_sistema=usuario_sistema,
        )

    # =========================================================================
    # LIQUIDACIONES
    # =========================================================================

    def generar_liquidacion_mensual(
        self,
        id_contrato_m: int,
        periodo: str,
        datos_adicionales: Dict[str, Any],
        usuario_sistema: str,
    ) -> Liquidacion:
        """
        Genera la liquidación mensual de un contrato de mandato.
        Aplica la fórmula completa: Canon - Comisión - IVA - 4x1000 - Gastos

        Args:
            id_contrato_m: ID del contrato de mandato
            periodo: Período de liquidación (YYYY-MM)
            datos_adicionales: {
                'otros_ingresos': int (opcional, default 0),
                'gastos_administracion': int (opcional, default 0),
                'gastos_servicios': int (opcional, default 0),
                'gastos_reparaciones': int (opcional, default 0),
                'otros_egresos': int (opcional, default 0),
                'observaciones': str (opcional),
                'comision_porcentaje': int (base 10000, ej: 1000 = 10%)
            }
            usuario_sistema: str

        Returns:
            Liquidacion creada en estado 'En Proceso'
        """
        # Obtener el contrato de mandato
        contrato = self.repo_mandato.obtener_por_id(id_contrato_m)
        if not contrato:
            raise ValueError(f"No existe el contrato de mandato con ID {id_contrato_m}")

        # Verificar que no exista ya una liquidación para este período
        existente = self.repo_liquidacion.obtener_por_contrato_y_periodo(id_contrato_m, periodo)
        if existente:
            raise ValueError(f"Ya existe una liquidación para el período {periodo}")

        # ===== CÁLCULO DE INGRESOS =====
        canon_bruto = contrato.canon_mandato
        otros_ingresos = datos_adicionales.get("otros_ingresos", 0)
        total_ingresos = canon_bruto + otros_ingresos

        # ===== CÁLCULO DE EGRESOS =====
        # 1. Comisión de administración
        comision_porcentaje = datos_adicionales.get(
            "comision_porcentaje", contrato.comision_porcentaje_contrato_m
        )
        comision_monto = int((canon_bruto * comision_porcentaje) / 10000)

        # 2. IVA sobre la comisión (19%)
        iva_comision = int(comision_monto * 0.19)

        # 3. Impuesto 4x1000 sobre el total de ingresos
        impuesto_4x1000 = int(total_ingresos * 0.004)

        # 4. Gastos operativos
        gastos_administracion = datos_adicionales.get("gastos_administracion", 0)
        gastos_servicios = datos_adicionales.get("gastos_servicios", 0)
        gastos_reparaciones = datos_adicionales.get("gastos_reparaciones", 0)
        otros_egresos = datos_adicionales.get("otros_egresos", 0)

        # Crear la entidad Liquidacion
        liquidacion = Liquidacion(
            id_contrato_m=id_contrato_m,
            periodo=periodo,
            fecha_generacion=datetime.now().date().isoformat(),
            canon_bruto=canon_bruto,
            otros_ingresos=otros_ingresos,
            comision_porcentaje=comision_porcentaje,
            comision_monto=comision_monto,
            iva_comision=iva_comision,
            impuesto_4x1000=impuesto_4x1000,
            gastos_administracion=gastos_administracion,
            gastos_servicios=gastos_servicios,
            gastos_reparaciones=gastos_reparaciones,
            otros_egresos=otros_egresos,
            estado_liquidacion="En Proceso",
            observaciones=datos_adicionales.get("observaciones"),
        )

        # El método calcular_totales() se ejecutará en el repositorio
        return self.repo_liquidacion.crear(liquidacion, usuario_sistema)

    def listar_todas_liquidaciones(self) -> List[Dict[str, Any]]:
        """
        Lista todas las liquidaciones del sistema con información enriquecida.
        Útil para la vista administrativa de liquidaciones.

        Returns:
            List[Dict]: Lista con información completa de cada liquidación
        """
        return self.repo_liquidacion.listar_todas()

    def aprobar_liquidacion(self, id_liquidacion: int, usuario_sistema: str) -> None:
        """
        Aprueba una liquidación (cambio de 'En Proceso' a 'Aprobada').
        Solo puede hacerlo un Administrador Financiero.

        Args:
            id_liquidacion: ID de la liquidación
            usuario_sistema: Usuario que aprueba (debe tener permisos)

        Raises:
            ValueError: Si la liquidación no existe o no está en estado correcto
        """
        self.repo_liquidacion.aprobar(id_liquidacion, usuario_sistema)

    def marcar_liquidacion_pagada(
        self,
        id_liquidacion: int,
        fecha_pago: str,
        metodo_pago: str,
        referencia_pago: str,
        usuario_sistema: str,
    ) -> None:
        """
        Marca una liquidación como pagada (cambio de 'Aprobada' a 'Pagada').
        Se ejecuta al registrar el comprobante de transferencia al propietario.

        Args:
            id_liquidacion: ID de la liquidación
            fecha_pago: Fecha en que se transfirió el dinero
            metodo_pago: Método usado (ej: 'Transferencia Electrónica')
            referencia_pago: Número de comprobante bancario
            usuario_sistema: Usuario que registra el pago

        Raises:
            ValueError: Si la liquidación no existe o no está en estado 'Aprobada'
        """
        self.repo_liquidacion.marcar_como_pagada(
            id_liquidacion, fecha_pago, metodo_pago, referencia_pago, usuario_sistema
        )

    def cancelar_liquidacion(self, id_liquidacion: int, motivo: str, usuario_sistema: str) -> None:
        """
        Cancela una liquidación (estado 'Cancelada').
        Solo puede hacerlo un Gerente en casos excepcionales.

        Args:
            id_liquidacion: ID de la liquidación
            motivo: Justificación de la cancelación
            usuario_sistema: Usuario que cancela (debe ser Gerente)

        Raises:
            ValueError: Si no tiene permisos o la liquidación no existe
        """
        # TODO: Validar rol de usuario (cuando implementemos sistema de permisos)
        self.repo_liquidacion.cancelar(id_liquidacion, motivo, usuario_sistema)

    def reversar_liquidacion(self, id_liquidacion: int, usuario_sistema: str) -> None:
        """
        Reversa una liquidación de 'Aprobada' a 'En Proceso'.
        Permite corregir liquidaciones que fueron aprobadas por error.

        Args:
            id_liquidacion: ID de la liquidación
            usuario_sistema: Usuario que reversa

        Raises:
            ValueError: Si la liquidación no está en estado 'Aprobada'
        """
        self.repo_liquidacion.reversar(id_liquidacion, usuario_sistema)

    def cancelar_liquidaciones_masivas(
        self, ids_liquidaciones: List[int], motivo: str, usuario_sistema: str
    ) -> Dict[str, List[int]]:
        """
        Cancela múltiples liquidaciones.

        Args:
            ids_liquidaciones: Lista de IDs de liquidaciones a cancelar
            motivo: Motivo común para todas las cancelaciones
            usuario_sistema: Usuario que cancela

        Returns:
            {'exitosas': [ids exitosos], 'fallidas': [ids fallidos]}
        """
        return self.repo_liquidacion.cancelar_masivamente(
            ids_liquidaciones, motivo, usuario_sistema
        )

    def reversar_liquidaciones_masivas(
        self, ids_liquidaciones: List[int], usuario_sistema: str
    ) -> Dict[str, List[int]]:
        """
        Reversa múltiples liquidaciones de 'Aprobada' a 'En Proceso'.

        Args:
            ids_liquidaciones: Lista de IDs de liquidaciones a reversar
            usuario_sistema: Usuario que reversa

        Returns:
            {'exitosas': [ids exitosos], 'fallidas': [ids fallidos]}
        """
        return self.repo_liquidacion.reversar_masivamente(ids_liquidaciones, usuario_sistema)

    def cancelar_liquidaciones_por_propietario(
        self, id_propietario: int, periodo: str, motivo: str, usuario_sistema: str
    ) -> int:
        """
        Cancela todas las liquidaciones de un propietario para un período.

        Returns:
            Cantidad de liquidaciones canceladas
        """
        return self.repo_liquidacion.cancelar_por_propietario_y_periodo(
            id_propietario, periodo, motivo, usuario_sistema
        )

    def reversar_liquidaciones_por_propietario(
        self, id_propietario: int, periodo: str, usuario_sistema: str
    ) -> int:
        """
        Reversa todas las liquidaciones aprobadas de un propietario para un período.

        Returns:
            Cantidad de liquidaciones reversadas
        """
        return self.repo_liquidacion.reversar_por_propietario_y_periodo(
            id_propietario, periodo, usuario_sistema
        )

    # =========================================================================
    # CONSULTAS Y REPORTES
    # =========================================================================

    def obtener_saldo_inquilino(self, id_contrato_a: int) -> Dict[str, Any]:
        """
        Calcula el saldo actual de un inquilino (pagos vs. canon debido).
        Útil para saber si tiene pagos anticipados o deudas.

        Returns:
            {
                'total_pagado': int,
                'total_debido': int,
                'saldo': int (positivo = a favor, negativo = deuda),
                'meses_pagados': int
            }
        """
        # Obtener todos los recaudos del contrato
        recaudos = self.repo_recaudo.listar_por_contrato(id_contrato_a)

        # Sumar el total pagado
        total_pagado = sum(r.valor_total for r in recaudos if r.esta_aplicado)

        # TODO: Calcular el total debido según la fecha actual y el contrato
        # Por ahora, retornamos solo lo pagado
        return {
            "total_pagado": total_pagado,
            "total_debido": 0,  # Requiere lógica adicional
            "saldo": total_pagado,
            "meses_pagados": 0,  # Requiere análisis de conceptos
        }

    def listar_todos_recaudos(self) -> List[Dict[str, Any]]:
        """
        Lista todos los recaudos del sistema con información del contrato.

        Returns:
            Lista de diccionarios con información resumida de cada recaudo
        """
        recaudos = self.repo_recaudo.listar_todos()

        # Convertir a formato dict para la UI
        return [
            {
                "id": r.id_recaudo,
                "fecha": r.fecha_pago,
                "contrato": r.direccion_propiedad,  # Mostrar dirección del inmueble
                "valor": r.valor_total,
                "metodo": r.metodo_pago,
                "estado": r.estado_recaudo,
            }
            for r in recaudos
        ]

    # Integración Fase 4: Paginación
    # @cache_manager.cached('recaudos:list_paginated', level=1, ttl=300) # Comentado si no se quiere cachear inmediato por alta volatilidad, o usar TTL corto
    def listar_recaudos_paginado(
        self,
        page: int = 1,
        page_size: int = 25,
        estado: Optional[str] = None,
        fecha_desde: Optional[str] = None,
        fecha_hasta: Optional[str] = None,
        busqueda: Optional[str] = None,
    ):
        """
        Lista recaudos con paginación y filtros complejos (SQL).
        Optimiza la carga evitando traer toda la base de datos.
        """
        from src.dominio.modelos.pagination import PaginatedResult, PaginationParams

        params = PaginationParams(page=page, page_size=page_size)

        placeholder = self.db.get_placeholder()

        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)

            # Base query
            base_from = """
                FROM RECAUDOS r
                JOIN CONTRATOS_ARRENDAMIENTOS ca ON r.ID_CONTRATO_A = ca.ID_CONTRATO_A
                JOIN PROPIEDADES p ON ca.ID_PROPIEDAD = p.ID_PROPIEDAD
            """

            conditions = []
            query_params = []

            if estado and estado != "Todos":
                conditions.append(f"r.ESTADO_RECAUDO = {placeholder}")
                query_params.append(estado)

            if fecha_desde:
                conditions.append(f"r.FECHA_PAGO >= {placeholder}")
                query_params.append(fecha_desde)

            if fecha_hasta:
                conditions.append(f"r.FECHA_PAGO <= {placeholder}")
                query_params.append(fecha_hasta)

            if busqueda:
                # Buscamos por referencia bancaria, id contrato, o dirección propiedad
                conditions.append(
                    f"""(
                    r.REFERENCIA_BANCARIA LIKE {placeholder} OR
                    p.DIRECCION_PROPIEDAD LIKE {placeholder} OR
                    CAST(r.ID_RECAUDO AS TEXT) LIKE {placeholder}
                )"""
                )
                term = f"%{busqueda}%"
                query_params.extend([term, term, term])

            where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""

            # Count
            count_query = f"SELECT COUNT(*) AS TOTAL {base_from} {where_clause}"
            cursor.execute(count_query, query_params)
            total = cursor.fetchone()["TOTAL"]

            # Data
            data_query = f"""
                SELECT 
                    r.ID_RECAUDO,
                    r.FECHA_PAGO,
                    r.ESTADO_RECAUDO,
                    r.VALOR_TOTAL,
                    r.METODO_PAGO,
                    p.DIRECCION_PROPIEDAD
                {base_from}
                {where_clause}
                ORDER BY r.FECHA_PAGO DESC, r.ID_RECAUDO DESC
                LIMIT {placeholder} OFFSET {placeholder}
            """

            cursor.execute(data_query, query_params + [params.page_size, params.offset])

            items = [
                {
                    "id": row["ID_RECAUDO"],
                    "fecha": row["FECHA_PAGO"],
                    "estado": row["ESTADO_RECAUDO"],
                    "valor": row["VALOR_TOTAL"],
                    "metodo": row["METODO_PAGO"],
                    "contrato": row[
                        "DIRECCION_PROPIEDAD"
                    ],  # Mapeamos dirección como 'contrato' para compatibilidad UI
                }
                for row in cursor.fetchall()
            ]

            return PaginatedResult(
                items=items, total=total, page=params.page, page_size=params.page_size
            )

    def obtener_detalle_recaudo_ui(self, id_recaudo: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene detalles completos de un recaudo para mostrar en la UI.
        Incluye información del pago, contrato, propiedad y conceptos detallados.

        Args:
            id_recaudo: ID del recaudo a consultar

        Returns:
            Diccionario con información completa del recaudo, o None si no existe
        """
        # Obtener el recaudo
        recaudo = self.repo_recaudo.obtener_por_id(id_recaudo)
        if not recaudo:
            return None

        # Obtener información del contrato de arrendamiento
        contrato = self.repo_arriendo.obtener_por_id(recaudo.id_contrato_a)
        if not contrato:
            return None

        # Obtener información de la propiedad
        from src.infraestructura.persistencia.repositorio_propiedad_sqlite import (
            RepositorioPropiedadSQLite,
        )

        repo_propiedad = RepositorioPropiedadSQLite(self.db)
        propiedad = repo_propiedad.obtener_por_id(contrato.id_propiedad)

        # Obtener conceptos del recaudo
        conceptos = self.repo_recaudo.obtener_conceptos_por_recaudo(id_recaudo)

        # Construir la información detallada
        return {
            "id_recaudo": recaudo.id_recaudo,
            "fecha_pago": recaudo.fecha_pago,
            "valor_total": recaudo.valor_total,
            "metodo_pago": recaudo.metodo_pago,
            "referencia_bancaria": recaudo.referencia_bancaria or "N/A",
            "estado_recaudo": recaudo.estado_recaudo,
            "observaciones": recaudo.observaciones or "Sin observaciones",
            # Información del contrato
            "id_contrato_a": recaudo.id_contrato_a,
            "direccion_propiedad": propiedad.direccion_propiedad if propiedad else "N/A",
            "id_propiedad": contrato.id_propiedad,
            # Conceptos del pago
            "conceptos": [
                {"tipo_concepto": c.tipo_concepto, "periodo": c.periodo, "valor": c.valor}
                for c in conceptos
            ],
            # Auditoría
            "created_at": recaudo.created_at,
            "created_by": recaudo.created_by or "Sistema",
            "updated_at": recaudo.updated_at,
            "updated_by": recaudo.updated_by,
        }

    def aprobar_recaudo(self, id_recaudo: int, usuario_sistema: str) -> None:
        """
        Aprueba un recaudo pendiente (cambio a 'Aplicado').

        Args:
            id_recaudo: ID del recaudo
            usuario_sistema: Usuario que aprueba
        """
        recaudo = self.repo_recaudo.obtener_por_id(id_recaudo)
        if not recaudo:
            raise ValueError(f"Recaudo {id_recaudo} no encontrado")

        if recaudo.estado_recaudo != "Pendiente":
            raise ValueError(
                f"Solo se pueden aprobar recaudos en estado Pendiente (Estado actual: {recaudo.estado_recaudo})"
            )

        self.repo_recaudo.cambiar_estado(id_recaudo, "Aplicado", usuario_sistema)

    def reversar_recaudo(self, id_recaudo: int, usuario_sistema: str) -> None:
        """
        Reversa un recaudo pendiente (cambio a 'Reversado').

        Args:
            id_recaudo: ID del recaudo
            usuario_sistema: Usuario que reversa
        """
        recaudo = self.repo_recaudo.obtener_por_id(id_recaudo)
        if not recaudo:
            raise ValueError(f"Recaudo {id_recaudo} no encontrado")

        if recaudo.estado_recaudo != "Pendiente":
            raise ValueError(
                f"Solo se pueden reversar recaudos en estado Pendiente (Estado actual: {recaudo.estado_recaudo})"
            )

        self.repo_recaudo.cambiar_estado(id_recaudo, "Reversado", usuario_sistema)

    def listar_liquidaciones_pendientes(self) -> List[Liquidacion]:
        """
        Lista todas las liquidaciones en estado 'Aprobada' que esperan pago.
        Útil para el dashboard de Tesorería.
        """
        query = """
        SELECT * FROM LIQUIDACIONES 
        WHERE ESTADO_LIQUIDACION = 'Aprobada'
        ORDER BY PERIODO DESC
        """
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            cursor.execute(query)

            return [self.repo_liquidacion._row_to_entity(row) for row in cursor.fetchall()]

    # Integración Fase 4: Paginación
    @cache_manager.cached("liquidaciones:list_paginated", level=1, ttl=300)
    def listar_liquidaciones_paginado(
        self,
        page: int = 1,
        page_size: int = 25,
        estado: Optional[str] = None,
        periodo: Optional[str] = None,
        busqueda: Optional[str] = None,
    ):
        """
        Lista liquidaciones con paginación y filtros complejos.
        """
        from src.dominio.modelos.pagination import PaginatedResult, PaginationParams

        params = PaginationParams(page=page, page_size=page_size)

        placeholder = self.db.get_placeholder()

        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)

            # Base query
            base_from = """
                FROM LIQUIDACIONES l
                JOIN CONTRATOS_MANDATOS cm ON l.ID_CONTRATO_M = cm.ID_CONTRATO_M
                JOIN PROPIEDADES p ON cm.ID_PROPIEDAD = p.ID_PROPIEDAD
                JOIN PROPIETARIOS prop ON cm.ID_PROPIETARIO = prop.ID_PROPIETARIO
                JOIN PERSONAS per ON prop.ID_PERSONA = per.ID_PERSONA
            """

            conditions = []
            query_params = []

            if estado and estado != "Todos":
                conditions.append(f"l.ESTADO_LIQUIDACION = {placeholder}")
                query_params.append(estado)

            if periodo:
                conditions.append(f"l.PERIODO LIKE {placeholder}")
                query_params.append(f"%{periodo}%")

            if busqueda:
                conditions.append(
                    f"""(
                    p.DIRECCION_PROPIEDAD LIKE {placeholder} OR
                    per.NOMBRE_COMPLETO LIKE {placeholder} OR
                    per.NUMERO_DOCUMENTO LIKE {placeholder} OR
                    CAST(l.ID_CONTRATO_M AS TEXT) LIKE {placeholder}
                )"""
                )
                term = f"%{busqueda}%"
                query_params.extend([term, term, term, term])

            where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""

            # Count
            count_query = f"SELECT COUNT(*) AS TOTAL {base_from} {where_clause}"
            cursor.execute(count_query, query_params)
            total = cursor.fetchone()["TOTAL"]

            # Data
            # Calculamos neto en SQL para eficiencia si es posible, o mantenemos lógica simple
            data_query = f"""
                SELECT 
                    l.ID_LIQUIDACION,
                    l.PERIODO,
                    l.ESTADO_LIQUIDACION,
                    l.CANON_BRUTO,
                    l.OTROS_INGRESOS,
                    l.COMISION_MONTO,
                    l.IVA_COMISION,
                    l.IMPUESTO_4X1000,
                    l.GASTOS_ADMINISTRACION,
                    l.GASTOS_SERVICIOS,
                    l.GASTOS_REPARACIONES,
                    l.OTROS_EGRESOS,
                    p.DIRECCION_PROPIEDAD
                {base_from}
                {where_clause}
                ORDER BY l.PERIODO DESC, l.ID_LIQUIDACION DESC
                LIMIT {placeholder} OFFSET {placeholder}
            """

            cursor.execute(data_query, query_params + [params.page_size, params.offset])

            items = []
            for row in cursor.fetchall():
                # Calcular neto
                ingresos = row["CANON_BRUTO"] + row["OTROS_INGRESOS"]
                # suma de gastos/comisiones
                egresos = (
                    row["COMISION_MONTO"]
                    + row["IVA_COMISION"]
                    + row["IMPUESTO_4X1000"]
                    + row["GASTOS_ADMINISTRACION"]
                    + row["GASTOS_SERVICIOS"]
                    + row["GASTOS_REPARACIONES"]
                    + row["OTROS_EGRESOS"]
                )
                neto = ingresos - egresos

                items.append(
                    {
                        "id": row["ID_LIQUIDACION"],
                        "periodo": row["PERIODO"],
                        "estado": row["ESTADO_LIQUIDACION"],
                        "canon": row["CANON_BRUTO"],
                        "neto": neto,
                        "contrato": row["DIRECCION_PROPIEDAD"],  # Dirección propiedad
                    }
                )

            return PaginatedResult(
                items=items, total=total, page=params.page, page_size=params.page_size
            )

    def obtener_detalle_liquidacion_ui(self, id_liquidacion: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene los detalles completos de una liquidación para la UI.

        Args:
            id_liquidacion: ID de la liquidación

        Returns:
            Diccionario con datos completos o None
        """
        placeholder = self.db.get_placeholder()
        query = f"""
        SELECT 
            l.ID_LIQUIDACION,
            l.PERIODO,
            l.FECHA_GENERACION,
            l.CANON_BRUTO,
            l.OTROS_INGRESOS,
            l.COMISION_PORCENTAJE,
            l.COMISION_MONTO,
            l.IVA_COMISION,
            l.IMPUESTO_4X1000,
            l.GASTOS_ADMINISTRACION,
            l.GASTOS_SERVICIOS,
            l.GASTOS_REPARACIONES,
            l.OTROS_EGRESOS,
            l.ESTADO_LIQUIDACION,
            l.OBSERVACIONES,
            l.CREATED_AT,
            l.CREATED_BY,
            l.FECHA_PAGO,
            l.METODO_PAGO,
            l.REFERENCIA_PAGO,
            l.ID_CONTRATO_M,
            p.DIRECCION_PROPIEDAD,
            p.MATRICULA_INMOBILIARIA,
            per.NOMBRE_COMPLETO as PROPIETARIO,
            per.NUMERO_DOCUMENTO
        FROM LIQUIDACIONES l
        JOIN CONTRATOS_MANDATOS cm ON l.ID_CONTRATO_M = cm.ID_CONTRATO_M
        JOIN PROPIEDADES p ON cm.ID_PROPIEDAD = p.ID_PROPIEDAD
        JOIN PROPIETARIOS prop ON cm.ID_PROPIETARIO = prop.ID_PROPIETARIO
        JOIN PERSONAS per ON prop.ID_PERSONA = per.ID_PERSONA
        WHERE l.ID_LIQUIDACION = {placeholder}
        """

        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            cursor.execute(query, (id_liquidacion,))
            row = cursor.fetchone()

            if not row:
                return None

            # Calcular totales al vuelo para visualización
            total_ingresos = row["CANON_BRUTO"] + row["OTROS_INGRESOS"]
            total_egresos = (
                row["COMISION_MONTO"]
                + row["IVA_COMISION"]
                + row["IMPUESTO_4X1000"]
                + row["GASTOS_ADMINISTRACION"]
                + row["GASTOS_SERVICIOS"]
                + row["GASTOS_REPARACIONES"]
                + row["OTROS_EGRESOS"]
            )
            neto = total_ingresos - total_egresos

            return {
                "id": row["ID_LIQUIDACION"],
                "periodo": row["PERIODO"],
                "fecha_generacion": row["FECHA_GENERACION"],
                "estado": row["ESTADO_LIQUIDACION"],
                "observaciones": row["OBSERVACIONES"] or "Sin observaciones",
                # Contexto
                "id_contrato": row["ID_CONTRATO_M"],
                "propiedad": row["DIRECCION_PROPIEDAD"],
                "matricula": row["MATRICULA_INMOBILIARIA"],
                "propietario": row["PROPIETARIO"],
                "documento": row["NUMERO_DOCUMENTO"],
                # Financiero
                "canon": row["CANON_BRUTO"],
                "otros_ingresos": row["OTROS_INGRESOS"],
                "total_ingresos": total_ingresos,
                "comision_pct": row["COMISION_PORCENTAJE"],
                "comision_pct_view": row["COMISION_PORCENTAJE"] / 100,
                "comision_monto": row["COMISION_MONTO"],
                "iva_comision": row["IVA_COMISION"],
                "impuesto_4x1000": row["IMPUESTO_4X1000"],
                "gastos_admin": row["GASTOS_ADMINISTRACION"],
                "gastos_serv": row["GASTOS_SERVICIOS"],
                "gastos_rep": row["GASTOS_REPARACIONES"],
                "otros_egr": row["OTROS_EGRESOS"],
                "total_egresos": total_egresos,
                "neto_pagar": neto,
                # Pago
                "fecha_pago": row["FECHA_PAGO"],
                "metodo_pago": row["METODO_PAGO"],
                "referencia_pago": row["REFERENCIA_PAGO"],
                # Auditoria
                "created_at": row["CREATED_AT"],
                "created_by": row["CREATED_BY"],
            }

    def obtener_datos_liquidacion_para_pdf(self, id_liquidacion: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene los datos completos de una liquidación específicamente formateados para generación de PDF.
        Similar a obtener_detalle_liquidacion_ui pero con información adicional requerida por el PDF.

        Args:
            id_liquidacion: ID de la liquidación

        Returns:
            Diccionario con estructura completa para PDF o None si no existe
        """
        placeholder = self.db.get_placeholder()
        query = f"""
        SELECT 
            l.ID_LIQUIDACION,
            l.PERIODO,
            l.FECHA_GENERACION,
            l.CANON_BRUTO,
            l.OTROS_INGRESOS,
            l.COMISION_PORCENTAJE,
            l.COMISION_MONTO,
            l.IVA_COMISION,
            l.IMPUESTO_4X1000,
            l.GASTOS_ADMINISTRACION,
            l.GASTOS_SERVICIOS,
            l.GASTOS_REPARACIONES,
            l.OTROS_EGRESOS,
            l.ESTADO_LIQUIDACION,
            l.OBSERVACIONES,
            l.CREATED_AT,
            l.CREATED_BY,
            l.FECHA_PAGO,
            l.METODO_PAGO,
            l.REFERENCIA_PAGO,
            l.ID_CONTRATO_M,
            p.DIRECCION_PROPIEDAD,
            p.MATRICULA_INMOBILIARIA,
            per.NOMBRE_COMPLETO as PROPIETARIO,
            per.NUMERO_DOCUMENTO,
            prop.BANCO_PROPIETARIO,
            prop.NUMERO_CUENTA_PROPIETARIO,
            prop.TIPO_CUENTA
        FROM LIQUIDACIONES l
        JOIN CONTRATOS_MANDATOS cm ON l.ID_CONTRATO_M = cm.ID_CONTRATO_M
        JOIN PROPIEDADES p ON cm.ID_PROPIEDAD = p.ID_PROPIEDAD
        JOIN PROPIETARIOS prop ON cm.ID_PROPIETARIO = prop.ID_PROPIETARIO
        JOIN PERSONAS per ON prop.ID_PERSONA = per.ID_PERSONA
        WHERE l.ID_LIQUIDACION = {placeholder}
        """

        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            cursor.execute(query, (id_liquidacion,))
            row = cursor.fetchone()

            if not row:
                return None

            # Calcular totales
            total_ingresos = row["CANON_BRUTO"] + row["OTROS_INGRESOS"]
            total_egresos = (
                row["COMISION_MONTO"]
                + row["IVA_COMISION"]
                + row["IMPUESTO_4X1000"]
                + row["GASTOS_ADMINISTRACION"]
                + row["GASTOS_SERVICIOS"]
                + row["GASTOS_REPARACIONES"]
                + row["OTROS_EGRESOS"]
            )
            neto = total_ingresos - total_egresos

            # Estructura de datos compatible con ServicioDocumentosPDF.generar_estado_cuenta
            return {
                "id": row["ID_LIQUIDACION"],
                "periodo": row["PERIODO"],
                "fecha_generacion": row["FECHA_GENERACION"],
                "estado": row["ESTADO_LIQUIDACION"],
                # Información del propietario (formato completo para PDF)
                "propietario": row["PROPIETARIO"],
                "documento": row["NUMERO_DOCUMENTO"],
                "telefono": "N/A",  # Not in PERSONAS table
                "email": "N/A",  # Not in PERSONAS table
                "direccion_propietario": "N/A",  # Not in PERSONAS table
                # Información bancaria para transferencia
                "cuenta_bancaria": row["NUMERO_CUENTA_PROPIETARIO"] or "No registrada",
                "tipo_cuenta": row["TIPO_CUENTA"] or "N/A",
                "banco": row["BANCO_PROPIETARIO"] or "N/A",
                # Información de la propiedad
                "propiedad": row["DIRECCION_PROPIEDAD"],
                "matricula": row["MATRICULA_INMOBILIARIA"] or "Sin matrícula",
                # Ingresos
                "canon": row["CANON_BRUTO"],
                "otros_ingresos": row["OTROS_INGRESOS"],
                "total_ingresos": total_ingresos,
                # Egresos detallados
                "comision_pct": row["COMISION_PORCENTAJE"],  # Base 10000 (ejemplo: 1000 = 10%)
                "comision_monto": row["COMISION_MONTO"],
                "iva_comision": row["IVA_COMISION"],
                "impuesto_4x1000": row["IMPUESTO_4X1000"],
                "gastos_admin": row["GASTOS_ADMINISTRACION"],
                "gastos_serv": row["GASTOS_SERVICIOS"],
                "gastos_rep": row["GASTOS_REPARACIONES"],
                "otros_egr": row["OTROS_EGRESOS"],
                "total_egresos": total_egresos,
                # Neto a pagar
                "neto_pagar": neto,
                # Información de pago (si está pagada)
                "fecha_pago": row["FECHA_PAGO"] or "Pendiente",
                "metodo_pago": row["METODO_PAGO"] or "N/A",
                "referencia_pago": row["REFERENCIA_PAGO"] or "N/A",
                # Observaciones
                "observaciones": row["OBSERVACIONES"] or "Sin observaciones",
                # Auditoría
                "created_at": row["CREATED_AT"],
                "created_by": row["CREATED_BY"] or "Sistema",
            }

    def obtener_datos_consolidados_para_pdf(
        self, propietario_id: int, periodo: str
    ) -> Optional[Dict[str, Any]]:
        """
        Obtiene datos consolidados de todas las liquidaciones de un propietario en un período.
        Usado para generar PDFs agrupados (Vista Por Propietario).

        Args:
            propietario_id: ID del propietario
            periodo: Período en formato YYYY-MM

        Returns:
            Diccionario con datos consolidados o None si no hay liquidaciones
        """
        placeholder = self.db.get_placeholder()

        # Query para obtener todas las liquidaciones del propietario en el período
        query = f"""
        SELECT 
            l.ID_LIQUIDACION,
            l.PERIODO,
            l.FECHA_GENERACION,
            l.CANON_BRUTO,
            l.OTROS_INGRESOS,
            l.COMISION_PORCENTAJE,
            l.COMISION_MONTO,
            l.IVA_COMISION,
            l.IMPUESTO_4X1000,
            l.GASTOS_ADMINISTRACION,
            l.GASTOS_SERVICIOS,
            l.GASTOS_REPARACIONES,
            l.OTROS_EGRESOS,
            l.ESTADO_LIQUIDACION,
            p.DIRECCION_PROPIEDAD,
            p.MATRICULA_INMOBILIARIA,
            per.NOMBRE_COMPLETO as PROPIETARIO,
            per.NUMERO_DOCUMENTO,
            prop.BANCO_PROPIETARIO,
            prop.NUMERO_CUENTA_PROPIETARIO,
            prop.TIPO_CUENTA
        FROM LIQUIDACIONES l
        JOIN CONTRATOS_MANDATOS cm ON l.ID_CONTRATO_M = cm.ID_CONTRATO_M
        JOIN PROPIEDADES p ON cm.ID_PROPIEDAD = p.ID_PROPIEDAD
        JOIN PROPIETARIOS prop ON cm.ID_PROPIETARIO = prop.ID_PROPIETARIO
        JOIN PERSONAS per ON prop.ID_PERSONA = per.ID_PERSONA
        WHERE prop.ID_PROPIETARIO = {placeholder} 
          AND l.PERIODO = {placeholder}
        ORDER BY p.DIRECCION_PROPIEDAD
        """

        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            cursor.execute(query, (propietario_id, periodo))
            rows = cursor.fetchall()

            if not rows:
                return None

            # Procesar primera fila para datos del propietario
            first_row = rows[0]

            # Inicializar acumuladores
            total_canon = 0
            total_otros_ingresos = 0
            total_comision = 0
            total_iva = 0
            total_4x1000 = 0
            total_gastos_admin = 0
            total_gastos_serv = 0
            total_gastos_rep = 0
            total_otros_egr = 0

            # Lista de propiedades con sus liquidaciones
            propiedades = []

            for row in rows:
                # Acumular totales
                canon = row["CANON_BRUTO"]
                otros_ing = row["OTROS_INGRESOS"]
                total_canon += canon
                total_otros_ingresos += otros_ing
                total_comision += row["COMISION_MONTO"]
                total_iva += row["IVA_COMISION"]
                total_4x1000 += row["IMPUESTO_4X1000"]
                total_gastos_admin += row["GASTOS_ADMINISTRACION"]
                total_gastos_serv += row["GASTOS_SERVICIOS"]
                total_gastos_rep += row["GASTOS_REPARACIONES"]
                total_otros_egr += row["OTROS_EGRESOS"]

                # Calcular neto para esta propiedad
                ingresos_prop = canon + otros_ing
                egresos_prop = (
                    row["COMISION_MONTO"]
                    + row["IVA_COMISION"]
                    + row["IMPUESTO_4X1000"]
                    + row["GASTOS_ADMINISTRACION"]
                    + row["GASTOS_SERVICIOS"]
                    + row["GASTOS_REPARACIONES"]
                    + row["OTROS_EGRESOS"]
                )
                neto_prop = ingresos_prop - egresos_prop

                propiedades.append(
                    {
                        "id_liquidacion": row["ID_LIQUIDACION"],
                        "direccion": row["DIRECCION_PROPIEDAD"],
                        "matricula": row["MATRICULA_INMOBILIARIA"] or "Sin matrícula",
                        "estado": row["ESTADO_LIQUIDACION"],
                        "canon": canon,
                        "otros_ingresos": otros_ing,
                        "comision_monto": row["COMISION_MONTO"],
                        "comision_pct": row["COMISION_PORCENTAJE"],
                        "iva_comision": row["IVA_COMISION"],
                        "impuesto_4x1000": row["IMPUESTO_4X1000"],
                        "gastos_admin": row["GASTOS_ADMINISTRACION"],
                        "gastos_serv": row["GASTOS_SERVICIOS"],
                        "gastos_rep": row["GASTOS_REPARACIONES"],
                        "otros_egr": row["OTROS_EGRESOS"],
                        "neto": neto_prop,
                    }
                )

            # Calcular totales consolidados
            total_ingresos = total_canon + total_otros_ingresos
            total_egresos = (
                total_comision
                + total_iva
                + total_4x1000
                + total_gastos_admin
                + total_gastos_serv
                + total_gastos_rep
                + total_otros_egr
            )
            neto_total = total_ingresos - total_egresos

            # Estructura consolidada para PDF
            return {
                "tipo": "consolidado",
                "periodo": periodo,
                "fecha_generacion": first_row["FECHA_GENERACION"],
                "cantidad_propiedades": len(propiedades),
                # Información del propietario
                "propietario": first_row["PROPIETARIO"],
                "documento": first_row["NUMERO_DOCUMENTO"],
                "cuenta_bancaria": first_row["NUMERO_CUENTA_PROPIETARIO"] or "No registrada",
                "tipo_cuenta": first_row["TIPO_CUENTA"] or "N/A",
                "banco": first_row["BANCO_PROPIETARIO"] or "N/A",
                "telefono": "N/A",
                "email": "N/A",
                "direccion_propietario": "N/A",
                # Totales consolidados
                "canon": total_canon,
                "otros_ingresos": total_otros_ingresos,
                "total_ingresos": total_ingresos,
                "comision_monto": total_comision,
                "iva_comision": total_iva,
                "impuesto_4x1000": total_4x1000,
                "gastos_admin": total_gastos_admin,
                "gastos_serv": total_gastos_serv,
                "gastos_rep": total_gastos_rep,
                "otros_egr": total_otros_egr,
                "total_egresos": total_egresos,
                "neto_pagar": neto_total,
                # Detalle por propiedad
                "propiedades": propiedades,
                # Observaciones
                "observaciones": f"Estado de cuenta consolidado - {len(propiedades)} propiedades",
                "created_by": "Sistema",
            }

    def actualizar_liquidacion(
        self, id_liquidacion: int, datos_actualizados: Dict[str, Any], usuario_sistema: str
    ) -> Liquidacion:
        """
        Actualiza una liquidación existente (solo si está en estado 'En Proceso').

        Args:
            id_liquidacion: ID de la liquidación a actualizar
            datos_actualizados: Dict con los campos a actualizar (misma estructura que generar_liquidacion_mensual)
            usuario_sistema: Usuario que realiza la actualización

        Returns:
            Liquidacion actualizada

        Raises:
            ValueError: Si la liquidación no existe, no está En Proceso, o datos inválidos
        """
        # Obtener liquidación actual
        liquidacion = self.repo_liquidacion.obtener_por_id(id_liquidacion)
        if not liquidacion:
            raise ValueError(f"No existe liquidación con ID {id_liquidacion}")

        # Validar que esté en estado editable
        if liquidacion.estado_liquidacion != "En Proceso":
            raise ValueError(
                f"Solo se pueden editar liquidaciones en estado 'En Proceso'. Estado actual: {liquidacion.estado_liquidacion}"
            )

        # Actualizar campos permitidos
        liquidacion.otros_ingresos = datos_actualizados.get(
            "otros_ingresos", liquidacion.otros_ingresos
        )
        liquidacion.gastos_administracion = datos_actualizados.get(
            "gastos_administracion", liquidacion.gastos_administracion
        )
        liquidacion.gastos_servicios = datos_actualizados.get(
            "gastos_servicios", liquidacion.gastos_servicios
        )
        liquidacion.gastos_reparaciones = datos_actualizados.get(
            "gastos_reparaciones", liquidacion.gastos_reparaciones
        )
        liquidacion.otros_egresos = datos_actualizados.get(
            "otros_egresos", liquidacion.otros_egresos
        )
        liquidacion.observaciones = datos_actualizados.get(
            "observaciones", liquidacion.observaciones
        )

        # Nota: No permitimos cambiar periodo ni contrato
        # Recalcular comisión si se proporciona nuevo porcentaje
        if "comision_porcentaje" in datos_actualizados:
            liquidacion.comision_porcentaje = datos_actualizados["comision_porcentaje"]
            liquidacion.comision_monto = int(
                (liquidacion.canon_bruto * liquidacion.comision_porcentaje) / 10000
            )
            liquidacion.iva_comision = int(liquidacion.comision_monto * 0.19)

        # Recalcular 4x1000 si cambiaron ingresos
        total_ingresos_nuevo = liquidacion.canon_bruto + liquidacion.otros_ingresos
        liquidacion.impuesto_4x1000 = int(total_ingresos_nuevo * 0.004)

        # El repositorio llamará a calcular_totales() automáticamente
        self.repo_liquidacion.actualizar(liquidacion, usuario_sistema)

        # Retornar liquidación actualizada
        return self.repo_liquidacion.obtener_por_id(id_liquidacion)

    # =========================================================================
    # GENERACIÓN DE DOCUMENTOS (PDF)
    # =========================================================================

    def generar_comprobante_pago(self, id_recaudo: int) -> str:
        """
        Genera el comprobante de pago en PDF para un recaudo.

        Args:
            id_recaudo: ID del recaudo

        Returns:
            Ruta absoluta del archivo PDF generado
        """
        datos = self.obtener_detalle_recaudo_ui(id_recaudo)
        if not datos:
            raise ValueError(f"Recaudo {id_recaudo} no encontrado")

        return self.pdf_service.generar_comprobante_recaudo(datos)

    def generar_estado_cuenta_pdf(self, id_liquidacion: int) -> str:
        """
        Genera el estado de cuenta en PDF para una liquidación.

        Args:
            id_liquidacion: ID de la liquidación

        Returns:
            Ruta absoluta del archivo PDF generado
        """
        datos = self.obtener_detalle_liquidacion_ui(id_liquidacion)
        if not datos:
            raise ValueError(f"Liquidación {id_liquidacion} no encontrada")

        return self.pdf_service.generar_estado_cuenta(datos)

    # =========================================================================
    # LIQUIDACIONES POR PROPIETARIO (Nuevo requerimiento)
    # =========================================================================

    def generar_liquidacion_propietario(
        self,
        id_propietario: int,
        periodo: str,
        datos_adicionales_por_contrato: Optional[Dict[int, Dict[str, Any]]] = None,
        usuario_sistema: str = "sistema",
    ) -> LiquidacionPropietario:
        """
        Genera la liquid ación consolidada de un propietario para un período.
        Crea UNA liquidación por cada contrato de mandato activo del propietario.

        Args:
            id_propietario: ID del propietario
            periodo: Período en formato YYYY-MM
            datos_adicionales_por_contrato: Dict opcional {id_contrato_m: { 'otros_ingresos': ..., 'gastos_...': ...}}
                Si no se proporciona, se usan valores por defecto (0) para cada contrato
            usuario_sistema: Usuario que genera

        Returns:
            LiquidacionPropietario consolidada con todas las liquidaciones individuales

        Raises:
            ValueError: Si el propietario no tiene contratos activos o ya existe liquidación para el período
        """
        # Obtener todos los contratos de mandato activos del propietario
        contratos_activos = self.repo_mandato.listar_por_propietario_activos(id_propietario)

        if not contratos_activos:
            raise ValueError(
                f"El propietario {id_propietario} no tiene contratos de mandato activos"
            )

        # Verificar que no existan ya liquidaciones para este período
        liquidaciones_existentes = self.repo_liquidacion.listar_por_propietario_y_periodo(
            id_propietario, periodo
        )
        if liquidaciones_existentes:
            raise ValueError(
                f"Ya existen liquidaciones para el propietario {id_propietario} en el período {periodo}"
            )

        # Generar una liquidación por cada contrato
        liquidaciones_generadas = []

        for contrato in contratos_activos:
            # Obtener datos adicionales para este contrato si existen
            datos_contrato = (
                datos_adicionales_por_contrato.get(contrato.id_contrato_m, {})
                if datos_adicionales_por_contrato
                else {}
            )

            # Generar liquidación individual usando el método existente
            try:
                liquidacion = self.generar_liquidacion_mensual(
                    id_contrato_m=contrato.id_contrato_m,
                    periodo=periodo,
                    datos_adicionales=datos_contrato,
                    usuario_sistema=usuario_sistema,
                )
                liquidaciones_generadas.append(liquidacion)
            except Exception as e:
                # Si falla alguna, hacer rollback de las ya generadas
                # TODO: Implementar rollback transaccional
                raise ValueError(
                    f"Error generando liquidación para contrato {contrato.id_contrato_m}: {str(e)}"
                )

        # Obtener datos del propietario con JOIN a PERSONAS
        placeholder = self.db.get_placeholder()
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            cursor.execute(
                f"""
                SELECT p.NOMBRE_COMPLETO, p.NUMERO_DOCUMENTO
                FROM PROPIETARIOS prop
                JOIN PERSONAS p ON prop.ID_PERSONA = p.ID_PERSONA
                WHERE prop.ID_PROPIETARIO = {placeholder}
            """,
                (id_propietario,),
            )
            prop_row = cursor.fetchone()

        if not prop_row:
            raise ValueError(f"Propietario con ID {id_propietario} no encontrado.")

        # Crear liquidación consolidada
        liquidacion_consolidada = LiquidacionPropietario(
            id_propietario=id_propietario,
            nombre_propietario=prop_row["NOMBRE_COMPLETO"],
            documento_propietario=prop_row["NUMERO_DOCUMENTO"],
            periodo=periodo,
            liquidaciones_contratos=liquidaciones_generadas,
        )

        # Consolidar totales
        liquidacion_consolidada.consolidar()

        return liquidacion_consolidada

    def generar_liquidaciones_masivas(
        self,
        periodo: str,
        filtro_asesor: Optional[int] = None,
        filtro_propietarios: Optional[List[int]] = None,
        usuario_sistema: str = "sistema",
    ) -> List[LiquidacionPropietario]:
        """
        Genera liquidaciones consolidadas para múltiples propietarios.
        Útil para procesar fin de mes masivamente.

        Args:
            periodo: Período en formato YYYY-MM
            filtro_asesor: Opcional, ID del asesor (genera solo para propietarios con contratos de ese asesor)
            filtro_propietarios: Opcional, lista de IDs de propietarios específicos
            usuario_sistema: Usuario que genera

        Returns:
            Lista de LiquidacionPropietario generadas
        """
        # Determinar qué propietarios procesar
        if filtro_propietarios:
            ids_propietarios = filtro_propietarios
        else:
            # Obtener todos los propietarios con contratos activos
            query = """
                SELECT DISTINCT cm.ID_PROPIETARIO
                FROM CONTRATOS_MANDATOS cm
                WHERE cm.ESTADO_CONTRATO_M = 'Activo'
            """

            placeholder = self.db.get_placeholder()
            if filtro_asesor:
                query += f" AND cm.ID_ASESOR = {placeholder}"
                params = (filtro_asesor,)
            else:
                params = ()

            with self.db.obtener_conexion() as conn:
                cursor = self.db.get_dict_cursor(conn)
                cursor.execute(query, params)
                ids_propietarios = [row["id_propietario"] for row in cursor.fetchall()]

        # Generar liquidación para cada propietario
        liquidaciones_generadas = []
        errores = []

        for id_prop in ids_propietarios:
            try:
                liq_prop = self.generar_liquidacion_propietario(
                    id_prop, periodo, usuario_sistema=usuario_sistema
                )
                liquidaciones_generadas.append(liq_prop)
            except Exception as e:
                # Log error pero continuar con los demás
                errores.append({"id_propietario": id_prop, "error": str(e)})
                pass  # print(f"Error generando liquidación para propietario {id_prop}: {e}") [OpSec Removed]

        if errores:
            pass  # print(f"Se generaron {len(liquidaciones_generadas)} liquidaciones. {len(errores)} fallaron.") [OpSec Removed]

        return liquidaciones_generadas

    def listar_liquidaciones_propietarios_paginado(
        self,
        page: int = 1,
        page_size: int = 25,
        estado: Optional[str] = None,
        periodo: Optional[str] = None,
        busqueda: Optional[str] = None,
    ):
        """
        Lista liquidaciones agrupadas por propietario con paginación.
        Reemplaza el método anterior `listar_liquidaciones_paginado` para UI.

        Returns:
            PaginatedResult con liquidaciones consolidadas por propietario
        """
        return self.repo_liquidacion.listar_agrupadas_por_propietario_paginado(
            page=page, page_size=page_size, estado=estado, periodo=periodo, busqueda=busqueda
        )

    def obtener_detalle_liquidacion_propietario_ui(
        self, id_propietario: int, periodo: str
    ) -> Optional[Dict[str, Any]]:
        """
        Obtiene el detalle completo de la liquidación consolidada de un propietario para la UI.

        Args:
            id_propietario: ID del propietario
            periodo: Período en formato YYYY-MM

        Returns:
            Dict con información consolidada y detalle de cada contrato, o None si no existe
        """
        # Obtener todas las liquidaciones del propietario para el período
        liquidaciones = self.repo_liquidacion.listar_por_propietario_y_periodo(
            id_propietario, periodo
        )

        if not liquidaciones:
            return None

        # Obtener info del propietario con JOIN a PERSONAS
        placeholder = self.db.get_placeholder()
        with self.db.obtener_conexion() as conn:
            cursor = self.db.get_dict_cursor(conn)
            cursor.execute(
                f"""
                SELECT p.NOMBRE_COMPLETO, p.NUMERO_DOCUMENTO
                FROM PROPIETARIOS prop
                JOIN PERSONAS p ON prop.ID_PERSONA = p.ID_PERSONA
                WHERE prop.ID_PROPIETARIO = {placeholder}
            """,
                (id_propietario,),
            )
            prop_row = cursor.fetchone()

        nombre_propietario = prop_row["nombre_completo"] if prop_row else "Propietario Desconocido"
        documento_propietario = prop_row["numero_documento"] if prop_row else "N/A"

        # Crear liquidación consolidada
        liq_consolidada = LiquidacionPropietario(
            id_propietario=id_propietario,
            nombre_propietario=nombre_propietario,
            documento_propietario=documento_propietario,
            periodo=periodo,
            liquidaciones_contratos=liquidaciones,
        )
        liq_consolidada.consolidar()

        # Obtener detalles de cada contrato para mostrar en UI
        detalles_contratos = []
        for liq in liquidaciones:
            # Obtener info del contrato
            contrato = self.repo_mandato.obtener_por_id(liq.id_contrato_m)
            if contrato:
                from src.infraestructura.persistencia.repositorio_propiedad_sqlite import (
                    RepositorioPropiedadSQLite,
                )

                repo_prop = RepositorioPropiedadSQLite(self.db)
                propiedad = repo_prop.obtener_por_id(contrato.id_propiedad)

                detalles_contratos.append(
                    {
                        "id_liquidacion": liq.id_liquidacion,
                        "id_contrato_m": liq.id_contrato_m,
                        "direccion": propiedad.direccion_propiedad if propiedad else "N/A",
                        "matricula": propiedad.matricula_inmobiliaria if propiedad else "N/A",
                        "canon_bruto": liq.canon_bruto,
                        "otros_ingresos": liq.otros_ingresos,
                        "total_ingresos": liq.total_ingresos,
                        "comision_monto": liq.comision_monto,
                        "iva_comision": liq.iva_comision,
                        "impuesto_4x1000": liq.impuesto_4x1000,
                        "gastos_administracion": liq.gastos_administracion,
                        "gastos_servicios": liq.gastos_servicios,
                        "gastos_reparaciones": liq.gastos_reparaciones,
                        "otros_egresos": liq.otros_egresos,
                        "total_egresos": liq.total_egresos,
                        "neto_a_pagar": liq.neto_a_pagar,
                        "estado": liq.estado_liquidacion,
                        "observaciones": liq.observaciones,
                    }
                )

        # Retornar estructura consolidada para UI
        return {**liq_consolidada.obtener_resumen_dict(), "contratos": detalles_contratos}

    def aprobar_liquidacion_propietario(
        self, id_propietario: int, periodo: str, usuario_sistema: str
    ) -> int:
        """
        Aprueba TODAS las liquidaciones de un propietario para un período.
        Wrapper del método del repositorio.

        Args:
            id_propietario: ID del propietario
            periodo: Período en formato YYYY-MM
            usuario_sistema: Usuario que aprueba

        Returns:
            Cantidad de liquidaciones aprobadas
        """
        affected = self.repo_liquidacion.aprobar_por_propietario_y_periodo(
            id_propietario, periodo, usuario_sistema
        )

        # Invalidar caché
        cache_manager.invalidate("liquidaciones:list_paginated")

        return affected

    def marcar_liquidacion_propietario_pagada(
        self,
        id_propietario: int,
        periodo: str,
        fecha_pago: str,
        metodo_pago: str,
        referencia_pago: str,
        usuario_sistema: str,
    ) -> int:
        """
        Marca como pagadas TODAS las liquidaciones de un propietario para un período.
        Wrapper del método del repositorio.

        Args:
            id_propietario: ID del propietario
            periodo: Período en formato YYYY-MM
            fecha_pago: Fecha del pago
            metodo_pago: Método de pago
            referencia_pago: Referencia bancaria
            usuario_sistema: Usuario que registra

        Returns:
            Cantidad de liquidaciones marcadas como pagadas
        """
        affected = self.repo_liquidacion.marcar_como_pagadas_por_propietario(
            id_propietario, periodo, fecha_pago, metodo_pago, referencia_pago, usuario_sistema
        )

        # Invalidar caché
        cache_manager.invalidate("liquidaciones:list_paginated")

        return affected
