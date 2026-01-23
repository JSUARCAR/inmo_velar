"""
Entidad de Dominio: SaldoFavor
Representa un saldo a favor de un propietario o asesor.

Business Rules:
- valor_saldo debe ser > 0
- tipo_beneficiario debe estar en: Propietario, Asesor
- estado debe estar en: Pendiente, Aplicado, Devuelto
- XOR: exactamente uno de id_propietario o id_asesor debe tener valor
"""

from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime, date


@dataclass
class SaldoFavor:
    """
    Entidad que representa un saldo a favor de un beneficiario.
    
    Un saldo a favor se genera cuando hay un excedente de pago que debe
    ser aplicado a futuras liquidaciones o devuelto al beneficiario.
    
    Attributes:
        id_saldo_favor: Identificador único
        id_propietario: FK a propietario (XOR con id_asesor)
        id_asesor: FK a asesor (XOR con id_propietario)
        tipo_beneficiario: 'Propietario' o 'Asesor'
        valor_saldo: Monto del saldo en centavos (> 0)
        motivo: Razón por la cual se generó el saldo
        fecha_generacion: Fecha de creación del saldo
        estado: Estado actual (Pendiente, Aplicado, Devuelto)
        fecha_resolucion: Fecha en que se resolvió (aplicó o devolvió)
        observaciones: Notas adicionales
    """
    
    # Identificación
    id_saldo_favor: Optional[int] = None
    id_propietario: Optional[int] = None  # FK - XOR con id_asesor
    id_asesor: Optional[int] = None       # FK - XOR con id_propietario
    
    # Datos del saldo
    tipo_beneficiario: str = ""  # 'Propietario' | 'Asesor'
    valor_saldo: int = 0         # Valor en centavos (> 0)
    motivo: str = ""             # Razón del saldo
    
    # Fechas
    fecha_generacion: Optional[str] = None  # Formato: 'YYYY-MM-DD'
    fecha_resolucion: Optional[str] = None  # Formato: 'YYYY-MM-DD'
    
    # Estado
    estado: str = "Pendiente"  # Pendiente, Aplicado, Devuelto
    observaciones: Optional[str] = None
    
    # Auditoría
    created_at: Optional[str] = field(default_factory=lambda: datetime.now().isoformat())
    created_by: Optional[str] = None
    updated_at: Optional[str] = None
    updated_by: Optional[str] = None
    
    # Constantes
    TIPOS_BENEFICIARIO = ['Propietario', 'Asesor']
    ESTADOS = ['Pendiente', 'Aplicado', 'Devuelto']
    
    def __post_init__(self):
        """Validaciones de reglas de negocio"""
        # Validar valor > 0
        if self.valor_saldo <= 0:
            raise ValueError("El valor del saldo debe ser mayor que cero")
        
        # Validar tipo_beneficiario
        if self.tipo_beneficiario and self.tipo_beneficiario not in self.TIPOS_BENEFICIARIO:
            raise ValueError(
                f"Tipo de beneficiario inválido: {self.tipo_beneficiario}. "
                f"Debe ser uno de: {', '.join(self.TIPOS_BENEFICIARIO)}"
            )
        
        # Validar estado
        if self.estado not in self.ESTADOS:
            raise ValueError(
                f"Estado inválido: {self.estado}. "
                f"Debe ser uno de: {', '.join(self.ESTADOS)}"
            )
        
        # Validar XOR: exactamente uno de propietario o asesor
        tiene_propietario = self.id_propietario is not None
        tiene_asesor = self.id_asesor is not None
        
        if tiene_propietario and tiene_asesor:
            raise ValueError(
                "Un saldo a favor no puede pertenecer a propietario Y asesor simultáneamente"
            )
        
        if not tiene_propietario and not tiene_asesor:
            raise ValueError(
                "Un saldo a favor debe pertenecer a un propietario O un asesor"
            )
        
        # Validar coherencia tipo_beneficiario con FK
        if tiene_propietario and self.tipo_beneficiario != 'Propietario':
            raise ValueError(
                "Si id_propietario está definido, tipo_beneficiario debe ser 'Propietario'"
            )
        
        if tiene_asesor and self.tipo_beneficiario != 'Asesor':
            raise ValueError(
                "Si id_asesor está definido, tipo_beneficiario debe ser 'Asesor'"
            )
    
    @property
    def esta_pendiente(self) -> bool:
        """Verifica si el saldo está pendiente de resolución"""
        return self.estado == "Pendiente"
    
    @property
    def esta_aplicado(self) -> bool:
        """Verifica si el saldo ya fue aplicado a una liquidación"""
        return self.estado == "Aplicado"
    
    @property
    def esta_devuelto(self) -> bool:
        """Verifica si el saldo ya fue devuelto al beneficiario"""
        return self.estado == "Devuelto"
    
    @property
    def esta_resuelto(self) -> bool:
        """Verifica si el saldo ya fue resuelto (aplicado o devuelto)"""
        return self.estado in ("Aplicado", "Devuelto")
    
    @property
    def valor_formateado(self) -> str:
        """Retorna el valor formateado como moneda colombiana"""
        valor_pesos = self.valor_saldo / 100
        return f"${valor_pesos:,.0f}"
    
    @property
    def dias_pendiente(self) -> Optional[int]:
        """Calcula los días que lleva pendiente el saldo"""
        if not self.fecha_generacion or self.esta_resuelto:
            return None
        
        try:
            fecha_gen = date.fromisoformat(self.fecha_generacion)
            delta = date.today() - fecha_gen
            return delta.days
        except (ValueError, TypeError):
            return None
    
    def aplicar(self, observacion: Optional[str] = None) -> None:
        """
        Marca el saldo como aplicado a una liquidación.
        
        Args:
            observacion: Nota sobre cómo se aplicó
        
        Raises:
            ValueError: Si el saldo ya está resuelto
        """
        if self.esta_resuelto:
            raise ValueError(
                f"El saldo ya está {self.estado.lower()}, no puede aplicarse"
            )
        
        self.estado = "Aplicado"
        self.fecha_resolucion = date.today().isoformat()
        self.updated_at = datetime.now().isoformat()
        
        if observacion:
            self.observaciones = observacion
    
    def devolver(self, observacion: Optional[str] = None) -> None:
        """
        Marca el saldo como devuelto al beneficiario.
        
        Args:
            observacion: Nota sobre cómo se devolvió
        
        Raises:
            ValueError: Si el saldo ya está resuelto
        """
        if self.esta_resuelto:
            raise ValueError(
                f"El saldo ya está {self.estado.lower()}, no puede devolverse"
            )
        
        self.estado = "Devuelto"
        self.fecha_resolucion = date.today().isoformat()
        self.updated_at = datetime.now().isoformat()
        
        if observacion:
            self.observaciones = observacion
