"""
Template para Informes (Stub)
=============================
Plantilla base para informes generales.
"""

from pathlib import Path
from typing import Any, Dict

from reportlab.lib import colors
from .base_template import BaseDocumentTemplate

class InformeTemplate(BaseDocumentTemplate):
    """
    Generador de informes (Placeholder con Membrete)
    """

    def __init__(self, output_dir: Path = None):
        super().__init__(output_dir)
        self.document_title = "INFORME GENERAL"

    def validate_data(self, data: Dict[str, Any]) -> bool:
        return True

    def generate(self, data: Dict[str, Any]) -> Path:
        self.enable_verification_qr("informe", data.get("id", 0))
        
        # Configurar Header/Footer con Membrete
        self.set_header_footer(self._header_footer_with_features, self._header_footer_with_features)
        
        filename = self._generate_filename("informe", data.get("id", 0))
        self.create_document(filename, self.document_title)
        
        self.add_title_main(self.document_title)
        self.add_paragraph("Contenido del informe pendiente de implementación.", alignment="CENTER")
        
        return self.build()

    def _header_footer_with_features(self, canvas_obj, doc):
        """
        Header y footer con Membrete (Imagen de fondo)
        """
        # 0. Dibujar MEMBRETE (Fondo completo)
        current_dir = Path(__file__).parent
        membrete_path = current_dir / "VELAR INMOBILIARIA_membrete_modificada.png"
        
        try:
            if membrete_path.exists():
                # Dibujar imagen cubriendo toda la página
                page_width, page_height = doc.pagesize
                # mask='auto' maneja transparencias si es PNG
                canvas_obj.drawImage(str(membrete_path), 0, 0, width=page_width, height=page_height, mask='auto', preserveAspectRatio=False)
        except Exception as e:
            # Fallo silencioso o log mínimo para no romper generación
            print(f"Advertencia: No se pudo cargar fondo {membrete_path}: {e}")

        # 1. Agregar marca de agua si aplica (logic from Base)
        if self.watermark_text:
            from ..components.watermarks import Watermark
            Watermark.add_text_watermark(
                canvas_obj,
                text=self.watermark_text,
                opacity=self.watermark_opacity,
                position=self.watermark_style,
            )
            
        # 2. Footer simple (SOLO Página)
        canvas_obj.saveState()
        
        # Página y Timestamp
        page_num = canvas_obj.getPageNumber()
        canvas_obj.setFont('Helvetica', 8)
        canvas_obj.setFillColor(colors.gray)
        
        center_x = doc.pagesize[0] / 2
        
        # Centrado Página (más abajo que la dirección)
        canvas_obj.drawCentredString(center_x, 20, f"Página {page_num}")
        
        # 4. Textos Verticales en Márgenes
        canvas_obj.setFont('Helvetica', 8)
        canvas_obj.setFillColor(colors.lightgrey) # Color tenue para no distraer
        
        from datetime import datetime
        dt_str = datetime.now().strftime('%Y-%m-%d %H:%M')
        
        # Margen Izquierdo (Vertical)
        canvas_obj.saveState()
        canvas_obj.translate(30, 250) # Ajustar posición X,Y
        canvas_obj.rotate(90)
        canvas_obj.drawString(0, 0, "Impreso por Inmobiliaria Velar SAS - NIT 901.703.515 - Correo: inmobiliariavelarsasaxm@gmail.com")
        canvas_obj.restoreState()
        
        # Margen Derecho (Vertical)
        canvas_obj.saveState()
        canvas_obj.translate(doc.pagesize[0] - 30, 250)
        canvas_obj.rotate(90)
        canvas_obj.drawString(0, 0, f"Generado: {dt_str}")
        canvas_obj.restoreState()
        
        canvas_obj.restoreState()

__all__ = ["InformeTemplate"]
