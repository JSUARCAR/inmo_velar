"""
Value Object: Dirección

Encapsula una dirección física completa.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Direccion:
    """
    Value Object: Dirección Física.
    
    Attributes:
        direccion_completa: Dirección en formato texto (ej: "Calle 123 #45-67")
        ciudad: Ciudad
        departamento: Departamento/Estado
        codigo_postal: Código postal opcional
        barrio: Barrio opcional
    
    Raises:
        ValueError: Si faltan campos obligatorios
    """
    
    direccion_completa: str
    ciudad: str
    departamento: str
    codigo_postal: Optional[str] = None
    barrio: Optional[str] = None
    
    def __post_init__(self) -> None:
        """Validación de campos obligatorios."""
        if not self.direccion_completa or not self.direccion_completa.strip():
            raise ValueError("La dirección completa es obligatoria")
        
        if not self.ciudad or not self.ciudad.strip():
            raise ValueError("La ciudad es obligatoria")
        
        if not self.departamento or not self.departamento.strip():
            raise ValueError("El departamento es obligatorio")
    
    def formato_completo(self) -> str:
        """Retorna la dirección en formato completo legible."""
        partes = [self.direccion_completa]
        
        if self.barrio:
            partes.append(f"Barrio {self.barrio}")
        
        partes.append(self.ciudad)
        partes.append(self.departamento)
        
        if self.codigo_postal:
            partes.append(f"CP {self.codigo_postal}")
        
        return ", ".join(partes)
    
    def __str__(self) -> str:
        return self.formato_completo()
