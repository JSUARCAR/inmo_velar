"""
Value Object: Email

Encapsula una dirección de email válida.
"""

from dataclasses import dataclass
import re


@dataclass(frozen=True)
class Email:
    """
    Value Object: Dirección de Email.
    
    Attributes:
        direccion: Email en formato estándar
    
    Raises:
        ValueError: Si el email no cumple formato válido
    """
    
    direccion: str
    
    # Regex básica para validar email
    _PATRON_EMAIL = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    def __post_init__(self) -> None:
        """Validación del formato de email."""
        if not self.direccion or not self.direccion.strip():
            raise ValueError("El email no puede estar vacío")
        
        if not self._PATRON_EMAIL.match(self.direccion.strip()):
            raise ValueError(f"Email inválido: {self.direccion}")
        
        # Normalizar a minúsculas
        object.__setattr__(self, 'direccion', self.direccion.lower().strip())
    
    def dominio(self) -> str:
        """Extrae el dominio del email."""
        return self.direccion.split("@")[1]
    
    def usuario(self) -> str:
        """Extrae el nombre de usuario del email."""
        return self.direccion.split("@")[0]
    
    def __str__(self) -> str:
        return self.direccion
