"""
Generador de Códigos QR
=======================
Utilidad para generar códigos QR personalizados para documentos PDF.

Autor: Sistema de Gestión Inmobiliaria
Fecha: 2026-01-18
"""

from io import BytesIO
from pathlib import Path
from typing import Literal

import qrcode
from PIL import Image
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import CircleModuleDrawer, RoundedModuleDrawer


class QRGenerator:
    """
    Generador de códigos QR personalizados

    Crea códigos QR con diferentes estilos y niveles de corrección de errores
    para incluir en documentos PDF.
    """

    @staticmethod
    def generate_qr(
        data: str,
        size: int = 200,
        border: int = 2,
        error_correction: Literal["L", "M", "Q", "H"] = "H",
        style: Literal["square", "rounded", "circle"] = "rounded",
    ) -> BytesIO:
        """
        Genera código QR personalizado

        Args:
            data: Datos a codificar (URL, texto, etc.)
            size: Tamaño en píxeles del código generado
            border: Grosor del borde en módulos
            error_correction: Nivel de corrección de errores
                - 'L': ~7% de corrección
                - 'M': ~15% de corrección
                - 'Q': ~25% de corrección
                - 'H': ~30% de corrección (recomendado)
            style: Estilo de los módulos
                - 'square': Cuadrados tradicionales
                - 'rounded': Esquinas redondeadas
                - 'circle': Círculos

        Returns:
            BytesIO con la imagen del QR en formato PNG

        Example:
            >>> qr_img = QRGenerator.generate_qr(
            ...     "https://inmovelar.com/verify/doc123",
            ...     size=150
            ... )
        """
        # Mapeo de niveles de corrección
        error_levels = {
            "L": qrcode.constants.ERROR_CORRECT_L,
            "M": qrcode.constants.ERROR_CORRECT_M,
            "Q": qrcode.constants.ERROR_CORRECT_Q,
            "H": qrcode.constants.ERROR_CORRECT_H,
        }

        # Crear objeto QR
        qr = qrcode.QRCode(
            version=1,  # Auto-ajusta el tamaño
            error_correction=error_levels.get(error_correction, qrcode.constants.ERROR_CORRECT_H),
            box_size=10,
            border=border,
        )

        # Agregar datos y generar
        qr.add_data(data)
        qr.make(fit=True)

        # Seleccionar drawer según estilo
        if style == "rounded":
            module_drawer = RoundedModuleDrawer()
        elif style == "circle":
            module_drawer = CircleModuleDrawer()
        else:
            module_drawer = None  # Cuadrados por defecto

        # Generar imagen
        if module_drawer:
            img = qr.make_image(
                fill_color="black",
                back_color="white",
                image_factory=StyledPilImage,
                module_drawer=module_drawer,
            )
        else:
            img = qr.make_image(fill_color="black", back_color="white")

        # Redimensionar al tamaño deseado
        img = img.resize((size, size), Image.Resampling.LANCZOS)

        # Convertir a BytesIO
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        return buffer

    @staticmethod
    def generate_verification_qr(
        doc_type: str, doc_id: int, base_url: str = "https://inmovelar.com/verify", size: int = 150
    ) -> BytesIO:
        """
        Genera QR para verificación de documentos

        Crea un código QR que apunta a una URL de verificación del documento.

        Args:
            doc_type: Tipo de documento (contrato, recibo, liquidacion, etc.)
            doc_id: ID único del documento
            base_url: URL base del sistema de verificación
            size: Tamaño del QR

        Returns:
            BytesIO con la imagen del QR

        Example:
            >>> qr = QRGenerator.generate_verification_qr(
            ...     "contrato", 12345
            ... )
        """
        verification_url = f"{base_url}/{doc_type}/{doc_id}"
        return QRGenerator.generate_qr(
            verification_url, size=size, error_correction="H", style="rounded"
        )

    @staticmethod
    def generate_contact_qr(name: str, phone: str, email: str, size: int = 180) -> BytesIO:
        """
        Genera QR con información de contacto (vCard)

        Args:
            name: Nombre completo
            phone: Teléfono
            email: Email
            size: Tamaño del QR

        Returns:
            BytesIO con la imagen del QR
        """
        # Formato vCard
        vcard = f"""BEGIN:VCARD
VERSION:3.0
FN:{name}
TEL:{phone}
EMAIL:{email}
END:VCARD"""

        return QRGenerator.generate_qr(vcard, size=size, error_correction="H")

    @staticmethod
    def generate_payment_qr(
        amount: float, reference: str, account: str, size: int = 200
    ) -> BytesIO:
        """
        Genera QR para pagos (formato simplificado)

        Args:
            amount: Monto a pagar
            reference: Referencia del pago
            account: Cuenta destino
            size: Tamaño del QR

        Returns:
            BytesIO con la imagen del QR
        """
        payment_data = f"PAGO|{amount}|{reference}|{account}"

        return QRGenerator.generate_qr(
            payment_data, size=size, error_correction="H", style="rounded"
        )

    @staticmethod
    def save_qr_to_file(qr_buffer: BytesIO, output_path: Path) -> None:
        """
        Guarda un QR en archivo

        Args:
            qr_buffer: Buffer con la imagen del QR
            output_path: Path donde guardar
        """
        with open(output_path, "wb") as f:
            f.write(qr_buffer.getvalue())

        # Resetear buffer
        qr_buffer.seek(0)


__all__ = ["QRGenerator"]
