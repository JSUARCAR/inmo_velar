"""
Template para Certificados Oficiales
====================================
Generador élite de certificados profesionales con diseño elegante.

Autor: Sistema de Gestión Inmobiliaria
Fecha: 2026-01-18
"""

from datetime import datetime
from pathlib import Path
from typing import Any, Dict

from reportlab.lib import colors
from ..components.tables import AdvancedTable
from ..core.config import Colors, config
from ..styles.themes import Themes
from .base_template import BaseDocumentTemplate


class CertificadoTemplate(BaseDocumentTemplate):
    """
    Generador de certificados oficiales

    Crea certificados profesionales para:
    - Paz y Salvo de arrendamiento
    - Cumplimiento de pagos
    - Órdenes de servicio completadas
    - Certificaciones administrativas

    Example:
        >>> gen = CertificadoTemplate()
        >>> data = {
        ...     'certificado_id': 456,
        ...     'tipo': 'paz_y_salvo',
        ...     'beneficiario': {...},
        ...     'contenido': '...',
        ...     'firmante': {...}
        ... }
        >>> pdf_path = gen.generate(data)
    """

    def __init__(self, output_dir: Path = None):
        """Inicializa el generador de certificados"""
        super().__init__(output_dir)
        # Usar tema elegante para certificados
        self.theme = Themes.CERTIFICATE

    def validate_data(self, data: Dict[str, Any]) -> bool:
        """Valida datos del certificado"""
        self._require_fields(
            data, "certificado_id", "tipo", "beneficiario", "contenido", "firmante", "fecha"
        )
        return True

    def generate(self, data: Dict[str, Any]) -> Path:
        """
        Genera el certificado en PDF

        Args:
            data: Diccionario con datos del certificado

        Returns:
            Path del PDF generado
        """
        # Habilitar QR de verificación
        self.enable_verification_qr("certificado", data["certificado_id"])

        # Configurar Header/Footer con Membrete
        self.set_header_footer(self._header_footer_with_features, self._header_footer_with_features)

        # Crear documento
        filename = self._generate_filename("certificado", data["certificado_id"])
        titulo = self._get_titulo_certificado(data["tipo"])
        self.create_document(filename, titulo)

        # Construir contenido
        self._add_header_elegante(data, titulo)
        self._add_contenido(data)
        self._add_validez(data)
        self._add_firma_certificado(data)

        # Construir PDF
        return self.build()

    def _get_titulo_certificado(self, tipo: str) -> str:
        """Obtiene título según tipo de certificado"""
        titulos = {
            "paz_y_salvo": "CERTIFICADO DE PAZ Y SALVO",
            "cumplimiento": "CERTIFICADO DE CUMPLIMIENTO",
            "residencia": "CERTIFICADO DE RESIDENCIA",
            "general": "CERTIFICACIÓN",
        }
        return titulos.get(tipo, "CERTIFICACIÓN")

    def _add_header_elegante(self, data: Dict[str, Any], titulo: str) -> None:
        """Agrega header elegante del certificado"""
        from reportlab.platypus import HRFlowable

        # Espacio superior (Ajustado para el membrete)
        self.add_spacer(1.5)

        # Título del certificado
        self.add_title_main(titulo)

        # Número de certificado
        self.add_paragraph(
            f"<font size=10>No. {data['certificado_id']:08d}</font>",
            style_name="Small",
            alignment="center",
        )

        self.add_spacer(0.4)

    def _add_contenido(self, data: Dict[str, Any]) -> None:
        """Agrega contenido del certificado"""
        # Introducción
        self.add_paragraph(
            f"<b>EL SUSCRITO REPRESENTANTE LEGAL DE {config.empresa_nombre.upper()}</b>",
            style_name="Body",
            alignment="center",
        )

        self.add_spacer(0.2)

        # Certifica que...
        self.add_paragraph("<b>CERTIFICA QUE:</b>", style_name="BodyBold", alignment="center")

        self.add_spacer(0.3)

        # Información del beneficiario
        if "beneficiario" in data:
            beneficiario = data["beneficiario"]
            self.add_paragraph(
                f"<b>{beneficiario.get('nombre', 'N/A')}</b>, identificado(a) con "
                f"{beneficiario.get('tipo_documento', 'C.C.')} No. "
                f"<b>{beneficiario.get('documento', 'N/A')}</b>",
                style_name="Body",
            )
            self.add_spacer(0.2)

        # Contenido principal del certificado
        contenido = data["contenido"]

        # Si es string, convertir a lista de párrafos
        if isinstance(contenido, str):
            parrafos = contenido.split("\n\n")
        else:
            parrafos = contenido

        for parrafo in parrafos:
            if parrafo.strip():
                self.add_paragraph(parrafo.strip(), style_name="Body")
                self.add_spacer(0.15)

        self.add_spacer(0.3)

    def _add_validez(self, data: Dict[str, Any]) -> None:
        """Agrega información de validez"""
        # Fecha y lugar de expedición
        fecha = data.get("fecha", datetime.now().strftime("%Y-%m-%d"))
        ciudad = data.get("ciudad", "Bogotá D.C.")

        self.add_paragraph(
            f"Se expide en <b>{ciudad}</b>, a los <b>{self._formatear_fecha(fecha)}</b>.",
            style_name="Body",
        )

        # Validez
        validez_dias = data.get("validez_dias", 30)
        self.add_paragraph(
            f"<i>Certificado válido por {validez_dias} días calendario.</i>",
            style_name="Small",
            alignment="justify",
        )

        self.add_spacer(0.5)

    def _add_firma_certificado(self, data: Dict[str, Any]) -> None:
        """Agrega firma del certificado"""
        firmante = data["firmante"]

        signatures = [
            (
                "REPRESENTANTE LEGAL",
                f"{firmante.get('nombre', 'N/A')}\n"
                f"{firmante.get('cargo', 'Gerente')}\n"
                f"{firmante.get('documento', 'N/A')}",
            )
        ]

        table = AdvancedTable.create_signature_table(signatures)
        self.story.append(table)

        # Nota de verificación
        self.add_legal_footer_text(
            "La autenticidad de este certificado puede ser verificada escaneando el código QR "
            "o consultando en www.inmovelar.com/verificar"
        )

    def _formatear_fecha(self, fecha_str: str) -> str:
        """Formatea fecha en texto elegante"""
        try:
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d")
            meses = [
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
            mes = meses[fecha.month - 1]
            return f"{fecha.day} días del mes de {mes} de {fecha.year}"
        except:
            return fecha_str

    def _header_footer_with_features(self, canvas_obj, doc):
        """
        Override completo para evitar el header por defecto 
        """
        # 0. Dibujar MEMBRETE (Fondo completo)
        current_dir = Path(__file__).parent
        membrete_path = current_dir / "VELAR INMOBILIARIA_membrete_modificada.png"
        
        try:
            if membrete_path.exists():
                # Dibujar imagen cubriendo toda la página
                page_width, page_height = doc.pagesize
                # mask='auto' maneja transparencias si es PNG
                canvas_obj.drawImage(str(membrete_path), 0, 0, width=page_width, height=page_height, mask='auto', preserveAspectRatio=False)
        except Exception as e:
            # Fallo silencioso o log mínimo para no romper generación
            print(f"Advertencia: No se pudo cargar fondo {membrete_path}: {e}")

        # 1. Agregar marca de agua si aplica (logic from Base)
        if self.watermark_text:
            from ..components.watermarks import Watermark
            Watermark.add_text_watermark(
                canvas_obj,
                text=self.watermark_text,
                opacity=self.watermark_opacity,
                position=self.watermark_style,
            )
            
        # 2. Footer simple (SOLO Página)
        canvas_obj.saveState()
        
        # Página y Timestamp
        page_num = canvas_obj.getPageNumber()
        canvas_obj.setFont('Helvetica', 8)
        canvas_obj.setFillColor(colors.gray)
        
        center_x = doc.pagesize[0] / 2
        
        # Centrado Página (más abajo que la dirección)
        canvas_obj.drawCentredString(center_x, 20, f"Página {page_num}")
        
        # 4. Textos Verticales en Márgenes
        canvas_obj.setFont('Helvetica', 8)
        canvas_obj.setFillColor(colors.lightgrey) # Color tenue para no distraer
        
        from datetime import datetime
        dt_str = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        # Margen Izquierdo (Vertical)
        canvas_obj.saveState()
        canvas_obj.translate(30, 250) # Ajustar posición X,Y
        canvas_obj.rotate(90)
        canvas_obj.drawString(0, 0, "Impreso por Inmobiliaria Velar SAS - NIT 901.703.515 - Correo: inmobiliariavelarsasaxm@gmail.com")
        canvas_obj.restoreState()
        
        # Margen Derecho (Vertical)
        canvas_obj.saveState()
        canvas_obj.translate(doc.pagesize[0] - 30, 250)
        canvas_obj.rotate(90)
        canvas_obj.drawString(0, 0, f"Generado: {dt_str}")
        canvas_obj.restoreState()
        
        canvas_obj.restoreState()


__all__ = ["CertificadoTemplate"]
