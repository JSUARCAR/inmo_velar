"""
Servicio de Aplicación: ServicioLiquidacionAsesores
Gestiona la lógica de negocio para liquidaciones de comisiones de asesores.
"""

from typing import List, Dict, Optional, Any
from datetime import datetime

from src.dominio.entidades.liquidacion_asesor import LiquidacionAsesor
from src.dominio.entidades.descuento_asesor import DescuentoAsesor
from src.dominio.entidades.pago_asesor import PagoAsesor
from src.infraestructura.repositorios.repositorio_liquidacion_asesor_sqlite import RepositorioLiquidacionAsesorSQLite
from src.infraestructura.repositorios.repositorio_descuento_asesor_sqlite import RepositorioDescuentoAsesorSQLite
from src.infraestructura.repositorios.repositorio_pago_asesor_sqlite import RepositorioPagoAsesorSQLite
from src.infraestructura.repositorios.repositorio_pago_asesor_sqlite import RepositorioPagoAsesorSQLite
from src.dominio.entidades.bonificacion_asesor import BonificacionAsesor
from src.infraestructura.repositorios.repositorio_bonificacion_asesor_sqlite import RepositorioBonificacionAsesorSQLite
from src.infraestructura.servicios.servicio_documentos_pdf import ServicioDocumentosPDF
from src.infraestructura.cache.cache_manager import cache_manager, invalidate_cache


class ServicioLiquidacionAsesores:
    """
    Servicio de aplicación para gestión de liquidaciones de asesores.
    Orquesta las operaciones entre repositorios y aplica reglas de negocio.
    """
    
    def __init__(
        self,
        repo_liquidacion: RepositorioLiquidacionAsesorSQLite,
        repo_descuento: RepositorioDescuentoAsesorSQLite,

        repo_pago: RepositorioPagoAsesorSQLite,
        repo_bonificacion: Optional[RepositorioBonificacionAsesorSQLite] = None,
        repo_contrato_arrendamiento = None,
        repo_propiedad = None,
        servicio_pdf: Optional[ServicioDocumentosPDF] = None,
        repo_asesor = None,
        repo_persona = None
    ):
        self.repo_liquidacion = repo_liquidacion
        self.repo_descuento = repo_descuento
        self.repo_pago = repo_pago
        self.repo_bonificacion = repo_bonificacion
        self.repo_contrato = repo_contrato_arrendamiento
        self.repo_propiedad = repo_propiedad
        self.servicio_pdf = servicio_pdf
        self.repo_asesor = repo_asesor
        self.repo_persona = repo_persona

    def _invalidar_caches(self):
        """Invalidates related caches to ensure fresh data on lists and metrics."""
        try:
            # Invalidate paginated lists
            invalidate_cache('liq_asesores:list_paginated')
            # Invalidate metrics
            invalidate_cache('liq_asesores:metrics')
            pass  # print("[CACHE] Caches de liquidaciones invalidados") [OpSec Removed]
        except Exception as e:
            pass  # print(f"[CACHE] Error invalidando caches: {e}") [OpSec Removed]

    def listar_liquidaciones_paginado(
        self,
        page: int = 1,
        page_size: int = 10,
        filtros: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Lista liquidaciones con paginación y filtros.
        
        Args:
            page: Número de página (1-based)
            page_size: Tamaño de página
            filtros: Diccionario de filtros (id_asesor, periodo, estado)
            
        Returns:
            Diccionario con items y total
        """
        if filtros is None:
            filtros = {}
            
        items, total = self.repo_liquidacion.listar_paginado(
            page=page,
            page_size=page_size,
            id_asesor=filtros.get('id_asesor'),
            periodo=filtros.get('periodo'),
            estado=filtros.get('estado')
        )
        
        return {
            'items': items,
            'total': total
        }

    
    def generar_pdf_comprobante(self, id_liquidacion: int) -> str:
        """
        Genera el PDF del comprobante/cuenta de cobro de la liquidación.
        
        Args:
            id_liquidacion: ID de la liquidación
            
        Returns:
            Ruta del archivo PDF generado
            
        Raises:
            ValueError: Si el servicio PDF no está configurado
        """
        if not self.servicio_pdf:
             raise ValueError("Servicio PDF no configurado en ServicioLiquidacionAsesores")
             
        detalle = self.obtener_detalle_completo(id_liquidacion)
        liquidacion = detalle['liquidacion']
        
        # Obtener datos del asesor
        nombre_asesor = f"Asesor {liquidacion['id_asesor']}"
        documento_asesor = "N/A"
        
        try:
            if self.repo_asesor and self.repo_persona:
                asesor = self.repo_asesor.obtener_por_id(liquidacion['id_asesor'])
                if asesor:
                    persona = self.repo_persona.obtener_por_id(asesor.id_persona)
                    if persona:
                        nombre_asesor = persona.nombre_completo
                        documento_asesor = persona.numero_documento
        except Exception as e:
            pass  # print(f"Advertencia: No se pudo obtener datos detallados del asesor: {e}") [OpSec Removed]

        datos_pdf = {
            "id_liquidacion": liquidacion['id_liquidacion_asesor'],
            "periodo": liquidacion['periodo_liquidacion'],
            "nombre_asesor": nombre_asesor,
            "documento_asesor": documento_asesor,
            "porcentaje_comision": liquidacion['porcentaje_comision'],
            "porcentaje_real": liquidacion['porcentaje_real'],
            "comision_bruta": liquidacion['comision_bruta'],
            "total_descuentos": liquidacion['total_descuentos'],
            "valor_neto": liquidacion['valor_neto_asesor'],
            "observaciones": liquidacion['observaciones_liquidacion'],
            "contratos": detalle['contratos'],
            "descuentos_lista": detalle['descuentos'],
            # Legacy fallback
            "id_contrato_legacy": liquidacion['id_contrato_a'],
            "direccion_legacy": (detalle.get('propiedad') or {}).get('direccion_propiedad'),
            "canon_legacy": (detalle.get('contrato') or {}).get('canon_arrendamiento')
        }
        
        return self.servicio_pdf.generar_cuenta_cobro_asesor(datos_pdf)
    
    # ==================== Métodos de Liquidación ====================
    
    def generar_liquidacion(
        self,
        id_contrato: int,
        id_asesor: int,
        periodo: str,
        canon_arrendamiento: int,
        porcentaje_comision: int,
        datos_adicionales: Optional[Dict[str, Any]] = None,
        usuario: str = "SYSTEM"
    ) -> LiquidacionAsesor:
        """
        Genera una nueva liquidación de comisión para un asesor (LEGACY - Un solo contrato).
        NOTA: Este método se mantiene por compatibilidad. Para nueva funcionalidad
        usar generar_liquidacion_multi_contrato().
        
        Args:
            id_contrato: ID del contrato de arrendamiento
            id_asesor: ID del asesor
            periodo: Período de liquidación (YYYY-MM)
            canon_arrendamiento: Canon del mes
            porcentaje_comision: Porcentaje de comisión (0-10000, representa 0.00%-100.00%)
            datos_adicionales: Dict opcional con observaciones, etc.
            usuario: Usuario que genera la liquidación
        
        Returns:
            LiquidacionAsesor creada
        
        Raises:
            ValueError: Si ya existe liquidación para ese contrato+período
        """
        # Validar que no exista liquidación duplicada
        existente = self.repo_liquidacion.obtener_por_contrato_periodo(id_contrato, periodo)
        if existente:
            raise ValueError(
                f"Ya existe una liquidación para el contrato {id_contrato} "
                f"en el período {periodo}"
            )
        
        # Calcular comisión bruta
        comision_bruta = LiquidacionAsesor.calcular_comision_bruta(
            canon_arrendamiento,
            porcentaje_comision
        )
        
        # Crear entidad de liquidación
        liquidacion = LiquidacionAsesor(
            id_contrato_a=id_contrato,
            id_asesor=id_asesor,
            periodo_liquidacion=periodo,
            canon_arrendamiento_liquidado=canon_arrendamiento,
            porcentaje_comision=porcentaje_comision,
            comision_bruta=comision_bruta,
            total_descuentos=0,
            valor_neto_asesor=comision_bruta,  # Inicialmente sin descuentos
            estado_liquidacion="Pendiente",
            observaciones_liquidacion=datos_adicionales.get("observaciones") if datos_adicionales else None
        )
        
        # Guardar en BD
        return self.repo_liquidacion.crear(liquidacion, usuario)
    
    def generar_liquidacion_multi_contrato(
        self,
        id_asesor: int,
        periodo: str,
        contratos_lista: List[Dict[str, Any]],
        porcentaje_comision: int,
        total_bonificaciones: int = 0,
        datos_adicionales: Optional[Dict[str, Any]] = None,
        usuario: str = "SYSTEM"
    ) -> LiquidacionAsesor:
        """
        Genera una nueva liquidación de comisión para un asesor con múltiples contratos.
        
        Args:
            id_asesor: ID del asesor
            periodo: Período de liquidación (YYYY-MM)
            contratos_lista: Lista de dicts con {'id': x, 'canon': y} para cada contrato
            porcentaje_comision: Porcentaje de comisión (0-10000, representa 0.00%-100.00%)
            datos_adicionales: Dict opcional con observaciones, etc.
            usuario: Usuario que genera la liquidación
        
        Returns:
            LiquidacionAsesor creada con contratos asociados
        
        Raises:
            ValueError: Si ya existe liquidación para ese asesor+período
        """
        # Validar que no exista liquidación duplicada (asesor + período)
        existente = self.repo_liquidacion.obtener_por_asesor_periodo(id_asesor, periodo)
        if existente:
            raise ValueError(
                f"Ya existe una liquidación para el asesor {id_asesor} "
                f"en el período {periodo}"
            )
        
        # Calcular suma total de cánones
        canon_total = sum(c.get('canon', 0) for c in contratos_lista)
        
        # Calcular comisión bruta sobre el total
        comision_bruta = LiquidacionAsesor.calcular_comision_bruta(
            canon_total,
            porcentaje_comision
        )
        
        # Crear entidad de liquidación
        # id_contrato_a se deja en None (campo legacy)
        liquidacion = LiquidacionAsesor(
            id_contrato_a=None,  # Ya no usamos este campo
            id_asesor=id_asesor,
            periodo_liquidacion=periodo,
            canon_arrendamiento_liquidado=canon_total,
            porcentaje_comision=porcentaje_comision,
            comision_bruta=comision_bruta,
            total_descuentos=0,
            total_bonificaciones=total_bonificaciones,
            valor_neto_asesor=comision_bruta + total_bonificaciones,
            estado_liquidacion="Pendiente",
            observaciones_liquidacion=datos_adicionales.get("observaciones") if datos_adicionales else None
        )
        
        # Guardar liquidación en BD
        liquidacion_creada = self.repo_liquidacion.crear(liquidacion, usuario)
        
        # Guardar relaciones con contratos en tabla intermedia
        # Deduplicar contratos por ID para evitar IntegrityError
        contratos_unicos = {c['id']: c for c in contratos_lista}.values()
        
        contratos_tuplas = [
            (c['id'], c.get('canon', 0)) 
            for c in contratos_unicos
        ]
        self.repo_liquidacion.guardar_contratos_liquidacion(
            liquidacion_creada.id_liquidacion_asesor,
            contratos_tuplas,
            usuario
        )
        
        self._invalidar_caches()
        return liquidacion_creada
    
    def actualizar_liquidacion(
        self,
        id_liquidacion: int,
        datos: Dict[str, Any],
        usuario: str
    ) -> LiquidacionAsesor:
        """
        Actualiza una liquidación existente (solo si está pendiente).
        
        Args:
            id_liquidacion: ID de la liquidación
            datos: Diccionario con campos a actualizar
            usuario: Usuario que actualiza
        
        Returns:
            LiquidacionAsesor actualizada
        
        Raises:
            ValueError: Si la liquidación no existe o no puede editarse
        """
        liquidacion = self.repo_liquidacion.obtener_por_id(id_liquidacion)
        if not liquidacion:
            raise ValueError(f"No se encontró la liquidación con ID {id_liquidacion}")
        
        if not liquidacion.puede_editarse:
            raise ValueError("Solo se pueden editar liquidaciones en estado Pendiente")
        
        # Actualizar campos permitidos
        if "porcentaje_comision" in datos:
            liquidacion.porcentaje_comision = datos["porcentaje_comision"]
            # Recalcular comisión bruta
            liquidacion.comision_bruta = LiquidacionAsesor.calcular_comision_bruta(
                liquidacion.canon_arrendamiento_liquidado,
                liquidacion.porcentaje_comision
            )
            # Recalcular valor neto
            liquidacion.valor_neto_asesor = liquidacion.calcular_valor_neto(
                liquidacion.total_descuentos,
                liquidacion.total_bonificaciones or 0
            )
        
        if "observaciones_liquidacion" in datos:
            liquidacion.observaciones_liquidacion = datos["observaciones_liquidacion"]
        
        result = self.repo_liquidacion.actualizar(liquidacion, usuario)
        self._invalidar_caches()
        return result
    
    def aprobar_liquidacion(self, id_liquidacion: int, usuario: str) -> LiquidacionAsesor:
        """
        Aprueba una liquidación.
        
        Args:
            id_liquidacion: ID de la liquidación
            usuario: Usuario que aprueba
        
        Returns:
            LiquidacionAsesor aprobada
        
        Raises:
            ValueError: Si la liquidación no puede ser aprobada
        """
        liquidacion = self.repo_liquidacion.obtener_por_id(id_liquidacion)
        if not liquidacion:
            raise ValueError(f"No se encontró la liquidación con ID {id_liquidacion}")
        
        liquidacion.aprobar(usuario)
        result = self.repo_liquidacion.actualizar(liquidacion, usuario)
        self._invalidar_caches()
        return result
    
    def anular_liquidacion(
        self,
        id_liquidacion: int,
        motivo: str,
        usuario: str
    ) -> LiquidacionAsesor:
        """
        Anula una liquidación.
        
        Args:
            id_liquidacion: ID de la liquidación
            motivo: Motivo de la anulación
            usuario: Usuario que anula
        
        Returns:
            LiquidacionAsesor anulada
        
        Raises:
            ValueError: Si la liquidación no puede ser anulada
        """
        liquidacion = self.repo_liquidacion.obtener_por_id(id_liquidacion)
        if not liquidacion:
            raise ValueError(f"No se encontró la liquidación con ID {id_liquidacion}")
        
        liquidacion.anular(motivo, usuario)
        result = self.repo_liquidacion.actualizar(liquidacion, usuario)
        self._invalidar_caches()
        return result
    
    # ==================== Métodos de Descuentos ====================
    
    def agregar_descuento(
        self,
        id_liquidacion: int,
        tipo: str,
        descripcion: str,
        valor: int,
        usuario: str
    ) -> DescuentoAsesor:
        """
        Agrega un descuento a una liquidación y recalcula el valor neto.
        
        Args:
            id_liquidacion: ID de la liquidación
            tipo: Tipo de descuento
            descripcion: Descripción del descuento
            valor: Valor del descuento
            usuario: Usuario que agrega el descuento
        
        Returns:
            DescuentoAsesor creado
        
        Raises:
            ValueError: Si la liquidación no puede editarse
        """
        liquidacion = self.repo_liquidacion.obtener_por_id(id_liquidacion)
        if not liquidacion:
            raise ValueError(f"No se encontró la liquidación con ID {id_liquidacion}")
        
        if not liquidacion.puede_editarse:
            raise ValueError("Solo se pueden agregar descuentos a liquidaciones pendientes")
        
        # Crear descuento
        descuento = DescuentoAsesor(
            id_liquidacion_asesor=id_liquidacion,
            tipo_descuento=tipo,
            descripcion_descuento=descripcion,
            valor_descuento=valor
        )
        descuento_creado = self.repo_descuento.crear(descuento, usuario)
        
        # Recalcular valor neto de la liquidación
        self._recalcular_valor_neto(id_liquidacion, usuario)
        
        self._invalidar_caches()
        return descuento_creado
    
    def eliminar_descuento(self, id_descuento: int, usuario: str) -> bool:
        """
        Elimina un descuento y recalcula el valor neto de la liquidación.
        
        Args:
            id_descuento: ID del descuento
            usuario: Usuario que elimina
        
        Returns:
            True si se eliminó
        
        Raises:
            ValueError: Si el descuento no existe o la liquidación no puede editarse
        """
        pass  # print(f"\n[SERVICE] eliminar_descuento CALLED") [OpSec Removed]
        pass  # print(f"[SERVICE] id_descuento: {id_descuento}, usuario: {usuario}") [OpSec Removed]
        
        descuento = self.repo_descuento.obtener_por_id(id_descuento)
        pass  # print(f"[SERVICE] Descuento obtenido: {descuento}") [OpSec Removed]
        
        if not descuento:
            error_msg = f"No se encontró el descuento con ID {id_descuento}"
            pass  # print(f"[SERVICE] ❌ {error_msg}") [OpSec Removed]
            raise ValueError(error_msg)
        
        # Verificar que la liquidación puede editarse
        liquidacion = self.repo_liquidacion.obtener_por_id(descuento.id_liquidacion_asesor)
        pass  # print(f"[SERVICE] Liquidación: ID={descuento.id_liquidacion_asesor}, puede_editarse={liquidacion.puede_editarse if liquidacion else 'N/A'}") [OpSec Removed]
        
        if not liquidacion or not liquidacion.puede_editarse:
            error_msg = "Solo se pueden eliminar descuentos de liquidaciones pendientes"
            pass  # print(f"[SERVICE] ❌ {error_msg}") [OpSec Removed]
            raise ValueError(error_msg)
        
        id_liquidacion = descuento.id_liquidacion_asesor
        
        pass  # print(f"[SERVICE] Llamando repo.eliminar({id_descuento})") [OpSec Removed]
        eliminado = self.repo_descuento.eliminar(id_descuento)
        pass  # print(f"[SERVICE] Repo retornó: {eliminado}") [OpSec Removed]
        
        if eliminado:
            pass  # print(f"[SERVICE] Recalculando valor neto para liquidación {id_liquidacion}") [OpSec Removed]
        self._recalcular_valor_neto(id_liquidacion, usuario)
        self._invalidar_caches()
        pass  # print(f"[SERVICE] Recálculo completado") [OpSec Removed]
        
        pass  # print(f"[SERVICE] Retornando: {eliminado}\n") [OpSec Removed]
        return eliminado
    
    def _recalcular_valor_neto(self, id_liquidacion: int, usuario: str) -> None:
        """
        Recalcula el valor neto de una liquidación basado en sus descuentos y bonificaciones.
        
        Args:
            id_liquidacion: ID de la liquidación
            usuario: Usuario que realiza el cambio
        """
        liquidacion = self.repo_liquidacion.obtener_por_id(id_liquidacion)
        if not liquidacion:
            return
        
        # Calcular total de descuentos
        total_descuentos = self.repo_descuento.calcular_total_descuentos(id_liquidacion)
        
        # Calcular total de bonificaciones (si el repo está disponible)
        total_bonificaciones = 0
        if self.repo_bonificacion:
             total_bonificaciones = self.repo_bonificacion.calcular_total_bonificaciones(id_liquidacion)
        else:
             # Fallback si no hay repo configurado (no debería pasar con el fix anterior)
             total_bonificaciones = liquidacion.total_bonificaciones
        
        # Actualizar liquidación
        liquidacion.recalcular_valor_neto(total_descuentos, total_bonificaciones)
        self.repo_liquidacion.actualizar(liquidacion, usuario)

    # ==================== Métodos de Bonificaciones ====================

    def agregar_bonificacion(
        self,
        id_liquidacion: int,
        tipo: str,
        descripcion: str,
        valor: int,
        usuario: str
    ) -> BonificacionAsesor:
        """
        Agrega una bonificación a una liquidación.
        """
        if not self.repo_bonificacion:
             raise ValueError("Repositorio de bonificaciones no configurado")

        liquidacion = self.repo_liquidacion.obtener_por_id(id_liquidacion)
        if not liquidacion:
            raise ValueError(f"No se encontró la liquidación con ID {id_liquidacion}")
        
        # Crear bonificación
        bonificacion = BonificacionAsesor(
            id_liquidacion_asesor=id_liquidacion,
            tipo_bonificacion=tipo,
            descripcion_bonificacion=descripcion,
            valor_bonificacion=valor
        )
        resultado = self.repo_bonificacion.crear(bonificacion, usuario)
        
        # Recalcular valor neto de la liquidación
        if resultado:
             self._recalcular_valor_neto(id_liquidacion, usuario)
             self._invalidar_caches()
             
        return resultado

    def eliminar_bonificacion(self, id_bonificacion: int, usuario: str) -> bool:
        """
        Elimina una bonificación y actualiza el total de la liquidación.
        """
        if not self.repo_bonificacion:
             raise ValueError("Repositorio de bonificaciones no configurado")

        bonificacion = self.repo_bonificacion.obtener_por_id(id_bonificacion)
        if not bonificacion:
            return False

        id_liquidacion = bonificacion.id_liquidacion_asesor
        valor_eliminado = bonificacion.valor_bonificacion

        if self.repo_bonificacion.eliminar(id_bonificacion):
            # Actualizar totales en la liquidación padre
            liquidacion = self.repo_liquidacion.obtener_por_id(id_liquidacion)
            if liquidacion:
                # Recalcular total de bonificaciones desde la DB para mayor precision
                nuevo_total_bonif = self.repo_bonificacion.calcular_total_bonificaciones(id_liquidacion)
                
                # Actualizar entidad liquidación
                liquidacion.total_bonificaciones = nuevo_total_bonif
                
                # Recalcular Valor Neto: (Comisión + Bonificaciones) - Descuentos
                descuentos = self.repo_descuento.listar_por_liquidacion(id_liquidacion)
                total_descuentos = sum(d.valor_descuento for d in descuentos)
                
                liquidacion.valor_neto = (liquidacion.comision_bruta + liquidacion.total_bonificaciones) - total_descuentos
                
                self.repo_liquidacion.actualizar(liquidacion, usuario)
            
            self._invalidar_caches()
            return True
        return False

    def remover_bonificacion_consolidada(self, id_liquidacion: int, usuario: str) -> bool:
        """
        Elimina la bonificación consolidada antigua (legacy) estableciendo el total a 0.
        Solo se usa para datos antiguos que no tienen detalle.
        """
        liquidacion = self.repo_liquidacion.obtener_por_id(id_liquidacion)
        if not liquidacion:
            return False

        # Resetear bonificaciones
        liquidacion.total_bonificaciones = 0
        
        # Recalcular Valor Neto
        descuentos = self.repo_descuento.listar_por_liquidacion(id_liquidacion)
        total_descuentos = sum(d.valor_descuento for d in descuentos)
        
        liquidacion.valor_neto = (liquidacion.comision_bruta + liquidacion.total_bonificaciones) - total_descuentos
        
        # Guardar cambios
        # Guardar cambios
        self.repo_liquidacion.actualizar(liquidacion, usuario)
        self._invalidar_caches()
        
        # Auditoría puede ser agregada aqui si es necesario
        return True
    
    # ==================== Métodos de Pagos ====================
    
    def programar_pago(
        self,
        id_liquidacion: int,
        id_asesor: int,
        valor: int,
        fecha_programada: str,
        medio_pago: str,
        datos_adicionales: Optional[Dict[str, Any]] = None,
        usuario: str = "SYSTEM"
    ) -> PagoAsesor:
        """
        Programa un pago para una liquidación aprobada.
        
        Args:
            id_liquidacion: ID de la liquidación
            id_asesor: ID del asesor
            valor: Valor del pago
            fecha_programada: Fecha programada (YYYY-MM-DD)
            medio_pago: Medio de pago
            datos_adicionales: Dict con referencia, observaciones, etc.
            usuario: Usuario que programa
        
        Returns:
            PagoAsesor creado
        
        Raises:
            ValueError: Si la liquidación no está aprobada
        """
        liquidacion = self.repo_liquidacion.obtener_por_id(id_liquidacion)
        if not liquidacion:
            raise ValueError(f"No se encontró la liquidación con ID {id_liquidacion}")
        
        if not liquidacion.esta_aprobada:
            raise ValueError("Solo se pueden programar pagos para liquidaciones aprobadas")
        
        pago = PagoAsesor(
            id_liquidacion_asesor=id_liquidacion,
            id_asesor=id_asesor,
            valor_pago=valor,
            fecha_programada=fecha_programada,
            medio_pago=medio_pago,
            referencia_pago=datos_adicionales.get("referencia") if datos_adicionales else None,
            observaciones_pago=datos_adicionales.get("observaciones") if datos_adicionales else None,
            estado_pago="Programado"
        )
        
        result = self.repo_pago.crear(pago, usuario)
        self._invalidar_caches()
        return result
    
    def registrar_pago(
        self,
        id_pago: int,
        fecha_pago: str,
        comprobante: str,
        usuario: str
    ) -> PagoAsesor:
        """
        Registra un pago como efectuado y actualiza la liquidación a 'Pagada'.
        
        Args:
            id_pago: ID del pago
            fecha_pago: Fecha efectiva del pago
            comprobante: Comprobante del pago
            usuario: Usuario que registra
        
        Returns:
            PagoAsesor actualizado
        
        Raises:
            ValueError: Si el pago no puede ser registrado
        """
        pago = self.repo_pago.obtener_por_id(id_pago)
        if not pago:
            raise ValueError(f"No se encontró el pago con ID {id_pago}")
        
        pago.marcar_como_pagado(fecha_pago, comprobante, usuario)
        pago_actualizado = self.repo_pago.actualizar(pago, usuario)
        
        # Actualizar liquidación a estado 'Pagada'
        liquidacion = self.repo_liquidacion.obtener_por_id(pago.id_liquidacion_asesor)
        if liquidacion:
            liquidacion.marcar_como_pagada(usuario)
            self.repo_liquidacion.actualizar(liquidacion, usuario)
        
        self._invalidar_caches()
        return pago_actualizado
    
    def rechazar_pago(self, id_pago: int, motivo: str, usuario: str) -> PagoAsesor:
        """
        Rechaza un pago.
        
        Args:
            id_pago: ID del pago
            motivo: Motivo del rechazo
            usuario: Usuario que rechaza
        
        Returns:
            PagoAsesor actualizado
        """
        pago = self.repo_pago.obtener_por_id(id_pago)
        if not pago:
            raise ValueError(f"No se encontró el pago con ID {id_pago}")
        
        pago.rechazar(motivo, usuario)
        result = self.repo_pago.actualizar(pago, usuario)
        self._invalidar_caches()
        return result
    
    def anular_pago(self, id_pago: int, usuario: str) -> PagoAsesor:
        """
        Anula un pago.
        
        Args:
            id_pago: ID del pago
            usuario: Usuario que anula
        
        Returns:
            PagoAsesor actualizado
        """
        pago = self.repo_pago.obtener_por_id(id_pago)
        if not pago:
            raise ValueError(f"No se encontró el pago con ID {id_pago}")
        
        
        pago.anular(usuario)
        result = self.repo_pago.actualizar(pago, usuario)
        self._invalidar_caches()
        return result
    
    # ==================== Consultas y Reportes ====================
    
    def listar_liquidaciones(
        self,
        id_asesor: Optional[int] = None,
        periodo: Optional[str] = None,
        estado: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Lista liquidaciones con filtros opcionales.
        
        Args:
            id_asesor: Filtrar por asesor
            periodo: Filtrar por período
            estado: Filtrar por estado
        
        Returns:
            Lista de diccionarios con datos de liquidaciones
        """
        liquidaciones = self.repo_liquidacion.listar_con_filtros(
            id_asesor=id_asesor,
            periodo=periodo,
            estado=estado
        )
        
        return [self._liquidacion_to_dict(liq) for liq in liquidaciones]

    # Integración Fase 4: Paginación
    @cache_manager.cached('liq_asesores:list_paginated', level=1, ttl=300)
    def listar_liq_asesores_paginado(
        self,
        page: int = 1,
        page_size: int = 25,
        estado: Optional[str] = None,
        periodo: Optional[str] = None,
        busqueda: Optional[str] = None,
        id_asesor: Optional[int] = None
    ):
        """
        Lista liquidaciones de asesores con paginación y filtros.
        """
        from src.dominio.modelos.pagination import PaginationParams, PaginatedResult

        
        params = PaginationParams(page=page, page_size=page_size)
        
        # Acceder a la conexión a través del repositorio (dependency injection)
        db_manager = self.repo_liquidacion.db_manager
        
        placeholder = db_manager.get_placeholder() if hasattr(db_manager, 'get_placeholder') else '?'
        
        with db_manager.obtener_conexion() as conn:
            cursor = db_manager.get_dict_cursor(conn)
            
            # Base query
            base_from = """
                FROM LIQUIDACIONES_ASESORES l
                JOIN ASESORES a ON l.ID_ASESOR = a.ID_ASESOR
                JOIN PERSONAS per ON a.ID_PERSONA = per.ID_PERSONA
            """
            
            conditions = []
            query_params = []
            
            if estado and estado != "Todos":
                conditions.append(f"l.ESTADO_LIQUIDACION = {placeholder}")
                query_params.append(estado)
                
            if periodo:
                conditions.append(f"l.PERIODO_LIQUIDACION LIKE {placeholder}")
                query_params.append(f"%{periodo}%")
                
            if id_asesor:
                 conditions.append(f"l.ID_ASESOR = {placeholder}")
                 query_params.append(id_asesor)
            
            if busqueda:
                conditions.append(f"""(
                    per.NOMBRE_COMPLETO LIKE {placeholder} OR
                    per.NUMERO_DOCUMENTO LIKE {placeholder} OR
                    CAST(l.ID_LIQUIDACION_ASESOR AS TEXT) LIKE {placeholder}
                )""")
                term = f"%{busqueda}%"
                query_params.extend([term, term, term])
            
            where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
            
            # Count
            count_query = f"SELECT COUNT(*) as total {base_from} {where_clause}"
            cursor.execute(count_query, query_params)
            total = cursor.fetchone()['total']
            
            # Data
            data_query = f"""
                SELECT 
                    l.ID_LIQUIDACION_ASESOR,
                    l.PERIODO_LIQUIDACION,
                    l.ESTADO_LIQUIDACION,
                    l.COMISION_BRUTA,
                    l.TOTAL_DESCUENTOS,
                    l.TOTAL_BONIFICACIONES,
                    l.VALOR_NETO_ASESOR,
                    l.PORCENTAJE_COMISION,
                    l.ID_CONTRATO_A,
                    l.ID_ASESOR,
                    per.NOMBRE_COMPLETO
                {base_from}
                {where_clause}
                ORDER BY l.PERIODO_LIQUIDACION DESC, l.ID_LIQUIDACION_ASESOR DESC
                LIMIT {placeholder} OFFSET {placeholder}
            """
            
            cursor.execute(data_query, query_params + [params.page_size, params.offset])
            
            items = []
            for row in cursor.fetchall():
                # Calcular porcentaje real
                pct = float(row['porcentaje_comision']) / 100.0 if row['porcentaje_comision'] else 0.0
                estado = row['estado_liquidacion']
                
                items.append({
                    'id_liquidacion_asesor': row['id_liquidacion_asesor'], # Compatibilidad con UI
                    'periodo_liquidacion': row['periodo_liquidacion'],
                    'estado_liquidacion': estado,
                    'comision_bruta': row['comision_bruta'],
                    'total_descuentos': row['total_descuentos'],
                    'total_bonificaciones': row['total_bonificaciones'] or 0,
                    'valor_neto_asesor': row['valor_neto_asesor'],
                    'porcentaje_real': pct,
                    'id_contrato_a': row['id_contrato_a'], # Legacy id display
                    'id_asesor': row['id_asesor'],
                    'nombre_asesor': row['nombre_completo'], # Extra field
                    'puede_editarse': estado == 'Pendiente',
                    'puede_aprobarse': estado == 'Pendiente',
                    'puede_anularse': estado not in ['Anulada', 'Pagada'] # Según lógica de negocio típica
                })
            
            return PaginatedResult(
                items=items,
                total=total,
                page=params.page,
                page_size=params.page_size
            )
            
    # Integración Fase 4: Métricas
    @cache_manager.cached('liq_asesores:metrics', level=1, ttl=60)
    def obtener_metricas_filtradas(
        self,
        estado: Optional[str] = None,
        periodo: Optional[str] = None,
        busqueda: Optional[str] = None,
        id_asesor: Optional[int] = None
    ) -> Dict[str, int]:
        """
        Calcula totales monetarios por estado según filtros aplicados.
        """
        """
        Calcula totales monetarios por estado según filtros aplicados.
        """
        
        # Acceder a la conexión a través del repositorio
        db_manager = self.repo_liquidacion.db_manager
        
        placeholder = db_manager.get_placeholder() if hasattr(db_manager, 'get_placeholder') else '?'
        
        with db_manager.obtener_conexion() as conn:
            cursor = db_manager.get_dict_cursor(conn)
            
            # Base query
            query = """
                SELECT 
                    l.ESTADO_LIQUIDACION,
                    SUM(l.VALOR_NETO_ASESOR) as total
                FROM LIQUIDACIONES_ASESORES l
                JOIN ASESORES a ON l.ID_ASESOR = a.ID_ASESOR
                JOIN PERSONAS per ON a.ID_PERSONA = per.ID_PERSONA
            """
            
            conditions = []
            query_params = []
            
            if estado and estado != "Todos":
                conditions.append(f"l.ESTADO_LIQUIDACION = {placeholder}")
                query_params.append(estado)
                
            if periodo:
                conditions.append(f"l.PERIODO_LIQUIDACION LIKE {placeholder}")
                query_params.append(f"%{periodo}%")
                
            if id_asesor:
                 conditions.append(f"l.ID_ASESOR = {placeholder}")
                 query_params.append(id_asesor)
            
            if busqueda:
                conditions.append(f"""(
                    per.NOMBRE_COMPLETO LIKE {placeholder} OR
                    per.NUMERO_DOCUMENTO LIKE {placeholder} OR
                    CAST(l.ID_LIQUIDACION_ASESOR AS TEXT) LIKE {placeholder}
                )""")
                term = f"%{busqueda}%"
                query_params.extend([term, term, term])
            
            where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""
            
            full_query = f"{query} {where_clause} GROUP BY l.ESTADO_LIQUIDACION"
            
            cursor.execute(full_query, query_params)
            
            resultados = {
                'Pendiente': 0,
                'Aprobada': 0,
                'Pagada': 0,
                'Anulada': 0
            }
            
            for row in cursor.fetchall():
                estado_row = row['estado_liquidacion']
                total_row = row['total'] if row['total'] else 0
                if estado_row in resultados:
                    resultados[estado_row] = total_row
                    
            return resultados
    
    def obtener_detalle_completo(self, id_liquidacion: int) -> Dict[str, Any]:
        """
        Obtiene el detalle completo de una liquidación incluyendo descuentos, pagos,
        y detalles de TODOS los contratos asociados.
        
        Args:
            id_liquidacion: ID de la liquidación
        
        Returns:
            Diccionario con toda la información
        
        Raises:
            ValueError: Si no se encuentra la liquidacion
        """
        liquidacion = self.repo_liquidacion.obtener_por_id(id_liquidacion)
        if not liquidacion:
            raise ValueError(f"No se encontró la liquidación con ID {id_liquidacion}")
        
        descuentos = self.repo_descuento.listar_por_liquidacion(id_liquidacion)
        pagos = self.repo_pago.listar_por_liquidacion(id_liquidacion)
        
        # Obtener bonificaciones asociadas
        bonificaciones = []
        if self.repo_bonificacion:
            try:
                bonif_entities = self.repo_bonificacion.listar_por_liquidacion(id_liquidacion)
                bonificaciones = [
                    {
                        "id_bonificacion_asesor": b.id_bonificacion_asesor,
                        "id_liquidacion_asesor": b.id_liquidacion_asesor,
                        "tipo_bonificacion": b.tipo_bonificacion,
                        "descripcion_bonificacion": b.descripcion_bonificacion,
                        "valor_bonificacion": b.valor_bonificacion,
                        "fecha_registro": b.fecha_registro
                    }
                    for b in bonif_entities
                ]
            except Exception as e:
                pass  # print(f"Error obteniendo bonificaciones del repositorio: {e}") [OpSec Removed]
                bonificaciones = []
        else:
             # Fallback manual query if repo not provided
             try:
                with self.repo_liquidacion.db_manager.obtener_conexion() as conn:
                    cursor = self.repo_liquidacion.db_manager.get_dict_cursor(conn)
                    ph = self.repo_liquidacion.db_manager.get_placeholder()
                    query = f"SELECT * FROM BONIFICACIONES_ASESORES WHERE ID_LIQUIDACION_ASESOR = {ph} ORDER BY FECHA_REGISTRO DESC"
                    cursor.execute(query, (id_liquidacion,))
                    bonif_rows = cursor.fetchall()
                    bonificaciones = [
                        {
                            "id_bonificacion_asesor": row.get('ID_BONIFICACION_ASESOR') or row.get('id_bonificacion_asesor'),
                            "id_liquidacion_asesor": row.get('ID_LIQUIDACION_ASESOR') or row.get('id_liquidacion_asesor'),
                            "tipo_bonificacion": row.get('TIPO_BONIFICACION') or row.get('tipo_bonificacion'),
                            "descripcion_bonificacion": row.get('DESCRIPCION_BONIFICACION') or row.get('descripcion_bonificacion'),
                            "valor_bonificacion": row.get('VALOR_BONIFICACION') or row.get('valor_bonificacion'),
                            "fecha_registro": row.get('FECHA_REGISTRO') or row.get('fecha_registro')
                        }
                        for row in bonif_rows
                    ]
             except Exception as e:
                pass  # print(f"Error obteniendo bonificaciones: {e}") [OpSec Removed]
                bonificaciones = []

        # FIX: Si no hay bonificaciones detalladas pero el total es > 0, crear una sintética
        # Esto pasa porque en la creación solo se guardaba el total y no los items individuales
        total_bonif = liquidacion.total_bonificaciones or 0
        if not bonificaciones and total_bonif > 0:
            bonificaciones.append({
                "id_bonificacion_asesor": -1, # ID temporal
                "id_liquidacion_asesor": id_liquidacion,
                "tipo_bonificacion": "Bonificación Consolidada",
                "descripcion_bonificacion": "Total de bonificaciones (registrado sin desglose)",
                "valor_bonificacion": total_bonif,
                "fecha_registro": liquidacion.fecha_creacion
            })
            
        # Obtener lista de contratos asociados desde la tabla intermedia
        contratos_asociados = self.repo_liquidacion.obtener_contratos_de_liquidacion(id_liquidacion)
        
        # LEGACY: Obtener información del contrato legacy (si existe)
        contrato_info = None
        propiedad_info = None
        
        if liquidacion.id_contrato_a and self.repo_contrato_arrendamiento:
            try:
                contrato = self.repo_contrato_arrendamiento.obtener_por_id(liquidacion.id_contrato_a)
                if contrato:
                    contrato_info = {
                        "id_contrato_a": contrato.id_contrato_a,
                        "id_propiedad": contrato.id_propiedad,
                        "canon_arrendamiento": contrato.canon_arrendamiento,
                    }
                    
                    # Si tenemos repo de propiedad, obtener detalles de la propiedad
                    if self.repo_propiedad and contrato.id_propiedad:
                        propiedad = self.repo_propiedad.obtener_por_id(contrato.id_propiedad)
                        if propiedad:
                            propiedad_info = {
                                "id_propiedad": propiedad.id_propiedad,
                                "direccion_propiedad": propiedad.direccion_propiedad,
                                "matricula_inmobiliaria": propiedad.matricula_inmobiliaria,
                            }
            except Exception as e:
                pass  # print(f"Error obteniendo detalles de contrato/propiedad legacy: {e}") [OpSec Removed]
        
        return {
            "liquidacion": self._liquidacion_to_dict(liquidacion),
            "contratos": contratos_asociados,  # NUEVA: Lista de todos los contratos asociados
            "descuentos": [self._descuento_to_dict(d) for d in descuentos],
            "bonificaciones": bonificaciones,  # NUEVA: Lista de bonificaciones
            "pagos": [self._pago_to_dict(p) for p in pagos],
            "contrato": contrato_info,  # LEGACY: Mantenido por compatibilidad
            "propiedad": propiedad_info  # LEGACY: Mantenido por compatibilidad
        }
    
    def obtener_resumen_por_asesor(self, id_asesor: int) -> Dict[str, Any]:
        """
        Obtiene resumen de liquidaciones de un asesor.
        
        Args:
            id_asesor: ID del asesor
        
        Returns:
            Diccionario con resumen
        """
        liquidaciones = self.repo_liquidacion.listar_por_asesor(id_asesor)
        
        total_pendiente = sum(
            liq.valor_neto_asesor for liq in liquidaciones if liq.esta_pendiente
        )
        total_aprobado = sum(
            liq.valor_neto_asesor for liq in liquidaciones if liq.esta_aprobada
        )
        total_pagado = sum(
            liq.valor_neto_asesor for liq in liquidaciones if liq.esta_pagada
        )
        
        return {
            "id_asesor": id_asesor,
            "total_liquidaciones": len(liquidaciones),
            "total_pendiente": total_pendiente,
            "total_aprobado": total_aprobado,
            "total_pagado": total_pagado,
            "pendientes_aprobacion": sum(1 for liq in liquidaciones if liq.esta_pendiente),
            "pendientes_pago": sum(1 for liq in liquidaciones if liq.esta_aprobada)
        }
    
    def obtener_liquidaciones_pendientes_aprobacion(self) -> List[Dict[str, Any]]:
        """
        Obtiene todas las liquidaciones pendientes de aprobación.
        
        Returns:
            Lista de liquidaciones pendientes
        """
        liquidaciones = self.repo_liquidacion.listar_por_estado("Pendiente")
        return [self._liquidacion_to_dict(liq) for liq in liquidaciones]
    
    # ==================== Métodos Auxiliares ====================
    
    def _liquidacion_to_dict(self, liq: LiquidacionAsesor) -> Dict[str, Any]:
        """Convierte entidad a diccionario para UI"""
        return {
            "id_liquidacion_asesor": liq.id_liquidacion_asesor,
            "id_contrato_a": liq.id_contrato_a,
            "id_asesor": liq.id_asesor,
            "nombre_asesor": liq.nombre_asesor if hasattr(liq, 'nombre_asesor') else None,
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
            "puede_anularse": liq.puede_anularse
        }
    
    def _descuento_to_dict(self, desc: DescuentoAsesor) -> Dict[str, Any]:
        """Convierte descuento a diccionario"""
        return {
            "id_descuento_asesor": desc.id_descuento_asesor,
            "id_liquidacion_asesor": desc.id_liquidacion_asesor,
            "tipo_descuento": desc.tipo_descuento,
            "descripcion_descuento": desc.descripcion_descuento,
            "valor_descuento": desc.valor_descuento,
            "fecha_registro": desc.fecha_registro
        }
    
    def _pago_to_dict(self, pago: PagoAsesor) -> Dict[str, Any]:
        """Convierte pago a diccionario"""
        return {
            "id_pago_asesor": pago.id_pago_asesor,
            "id_liquidacion_asesor": pago.id_liquidacion_asesor,
            "id_asesor": pago.id_asesor,
            "valor_pago": pago.valor_pago,
            "fecha_pago": pago.fecha_pago,
            "fecha_programada": pago.fecha_programada,
            "medio_pago": pago.medio_pago,
            "referencia_pago": pago.referencia_pago,
            "estado_pago": pago.estado_pago,
            "motivo_rechazo": pago.motivo_rechazo,
            "comprobante_pago": pago.comprobante_pago,
            "observaciones_pago": pago.observaciones_pago,
            "fecha_confirmacion": pago.fecha_confirmacion
        }
