"""
Template para Certificados Oficiales
====================================
Generador élite de certificados profesionales con diseño elegante.

Autor: Sistema de Gestión Inmobiliaria
Fecha: 2026-01-18
"""

from typing import Dict, Any
from pathlib import Path
from datetime import datetime

from .base_template import BaseDocumentTemplate
from ..components.tables import AdvancedTable
from ..core.config import config, Colors, Fonts
from ..styles.themes import Themes


class CertificadoTemplate(BaseDocumentTemplate):
    """
    Generador de certificados oficiales
    
    Crea certificados profesionales para:
    - Paz y Salvo de arrendamiento
    - Cumplimiento de pagos
    - Órdenes de servicio completadas
    - Certificaciones administrativas
    
    Example:
        >>> gen = CertificadoTemplate()
        >>> data = {
        ...     'certificado_id': 456,
        ...     'tipo': 'paz_y_salvo',
        ...     'beneficiario': {...},
        ...     'contenido': '...',
        ...     'firmante': {...}
        ... }
        >>> pdf_path = gen.generate(data)
    """
    
    def __init__(self, output_dir: Path = None):
        """Inicializa el generador de certificados"""
        super().__init__(output_dir)
        # Usar tema elegante para certificados
        self.theme = Themes.CERTIFICATE
    
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """Valida datos del certificado"""
        self._require_fields(
            data,
            'certificado_id', 'tipo', 'beneficiario',
            'contenido', 'firmante', 'fecha'
        )
        return True
    
    def generate(self, data: Dict[str, Any]) -> Path:
        """
        Genera el certificado en PDF
        
        Args:
            data: Diccionario con datos del certificado
            
        Returns:
            Path del PDF generado
        """
        # Habilitar QR de verificación
        self.enable_verification_qr('certificado', data['certificado_id'])
        
        # Crear documento
        filename = self._generate_filename('certificado', data['certificado_id'])
        titulo = self._get_titulo_certificado(data['tipo'])
        self.create_document(filename, titulo)
        
        # Construir contenido
        self._add_header_elegante(data, titulo)
        self._add_contenido(data)
        self._add_validez(data)
        self._add_firma_certificado(data)
        
        # Construir PDF
        return self.build()
    
    def _get_titulo_certificado(self, tipo: str) -> str:
        """Obtiene título según tipo de certificado"""
        titulos = {
            'paz_y_salvo': 'CERTIFICADO DE PAZ Y SALVO',
            'cumplimiento': 'CERTIFICADO DE CUMPLIMIENTO',
            'residencia': 'CERTIFICADO DE RESIDENCIA',
            'general': 'CERTIFICACIÓN'
        }
        return titulos.get(tipo, 'CERTIFICACIÓN')
    
    def _add_header_elegante(self, data: Dict[str, Any], titulo: str) -> None:
        """Agrega header elegante del certificado"""
        from reportlab.platypus import HRFlowable
        
        # Espacio superior
        self.add_spacer(0.5)
        
        # Logo/Título empresa (centrado y elegante)
        self.add_paragraph(
            f"<font size=18 color='#{int(self.theme.primary_color[0]*255):02X}{int(self.theme.primary_color[1]*255):02X}{int(self.theme.primary_color[2]*255):02X}'>"
            f"<b>{config.empresa_nombre}</b></font>",
            style_name='Body',
            alignment='center'
        )
        
        self.add_paragraph(
            f"<font size=9>{config.empresa_nit}</font>",
            style_name='Small',
            alignment='center'
        )
        
        # Línea decorativa dorada
        hr = HRFlowable(
            width="30%",
            thickness=1,
            color=Colors.to_reportlab(self.theme.accent_color),
            spaceAfter=20,
            spaceBefore=15,
            hAlign='CENTER'
        )
        self.story.append(hr)
        
        # Título del certificado
        self.add_title_main(titulo)
        
        # Número de certificado
        self.add_paragraph(
            f"<font size=10>No. {data['certificado_id']:08d}</font>",
            style_name='Small',
            alignment='center'
        )
        
        self.add_spacer(0.4)
    
    def _add_contenido(self, data: Dict[str, Any]) -> None:
        """Agrega contenido del certificado"""
        # Introducción
        self.add_paragraph(
            f"<b>EL SUSCRITO REPRESENTANTE LEGAL DE {config.empresa_nombre.upper()}</b>",
            style_name='Body',
            alignment='center'
        )
        
        self.add_spacer(0.2)
        
        # Certifica que...
        self.add_paragraph(
            "<b>CERTIFICA QUE:</b>",
            style_name='BodyBold',
            alignment='center'
        )
        
        self.add_spacer(0.3)
        
        # Información del beneficiario
        if 'beneficiario' in data:
            beneficiario = data['beneficiario']
            self.add_paragraph(
                f"<b>{beneficiario.get('nombre', 'N/A')}</b>, identificado(a) con "
                f"{beneficiario.get('tipo_documento', 'C.C.')} No. "
                f"<b>{beneficiario.get('documento', 'N/A')}</b>",
                style_name='Body',

            )
            self.add_spacer(0.2)
        
        # Contenido principal del certificado
        contenido = data['contenido']
        
        # Si es string, convertir a lista de párrafos
        if isinstance(contenido, str):
            parrafos = contenido.split('\n\n')
        else:
            parrafos = contenido
        
        for parrafo in parrafos:
            if parrafo.strip():
                self.add_paragraph(parrafo.strip(), style_name='Body')
                self.add_spacer(0.15)
        
        self.add_spacer(0.3)
    
    def _add_validez(self, data: Dict[str, Any]) -> None:
        """Agrega información de validez"""
        # Fecha y lugar de expedición
        fecha = data.get('fecha', datetime.now().strftime('%Y-%m-%d'))
        ciudad = data.get('ciudad', 'Bogotá D.C.')
        
        self.add_paragraph(
            f"Se expide en <b>{ciudad}</b>, a los <b>{self._formatear_fecha(fecha)}</b>.",
            style_name='Body',

        )
        
        # Validez
        validez_dias = data.get('validez_dias', 30)
        self.add_paragraph(
            f"<i>Certificado válido por {validez_dias} días calendario.</i>",
            style_name='Small',
            alignment='justify'
        )
        
        self.add_spacer(0.5)
    
    def _add_firma_certificado(self, data: Dict[str, Any]) -> None:
        """Agrega firma del certificado"""
        firmante = data['firmante']
        
        signatures = [(
            "REPRESENTANTE LEGAL",
            f"{firmante.get('nombre', 'N/A')}\n"
            f"{firmante.get('cargo', 'Gerente')}\n"
            f"{firmante.get('documento', 'N/A')}"
        )]
        
        table = AdvancedTable.create_signature_table(signatures)
        self.story.append(table)
        
        # Nota de verificación
        self.add_legal_footer_text(
            "La autenticidad de este certificado puede ser verificada escaneando el código QR "
            "o consultando en www.inmovelar.com/verificar"
        )
    
    def _formatear_fecha(self, fecha_str: str) -> str:
        """Formatea fecha en texto elegante"""
        try:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d')
            meses = [
                'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
                'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'
            ]
            mes = meses[fecha.month - 1]
            return f"{fecha.day} días del mes de {mes} de {fecha.year}"
        except:
            return fecha_str


__all__ = ['CertificadoTemplate']
