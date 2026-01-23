"""
Validadores de Datos
====================
Validadores para datos de entrada en generación de PDFs.

Autor: Sistema de Gestión Inmobiliaria
Fecha: 2026-01-18
"""

from typing import Any, Dict, List, Optional
from datetime import datetime, date
import re


class DataValidator:
    """
    Validador de datos para generación de PDFs
    
    Proporciona métodos estáticos para validar diferentes tipos de datos
    antes de usarlos en la generación de documentos.
    """
    
    # Expresiones regulares
    EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    PHONE_REGEX = re.compile(r'^\+?[\d\s\-()]{7,20}$')
    NIT_REGEX = re.compile(r'^\d{9,10}-\d$')
    CC_REGEX = re.compile(r'^\d{6,12}$')
    
    @staticmethod
    def validate_required_fields(
        data: Dict[str, Any],
        required_fields: List[str]
    ) -> tuple[bool, List[str]]:
        """
        Valida que campos requeridos estén presentes
        
        Args:
            data: Diccionario de datos
            required_fields: Lista de campos requeridos
            
        Returns:
            Tupla (es_válido, campos_faltantes)
        """
        missing = [field for field in required_fields if field not in data or data[field] is None]
        return (len(missing) == 0, missing)
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Valida formato de email
        
        Args:
            email: Email a validar
            
        Returns:
            True si es válido
        """
        if not email:
            return False
        return bool(DataValidator.EMAIL_REGEX.match(email))
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """
        Valida formato de teléfono
        
        Args:
            phone: Teléfono a validar
            
        Returns:
            True si es válido
        """
        if not phone:
            return False
        return bool(DataValidator.PHONE_REGEX.match(phone))
    
    @staticmethod
    def validate_nit(nit: str) -> bool:
        """
        Valida formato de NIT colombiano
        
        Args:
            nit: NIT a validar (formato: 123456789-0)
            
        Returns:
            True si es válido
        """
        if not nit:
            return False
        return bool(DataValidator.NIT_REGEX.match(nit))
    
    @staticmethod
    def validate_cedula(cedula: str) -> bool:
        """
        Valida formato de cédula
        
        Args:
            cedula: Cédula a validar
            
        Returns:
            True si es válido
        """
        if not cedula:
            return False
        return bool(DataValidator.CC_REGEX.match(cedula))
    
    @staticmethod
    def validate_date(
        date_value: Any,
        allow_future: bool = True
    ) -> bool:
        """
        Valida que sea una fecha válida
        
        Args:
            date_value: Valor a validar (str, date, datetime)
            allow_future: Permitir fechas futuras
            
        Returns:
            True si es válida
        """
        try:
            if isinstance(date_value, str):
                # Intentar parsear
                parsed_date = datetime.strptime(date_value, '%Y-%m-%d').date()
            elif isinstance(date_value, datetime):
                parsed_date = date_value.date()
            elif isinstance(date_value, date):
                parsed_date = date_value
            else:
                return False
            
            # Validar que no sea futura si no se permite
            if not allow_future and parsed_date > date.today():
                return False
            
            return True
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_numeric_range(
        value: Any,
        min_value: Optional[float] = None,
        max_value: Optional[float] = None
    ) -> bool:
        """
        Valida que un valor numérico esté en un rango
        
        Args:
            value: Valor a validar
            min_value: Valor mínimo permitido
            max_value: Valor máximo permitido
            
        Returns:
            True si está en rango
        """
        try:
            num_value = float(value)
            
            if min_value is not None and num_value < min_value:
                return False
            
            if max_value is not None and num_value > max_value:
                return False
            
            return True
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_string_length(
        value: str,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None
    ) -> bool:
        """
        Valida longitud de string
        
        Args:
            value: String a validar
            min_length: Longitud mínima
            max_length: Longitud máxima
            
        Returns:
            True si cumple con las longitudes
        """
        if not isinstance(value, str):
            return False
        
        length = len(value)
        
        if min_length is not None and length < min_length:
            return False
        
        if max_length is not None and length > max_length:
            return False
        
        return True
    
    @staticmethod
    def sanitize_string(value: str, max_length: Optional[int] = None) -> str:
        """
        Sanitiza un string para uso en PDF
        
        Args:
            value: String a sanitizar
            max_length: Longitud máxima
            
        Returns:
            String sanitizado
        """
        # Remover caracteres de control
        sanitized = ''.join(char for char in value if ord(char) >= 32 or char == '\n')
        
        # Truncar si es necesario
        if max_length and len(sanitized) > max_length:
            sanitized = sanitized[:max_length - 3] + '...'
        
        return sanitized
    
    @staticmethod
    def validate_money_amount(amount: Any, allow_zero: bool = False) -> bool:
        """
        Valida monto de dinero
        
        Args:
            amount: Monto a validar
            allow_zero: Permitir valor cero
            
        Returns:
            True si es válido
        """
        try:
            num_amount = float(amount)
            
            if not allow_zero and num_amount == 0:
                return False
            
            if num_amount < 0:
                return False
            
            # Validar que tenga máximo 2 decimales
            if round(num_amount, 2) != num_amount:
                return False
            
            return True
        except (ValueError, TypeError):
            return False


__all__ = ['DataValidator']
