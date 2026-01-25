"""
Generador de Códigos de Barra
==============================
Utilidad para generar códigos de barra en diversos formatos.

Autor: Sistema de Gestión Inmobiliaria
Fecha: 2026-01-18
"""

from io import BytesIO
from typing import Literal

import barcode
from barcode.writer import ImageWriter


class BarcodeGenerator:
    """
    Generador de códigos de barra

    Soporta múltiples formatos de códigos de barra para identificación
    de documentos y productos.
    """

    SUPPORTED_FORMATS = {
        "code128": barcode.Code128,
        "code39": barcode.Code39,
        "ean13": barcode.EAN13,
        "ean8": barcode.EAN8,
        "upca": barcode.UPCA,
    }

    @staticmethod
    def generate_barcode(
        data: str,
        format_type: Literal["code128", "code39", "ean13", "ean8", "upca"] = "code128",
        width: int = 300,
        height: int = 100,
        font_size: int = 10,
        text_distance: int = 5,
        quiet_zone: float = 6.5,
    ) -> BytesIO:
        """
        Genera código de barra

        Args:
            data: Datos a codificar
            format_type: Tipo de código de barra
            width: Ancho deseado en píxeles
            height: Alto deseado en píxeles
            font_size: Tamaño de fuente del texto
            text_distance: Distancia entre barras y texto
            quiet_zone: Zona silenciosa en mm

        Returns:
            BytesIO con la imagen del código de barra
        """
        # Obtener clase del formato
        barcode_class = BarcodeGenerator.SUPPORTED_FORMATS.get(format_type)
        if not barcode_class:
            raise ValueError(f"Formato no soportado: {format_type}")

        # Configurar writer de imagen
        writer = ImageWriter()
        writer.set_options(
            {
                "module_width": width / 100,  # Ancho de módulo
                "module_height": height / 10,  # Alto de módulo
                "font_size": font_size,
                "text_distance": text_distance,
                "quiet_zone": quiet_zone,
            }
        )

        # Generar código de barra
        barcode_instance = barcode_class(data, writer=writer)

        # Renderizar a BytesIO
        buffer = BytesIO()
        barcode_instance.write(buffer)
        buffer.seek(0)

        return buffer

    @staticmethod
    def generate_document_barcode(
        doc_id: int, prefix: str = "DOC", width: int = 350, height: int = 80
    ) -> BytesIO:
        """
        Genera código de barra para identificación de documentos

        Args:
            doc_id: ID del documento
            prefix: Prefijo identificador
            width: Ancho del código
            height: Alto del código

        Returns:
            BytesIO con la imagen del código
        """
        # Formatear código: PREFIX + ID (8 dígitos con ceros a la izquierda)
        code = f"{prefix}{doc_id:08d}"

        return BarcodeGenerator.generate_barcode(
            code, format_type="code128", width=width, height=height
        )


__all__ = ["BarcodeGenerator"]
