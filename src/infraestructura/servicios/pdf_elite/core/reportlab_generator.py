"""
Generador PDF usando ReportLab
===============================
Implementación concreta del generador PDF usando la biblioteca ReportLab.
Proporciona funcionalidades avanzadas de generación de documentos.

Autor: Sistema de Gestión Inmobiliaria
Fecha: 2026-01-18
"""

from reportlab.lib.pagesizes import A4, letter
from reportlab.lib.units import inch, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, KeepTogether, FrameBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas as pdf_canvas
from reportlab.lib import colors as rl_colors

from typing import Any, Dict, List, Optional, Tuple, Callable
from pathlib import Path
from datetime import datetime

from .base_generator import BasePDFGenerator
from .config import config, Colors, Fonts, Constants


class ReportLabGenerator(BasePDFGenerator):
    """
    Generador PDF élite usando ReportLab
    
    Implementa generación avanzada de PDFs con ReportLab, proporcionando
    métodos de alto nivel para crear documentos profesionales con facilidad.
    
    Attributes:
        pagesize: Tamaño de página (A4 o Letter)
        styles: Diccionario de estilos de párrafo personalizados
        story: Lista de elementos (flowables) del documento
        doc: Objeto SimpleDocTemplate de ReportLab
        
    Example:
        >>> gen = ReportLabGenerator()
        >>> gen.create_document("mi_doc.pdf", "Mi Documento")
        >>> gen.add_title("Título Principal")
        >>> gen.add_paragraph("Contenido del documento")
        >>> gen.build()
    """
    
    def __init__(self, output_dir: Optional[Path] = None):
        """
        Inicializa el generador ReportLab
        
        Args:
            output_dir: Directorio de salida opcional
        """
        super().__init__(output_dir)
        
        # Configuración de página
        self.pagesize = A4 if config.page_size == "A4" else letter
        
        # Estilos personalizados
        self.styles = self._create_custom_styles()
        
        # Story (lista de flowables)
        self.story: List = []
        
        # Documento
        self.doc: Optional[SimpleDocTemplate] = None
        
        # Callbacks para header/footer
        self._on_first_page: Optional[Callable] = None
        self._on_later_pages: Optional[Callable] = None
    
    # ========================================================================
    # CREACIÓN Y CONFIGURACIÓN DE DOCUMENTO
    # ========================================================================
    
    def create_document(
        self,
        filename: str,
        title: str = "Documento",
        author: str = None
    ) -> SimpleDocTemplate:
        """
        Crea un nuevo documento PDF
        
        Args:
            filename: Nombre del archivo de salida
            title: Título del documento
            author: Autor del documento (default: nombre empresa)
            
        Returns:
            Objeto SimpleDocTemplate configurado
        """
        output_path = self._get_output_path(filename)
        
        # Log core layer activity
        import logging
        logger = logging.getLogger('PDFElite')
        logger.debug(f"⚙️  CORE: ReportLabGenerator.create_document() invoked")
        logger.debug(f"📄 Output path: {output_path}")
        logger.debug(f"📑 Document title: {title}")
        logger.debug(f"📏 Page size: {self.pagesize}")
        
        # Establecer metadata
        self.document_title = title
        self.add_metadata('author', author or config.empresa_nombre)
        
        # Crear documento
        self.doc = SimpleDocTemplate(
            str(output_path),
            pagesize=self.pagesize,
            topMargin=config.margins_top,
            rightMargin=config.margins_right,
            bottomMargin=config.margins_bottom,
            leftMargin=config.margins_left,
            title=title,
            author=self.metadata['author'],
            creator=self.metadata['creator'],
            compress=config.compression
        )
        
        # Reiniciar story
        self.story = []
        
        return self.doc
    
    def _create_custom_styles(self) -> Dict[str, ParagraphStyle]:
        """
        Crea estilos personalizados para el documento
        
        Returns:
            Diccionario con estilos personalizados
        """
        # Obtener estilos base de ReportLab
        base_styles = getSampleStyleSheet()
        
        # Definir estilos personalizados
        custom_styles = {
            'TitleMain': ParagraphStyle(
                'TitleMain',
                parent=base_styles['Title'],
                fontSize=Fonts.SIZE_TITLE_MAIN,
                textColor=Colors.to_reportlab(Colors.PRIMARY),
                spaceAfter=20,
                spaceBefore=10,
                alignment=TA_CENTER,
                fontName=Fonts.TITLE,
                leading=Fonts.get_leading(Fonts.SIZE_TITLE_MAIN, 'tight')
            ),
            
            'Title': ParagraphStyle(
                'CustomTitle',
                parent=base_styles['Title'],
                fontSize=Fonts.SIZE_TITLE,
                textColor=Colors.to_reportlab(Colors.PRIMARY),
                spaceAfter=16,
                spaceBefore=10,
                alignment=TA_CENTER,
                fontName=Fonts.TITLE,
                leading=Fonts.get_leading(Fonts.SIZE_TITLE, 'normal')
            ),
            
            'Subtitle': ParagraphStyle(
                'CustomSubtitle',
                parent=base_styles['Heading2'],
                fontSize=Fonts.SIZE_SUBTITLE,
                textColor=Colors.to_reportlab(Colors.SECONDARY),
                spaceAfter=12,
                spaceBefore=8,
                fontName=Fonts.SUBTITLE,
                leading=Fonts.get_leading(Fonts.SIZE_SUBTITLE, 'normal')
            ),
            
            'Heading1': ParagraphStyle(
                'CustomHeading1',
                parent=base_styles['Heading1'],
                fontSize=Fonts.SIZE_HEADING_1,
                textColor=Colors.to_reportlab(Colors.GRAY_DARKEST),
                spaceAfter=10,
                spaceBefore=12,
                fontName=Fonts.HEADING,
                leading=Fonts.get_leading(Fonts.SIZE_HEADING_1, 'normal')
            ),
            
            'Heading2': ParagraphStyle(
                'CustomHeading2',
                parent=base_styles['Heading2'],
                fontSize=Fonts.SIZE_HEADING_2,
                textColor=Colors.to_reportlab(Colors.GRAY_DARK),
                spaceAfter=8,
                spaceBefore=10,
                fontName=Fonts.HEADING,
                leading=Fonts.get_leading(Fonts.SIZE_HEADING_2, 'normal')
            ),
            
            'Body': ParagraphStyle(
                'CustomBody',
                parent=base_styles['Normal'],
                fontSize=Fonts.SIZE_BODY,
                spaceAfter=6,
                alignment=TA_LEFT,  # Changed from TA_JUSTIFY to fix ReportLab bug
                fontName=Fonts.BODY,
                leading=Fonts.get_leading(Fonts.SIZE_BODY, 'normal')
            ),
            
            'BodyBold': ParagraphStyle(
                'CustomBodyBold',
                parent=base_styles['Normal'],
                fontSize=Fonts.SIZE_BODY,
                spaceAfter=6,
                alignment=TA_LEFT,  # Changed from TA_JUSTIFY to fix ReportLab bug
                fontName='Helvetica-Bold',  # Usar fuente estándar
                leading=Fonts.get_leading(Fonts.SIZE_BODY, 'normal')
            ),
            
            'Small': ParagraphStyle(
                'CustomSmall',
                parent=base_styles['Normal'],
                fontSize=Fonts.SIZE_SMALL,
                textColor=Colors.to_reportlab(Colors.GRAY_DARK),
                fontName=Fonts.BODY,
                leading=Fonts.get_leading(Fonts.SIZE_SMALL, 'normal')
            ),
            
            'Tiny': ParagraphStyle(
                'CustomTiny',
                parent=base_styles['Normal'],
                fontSize=Fonts.SIZE_TINY,
                textColor=Colors.to_reportlab(Colors.GRAY_MEDIUM),
                fontName=Fonts.BODY,
                leading=Fonts.get_leading(Fonts.SIZE_TINY, 'tight')
            ),
            
            'Code': ParagraphStyle(
                'CustomCode',
                parent=base_styles['Code'],
                fontSize=Fonts.SIZE_SMALL,
                fontName=Fonts.CODE,
                backColor=Colors.to_reportlab(Colors.GRAY_LIGHTEST),
                leftIndent=10,
                rightIndent=10,
                spaceAfter=8
            ),
        }
        
        return custom_styles
    
    # ========================================================================
    # MÉTODOS PARA AGREGAR CONTENIDO
    # ========================================================================
    
    def add_title_main(self, text: str) -> None:
        """Agrega título principal del documento"""
        self.story.append(Paragraph(text, self.styles['TitleMain']))
        self.story.append(Spacer(1, Constants.SPACING_NORMAL))
    
    def add_title(self, text: str) -> None:
        """Agrega título de sección"""
        self.story.append(Paragraph(text, self.styles['Title']))
        self.story.append(Spacer(1, Constants.SPACING_SMALL))
    
    def add_subtitle(self, text: str) -> None:
        """Agrega subtítulo"""
        self.story.append(Paragraph(text, self.styles['Subtitle']))
        self.story.append(Spacer(1, Constants.SPACING_SMALL))
    
    def add_heading(self, text: str, level: int = 1) -> None:
        """
        Agrega encabezado de nivel 1 o 2
        
        Args:
            text: Texto del encabezado
            level: Nivel (1 o 2)
        """
        style_name = f'Heading{level}' if level in [1, 2] else 'Heading1'
        self.story.append(Paragraph(text, self.styles[style_name]))
        self.story.append(Spacer(1, Constants.SPACING_TINY))
    
    def add_paragraph(
        self,
        text: str,
        style_name: str = 'Body',
        **style_overrides
    ) -> None:
        """
        Agrega párrafo de texto
        
        Args:
            text: Texto del párrafo (puede incluir HTML básico)
            style_name: Nombre del estilo a usar
            **style_overrides: Sobrescribir propiedades del estilo
        """
        style = self.styles.get(style_name, self.styles['Body'])
        
        # Aplicar sobrescrituras si hay
        if style_overrides:
            # Convertir alignment string a constante TA_*
            if 'alignment' in style_overrides:
                align_map = {
                    'left': TA_LEFT,
                    'center': TA_CENTER,
                    'right': TA_RIGHT,
                    'justify': TA_LEFT  # Usar LEFT en lugar de JUSTIFY para evitar bug
                }
                align_val = style_overrides['alignment']
                if isinstance(align_val, str):
                    style_overrides['alignment'] = align_map.get(align_val.lower(), TA_LEFT)
            
            style = ParagraphStyle('Temp', parent=style, **style_overrides)
        
        self.story.append(Paragraph(text, style))
    
    def add_spacer(self, height_inches: float = 0.2) -> None:
        """
        Agrega espacio vertical
        
        Args:
            height_inches: Altura en pulgadas
        """
        self.story.append(Spacer(1, height_inches * inch))
    
    def add_page_break(self) -> None:
        """Agrega salto de página"""
        self.story.append(PageBreak())
    
    def add_table(
        self,
        data: List[List[Any]],
        col_widths: Optional[List[float]] = None,
        style: str = 'default',
        custom_style_commands: Optional[List] = None
    ) -> None:
        """
        Agrega tabla al documento
        
        Args:
            data: Datos de la tabla [[row1], [row2], ...]
            col_widths: Anchos de columnas en puntos
            style: Estilo predefinido ('default', 'striped', 'minimal')
            custom_style_commands: Comandos de estilo personalizados
        """
        from ..components.tables import AdvancedTable
        
        if custom_style_commands:
            # Estilo personalizado
            table = Table(data, colWidths=col_widths, repeatRows=1)
            table.setStyle(TableStyle(custom_style_commands))
        else:
            # Usar componente avanzado
            table = AdvancedTable.create_data_table(
                headers=data[0],
                rows=data[1:],
                col_widths=col_widths
            )
        
        self.story.append(table)
        self.story.append(Spacer(1, Constants.SPACING_NORMAL))
    
    def add_image(
        self,
        image_path: Path,
        width: Optional[float] = None,
        height: Optional[float] = None,
        align: str = 'center'
    ) -> None:
        """
        Agrega imagen al documento
        
        Args:
            image_path: Path de la imagen
            width: Ancho deseado (None = tamaño original)
            height: Alto deseado (None = tamaño original)
            align: Alineación ('left', 'center', 'right')
        """
        if not image_path.exists():
            raise FileNotFoundError(f"Imagen no encontrada: {image_path}")
        
        img = Image(str(image_path), width=width, height=height)
        
        # Aplicar alineación
        if align == 'center':
            img.hAlign = 'CENTER'
        elif align == 'right':
            img.hAlign = 'RIGHT'
        else:
            img.hAlign = 'LEFT'
        
        self.story.append(img)
        self.story.append(Spacer(1, Constants.SPACING_SMALL))
    
    # ========================================================================
    # CONSTRUCCIÓN DEL PDF
    # ========================================================================
    
    def set_header_footer(
        self,
        on_first_page: Optional[Callable] = None,
        on_later_pages: Optional[Callable] = None
    ) -> None:
        """
        Establece funciones callback para header/footer
        
        Args:
            on_first_page: Función para primera página
            on_later_pages: Función para páginas siguientes
        """
        self._on_first_page = on_first_page or self._default_header_footer
        self._on_later_pages = on_later_pages or self._default_header_footer
    
    def build(self) -> Path:
        """
        Construye el documento PDF final
        
        Returns:
            Path del archivo generado
            
        Raises:
            ValueError: Si no se ha creado el documento
        """
        if not self.doc:
            raise ValueError(
                "Debe crear el documento con create_document() primero"
            )
        
        # Establecer callbacks si no están definidos
        if not self._on_first_page:
            self.set_header_footer()
        
        # Log build process
        import logging
        logger = logging.getLogger('PDFElite')
        logger.debug(f"🏗️  CORE: Building PDF document...")
        logger.debug(f"📊 Story elements: {len(self.story)}")
        logger.debug(f"📄 Output file: {self.doc.filename}")
        
        # Construir PDF
        self.doc.build(
            self.story,
            onFirstPage=self._on_first_page,
            onLaterPages=self._on_later_pages
        )
        
        output_path = Path(self.doc.filename)
        self._generated_file = output_path
        
        return output_path
    
    def _default_header_footer(
        self,
        canvas_obj: pdf_canvas.Canvas,
        doc: SimpleDocTemplate
    ) -> None:
        """
        Header y footer por defecto
        
        Args:
            canvas_obj: Objeto canvas de ReportLab
            doc: Documento SimpleDocTemplate
        """
        canvas_obj.saveState()
        
        # === HEADER ===
        # Nombre de la empresa
        canvas_obj.setFont(Fonts.MAIN_BOLD, Fonts.SIZE_BODY)
        canvas_obj.setFillColorRGB(*Colors.PRIMARY)
        canvas_obj.drawString(
            inch,
            doc.height + doc.topMargin - 0.3*inch,
            config.empresa_nombre
        )
        
        # Información de contacto
        canvas_obj.setFont(Fonts.MAIN, Fonts.SIZE_TINY)
        canvas_obj.setFillColorRGB(*Colors.GRAY_DARK)
        info_text = (
            f"{config.empresa_nit} | "
            f"{config.empresa_telefono} | "
            f"{config.empresa_email}"
        )
        canvas_obj.drawString(
            inch,
            doc.height + doc.topMargin - 0.5*inch,
            info_text
        )
        
        # Línea separadora
        canvas_obj.setStrokeColorRGB(*Colors.PRIMARY)
        canvas_obj.setLineWidth(2)
        canvas_obj.line(
            inch,
            doc.height + doc.topMargin - 0.6*inch,
            doc.width + doc.leftMargin - inch,
            doc.height + doc.topMargin - 0.6*inch
        )
        
        # === FOOTER ===
        # Número de página
        canvas_obj.setFont(Fonts.MAIN, Fonts.SIZE_TINY)
        canvas_obj.setFillColorRGB(*Colors.GRAY_MEDIUM)
        page_text = f"Página {doc.page}"
        canvas_obj.drawCentredString(
            doc.width/2 + doc.leftMargin,
            0.5*inch,
            page_text
        )
        
        # Fecha de generación
        date_text = f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        canvas_obj.drawRightString(
            doc.width + doc.leftMargin - inch,
            0.5*inch,
            date_text
        )
        
        canvas_obj.restoreState()
    
    # ========================================================================
    # IMPLEMENTACIÓN DE MÉTODOS ABSTRACTOS
    # ========================================================================
    
    def generate(self, data: Dict[str, Any]) -> Path:
        """
        Implementación base del método generate
        
        Este método debe ser sobrescrito por generadores específicos.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} debe implementar el método generate()"
        )
    
    def validate_data(self, data: Dict[str, Any]) -> bool:
        """
        Validación base de datos
        
        Sobrescribir en subclases para validación específica.
        """
        return isinstance(data, dict)


__all__ = ['ReportLabGenerator']
