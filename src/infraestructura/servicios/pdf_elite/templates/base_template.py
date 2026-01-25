"""
Template Base para Documentos
==============================
Clase base que extiende ReportLabGenerator con características avanzadas
como marcas de agua y códigos QR integrados.

Autor: Sistema de Gestión Inmobiliaria
Fecha: 2026-01-18
"""

from pathlib import Path
from typing import Optional

from reportlab.pdfgen import canvas as pdf_canvas

from ..components.watermarks import Watermark
from ..core.reportlab_generator import ReportLabGenerator
from ..utils.qr_generator import QRGenerator


class BaseDocumentTemplate(ReportLabGenerator):
    """
    Template base con características avanzadas

    Extiende ReportLabGenerator agregando funcionalidades comunes
    a todos los documentos élite como watermarks y QR codes.

    Attributes:
        watermark_text: Texto de marca de agua (None = sin marca)
        include_qr: Si incluir código QR de verificación
        qr_data: Datos para el código QR

    Example:
        >>> class MiDocumento(BaseDocumentTemplate):
        ...     def generate(self, data):
        ...         self.set_watermark("BORRADOR")
        ...         self.set_qr_code(f"https://verify.com/{data['id']}")
        ...         # ... generar documento
    """

    def __init__(self, output_dir: Optional[Path] = None):
        """
        Inicializa el template base

        Args:
            output_dir: Directorio de salida opcional
        """
        super().__init__(output_dir)

        # Características avanzadas
        self.watermark_text: Optional[str] = None
        self.watermark_style: str = "diagonal"
        self.watermark_opacity: float = 0.15

        self.include_qr: bool = False
        self.qr_data: Optional[str] = None
        self.qr_size: int = 100
        self.qr_position: str = "top-right"  # top-right, top-left, bottom-right, bottom-left

        # Estado del documento
        self._document_id: Optional[int] = None
        self._document_type: Optional[str] = None

    # ========================================================================
    # CONFIGURACIÓN DE CARACTERÍSTICAS AVANZADAS
    # ========================================================================

    def set_watermark(self, text: str, style: str = "diagonal", opacity: float = 0.15) -> None:
        """
        Establece marca de agua para el documento

        Args:
            text: Texto de la marca de agua
            style: Estilo ('diagonal', 'center', 'top', 'bottom')
            opacity: Opacidad (0.0 - 1.0)
        """
        self.watermark_text = text
        self.watermark_style = style
        self.watermark_opacity = opacity

    def set_qr_code(self, data: str, size: int = 100, position: str = "top-right") -> None:
        """
        Establece código QR para el documento

        Args:
            data: Datos a codificar (típicamente URL de verificación)
            size: Tamaño del QR en píxeles
            position: Posición ('top-right', 'top-left', 'bottom-right', 'bottom-left')
        """
        self.include_qr = True
        self.qr_data = data
        self.qr_size = size
        self.qr_position = position

    def enable_verification_qr(
        self, doc_type: str, doc_id: int, base_url: str = "https://inmovelar.com/verify"
    ) -> None:
        """
        Habilita QR de verificación automático

        Args:
            doc_type: Tipo de documento
            doc_id: ID del documento
            base_url: URL base del sistema
        """
        self._document_type = doc_type
        self._document_id = doc_id
        verification_url = f"{base_url}/{doc_type}/{doc_id}"
        self.set_qr_code(verification_url)

    # ========================================================================
    # HEADER/FOOTER CON CARACTERÍSTICAS AVANZADAS
    # ========================================================================

    def _header_footer_with_features(self, canvas_obj: pdf_canvas.Canvas, doc) -> None:
        """
        Header/footer que incluye watermark y QR code

        Args:
            canvas_obj: Objeto canvas de ReportLab
            doc: Documento SimpleDocTemplate
        """
        # Renderizar header/footer básico
        self._default_header_footer(canvas_obj, doc)

        # Agregar marca de agua si está configurada
        if self.watermark_text:
            Watermark.add_text_watermark(
                canvas_obj,
                text=self.watermark_text,
                opacity=self.watermark_opacity,
                position=self.watermark_style,
            )

        # TEMPORAL: QR code deshabilitado para evitar bug de ReportLab
        # Se reactivará cuando se solucione el problema de estilos
        # if self.include_qr and self.qr_data:
        #     self._add_qr_to_page(canvas_obj, doc)

    def _add_qr_to_page(self, canvas_obj: pdf_canvas.Canvas, doc) -> None:
        """
        Agrega código QR a la página

        Args:
            canvas_obj: Objeto canvas
            doc: Documento
        """
        # Generar QR code
        qr_buffer = QRGenerator.generate_qr(self.qr_data, size=self.qr_size, style="rounded")

        # Calcular posición según configuración

        if self.qr_position == "top-right":
            x = doc.width + doc.leftMargin - self.qr_size - 10
            y = doc.height + doc.topMargin - self.qr_size - 10
        elif self.qr_position == "top-left":
            x = doc.leftMargin + 10
            y = doc.height + doc.topMargin - self.qr_size - 10
        elif self.qr_position == "bottom-right":
            x = doc.width + doc.leftMargin - self.qr_size - 10
            y = doc.bottomMargin + 10
        else:  # bottom-left
            x = doc.leftMargin + 10
            y = doc.bottomMargin + 10

        # Dibujar QR code
        from reportlab.lib.utils import ImageReader

        # Envolver buffer en ImageReader para compatibilidad con ReportLab
        qr_image = ImageReader(qr_buffer)

        canvas_obj.drawImage(
            qr_image,
            x,
            y,
            width=self.qr_size,
            height=self.qr_size,
            preserveAspectRatio=True,
            mask="auto",
        )

    # ========================================================================
    # MÉTODOS DE UTILIDAD PARA TEMPLATES
    # ========================================================================

    def add_document_info_header(
        self, doc_number: str, doc_date: str, doc_status: str = None
    ) -> None:
        """
        Agrega header con información del documento

        Args:
            doc_number: Número del documento
            doc_date: Fecha del documento
            doc_status: Estado opcional (Borrador, Aprobado, etc.)
        """
        from ..components.tables import AdvancedTable

        info = {
            "Documento No.": doc_number,
            "Fecha": doc_date,
        }

        if doc_status:
            info["Estado"] = doc_status

        table = AdvancedTable.create_key_value_table(info)
        self.story.append(table)
        self.add_spacer(0.2)

    def add_section_divider(self, title: str = None) -> None:
        """
        Agrega divisor de sección

        Args:
            title: Título opcional de la sección
        """
        from reportlab.platypus import HRFlowable

        from ..core.config import Colors

        if title:
            self.add_heading(title, level=1)

        # Línea separadora
        hr = HRFlowable(
            width="100%",
            thickness=2,
            color=Colors.to_reportlab(Colors.PRIMARY),
            spaceAfter=10,
            spaceBefore=10,
        )
        self.story.append(hr)

    def add_legal_footer_text(self, text: str) -> None:
        """
        Agrega texto legal al pie del documento

        Args:
            text: Texto legal/disclaimer
        """
        self.add_spacer(0.3)
        self.add_paragraph(text, style_name="Tiny", alignment="center")

    # ========================================================================
    # OVERRIDE DE BUILD PARA USAR FEATURES
    # ========================================================================

    def build(self) -> Path:
        """
        Construye el documento con características avanzadas

        Returns:
            Path del archivo generado
        """
        # Establecer callbacks con características
        self.set_header_footer(
            on_first_page=self._header_footer_with_features,
            on_later_pages=self._header_footer_with_features,
        )

        # Llamar al build del padre
        return super().build()


__all__ = ["BaseDocumentTemplate"]
