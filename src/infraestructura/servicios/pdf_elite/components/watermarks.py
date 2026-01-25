"""
Componente de Marcas de Agua
============================
Gestor de marcas de agua (watermarks) para documentos PDF.

Autor: Sistema de Gestión Inmobiliaria
Fecha: 2026-01-18
"""

from typing import Literal, Tuple

from reportlab.pdfgen import canvas as pdf_canvas

from ..core.config import Colors, Fonts


class Watermark:
    """
    Gestor de marcas de agua para PDFs

    Proporciona métodos para agregar marcas de agua de texto con diferentes
    estilos y posiciones en las páginas del PDF.
    """

    @staticmethod
    def add_text_watermark(
        canvas_obj: pdf_canvas.Canvas,
        text: str,
        opacity: float = 0.1,
        angle: int = 45,
        position: Literal["center", "diagonal", "top", "bottom"] = "diagonal",
        font_size: int = 60,
        color: Tuple[float, float, float] = None,
    ) -> None:
        """
        Agrega marca de agua de texto al canvas

        Args:
            canvas_obj: Objeto canvas de ReportLab
            text: Texto de la marca de agua
            opacity: Opacidad (0.0 transparent - 1.0 opaque)
            angle: Ángulo de rotación en grados
            position: Posición ('center', 'diagonal', 'top', 'bottom')
            font_size: Tamaño de fuente
            color: Color RGB (default: gris oscuro)

        Example:
            >>> def my_page_template(canvas, doc):
            ...     Watermark.add_text_watermark(
            ...         canvas, "BORRADOR", opacity=0.15
            ...     )
        """
        canvas_obj.saveState()

        # Color por defecto: gris oscuro
        if color is None:
            color = Colors.GRAY_DARK

        # Configurar transparencia y color
        canvas_obj.setFillColorRGB(*color, alpha=opacity)
        canvas_obj.setFont(Fonts.MAIN_BOLD, font_size)

        # Obtener dimensiones de página
        width, height = canvas_obj._pagesize

        # Calcular posición según parámetro
        if position == "center":
            x, y = width / 2, height / 2
        elif position == "diagonal":
            x, y = width / 2, height / 3
        elif position == "top":
            x, y = width / 2, height * 0.75
        elif position == "bottom":
            x, y = width / 2, height * 0.25
        else:
            x, y = width / 2, height / 2

        # Aplicar transformación y dibujar
        canvas_obj.translate(x, y)
        canvas_obj.rotate(angle)
        canvas_obj.drawCentredString(0, 0, text)

        canvas_obj.restoreState()

    @staticmethod
    def add_draft_watermark(canvas_obj: pdf_canvas.Canvas, opacity: float = 0.15) -> None:
        """
        Agrega marca de agua "BORRADOR"

        Args:
            canvas_obj: Objeto canvas
            opacity: Opacidad de la marca
        """
        Watermark.add_text_watermark(
            canvas_obj,
            text="BORRADOR",
            opacity=opacity,
            angle=45,
            position="diagonal",
            color=Colors.WARNING,
        )

    @staticmethod
    def add_confidential_watermark(canvas_obj: pdf_canvas.Canvas, opacity: float = 0.12) -> None:
        """
        Agrega marca de agua "CONFIDENCIAL"

        Args:
            canvas_obj: Objeto canvas
            opacity: Opacidad de la marca
        """
        Watermark.add_text_watermark(
            canvas_obj,
            text="CONFIDENCIAL",
            opacity=opacity,
            angle=45,
            position="diagonal",
            color=Colors.DANGER,
        )

    @staticmethod
    def add_copy_watermark(canvas_obj: pdf_canvas.Canvas, opacity: float = 0.1) -> None:
        """
        Agrega marca de agua "COPIA"

        Args:
            canvas_obj: Objeto canvas
            opacity: Opacidad de la marca
        """
        Watermark.add_text_watermark(
            canvas_obj, text="COPIA", opacity=opacity, angle=45, position="diagonal"
        )

    @staticmethod
    def add_void_watermark(canvas_obj: pdf_canvas.Canvas, opacity: float = 0.2) -> None:
        """
        Agrega marca de agua "ANULADO"

        Args:
            canvas_obj: Objeto canvas
            opacity: Opacidad de la marca
        """
        Watermark.add_text_watermark(
            canvas_obj,
            text="ANULADO",
            opacity=opacity,
            angle=45,
            position="center",
            font_size=80,
            color=Colors.DANGER,
        )

    @staticmethod
    def add_multi_watermark(
        canvas_obj: pdf_canvas.Canvas, text: str, repeats: int = 3, opacity: float = 0.08
    ) -> None:
        """
        Agrega múltiples instancias de la marca de agua

        Crea un patrón de marca de agua repetida en la página.

        Args:
            canvas_obj: Objeto canvas
            text: Texto de la marca
            repeats: Número de repeticiones
            opacity: Opacidad
        """
        width, height = canvas_obj._pagesize

        positions = [
            (width * 0.25, height * 0.25),
            (width * 0.75, height * 0.25),
            (width * 0.5, height * 0.5),
            (width * 0.25, height * 0.75),
            (width * 0.75, height * 0.75),
        ]

        canvas_obj.saveState()
        canvas_obj.setFillColorRGB(*Colors.GRAY_DARK, alpha=opacity)
        canvas_obj.setFont(Fonts.MAIN_BOLD, 40)

        for i, (x, y) in enumerate(positions[:repeats]):
            canvas_obj.saveState()
            canvas_obj.translate(x, y)
            canvas_obj.rotate(45)
            canvas_obj.drawCentredString(0, 0, text)
            canvas_obj.restoreState()

        canvas_obj.restoreState()


__all__ = ["Watermark"]
