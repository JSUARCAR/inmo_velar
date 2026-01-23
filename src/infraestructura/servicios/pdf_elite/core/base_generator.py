"""
Generador PDF Base Abstracto
============================
Clase base abstracta que define la interfaz para todos los generadores PDF.
Implementa el patrón Template Method para estructurar la generación de documentos.

Autor: Sistema de Gestión Inmobiliaria
Fecha: 2026-01-18
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional, List
from datetime import datetime
import logging

# Configurar logger
logger = logging.getLogger(__name__)


class BasePDFGenerator(ABC):
    """
    Clase base abstracta para generadores PDF
    
    Implementa el patrón Template Method, definiendo el esqueleto del algoritmo
    de generación de PDFs mientras permite a las subclases sobrescribir pasos específicos.
    
    Attributes:
        output_dir: Directorio donde se guardarán los PDFs generados
        metadata: Diccionario con metadata del documento
        
    Example:
        >>> class MiGenerador(BasePDFGenerator):
        ...     def generate(self, data):
        ...         # implementación
        ...         pass
        ...     def validate_data(self, data):
        ...         return True
    """
    
    def __init__(self, output_dir: Optional[Path] = None):
        """
        Inicializa el generador base
        
        Args:
            output_dir: Directorio de salida. Si es None, usa el configurado globalmente.
        """
        from .config import config
        
        self.config = config
        self.output_dir = output_dir or config.output_dir
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
        # Metadata del documento
        self.metadata: Dict[str, Any] = {
            'creator': 'Sistema PDF Élite - Inmobiliaria Velar',
            'producer': 'ReportLab PDF Library',
            'created_at': datetime.now()
        }
        
        # Estado interno
        self._generated_file: Optional[Path] = None
        
        logger.debug(f"Inicializado {self.__class__.__name__}")
    
    # ========================================================================
    # MÉTODOS ABSTRACTOS (Deben ser implementados por subclases)
    # ========================================================================
    
    @abstractmethod
    def generate(self, data: Dict[str, Any]) -> Path:
        """
        Genera el documento PDF
        
        Este es el método principal que debe ser implementado por cada
        generador específico. Debe crear el PDF y retornar su path.
        
        Args:
            data: Diccionario con los datos para generar el documento
            
        Returns:
            Path del archivo PDF generado
            
        Raises:
            ValueError: Si los datos son inválidos
            IOError: Si hay problemas escribiendo el archivo
        """
        pass
    
    @abstractmethod
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """
        Valida que los datos de entrada sean correctos
        
        Args:
            data: Datos a validar
            
        Returns:
            True si los datos son válidos, False en caso contrario
            
        Raises:
            ValueError: Si hay errores de validación críticos
        """
        pass
    
    # ========================================================================
    # MÉTODOS TEMPLATE (Pueden ser sobrescritos opcionalmente)
    # ========================================================================
    
    def before_generate(self, data: Dict[str, Any]) -> None:
        """
        Hook ejecutado antes de generar el PDF
        
        Puede ser sobrescrito para realizar operaciones previas como:
        - Validación adicional
        - Preparación de datos
        - Logging
        
        Args:
            data: Datos que se usarán para generar el PDF
        """
        logger.info(f"Iniciando generación de PDF con {self.__class__.__name__}")
    
    def after_generate(self, output_path: Path, data: Dict[str, Any]) -> None:
        """
        Hook ejecutado después de generar el PDF
        
        Puede ser sobrescrito para realizar operaciones posteriores como:
        - Logging de auditoría
        - Notificaciones
        - Post-procesamiento
        
        Args:
            output_path: Path del archivo generado
            data: Datos usados para generar el PDF
        """
        logger.info(f"PDF generado exitosamente: {output_path}")
    
    def on_error(self, error: Exception, data: Dict[str, Any]) -> None:
        """
        Hook ejecutado cuando ocurre un error durante la generación
        
        Args:
            error: La excepción que ocurrió
            data: Datos que se estaban procesando
        """
        logger.error(
            f"Error generando PDF con {self.__class__.__name__}: {error}",
            exc_info=True
        )
    
    # ========================================================================
    # MÉTODOS PÚBLICOS DE UTILIDAD
    # ========================================================================
    
    def generate_safe(self, data: Dict[str, Any]) -> Optional[Path]:
        """
        Genera el PDF de forma segura, capturando excepciones
        
        Este método envuelve generate() con manejo de errores completo,
        ejecutando los hooks before/after/on_error apropiados.
        
        Args:
            data: Datos para generar el PDF
            
        Returns:
            Path del archivo generado, o None si hubo error
        """
        try:
            # Validar datos primero
            if not self.validate_data(data):
                raise ValueError("Datos de entrada inválidos")
            
            # Hook pre-generación
            self.before_generate(data)
            
            # Generar PDF
            output_path = self.generate(data)
            self._generated_file = output_path
            
            # Hook post-generación
            self.after_generate(output_path, data)
            
            return output_path
            
        except Exception as e:
            self.on_error(e, data)
            return None
    
    def add_metadata(self, key: str, value: Any) -> None:
        """
        Agrega o actualiza metadata del documento
        
        Args:
            key: Clave de la metadata
            value: Valor de la metadata
        """
        self.metadata[key] = value
        logger.debug(f"Metadata agregada: {key} = {value}")
    
    def get_metadata(self, key: str, default: Any = None) -> Any:
        """
        Obtiene un valor de metadata
        
        Args:
            key: Clave de la metadata
            default: Valor por defecto si la clave no existe
            
        Returns:
            Valor de la metadata o default
        """
        return self.metadata.get(key, default)
    
    # ========================================================================
    # MÉTODOS PROTEGIDOS (Para uso interno y de subclases)
    # ========================================================================
    
    def _generate_filename(
        self,
        prefix: str,
        doc_id: Any,
        extension: str = "pdf"
    ) -> str:
        """
        Genera un nombre de archivo estandarizado
        
        Formato: {prefix}_{doc_id}_{timestamp}.{extension}
        
        Args:
            prefix: Prefijo del archivo (ej: "contrato", "recibo")
            doc_id: Identificador del documento
            extension: Extensión del archivo (default: "pdf")
            
        Returns:
            Nombre de archivo generado
        """
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{prefix}_{doc_id}_{timestamp}.{extension}"
        
        # Sanitizar nombre de archivo (remover caracteres inválidos)
        filename = self._sanitize_filename(filename)
        
        return filename
    
    def _sanitize_filename(self, filename: str) -> str:
        """
        Sanitiza un nombre de archivo removiendo caracteres inválidos
        
        Args:
            filename: Nombre original
            
        Returns:
            Nombre sanitizado
        """
        # Caracteres no permitidos en nombres de archivo
        invalid_chars = '<>:"/\\|?*'
        
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        return filename
    
    def _get_output_path(self, filename: str) -> Path:
        """
        Retorna el path completo del archivo de salida
        
        Args:
            filename: Nombre del archivo
            
        Returns:
            Path completo del archivo
        """
        return self.output_dir / filename
    
    def _require_fields(self, data: Dict[str, Any], *fields: str) -> None:
        """
        Valida que los campos requeridos estén presentes en los datos
        
        Args:
            data: Diccionario de datos
            *fields: Nombres de campos requeridos
            
        Raises:
            ValueError: Si falta algún campo requerido
        """
        missing = [f for f in fields if f not in data]
        
        if missing:
            raise ValueError(
                f"Campos requeridos faltantes: {', '.join(missing)}"
            )
    
    def _validate_field_type(
        self,
        data: Dict[str, Any],
        field: str,
        expected_type: type
    ) -> None:
        """
        Valida que un campo tenga el tipo esperado
        
        Args:
            data: Diccionario de datos
            field: Nombre del campo
            expected_type: Tipo esperado
            
        Raises:
            TypeError: Si el tipo no coincide
        """
        if field not in data:
            return  # Campo opcional, no validar
        
        value = data[field]
        if not isinstance(value, expected_type):
            raise TypeError(
                f"Campo '{field}' debe ser de tipo {expected_type.__name__}, "
                f"recibido {type(value).__name__}"
            )
    
    # ========================================================================
    # PROPIEDADES
    # ========================================================================
    
    @property
    def last_generated_file(self) -> Optional[Path]:
        """Retorna el path del último archivo generado"""
        return self._generated_file
    
    @property
    def document_title(self) -> str:
        """Retorna el título del documento desde metadata"""
        return self.metadata.get('title', 'Documento PDF')
    
    @document_title.setter
    def document_title(self, value: str) -> None:
        """Establece el título del documento"""
        self.add_metadata('title', value)
    
    # ========================================================================
    # REPRESENTACIÓN
    # ========================================================================
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(output_dir='{self.output_dir}')"
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}"


__all__ = ['BasePDFGenerator']
