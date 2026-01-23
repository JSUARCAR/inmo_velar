"""
Value Object: Dinero

Encapsula un monto monetario con su moneda, evitando errores de cálculo
entre diferentes monedas.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional


@dataclass(frozen=True)
class Dinero:
    """
    Value Object inmutable que representa un monto de dinero.
    
    Attributes:
        monto: Cantidad numérica con precisión decimal
        moneda: Código de moneda ISO 4217 (ej: "COP", "USD")
    
    Raises:
        ValueError: Si el monto es negativo o la moneda es inválida
    """
    
    monto: Decimal
    moneda: str = "COP"  # Peso colombiano por defecto
    
    def __post_init__(self) -> None:
        """Validaciones al crear el objeto."""
        if self.monto < 0:
            raise ValueError(f"El monto no puede ser negativo: {self.monto}")
        
        if not self.moneda or len(self.moneda) != 3:
            raise ValueError(f"Moneda inválida: {self.moneda}")
        
        # Forzar uppercase para la moneda
        object.__setattr__(self, 'moneda', self.moneda.upper())
    
    def __add__(self, otro: 'Dinero') -> 'Dinero':
        """
        Suma dos montos de dinero.
        
        Raises:
            ValueError: Si las monedas son diferentes
        """
        if self.moneda != otro.moneda:
            raise ValueError(
                f"No se pueden sumar monedas diferentes: {self.moneda} + {otro.moneda}"
            )
        
        return Dinero(self.monto + otro.monto, self.moneda)
    
    def __sub__(self, otro: 'Dinero') -> 'Dinero':
        """Resta dos montos de dinero."""
        if self.moneda != otro.moneda:
            raise ValueError(
                f"No se pueden restar monedas diferentes: {self.moneda} - {otro.moneda}"
            )
        
        return Dinero(self.monto - otro.monto, self.moneda)
    
    def __mul__(self, factor: Decimal) -> 'Dinero':
        """Multiplica el monto por un factor."""
        return Dinero(self.monto * factor, self.moneda)
    
    def __truediv__(self, divisor: Decimal) -> 'Dinero':
        """Divide el monto por un divisor."""
        if divisor == 0:
            raise ValueError("No se puede dividir por cero")
        
        return Dinero(self.monto / divisor, self.moneda)
    
    def es_cero(self) -> bool:
        """Retorna True si el monto es cero."""
        return self.monto == 0
    
    def es_positivo(self) -> bool:
        """Retorna True si el monto es mayor a cero."""
        return self.monto > 0
    
    def formatear(self, incluir_moneda: bool = True) -> str:
        """
        Formatea el dinero como string legible.
        
        Args:
            incluir_moneda: Si incluir el código de moneda
            
        Returns:
            String formateado (ej: "$1.500.000 COP")
        """
        # Formatear con separadores de miles
        monto_str = f"{self.monto:,.2f}".replace(",", ".")
        
        if incluir_moneda:
            return f"${monto_str} {self.moneda}"
        return f"${monto_str}"
    
    def __str__(self) -> str:
        return self.formatear()
    
    def __repr__(self) -> str:
        return f"Dinero(monto={self.monto}, moneda='{self.moneda}')"
