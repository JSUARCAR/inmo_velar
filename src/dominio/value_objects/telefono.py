"""
Value Object: Teléfono

Encapsula un número telefónico válido.
"""

from dataclasses import dataclass
from typing import Optional
import re


@dataclass(frozen=True)
class Telefono:
    """
    Value Object: Número de Teléfono.
    
    Attributes:
        numero: Número telefónico (puede incluir espacios, guiones, +)
        extension: Extensión opcional para teléfonos corporativos
    
    Raises:
        ValueError: Si el número no tiene al menos 7 dígitos
    """
    
    numero: str
    extension: Optional[str] = None
    
    def __post_init__(self) -> None:
        """Validación del número telefónico."""
        if not self.numero:
            raise ValueError("El número de teléfono no puede estar vacío")
        
        # Extraer solo dígitos para validar longitud
        solo_digitos = re.sub(r'\D', '', self.numero)
        
        if len(solo_digitos) < 7:
            raise ValueError(
                f"El número debe tener al menos 7 dígitos: {self.numero}"
            )
    
    def formato_internacional(self, codigo_pais: str = "+57") -> str:
        """
        Retorna el número en formato internacional.
        
        Args:
            codigo_pais: Código del país (por defecto Colombia +57)
        """
        # Si ya tiene +, no agregar código de país
        if self.numero.startswith("+"):
            numero_base = self.numero
        else:
            # Limpiar y agregar código de país
            solo_digitos = re.sub(r'\D', '', self.numero)
            numero_base = f"{codigo_pais} {solo_digitos}"
        
        if self.extension:
            return f"{numero_base} ext. {self.extension}"
        
        return numero_base
    
    def __str__(self) -> str:
        if self.extension:
            return f"{self.numero} ext. {self.extension}"
        return self.numero
