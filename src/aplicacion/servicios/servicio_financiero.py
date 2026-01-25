"""
Servicio de Aplicación: Gestión Financiera
Coordina la lógica de negocio para recaudos y liquidaciones.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from dateutil.relativedelta import relativedelta

from src.dominio.entidades.liquidacion import Liquidacion
from src.dominio.entidades.recaudo import Recaudo
from src.dominio.entidades.recaudo_concepto import RecaudoConcepto

from src.dominio.interfaces.repositorio_recaudo import IRepositorioRecaudo
from src.dominio.interfaces.repositorio_liquidacion import IRepositorioLiquidacion
from src.dominio.interfaces.repositorio_propiedad import IRepositorioPropiedad
# Interfaces para contratos se inyectarán después si es posible, por ahora usamos base
# Pero para ser estrictos con Fase 3, el servicio financiero debería recibir interfaces.

from src.infraestructura.cache.cache_manager import cache_manager
from src.infraestructura.servicios.servicio_documentos_pdf import ServicioDocumentosPDF


class ServicioFinanciero:
    """Servicio para gestión de recaudos y liquidaciones"""

    def __init__(
        self,
        repo_recaudo: IRepositorioRecaudo,
        repo_liquidacion: IRepositorioLiquidacion,
        repo_propiedad: IRepositorioPropiedad,
        repo_arriendo: Any, # Podría ser IRepositorioContratoArriendo
        repo_mandato: Any,  # Podría ser IRepositorioContratoMandato
        pdf_service: ServicioDocumentosPDF
    ):
        self.repo_recaudo = repo_recaudo
        self.repo_liquidacion = repo_liquidacion
        self.repo_propiedad = repo_propiedad
        self.repo_arriendo = repo_arriendo
        self.repo_mandato = repo_mandato
        self.pdf_service = pdf_service

    def registrar_recaudo(
        self, datos: Dict[str, Any], conceptos_data: List[Dict[str, Any]], usuario_sistema: str
    ) -> Recaudo:
        """Registra un nuevo pago del inquilino."""
        recaudo = Recaudo(
            id_contrato_a=datos["id_contrato_a"],
            fecha_pago=datos["fecha_pago"],
            valor_total=datos["valor_total"],
            metodo_pago=datos["metodo_pago"],
            referencia_bancaria=datos.get("referencia_bancaria"),
            observaciones=datos.get("observaciones"),
        )

        conceptos = [
            RecaudoConcepto(
                tipo_concepto=c["tipo_concepto"], periodo=c["periodo"], valor=c["valor"]
            )
            for c in conceptos_data
        ]

        return self.repo_recaudo.crear(recaudo, conceptos, usuario_sistema)

    def calcular_mora(
        self, id_contrato_a: int, fecha_limite: str, fecha_pago: str, valor_canon: int
    ) -> int:
        """Calcula el valor de mora."""
        fecha_lim = datetime.fromisoformat(fecha_limite)
        fecha_pag = datetime.fromisoformat(fecha_pago)
        dias_mora = (fecha_pag - fecha_lim).days
        if dias_mora <= 0: return 0
        tasa_diaria = 0.06 / 365
        return int(valor_canon * tasa_diaria * dias_mora)

    def aplicar_pago_anticipado(
        self, id_contrato_a: int, meses_adelantados: int, valor_canon_mensual: int,
        fecha_pago: str, metodo_pago: str, referencia_bancaria: Optional[str],
        usuario_sistema: str
    ) -> Recaudo:
        """Registra un pago anticipado."""
        valor_total = valor_canon_mensual * meses_adelantados
        conceptos_data = []
        fecha_base = datetime.fromisoformat(fecha_pago)

        for i in range(meses_adelantados):
            periodo = (fecha_base + relativedelta(months=i)).strftime("%Y-%m")
            conceptos_data.append({"tipo_concepto": "Canon", "periodo": periodo, "valor": valor_canon_mensual})

        return self.registrar_recaudo(
            datos={
                "id_contrato_a": id_contrato_a, "fecha_pago": fecha_pago,
                "valor_total": valor_total, "metodo_pago": metodo_pago,
                "referencia_bancaria": referencia_bancaria,
                "observaciones": f"Pago anticipado de {meses_adelantados} meses",
            },
            conceptos_data=conceptos_data,
            usuario_sistema=usuario_sistema,
        )

    def generar_liquidacion_mensual(
        self, id_contrato_m: int, periodo: str, datos_adicionales: Dict[str, Any],
        usuario_sistema: str
    ) -> Liquidacion:
        """Genera la liquidación mensual."""
        contrato = self.repo_mandato.obtener_por_id(id_contrato_m)
        if not contrato:
            raise ValueError(f"No existe el contrato de mandato con ID {id_contrato_m}")

        existente = self.repo_liquidacion.obtener_por_contrato_y_periodo(id_contrato_m, periodo)
        if existente:
            raise ValueError(f"Ya existe una liquidación para el período {periodo}")

        canon_bruto = contrato.canon_mandato
        otros_ingresos = datos_adicionales.get("otros_ingresos", 0)
        total_ingresos = canon_bruto + otros_ingresos

        comision_porcentaje = datos_adicionales.get("comision_porcentaje", contrato.comision_porcentaje_contrato_m)
        comision_monto = int((canon_bruto * comision_porcentaje) / 10000)
        iva_comision = int(comision_monto * 0.19)
        impuesto_4x1000 = int(total_ingresos * 0.004)

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
            gastos_administracion=datos_adicionales.get("gastos_administracion", 0),
            gastos_servicios=datos_adicionales.get("gastos_servicios", 0),
            gastos_reparaciones=datos_adicionales.get("gastos_reparaciones", 0),
            otros_egresos=datos_adicionales.get("otros_egresos", 0),
            estado_liquidacion="En Proceso",
            observaciones=datos_adicionales.get("observaciones"),
        )
        return self.repo_liquidacion.crear(liquidacion, usuario_sistema)

    def listar_todas_liquidaciones(self) -> List[Dict[str, Any]]:
        return self.repo_liquidacion.listar_todas()

    def aprobar_liquidacion(self, id_liquidacion: int, usuario_sistema: str) -> None:
        self.repo_liquidacion.aprobar(id_liquidacion, usuario_sistema)

    def marcar_liquidacion_pagada(
        self, id_liquidacion: int, fecha_pago: str, metodo_pago: str, referencia_pago: str, usuario_sistema: str
    ) -> None:
        self.repo_liquidacion.marcar_como_pagada(id_liquidacion, fecha_pago, metodo_pago, referencia_pago, usuario_sistema)

    def cancelar_liquidacion(self, id_liquidacion: int, motivo: str, usuario_sistema: str) -> None:
        self.repo_liquidacion.cancelar(id_liquidacion, motivo, usuario_sistema)

    def reversar_liquidacion(self, id_liquidacion: int, usuario_sistema: str) -> None:
        self.repo_liquidacion.reversar(id_liquidacion, usuario_sistema)

    def listar_liquidaciones_pendientes(self) -> List[Liquidacion]:
        """Extraído de repo."""
        # Esta lógica debería estar en el repo, pero como ya existe como método, lo usaremos
        all_aps = self.repo_liquidacion.listar_todas()
        # Nota: listar_todas suele retornar dicts. El servicio original devolvía entidades.
        # Implementaremos un método específico en repo si es necesario.
        return [self.repo_liquidacion._row_to_entity(r) for r in all_aps if r.get('estado') == 'Aprobada']

    def listar_recaudos_paginado(self, page: int = 1, page_size: int = 25, estado: Optional[str] = None,
                                fecha_desde: Optional[str] = None, fecha_hasta: Optional[str] = None, busqueda: Optional[str] = None):
        from src.dominio.modelos.pagination import PaginatedResult, PaginationParams
        params = PaginationParams(page=page, page_size=page_size)
        total = self.repo_recaudo.contar_con_filtros(estado, fecha_desde, fecha_hasta, busqueda)
        items = self.repo_recaudo.listar_paginado(params.page_size, params.offset, estado, fecha_desde, fecha_hasta, busqueda)
        return PaginatedResult(items=items, total=total, page=params.page, page_size=params.page_size)

    def listar_liquidaciones_paginado(self, page: int = 1, page_size: int = 25, estado: Optional[str] = None,
                                     periodo: Optional[str] = None, busqueda: Optional[str] = None):
        from src.dominio.modelos.pagination import PaginatedResult, PaginationParams
        params = PaginationParams(page=page, page_size=page_size)
        total = self.repo_liquidacion.contar_con_filtros(estado, periodo, busqueda)
        items = self.repo_liquidacion.listar_paginado(params.page_size, params.offset, estado, periodo, busqueda)
        return PaginatedResult(items=items, total=total, page=params.page, page_size=params.page_size)

    def obtener_detalle_recaudo_ui(self, id_recaudo: int) -> Optional[Dict[str, Any]]:
        recaudo = self.repo_recaudo.obtener_por_id(id_recaudo)
        if not recaudo: return None
        contrato = self.repo_arriendo.obtener_por_id(recaudo.id_contrato_a)
        if not contrato: return None
        propiedad = self.repo_propiedad.obtener_por_id(contrato.id_propiedad)
        conceptos = self.repo_recaudo.obtener_conceptos_por_recaudo(id_recaudo)
        return {
            "id_recaudo": recaudo.id_recaudo, "fecha_pago": recaudo.fecha_pago,
            "valor_total": recaudo.valor_total, "metodo_pago": recaudo.metodo_pago,
            "referencia_bancaria": recaudo.referencia_bancaria or "N/A",
            "estado_recaudo": recaudo.estado_recaudo, "observaciones": recaudo.observaciones or "Sin observaciones",
            "id_contrato_a": recaudo.id_contrato_a,
            "direccion_propiedad": propiedad.direccion_propiedad if propiedad else "N/A",
            "conceptos": [{"tipo_concepto": c.tipo_concepto, "periodo": c.periodo, "valor": c.valor} for c in conceptos],
            "created_at": recaudo.created_at, "created_by": recaudo.created_by or "Sistema"
        }

    def aprobar_recaudo(self, id_recaudo: int, usuario_sistema: str) -> None:
        self.repo_recaudo.cambiar_estado(id_recaudo, "Aplicado", usuario_sistema)

    def reversar_recaudo(self, id_recaudo: int, usuario_sistema: str) -> None:
        self.repo_recaudo.cambiar_estado(id_recaudo, "Reversado", usuario_sistema)

    def listar_liquidaciones_propietarios_paginado(
        self,
        page: int = 1,
        page_size: int = 25,
        estado: Optional[str] = None,
        periodo: Optional[str] = None,
        busqueda: Optional[str] = None,
    ):
        """Lista liquidaciones agrupadas por propietario (delegada a repo)."""
        return self.repo_liquidacion.listar_agrupadas_por_propietario_paginado(
            page=page,
            page_size=page_size,
            estado=estado,
            periodo=periodo,
            busqueda=busqueda,
        )
