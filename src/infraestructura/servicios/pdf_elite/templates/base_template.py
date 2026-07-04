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
        self.qr_position: str = (
            "top-right"  # top-right, top-left, bottom-right, bottom-left
        )

        # Estado del documento
        self._document_id: Optional[int] = None
        self._document_type: Optional[str] = None

    # ========================================================================
    # CONFIGURACIÓN DE CARACTERÍSTICAS AVANZADAS
    # ========================================================================

    def set_watermark(
        self, text: str, style: str = "diagonal", opacity: float = 0.15
    ) -> None:
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

    def set_qr_code(
        self, data: str, size: int = 100, position: str = "top-right"
    ) -> None:
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
        Header/footer que incluye membrete, watermark, QR code y textos marginales.

        Args:
            canvas_obj: Objeto canvas de ReportLab
            doc: Documento (BaseDocTemplate)
        """
        # 0. Dibujar MEMBRETE (Si aplica)
        self._add_background_membrete(canvas_obj, doc)

        # 1. Agregar marca de agua
        if self.watermark_text:
            Watermark.add_text_watermark(
                canvas_obj,
                text=self.watermark_text,
                opacity=self.watermark_opacity,
                position=self.watermark_style,
            )

        # 2. Agregar QR Code (Si aplica)
        if self.include_qr and self.qr_data:
            self._add_qr_to_page(canvas_obj, doc)

        # 3. Textos Marginales (Verticales)
        self._add_marginal_texts(canvas_obj, doc)

        # 4. Footer básico (Paginación)
        self._add_standard_footer(canvas_obj, doc)

    def _add_background_membrete(self, canvas_obj, doc):
        """Dibuja el fondo de membrete corporativo."""
        current_dir = Path(__file__).parent
        membrete_path = current_dir / "VELAR INMOBILIARIA_membrete_modificada.png"

        from ..utils.validators import DataValidator

        valid_path = DataValidator.validate_asset_path(membrete_path)
        if valid_path:
            try:
                page_width, page_height = doc.pagesize
                canvas_obj.saveState()
                canvas_obj.drawImage(
                    str(valid_path),
                    0,
                    0,
                    width=page_width,
                    height=page_height,
                    mask=None,
                    preserveAspectRatio=False,
                )
                canvas_obj.restoreState()
            except Exception as e:
                import logging

                logger = logging.getLogger("PDFElite")
                logger.warning(f"Error renderizando membrete base: {e}")

    def _add_marginal_texts(self, canvas_obj, doc):
        """Agrega textos legales y de auditoría en los márgenes verticales."""
        from reportlab.lib import colors

        from ..core.config import config

        canvas_obj.saveState()
        canvas_obj.setFont("Helvetica", 7)
        canvas_obj.setFillColor(colors.lightgrey)

        page_width, page_height = doc.pagesize

        # Margen Izquierdo (Vertical)
        canvas_obj.saveState()
        canvas_obj.translate(25, page_height / 3)
        canvas_obj.rotate(90)
        info_text = f"Impreso por {config.empresa_nombre} - NIT {config.empresa_nit} - Correo: {config.empresa_email}"
        canvas_obj.drawString(0, 0, info_text)
        canvas_obj.restoreState()

        # Margen Derecho (Vertical)
        from datetime import datetime

        dt_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        canvas_obj.saveState()
        canvas_obj.translate(page_width - 25, page_height / 3)
        canvas_obj.rotate(90)
        canvas_obj.drawString(
            0, 0, f"Generado por Sistema Velar SAS - Auditoría: {dt_str}"
        )
        canvas_obj.restoreState()

        canvas_obj.restoreState()

    def _add_standard_footer(self, canvas_obj, doc):
        """Agrega paginación estándar al pie de página."""
        from reportlab.lib import colors

        canvas_obj.saveState()
        canvas_obj.setFont("Helvetica", 8)
        canvas_obj.setFillColor(colors.gray)

        page_width, _ = doc.pagesize
        page_num = canvas_obj.getPageNumber()

        canvas_obj.drawCentredString(page_width / 2, 20, f"Página {page_num}")
        canvas_obj.restoreState()

    def _add_qr_to_page(self, canvas_obj: pdf_canvas.Canvas, doc) -> None:
        """
        Agrega código QR a la página usando posicionamiento absoluto.

        Args:
            canvas_obj: Objeto canvas
            doc: Documento (BaseDocTemplate)
        """
        try:
            # Generar QR code
            qr_buffer = QRGenerator.generate_qr(
                self.qr_data, size=self.qr_size, style="rounded"
            )

            # Calcular posición absoluta usando el tamaño de página
            page_width, page_height = doc.pagesize

            if self.qr_position == "top-right":
                x = page_width - self.qr_size - 20
                y = page_height - self.qr_size - 20
            elif self.qr_position == "top-left":
                x = 20
                y = page_height - self.qr_size - 20
            elif self.qr_position == "bottom-right":
                x = page_width - self.qr_size - 20
                y = 20
            else:  # bottom-left
                x = 20
                y = 20

            # Dibujar QR code
            from reportlab.lib.utils import ImageReader

            # Envolver buffer en ImageReader para compatibilidad con ReportLab
            qr_image = ImageReader(qr_buffer)

            canvas_obj.saveState()
            canvas_obj.drawImage(
                qr_image,
                x,
                y,
                width=self.qr_size,
                height=self.qr_size,
                preserveAspectRatio=True,
                mask="auto",
            )
            canvas_obj.restoreState()
        except Exception as e:
            import logging

            logger = logging.getLogger("PDFElite")
            logger.warning(f"No se pudo agregar QR al PDF: {e}")

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
            color=Colors.to_reportlab(Colors.BLACK),
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
