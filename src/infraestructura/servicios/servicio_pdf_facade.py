"""
Servicio PDF Facade Unificado
==============================
Punto de entrada único que unifica el servicio legacy y las nuevas capacidades élite.
Mantiene 100% compatibilidad con código existente mientras expone nuevas funcionalidades.

Autor: Sistema de Gestión Inmobiliaria
Fecha: 2026-01-18
"""

from typing import Dict, Any, Optional
from pathlib import Path
import logging

# Setup logger
logger = logging.getLogger('PDFElite')

# Importar servicio legacy
from src.infraestructura.servicios.servicio_documentos_pdf import ServicioDocumentosPDF

# Importar nuevos templates élite
from .pdf_elite.templates.contrato_template import ContratoArrendamientoElite
from .pdf_elite.templates.certificado_template import CertificadoTemplate
from .pdf_elite.templates.estado_cuenta_elite import EstadoCuentaElite
from .pdf_elite.core.config import config


class ServicioPDFFacade:
    """
    Facade unificador de servicios PDF
    
    Proporciona un punto de entrada único que:
    - Mantiene 100% compatibilidad con ServicioDocumentosPDF legacy
    - Expone nuevos generadores élite
    - Permite migración gradual del código existente
    
    Attributes:
        legacy_service: Instancia del servicio legacy
        elite_enabled: Si habilitar características élite
        
    Example:
        >>> # Uso legacy (100% compatible)
        >>> facade = ServicioPDFFacade()
        >>> pdf = facade.generar_comprobante_recaudo(datos)
        
        >>> # Uso élite nuevo
        >>> pdf = facade.generar_contrato_elite(datos)
    """
    
    def __init__(
        self,
        output_dir: Optional[str] = None,
        elite_enabled: bool = True
    ):
        """
        Inicializa el facade
        
        Args:
            output_dir: Directorio de salida (usa el configurado si es None)
            elite_enabled: Habilitar características élite
        """
        # Servicio legacy
        self.legacy_service = ServicioDocumentosPDF(
            output_dir=output_dir or "documentos_generados"
        )
        
        # Configuración
        self.elite_enabled = elite_enabled
        self.output_dir = Path(output_dir) if output_dir else config.output_dir
        
        # Generadores élite (lazy initialization)
        self._contrato_gen: Optional[ContratoArrendamientoElite] = None
        self._certificado_gen: Optional[CertificadoTemplate] = None
        self._estado_cuenta_gen: Optional[EstadoCuentaElite] = None
    
    # ========================================================================
    # MÉTODOS LEGACY (100% COMPATIBILIDAD)
    # ========================================================================
    
    def generar_comprobante_recaudo(self, datos: Dict[str, Any]) -> str:
        """
        Genera comprobante de recaudo (método legacy)
        
        Mantiene 100% compatibilidad con código existente.
        
        Args:
            datos: Datos del comprobante
            
        Returns:
            Path del PDF generado
        """
        return self.legacy_service.generar_comprobante_recaudo(datos)
    
    def generar_estado_cuenta(self, datos: Dict[str, Any]) -> str:
        """
        Genera estado de cuenta (método legacy)
        
        Args:
            datos: Datos del estado de cuenta
            
        Returns:
            Path del PDF generado
        """
        return self.legacy_service.generar_estado_cuenta(datos)
    
    def generar_cuenta_cobro_asesor(self, datos: Dict[str, Any]) -> str:
        """
        Genera cuenta de cobro de asesor (método legacy)
        
        Args:
            datos: Datos de la cuenta de cobro
            
        Returns:
            Path del PDF generado
        """
        return self.legacy_service.generar_cuenta_cobro_asesor(datos)
    
    def generar_checklist_desocupacion(self, datos: Dict[str, Any]) -> str:
        """
        Genera checklist de desocupación (método legacy)
        
        Args:
            datos: Datos del checklist
            
        Returns:
            Path del PDF generado
        """
        return self.legacy_service.generar_checklist_desocupacion(datos)
    
    # ========================================================================
    # MÉTODOS ÉLITE (NUEVAS CAPACIDADES)
    # ========================================================================
    
    def generar_contrato_elite(
        self,
        datos: Dict[str, Any],
        usar_borrador: bool = False
    ) -> str:
        """
        Genera contrato de arrendamiento élite
        
        Nuevo método con características avanzadas:
        - Cláusulas dinámicas
        - QR de verificación
        - Marca de agua para borradores
        - Validación robusta
        
        Args:
            datos: Datos del contrato
            usar_borrador: Si marcar como borrador
            
        Returns:
            Path del PDF generado
            
        Raises:
            ValueError: Si elite no está habilitado o datos inválidos
        """
        if not self.elite_enabled:
            raise ValueError("Características élite no habilitadas")
        
        logger.debug(f"🔧 SERVICE LAYER: Facade method called - generar_contrato_elite")
        logger.debug(f"📦 Data keys received: {list(datos.keys())}")
        logger.debug(f"🎯 Template type: {'borrador' if usar_borrador else 'oficial'}")
        logger.debug(f"📂 Output directory: {self.output_dir}")
        
        # Lazy initialization del generador
        if not self._contrato_gen:
            self._contrato_gen = ContratoArrendamientoElite(self.output_dir)
        
        # Agregar estado si es borrador
        if usar_borrador:
            datos['estado'] = 'borrador'
        
        # Generar contrato
        path = self._contrato_gen.generate_safe(datos)
        
        if not path:
            raise ValueError("Error generando contrato élite")
        
        return str(path)
    
    def generar_certificado_elite(
        self,
        datos: Dict[str, Any]
    ) -> str:
        """
        Genera certificado profesional élite
        
        Tipos soportados:
        - paz_y_salvo: Certificado de paz y salvo
        - cumplimiento: Certificado de cumplimiento
        - residencia: Certificado de residencia
        - general: Certificación general
        
        Args:
            datos: Datos del certificado (debe incluir 'tipo')
            
        Returns:
            Path del PDF generado
        """
        if not self.elite_enabled:
            raise ValueError("Características élite no habilitadas")
        
        logger.debug(f"🔧 SERVICE LAYER: Facade method called - generar_certificado_elite")
        logger.debug(f"📦 Data keys received: {list(datos.keys())}")
        logger.debug(f"🏅 Certificate type: {datos.get('tipo', 'unknown')}")
        
        if not self._certificado_gen:
            self._certificado_gen = CertificadoTemplate(self.output_dir)
        
        path = self._certificado_gen.generate_safe(datos)
        
        if not path:
            raise ValueError("Error generando certificado élite")
        
        return str(path)
    
    def generar_estado_cuenta_elite(
        self,
        datos: Dict[str, Any]
    ) -> str:
        """
        Genera estado de cuenta mejorado (élite)
        
        Mejoras sobre versión legacy:
        - Tabla de movimientos profesional
        - Resumen financiero destacado
        - Zebra striping para mejor legibilidad
        - QR de verificación
        
        Args:
            datos: Datos del estado de cuenta
            
        Returns:
            Path del PDF generado
        """
        if not self.elite_enabled:
            raise ValueError("Características élite no habilitadas")
        
        logger.debug(f"🔧 SERVICE LAYER: Facade method called - generar_estado_cuenta_elite")
        logger.debug(f"📦 Data keys received: {list(datos.keys())}")
        logger.debug(f"📊 Movements count: {len(datos.get('movimientos', []))}")
        
        if not self._estado_cuenta_gen:
            self._estado_cuenta_gen = EstadoCuentaElite(self.output_dir)
        
        path = self._estado_cuenta_gen.generate_safe(datos)
        
        if not path:
            raise ValueError("Error generando estado de cuenta élite")
        
        return str(path)
    
    # ========================================================================
    # MÉTODOS DE MIGRACIÓN
    # ========================================================================
    
    def migrar_a_elite(
        self,
        tipo_documento: str,
        datos: Dict[str, Any]
    ) -> str:
        """
        Migra documento legacy a versión élite
        
        Detecta automáticamente el tipo y usa el generador élite apropiado.
        
        Args:
            tipo_documento: Tipo ('contrato', 'certificado', 'estado_cuenta')
            datos: Datos del documento
            
        Returns:
            Path del PDF generado
        """
        if tipo_documento == 'contrato':
            return self.generar_contrato_elite(datos)
        elif tipo_documento == 'certificado':
            return self.generar_certificado_elite(datos)
        elif tipo_documento == 'estado_cuenta':
            return self.generar_estado_cuenta_elite(datos)
        else:
            raise ValueError(f"Tipo de documento no soportado: {tipo_documento}")
    
    # ========================================================================
    # MÉTODOS DE UTILIDAD
    # ========================================================================
    
    def listar_capacidades_elite(self) -> Dict[str, list]:
        """
        Lista capacidades élite disponibles
        
        Returns:
            Diccionario con tipos de documentos y sus características
        """
        return {
            'contratos': [
                'Cláusulas dinámicas',
                'QR de verificación',
                'Marcas de agua',
                'Validación robusta',
                'Firma digital'
            ],
            'certificados': [
                'Diseño elegante',
                'Múltiples tipos',
                'QR de verificación',
                'Formateo de fechas',
                'Validez configurable'
            ],
            'estados_cuenta': [
                'Tabla profesional',
                'Zebra striping',
                'Resumen financiero',
                'Saldo corrido',
                'QR de verificación'
            ]
        }
    
    def get_version_info(self) -> Dict[str, str]:
        """
        Obtiene información de versión
        
        Returns:
            Diccionario con información de versiones
        """
        return {
            'sistema': 'PDF Elite',
            'version': '1.0.0',
            'legacy_compatible': 'True',
            'elite_enabled': str(self.elite_enabled)
        }


__all__ = ['ServicioPDFFacade']
