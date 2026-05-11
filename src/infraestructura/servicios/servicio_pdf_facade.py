"""
Servicio PDF Facade Unificado
==============================
Punto de entrada único que unifica el servicio legacy y las nuevas capacidades élite.
Mantiene 100% compatibilidad con código existente mientras expone nuevas funcionalidades.

Autor: Sistema de Gestión Inmobiliaria
Fecha: 2026-01-18
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Setup logger
logger = logging.getLogger("PDFElite")

# Importar servicio legacy
from src.infraestructura.servicios.servicio_documentos_pdf import ServicioDocumentosPDF

from .pdf_elite.core.config import config
from .pdf_elite.templates.certificado_template import CertificadoTemplate

# Importar nuevos templates élite
from .pdf_elite.templates.contrato_template import ContratoArrendamientoElite
from .pdf_elite.templates.contrato_template_local import (
    ContratoArrendamientoElite as ContratoLocalElite,
)
from .pdf_elite.templates.contrato_template_mandato import ContratoMandatoElite
from .pdf_elite.templates.estado_cuenta_elite import EstadoCuentaElite
from .pdf_elite.templates.recibo_recaudo_elite import ReciboRecaudoElite
from .pdf_elite.templates.informe_recaudos_elite import InformeRecaudosElite


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

    def __init__(self, output_dir: Optional[str] = None, elite_enabled: bool = True):
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
        self, datos: Dict[str, Any], usar_borrador: bool = False
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

        logger.debug("🔧 SERVICE LAYER: Facade method called - generar_contrato_elite")
        logger.debug(f"📦 Data keys received: {list(datos.keys())}")
        logger.debug(f"🎯 Template type: {'borrador' if usar_borrador else 'oficial'}")
        logger.debug(f"📂 Output directory: {self.output_dir}")

        # Determinación de tipo de contrato y propiedad
        tipo_contrato = datos.get("tipo_contrato", "Arrendamiento")
        tipo_propiedad = datos.get("inmueble", {}).get("tipo", "")

        logger.debug(f"📋 Contract Type: {tipo_contrato}")
        logger.debug(f"🏠 Property Type: {tipo_propiedad}")

        # Lógica de selección de plantilla - Instanciación local para Thread-Safety
        if tipo_contrato.upper() == "MANDATO":
            generator = ContratoMandatoElite(self.output_dir)
        elif tipo_contrato == "Arrendamiento":
            if tipo_propiedad == "Local Comercial":
                generator = ContratoLocalElite(self.output_dir)
            else:
                # Default Arrendamiento (Vivienda/Otros)
                generator = ContratoArrendamientoElite(self.output_dir)
        else:
            # Fallback a Arrendamiento estándar si no coincide nada
            logger.warning(
                f"⚠️ Tipo de contrato desconocido: {tipo_contrato}. Usando estándar."
            )
            generator = ContratoArrendamientoElite(self.output_dir)

        # Agregar estado si es borrador
        if usar_borrador:
            datos["estado"] = "borrador"

        # Generar contrato
        path = generator.generate_safe(datos)

        if not path:
            raise ValueError("Error generando contrato élite")

        return str(path)

    def generar_certificado_elite(self, datos: Dict[str, Any]) -> str:
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

        logger.debug(
            "🔧 SERVICE LAYER: Facade method called - generar_certificado_elite"
        )
        logger.debug(f"📦 Data keys received: {list(datos.keys())}")
        logger.debug(f"🏅 Certificate type: {datos.get('tipo', 'unknown')}")

        generator = CertificadoTemplate(self.output_dir)
        path = generator.generate_safe(datos)

        if not path:
            raise ValueError("Error generando certificado élite")

        return str(path)

    def generar_estado_cuenta_elite(self, datos: Dict[str, Any]) -> str:
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

        logger.debug(
            "🔧 SERVICE LAYER: Facade method called - generar_estado_cuenta_elite"
        )
        logger.debug(f"📦 Data keys received: {list(datos.keys())}")
        logger.debug(f"📊 Movements count: {len(datos.get('movimientos', []))}")

        generator = EstadoCuentaElite(self.output_dir)
        path = generator.generate_safe(datos)

        if not path:
            raise ValueError("Error generando estado de cuenta élite")

        return str(path)

    def generar_recibo_recaudo_elite(self, datos: Dict[str, Any]) -> str:
        """
        Genera recibo de pago para recaudos (élite)

        Args:
            datos: Datos del recaudo

        Returns:
            Path del PDF generado
        """
        if not self.elite_enabled:
            raise ValueError("Características élite no habilitadas")

        logger.debug(
            "🔧 SERVICE LAYER: Facade method called - generar_recibo_recaudo_elite"
        )
        logger.debug(f"📦 Data keys received: {list(datos.keys())}")

        generator = ReciboRecaudoElite(self.output_dir)
        path = generator.generate_safe(datos)

        if not path:
            raise ValueError("Error generando recibo de recaudo élite")

        return str(path)

    def generar_informe_recaudos(self, datos: Dict[str, Any]) -> str:
        """
        Genera informe consolidado de recaudos.

        Args:
            datos: Datos del informe (periodo_inicio, periodo_fin, resumen, detalles)

        Returns:
            Path del PDF generado
        """
        if not self.elite_enabled:
            raise ValueError("Características élite no habilitadas")

        logger.debug(
            "🔧 SERVICE LAYER: Facade method called - generar_informe_recaudos"
        )
        logger.debug(f"📦 Data keys received: {list(datos.keys())}")

        generator = InformeRecaudosElite(self.output_dir)
        path = generator.generate_safe(datos)

        if not path:
            raise ValueError("Error generando informe de recaudos")

        return str(path)

    def generar_lote_recibos_recaudo_zip(
        self, lista_datos: List[Dict[str, Any]], filename_prefix: str = "lote_recibos_recaudo"
    ) -> str:
        """Genera un lote de recibos de recaudo élite y los comprime en un archivo ZIP.

        Args:
            lista_datos: Lista de diccionarios con datos formateados para recibo recaudo élite.
            filename_prefix: Prefijo para el archivo ZIP de salida.

        Returns:
            Ruta absoluta del archivo ZIP generado.
        """
        if not self.elite_enabled:
            raise ValueError("Características élite no habilitadas")

        logger.debug(
            "🔧 SERVICE LAYER: Facade method called - generar_lote_recibos_recaudo_zip"
        )
        logger.debug(f"📦 Total recibos a generar: {len(lista_datos)}")

        return self.legacy_service.generar_lote_recibos_recaudo_zip(
            lista_datos=lista_datos,
            facade=self,
            filename_prefix=filename_prefix,
        )

    def generar_lote_liquidaciones_elite_zip(
        self, lista_datos: List[Dict[str, Any]], filename_prefix: str = "lote_liquidaciones_periodo"
    ) -> str:
        """Genera un lote de estados de cuenta élite (liquidaciones) y los comprime en un archivo ZIP.

        Args:
            lista_datos: Lista de diccionarios con datos formateados para estado de cuenta élite.
            filename_prefix: Prefijo para el archivo ZIP de salida.

        Returns:
            Ruta absoluta del archivo ZIP generado.
        """
        if not self.elite_enabled:
            raise ValueError("Características élite no habilitadas")

        logger.debug(
            "🔧 SERVICE LAYER: Facade method called - generar_lote_liquidaciones_elite_zip"
        )
        logger.debug(f"📦 Total liquidaciones a generar: {len(lista_datos)}")

        # Reutilizamos la lógica de compresión del servicio legacy pero pasando el método elite
        import zipfile
        from concurrent.futures import ThreadPoolExecutor, as_completed

        zip_filename = f"{filename_prefix}_{datetime.now().strftime('%Y%m%d%H%M%S')}.zip"
        zip_path = self.output_dir / zip_filename

        generated_files: List[Path] = []

        def _generate_one(datos_pdf: Dict[str, Any]) -> Optional[str]:
            """Worker para generar una liquidación individual (thread-safe)."""
            try:
                # IMPORTANTE: Usamos el generador ELITE
                path = self.generar_estado_cuenta_elite(datos_pdf)
                return path
            except Exception as e:
                logger.error(
                    f"Error generando liquidación PDF para ID {datos_pdf.get('id')}: {e}"
                )
                return None

        # Ejecutar en paralelo (I/O bound)
        with ThreadPoolExecutor(max_workers=5) as executor:
            future_to_id = {
                executor.submit(_generate_one, d): d.get("id") for d in lista_datos
            }

            for future in as_completed(future_to_id):
                path = future.result()
                if path:
                    generated_files.append(Path(path))

        if not generated_files:
            raise ValueError("No se pudo generar ninguna liquidación PDF para el lote")

        # Crear ZIP
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for file_path in generated_files:
                if file_path.exists():
                    zf.write(file_path, arcname=file_path.name)
                    try:
                        file_path.unlink()
                    except Exception:
                        pass

        logger.info(f"ZIP de liquidaciones generado con {len(generated_files)} archivos en: {zip_path}")
        return str(zip_path.absolute())

    # ========================================================================
    # MÉTODOS DE MIGRACIÓN
    # ========================================================================

    def migrar_a_elite(self, tipo_documento: str, datos: Dict[str, Any]) -> str:
        """
        Migra documento legacy a versión élite

        Detecta automáticamente el tipo y usa el generador élite apropiado.

        Args:
            tipo_documento: Tipo ('contrato', 'certificado', 'estado_cuenta')
            datos: Datos del documento

        Returns:
            Path del PDF generado
        """
        if tipo_documento == "contrato":
            return self.generar_contrato_elite(datos)
        elif tipo_documento == "certificado":
            return self.generar_certificado_elite(datos)
        elif tipo_documento == "estado_cuenta":
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
            "contratos": [
                "Cláusulas dinámicas",
                "QR de verificación",
                "Marcas de agua",
                "Validación robusta",
                "Firma digital",
            ],
            "certificados": [
                "Diseño elegante",
                "Múltiples tipos",
                "QR de verificación",
                "Formateo de fechas",
                "Validez configurable",
            ],
            "estados_cuenta": [
                "Tabla profesional",
                "Zebra striping",
                "Resumen financiero",
                "Saldo corrido",
                "QR de verificación",
            ],
        }

    def get_version_info(self) -> Dict[str, str]:
        """
        Obtiene información de versión

        Returns:
            Diccionario con información de versiones
        """
        return {
            "sistema": "PDF Elite",
            "version": "1.0.0",
            "legacy_compatible": "True",
            "elite_enabled": str(self.elite_enabled),
        }


__all__ = ["ServicioPDFFacade"]
