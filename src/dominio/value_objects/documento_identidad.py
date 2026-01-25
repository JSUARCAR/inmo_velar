"""
Value Object: Documento de Identidad

Encapsula un documento de identidad válido.
"""

from dataclasses import dataclass

from src.dominio.constantes.tipos_documento import TipoDocumento


@dataclass(frozen=True)
class DocumentoIdentidad:
    """
    Value Object: Documento de Identidad.

    Attributes:
        tipo: Tipo de documento (CC, NIT, etc.)
        numero: Número del documento sin caracteres especiales

    Raises:
        ValueError: Si el número está vacío o tiene formato inválido
    """

    tipo: TipoDocumento
    numero: str

    def __post_init__(self) -> None:
        """Validación inmediata al crear el objeto."""
        if not self.numero or not self.numero.strip():
            raise ValueError("El número de documento no puede estar vacío")

        # Validación específica según tipo
        if self.tipo == TipoDocumento.NIT:
            limpio = self.numero.replace("-", "").replace(" ", "")
            if not limpio.isdigit():
                raise ValueError("NIT debe contener solo dígitos")

        if self.tipo == TipoDocumento.CEDULA_CIUDADANIA:
            if not self.numero.replace(" ", "").isdigit():
                raise ValueError("Cédula debe contener solo dígitos")

    def __str__(self) -> str:
        return f"{self.tipo.value} {self.numero}"

    def __repr__(self) -> str:
        return f"DocumentoIdentidad(tipo={self.tipo}, numero='{self.numero}')"
