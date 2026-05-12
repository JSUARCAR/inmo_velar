"""
Servicio de Aplicación: ServicioLiquidacionAsesores
Gestiona la lógica de negocio para liquidaciones de comisiones de asesores.
Implementa el Protocolo de Operaciones Élite (Clean Architecture, Zero Leak).
"""

import logging
from typing import Any, Dict, List, Optional

from src.dominio.entidades.bonificacion_asesor import BonificacionAsesor
from src.dominio.entidades.descuento_asesor import DescuentoAsesor
from src.dominio.entidades.liquidacion_asesor import LiquidacionAsesor
from src.dominio.entidades.pago_asesor import PagoAsesor
from src.infraestructura.cache.cache_manager import cache_manager, invalidate_cache
from src.infraestructura.repositorios.repositorio_bonificacion_asesor import (
    RepositorioBonificacionAsesor,
)
from src.infraestructura.repositorios.repositorio_descuento_asesor import (
    RepositorioDescuentoAsesor,
)
from src.infraestructura.repositorios.repositorio_liquidacion_asesor import (
    RepositorioLiquidacionAsesor,
)
from src.infraestructura.repositorios.repositorio_pago_asesor import (
    RepositorioPagoAsesor,
)
from src.infraestructura.servicios.servicio_documentos_pdf import ServicioDocumentosPDF
from src.dominio.interfaces.repositorio_idempotencia import IRepositorioIdempotencia
from src.aplicacion.decorators.idempotent import idempotent

logger = logging.getLogger(__name__)


class ServicioLiquidacionAsesores:
    """
    Servicio de aplicación para gestión de liquidaciones de asesores.
    Orquesta las operaciones entre repositorios y aplica reglas de negocio.
    """

    def __init__(
        self,
        repo_liquidacion: RepositorioLiquidacionAsesor,
        repo_descuento: RepositorioDescuentoAsesor,
        repo_pago: RepositorioPagoAsesor,
        repo_bonificacion: Optional[RepositorioBonificacionAsesor] = None,
        repo_contrato_arrendamiento=None,
        repo_propiedad=None,
        servicio_pdf: Optional[ServicioDocumentosPDF] = None,
        repo_asesor=None,
        repo_persona=None,
        repo_idempotencia: Optional[IRepositorioIdempotencia] = None,
    ):
        self.repo_liquidacion = repo_liquidacion
        self.repo_descuento = repo_descuento
        self.repo_pago = repo_pago
        self.repo_bonificacion = repo_bonificacion
        self.repo_contrato_arrendamiento = repo_contrato_arrendamiento
        self.repo_propiedad = repo_propiedad
        self.servicio_pdf = servicio_pdf
        self.repo_asesor = repo_asesor
        self.repo_persona = repo_persona
        self.repo_idempotencia = repo_idempotencia

    def _invalidar_caches(self):
        """Invalida caches relacionados siguiendo el estándar Fail-Safe (con logging)."""
        try:
            invalidate_cache("liq_asesores:list_paginated")
            invalidate_cache("liq_asesores:metrics")
        except Exception as e:
            logger.warning(f"[CACHE] Error invalidando caches de liquidaciones: {e}")

    def listar_liquidaciones_paginado(
        self,
        page: int = 1,
        page_size: int = 10,
        filtros: Optional[Dict[str, Any]] = None,
        sort_by: str = "periodo_liquidacion",
        sort_order: str = "desc",
    ) -> Dict[str, Any]:
        """
        Lista liquidaciones con paginación delegando al repositorio.
        """
        if filtros is None:
            filtros = {}

        items, total = self.repo_liquidacion.listar_paginado(
            page=page,
            page_size=page_size,
            id_asesor=filtros.get("id_asesor"),
            periodo=filtros.get("periodo"),
            estado=filtros.get("estado"),
            busqueda=filtros.get("search") or filtros.get("busqueda"),
            sort_by=sort_by,
            sort_order=sort_order,
        )

        return {"items": items, "total": total}

    def generar_pdf_comprobante(self, id_liquidacion: int) -> str:
        """
        Genera el PDF del comprobante de la liquidación.
        """
        if not self.servicio_pdf:
            raise ValueError("Servicio PDF no configurado en ServicioLiquidacionAsesores")

        detalle = self.obtener_detalle_completo(id_liquidacion)
        liquidacion = detalle["liquidacion"]

        nombre_asesor = liquidacion.get("nombre_asesor") or f"Asesor {liquidacion['id_asesor']}"
        documento_asesor = "N/A"

        try:
            if self.repo_asesor and self.repo_persona:
                asesor = self.repo_asesor.obtener_por_id(liquidacion["id_asesor"])
                if asesor:
                    persona = self.repo_persona.obtener_por_id(asesor.id_persona)
                    if persona:
                        nombre_asesor = persona.nombre_completo
                        documento_asesor = persona.numero_documento
        except Exception as e:
            logger.error(f"Error obteniendo datos detallados del asesor para PDF: {e}")

        datos_pdf = {
            "id_liquidacion": liquidacion["id_liquidacion_asesor"],
            "periodo": liquidacion["periodo_liquidacion"],
            "nombre_asesor": nombre_asesor,
            "documento_asesor": documento_asesor,
            "porcentaje_comision": liquidacion["porcentaje_comision"],
            "porcentaje_real": liquidacion["porcentaje_real"],
            "comision_bruta": liquidacion["comision_bruta"],
            "total_descuentos": liquidacion["total_descuentos"],
            "valor_neto": liquidacion["valor_neto_asesor"],
            "observaciones": liquidacion["observaciones_liquidacion"],
            "contratos": detalle["contratos"],
            "descuentos_lista": detalle["descuentos"],
            "id_contrato_legacy": liquidacion["id_contrato_a"],
            "direccion_legacy": (detalle.get("propiedad") or {}).get("direccion_propiedad"),
            "canon_legacy": (detalle.get("contrato") or {}).get("canon_arrendamiento"),
        }

        return self.servicio_pdf.generar_cuenta_cobro_asesor(datos_pdf)

    @idempotent(key_prefix="liq_asesores:generar")
    def generar_liquidacion(
        self,
        id_contrato: int,
        id_asesor: int,
        periodo: str,
        canon_arrendamiento: int,
        porcentaje_comision: int,
        datos_adicionales: Optional[Dict[str, Any]] = None,
        usuario: str = "SYSTEM",
        idempotency_key: Optional[str] = None,
    ) -> LiquidacionAsesor:
        """
        Genera una nueva liquidación de comisión para un asesor (LEGACY - Un solo contrato).
        """
        existente = self.repo_liquidacion.obtener_por_contrato_periodo(id_contrato, periodo)
        if existente:
            raise ValueError(f"Ya existe una liquidación para el contrato {id_contrato} en el período {periodo}")

        comision_bruta = LiquidacionAsesor.calcular_comision_bruta(canon_arrendamiento, porcentaje_comision)

        liquidacion = LiquidacionAsesor(
            id_contrato_a=id_contrato,
            id_asesor=id_asesor,
            periodo_liquidacion=periodo,
            canon_arrendamiento_liquidado=canon_arrendamiento,
            porcentaje_comision=porcentaje_comision,
            comision_bruta=comision_bruta,
            total_descuentos=0,
            valor_neto_asesor=comision_bruta,
            estado_liquidacion="Pendiente",
            observaciones_liquidacion=(datos_adicionales.get("observaciones") if datos_adicionales else None),
        )

        resultado = self.repo_liquidacion.crear(liquidacion, usuario)

        if self.repo_idempotencia and idempotency_key:
            try:
                self.repo_idempotencia.registrar_evento(
                    entidad_tipo="LiquidacionAsesor",
                    entidad_id=resultado.id_liquidacion_asesor,
                    tipo_evento="CREATED",
                    idempotency_key=f"liq_asesores:generar:{idempotency_key}" if not idempotency_key.startswith("liq_asesores") else idempotency_key,
                    payload=self._liquidacion_to_dict(resultado),
                    usuario_id=1,
                )
            except Exception as e:
                logger.error(f"Error registrando evento de idempotencia: {e}")

        return resultado

    @idempotent(key_prefix="liq_asesores:generar_multi")
    def generar_liquidacion_multi_contrato(
        self,
        id_asesor: int,
        periodo: str,
        contratos_lista: List[Dict[str, Any]],
        porcentaje_comision: int,
        total_bonificaciones: int = 0,
        datos_adicionales: Optional[Dict[str, Any]] = None,
        usuario: str = "SYSTEM",
        idempotency_key: Optional[str] = None,
    ) -> LiquidacionAsesor:
        """
        Genera una nueva liquidación para un asesor con múltiples contratos.
        """
        existente = self.repo_liquidacion.obtener_por_asesor_periodo(id_asesor, periodo)
        if existente:
            raise ValueError(f"Ya existe una liquidación para el asesor {id_asesor} en el período {periodo}")

        canon_total = sum(c.get("canon", 0) for c in contratos_lista)
        comision_bruta = LiquidacionAsesor.calcular_comision_bruta(canon_total, porcentaje_comision)

        liquidacion = LiquidacionAsesor(
            id_contrato_a=None,
            id_asesor=id_asesor,
            periodo_liquidacion=periodo,
            canon_arrendamiento_liquidado=canon_total,
            porcentaje_comision=porcentaje_comision,
            comision_bruta=comision_bruta,
            total_descuentos=0,
            total_bonificaciones=total_bonificaciones,
            valor_neto_asesor=comision_bruta + total_bonificaciones,
            estado_liquidacion="Pendiente",
            observaciones_liquidacion=(datos_adicionales.get("observaciones") if datos_adicionales else None),
        )

        liquidacion_creada = self.repo_liquidacion.crear(liquidacion, usuario)

        contratos_unicos = {c["id"]: c for c in contratos_lista}.values()
        contratos_tuplas = [(c["id"], c.get("canon", 0)) for c in contratos_unicos]

        self.repo_liquidacion.guardar_contratos_liquidacion(
            liquidacion_creada.id_liquidacion_asesor, contratos_tuplas, usuario
        )

        if self.repo_idempotencia and idempotency_key:
            try:
                self.repo_idempotencia.registrar_evento(
                    entidad_tipo="LiquidacionAsesor",
                    entidad_id=liquidacion_creada.id_liquidacion_asesor,
                    tipo_evento="CREATED_MULTI",
                    idempotency_key=f"liq_asesores:generar_multi:{idempotency_key}" if not idempotency_key.startswith("liq_asesores") else idempotency_key,
                    payload=self._liquidacion_to_dict(liquidacion_creada),
                    usuario_id=1,
                )
            except Exception as e:
                logger.error(f"Error registrando evento multi-contrato: {e}")

        self._invalidar_caches()
        return liquidacion_creada

    def actualizar_liquidacion(self, id_liquidacion: int, datos: Dict[str, Any], usuario: str) -> LiquidacionAsesor:
        """Actualiza una liquidación pendiente."""
        liquidacion = self.repo_liquidacion.obtener_por_id(id_liquidacion)
        if not liquidacion:
            raise ValueError(f"No se encontró la liquidación con ID {id_liquidacion}")

        if not liquidacion.puede_editarse:
            raise ValueError("Solo se pueden editar liquidaciones en estado Pendiente")

        if "porcentaje_comision" in datos:
            liquidacion.porcentaje_comision = datos["porcentaje_comision"]
            liquidacion.comision_bruta = LiquidacionAsesor.calcular_comision_bruta(
                liquidacion.canon_arrendamiento_liquidado,
                liquidacion.porcentaje_comision,
            )
            liquidacion.valor_neto_asesor = liquidacion.calcular_valor_neto(
                liquidacion.total_descuentos, liquidacion.total_bonificaciones or 0
            )

        if "observaciones_liquidacion" in datos:
            liquidacion.observaciones_liquidacion = datos["observaciones_liquidacion"]

        result = self.repo_liquidacion.actualizar(liquidacion, usuario)
        self._invalidar_caches()
        return result

    def aprobar_liquidacion(self, id_liquidacion: int, usuario: str) -> LiquidacionAsesor:
        """Aprueba una liquidación."""
        liquidacion = self.repo_liquidacion.obtener_por_id(id_liquidacion)
        if not liquidacion:
            raise ValueError(f"No se encontró la liquidación con ID {id_liquidacion}")

        liquidacion.aprobar(usuario)
        result = self.repo_liquidacion.actualizar(liquidacion, usuario)
        self._invalidar_caches()
        return result

    def anular_liquidacion(self, id_liquidacion: int, motivo: str, usuario: str) -> LiquidacionAsesor:
        """Anula una liquidación."""
        liquidacion = self.repo_liquidacion.obtener_por_id(id_liquidacion)
        if not liquidacion:
            raise ValueError(f"No se encontró la liquidación con ID {id_liquidacion}")

        liquidacion.anular(motivo, usuario)
        result = self.repo_liquidacion.actualizar(liquidacion, usuario)
        self._invalidar_caches()
        return result

    def agregar_descuento(self, id_liquidacion: int, tipo: str, descripcion: str, valor: int, usuario: str) -> DescuentoAsesor:
        """Agrega un descuento y recalcula el neto."""
        liquidacion = self.repo_liquidacion.obtener_por_id(id_liquidacion)
        if not liquidacion or not liquidacion.puede_editarse:
            raise ValueError("Operación no permitida: liquidación no existe o no es editable")

        descuento = DescuentoAsesor(
            id_liquidacion_asesor=id_liquidacion,
            tipo_descuento=tipo,
            descripcion_descuento=descripcion,
            valor_descuento=valor,
        )
        descuento_creado = self.repo_descuento.crear(descuento, usuario)
        self._recalcular_valor_neto(id_liquidacion, usuario)
        self._invalidar_caches()
        return descuento_creado

    def eliminar_descuento(self, id_descuento: int, usuario: str) -> bool:
        """Elimina un descuento y recalcula el neto."""
        descuento = self.repo_descuento.obtener_por_id(id_descuento)
        if not descuento:
            raise ValueError(f"No se encontró el descuento {id_descuento}")

        liquidacion = self.repo_liquidacion.obtener_por_id(descuento.id_liquidacion_asesor)
        if not liquidacion or not liquidacion.puede_editarse:
            raise ValueError("No se puede eliminar descuentos de liquidaciones no editables")

        if self.repo_descuento.eliminar(id_descuento):
            self._recalcular_valor_neto(descuento.id_liquidacion_asesor, usuario)
            self._invalidar_caches()
            return True
        return False

    def _recalcular_valor_neto(self, id_liquidacion: int, usuario: str) -> None:
        """Recalcula el valor neto basado en descuentos y bonificaciones."""
        liquidacion = self.repo_liquidacion.obtener_por_id(id_liquidacion)
        if not liquidacion:
            return

        total_descuentos = self.repo_descuento.calcular_total_descuentos(id_liquidacion)
        total_bonificaciones = 0
        if self.repo_bonificacion:
            total_bonificaciones = self.repo_bonificacion.calcular_total_bonificaciones(id_liquidacion)
        else:
            total_bonificaciones = liquidacion.total_bonificaciones

        liquidacion.recalcular_valor_neto(total_descuentos, total_bonificaciones)
        self.repo_liquidacion.actualizar(liquidacion, usuario)

    def agregar_bonificacion(self, id_liquidacion: int, tipo: str, descripcion: str, valor: int, usuario: str) -> BonificacionAsesor:
        """Agrega una bonificación detallada."""
        if not self.repo_bonificacion:
            raise ValueError("Repositorio de bonificaciones no configurado")

        liquidacion = self.repo_liquidacion.obtener_por_id(id_liquidacion)
        if not liquidacion or not liquidacion.puede_editarse:
            raise ValueError("No se pueden agregar bonificaciones a esta liquidación")

        bonificacion = BonificacionAsesor(
            id_liquidacion_asesor=id_liquidacion,
            tipo_bonificacion=tipo,
            descripcion_bonificacion=descripcion,
            valor_bonificacion=valor,
        )
        resultado = self.repo_bonificacion.crear(bonificacion, usuario)
        self._recalcular_valor_neto(id_liquidacion, usuario)
        self._invalidar_caches()
        return resultado

    def eliminar_bonificacion(self, id_bonificacion: int, usuario: str) -> bool:
        """Elimina una bonificación detallada."""
        if not self.repo_bonificacion:
            raise ValueError("Repositorio de bonificaciones no configurado")

        bonificacion = self.repo_bonificacion.obtener_por_id(id_bonificacion)
        if not bonificacion:
            return False

        id_liq = bonificacion.id_liquidacion_asesor
        if self.repo_bonificacion.eliminar(id_bonificacion):
            self._recalcular_valor_neto(id_liq, usuario)
            self._invalidar_caches()
            return True
        return False

    def programar_pago(
        self, id_liquidacion: int, id_asesor: int, valor: int, 
        fecha_programada: str, medio_pago: str, 
        datos_adicionales: Optional[Dict[str, Any]] = None, usuario: str = "SYSTEM"
    ) -> PagoAsesor:
        """Programa un pago para una liquidación aprobada."""
        liquidacion = self.repo_liquidacion.obtener_por_id(id_liquidacion)
        if not liquidacion or not liquidacion.esta_aprobada:
            raise ValueError("Solo se pueden programar pagos para liquidaciones aprobadas")

        pago = PagoAsesor(
            id_liquidacion_asesor=id_liquidacion,
            id_asesor=id_asesor,
            valor_pago=valor,
            fecha_programada=fecha_programada,
            medio_pago=medio_pago,
            referencia_pago=datos_adicionales.get("referencia") if datos_adicionales else None,
            observaciones_pago=(datos_adicionales.get("observaciones") if datos_adicionales else None),
            estado_pago="Programado",
        )

        result = self.repo_pago.crear(pago, usuario)
        self._invalidar_caches()
        return result

    @idempotent(key_prefix="liquidacion:registrar_pago")
    def registrar_pago(self, id_pago: int, fecha_pago: str, comprobante: str, usuario: str) -> PagoAsesor:
        """Registra un pago efectivo."""
        pago = self.repo_pago.obtener_por_id(id_pago)
        if not pago:
            raise ValueError(f"No se encontró el pago con ID {id_pago}")

        pago.marcar_como_pagado(fecha_pago, comprobante, usuario)
        pago_actualizado = self.repo_pago.actualizar(pago, usuario)

        liquidacion = self.repo_liquidacion.obtener_por_id(pago.id_liquidacion_asesor)
        if liquidacion:
            liquidacion.marcar_como_pagada(usuario)
            self.repo_liquidacion.actualizar(liquidacion, usuario)

        self._invalidar_caches()
        return pago_actualizado

    @cache_manager.cached("liq_asesores:list_paginated", level=1, ttl=300)
    def listar_liq_asesores_paginado(
        self, page: int = 1, page_size: int = 25,
        estado: Optional[str] = None, periodo: Optional[str] = None,
        busqueda: Optional[str] = None, id_asesor: Optional[int] = None,
        sort_by: str = "periodo_liquidacion", sort_order: str = "desc"
    ):
        """Lista delegada al repositorio con cache."""
        from src.dominio.modelos.pagination import PaginatedResult
        items, total = self.repo_liquidacion.listar_paginado(
            page=page, page_size=page_size, id_asesor=id_asesor, 
            periodo=periodo, estado=estado, busqueda=busqueda,
            sort_by=sort_by, sort_order=sort_order
        )
        return PaginatedResult(items=items, total=total, page=page, page_size=page_size)

    @cache_manager.cached("liq_asesores:metrics", level=1, ttl=60)
    def obtener_metricas_filtradas(
        self, estado: Optional[str] = None, periodo: Optional[str] = None,
        busqueda: Optional[str] = None, id_asesor: Optional[int] = None
    ) -> Dict[str, int]:
        """Métricas delegadas al repositorio."""
        return self.repo_liquidacion.obtener_metricas_por_filtros(
            estado=estado, periodo=periodo, busqueda=busqueda, id_asesor=id_asesor
        )

    def obtener_detalle_completo(self, id_liquidacion: int) -> Dict[str, Any]:
        """Obtiene detalle integral (Cero SQL crudo)."""
        liquidacion = self.repo_liquidacion.obtener_por_id(id_liquidacion)
        if not liquidacion:
            raise ValueError(f"No se encontró la liquidación con ID {id_liquidacion}")

        descuentos = self.repo_descuento.listar_por_liquidacion(id_liquidacion)
        pagos = self.repo_pago.listar_por_liquidacion(id_liquidacion)
        
        bonificaciones = []
        if self.repo_bonificacion:
            try:
                bonif_entities = self.repo_bonificacion.listar_por_liquidacion(id_liquidacion)
                bonificaciones = [
                    {
                        "id_bonificacion_asesor": b.id_bonificacion_asesor,
                        "tipo_bonificacion": b.tipo_bonificacion,
                        "descripcion_bonificacion": b.descripcion_bonificacion,
                        "valor_bonificacion": b.valor_bonificacion,
                        "fecha_registro": b.fecha_registro,
                    } for b in bonif_entities
                ]
            except Exception as e:
                logger.error(f"Error obteniendo bonificaciones: {e}")

        # Sintética para legacy
        if not bonificaciones and (liquidacion.total_bonificaciones or 0) > 0:
            bonificaciones.append({
                "id_bonificacion_asesor": -1,
                "tipo_bonificacion": "Bonificación Consolidada",
                "descripcion_bonificacion": "Total (sin desglose)",
                "valor_bonificacion": liquidacion.total_bonificaciones,
                "fecha_registro": liquidacion.fecha_creacion,
            })

        contratos_asociados = self.repo_liquidacion.obtener_contratos_de_liquidacion(id_liquidacion)

        return {
            "liquidacion": self._liquidacion_to_dict(liquidacion),
            "contratos": contratos_asociados,
            "descuentos": [self._descuento_to_dict(d) for d in descuentos],
            "bonificaciones": bonificaciones,
            "pagos": [self._pago_to_dict(p) for p in pagos],
        }

    def generar_liquidaciones_masivas_optimizado(self, periodo: str, usuario: str) -> Dict[str, int]:
        """Generación masiva optimizada."""
        if not self.repo_asesor or not self.repo_contrato_arrendamiento:
            raise ValueError("Repositorios necesarios no configurados")

        stats = {"creadas": 0, "omitidas": 0, "errores": 0, "total": 0}
        asesores = self.repo_asesor.listar_activos()
        stats["total"] = len(asesores)
        contratos_agrupados = self.repo_contrato_arrendamiento.obtener_activos_todos_agrupados()

        for asesor in asesores:
            try:
                if self.repo_liquidacion.obtener_por_asesor_periodo(asesor.id_asesor, periodo):
                    stats["omitidas"] += 1
                    continue

                contratos_asesor = contratos_agrupados.get(asesor.id_asesor, [])
                if not contratos_asesor:
                    stats["omitidas"] += 1
                    continue

                self.generar_liquidacion_multi_contrato(
                    id_asesor=asesor.id_asesor,
                    periodo=periodo,
                    contratos_lista=[{"id": c.id_contrato_a, "canon": c.canon_arrendamiento} for c in contratos_asesor],
                    porcentaje_comision=int((asesor.comision_porcentaje_arriendo or 5.0) * 100),
                    usuario=usuario,
                )
                stats["creadas"] += 1
            except Exception as e:
                logger.error(f"Error en liquidación masiva para asesor {asesor.id_asesor}: {e}")
                stats["errores"] += 1

        return stats

    def _liquidacion_to_dict(self, liq: LiquidacionAsesor) -> Dict[str, Any]:
        return {
            "id_liquidacion_asesor": liq.id_liquidacion_asesor,
            "id_contrato_a": liq.id_contrato_a,
            "id_asesor": liq.id_asesor,
            "nombre_asesor": getattr(liq, "nombre_asesor", None),
            "periodo_liquidacion": liq.periodo_liquidacion,
            "canon_arrendamiento_liquidado": liq.canon_arrendamiento_liquidado,
            "porcentaje_comision": liq.porcentaje_comision,
            "porcentaje_real": liq.porcentaje_real,
            "comision_bruta": liq.comision_bruta,
            "total_descuentos": liq.total_descuentos,
            "total_bonificaciones": liq.total_bonificaciones,
            "valor_neto_asesor": liq.valor_neto_asesor,
            "estado_liquidacion": liq.estado_liquidacion,
            "fecha_creacion": liq.fecha_creacion,
            "fecha_aprobacion": liq.fecha_aprobacion,
            "usuario_creador": liq.usuario_creador,
            "usuario_aprobador": liq.usuario_aprobador,
            "observaciones_liquidacion": liq.observaciones_liquidacion,
            "motivo_anulacion": liq.motivo_anulacion,
            "puede_editarse": liq.puede_editarse,
            "puede_aprobarse": liq.puede_aprobarse,
            "puede_anularse": liq.puede_anularse,
        }

    def _descuento_to_dict(self, desc: DescuentoAsesor) -> Dict[str, Any]:
        return {
            "id_descuento_asesor": desc.id_descuento_asesor,
            "tipo_descuento": desc.tipo_descuento,
            "descripcion_descuento": desc.descripcion_descuento,
            "valor_descuento": desc.valor_descuento,
            "fecha_registro": desc.fecha_registro,
        }

    def _pago_to_dict(self, pago: PagoAsesor) -> Dict[str, Any]:
        return {
            "id_pago_asesor": pago.id_pago_asesor,
            "valor_pago": pago.valor_pago,
            "fecha_pago": pago.fecha_pago,
            "fecha_programada": pago.fecha_programada,
            "medio_pago": pago.medio_pago,
            "estado_pago": pago.estado_pago,
        }
