"""
Template para Recibos de Recaudo Élite (Layout Referencia)
==========================================================
Diseño basado en estructura visual 'Invoice' profesional:
- Encabezado limpio con Logo y Detalles.
- Bloques de 'Facturado a' y 'Propiedad' lado a lado.
- Tabla central de items.
- Pie de página con Totales destacados y Notas.

Autor: Sistema de Gestión Inmobiliaria
Fecha: 2026-02-04
"""

from pathlib import Path
from typing import Any, Dict

from reportlab.lib import colors
from reportlab.lib.units import inch, cm
from reportlab.platypus import Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT

from ..components.tables import AdvancedTable
from .base_template import BaseDocumentTemplate
from ..core.config import Colors, Fonts


class ReciboRecaudoElite(BaseDocumentTemplate):
    """
    Generador élite de recibos de pago - Layout Profesional
    """

    def __init__(self, output_dir: Path = None):
        super().__init__(output_dir)
        self.document_title = "RECIBO DE CAJA"

    def validate_data(self, data: Dict[str, Any]) -> bool:
        self._require_fields(
            data, "id", "propietario", "propiedad", "periodo", "fecha_pago", "valor_total", "arrendatario"
        )
        return True

    def generate(self, data: Dict[str, Any]) -> Path:
        self.empresa_config = data.get("empresa", {})
        self.data_source = data # Guardar ref completa para callbacks
        self.empresa_config = data.get("empresa", {})
        self.data_source = data # Guardar ref completa para callbacks
        self.enable_verification_qr("recaudo", data["id"])

        # Configurar Header/Footer con Membrete
        self.set_header_footer(self._header_footer_with_features, self._header_footer_with_features)
        
        filename = self._generate_filename("recibo_pago", data["id"])
        self.create_document(filename, self.document_title)

        # Ajuste de márgenes para maximizar espacio
        self.doc.leftMargin = 1.0 * cm
        self.doc.rightMargin = 1.0 * cm
        self.doc.topMargin = 1.0 * cm
        
        # --- ESTRUCTURA DEL DOCUMENTO ---
        
        # 1. HEADER SUPERIOR (Logo y Título/Fecha)
        self._layout_header(data)
        
        # 2. BLOQUES DE INFORMACIÓN (Arrendatario y Propiedad)
        self._layout_info_blocks(data)
        
        # 3. TABLA CENTRAL
        self._layout_table(data)
        
        # 4. FOOTER (Totales y Notas)
        self._layout_footer_totals(data)
        
        # 5. CONTACTO FINAL
        self._layout_contact_footer(data)

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


    def _format_fecha_es(self, fecha_str: str) -> str:
        """Convierte YYYY-MM-DD a 'DD de mes de YYYY'"""
        if not fecha_str: return "N/A"
        try:
            from datetime import datetime
            dt = datetime.strptime(str(fecha_str), '%Y-%m-%d')
            meses = {
                1: "enero", 2: "febrero", 3: "marzo", 4: "abril", 5: "mayo", 6: "junio",
                7: "julio", 8: "agosto", 9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
            }
            return f"{dt.day:02d} de {meses[dt.month]} de {dt.year}"
        except:
            return str(fecha_str)

    def _format_periodo_es(self, periodo_str: str) -> str:
        """Convierte YYYY-MM a 'mes de YYYY'"""
        if not periodo_str: return "N/A"
        try:
            # Soportar YYYY-MM o YYYY-MM-DD
            parts = str(periodo_str).split('-')
            if len(parts) >= 2:
                year = int(parts[0])
                month = int(parts[1])
                meses = {
                    1: "enero", 2: "febrero", 3: "marzo", 4: "abril", 5: "mayo", 6: "junio",
                    7: "julio", 8: "agosto", 9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
                }
                return f"{meses[month]} de {year}"
            return str(periodo_str)
        except:
            return str(periodo_str)

    def _layout_header(self, data: Dict[str, Any]):
        """
        Sección Superior:
        [ LOGO EMPRESA ]         [ TITULO RECIBO ]
                                 [ FECHA / ID    ]
        """
        # --- Bloque Título y Datos Clave (Alineado Derecha) ---
        style_title = self.styles["Heading1"]
        style_title.alignment = TA_LEFT
        style_title.fontSize = 18
        style_title.textColor = Colors.to_reportlab(Colors.GRAY_DARKEST)
        
        style_meta = self.styles["Heading2"]
        style_meta.alignment = TA_RIGHT
        style_meta.fontSize = 8
        style_meta.textColor = Colors.to_reportlab(Colors.GRAY_DARK)

        # Formatear fecha cabecera
        fecha_fmt = self._format_fecha_es(data.get('fecha_pago'))
        
        # Construir línea de detalles unificada
        detalles_linea = f"NO: <b>{data['id']:06d}</b>  |  FECHA: <b>{fecha_fmt.upper()}</b>  |  ESTADO: <b>{data.get('estado', 'PENDIENTE').upper()}</b>"

        header_content = [
            Spacer(1, 1.5*cm),
            Paragraph(self.document_title.upper(), style_title),
            Paragraph(detalles_linea, style_meta),
        ]

        # Tabla solo para el bloque derecho (Logo ya se dibuja en background)
        # Usamos una tabla que ocupe todo el ancho, celda izq vacía (espacio logo), celda der contenido
        # Ajuste de anchos: Logo area (3.5") + Texto area (4.0")
        # tbl = Table([["", header_content]], colWidths=[3.5*inch, 4.0*inch])
        tbl = Table([[header_content]])
        tbl.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'BOTTOM'),
            ('ALIGN', (1,0), (1,0), 'LEFT'),  # Alineación izquierda
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
        ]))
        
        self.story.append(tbl)
        #self.story.append(Spacer(1, 1.0*cm)) # Espacio generoso

    def _layout_info_blocks(self, data: Dict[str, Any]):
        """
        Bloques de información 'Facturado A' y 'Datos Propiedad'
        Línea separadora superior decorativa.
        """
        # Títulos de sección superior
        style_label_head = self.styles["Heading2"]
        style_label_head.textColor = Colors.to_reportlab(Colors.GRAY_DARKEST) # Color dorado/acento
        style_label_head.fontSize = 11
        style_label_head.alignment = TA_LEFT  # <--- Asegurar alineación izquierda explícita
        
        style_body = self.styles["Body"]
        style_body.fontSize = 9
        style_body.leading = 11
        style_body.alignment = TA_LEFT # Asegurar cuerpo a la izquierda también

        style_val = self.styles["Body"]
        style_val.fontSize = 9
        style_val.leading = 11
        style_val.alignment = TA_LEFT

        style_val_bold = self.styles["BodyBold"]
        style_val_bold.fontSize = 9
        style_val_bold.leading = 11
        style_val_bold.alignment = TA_LEFT

        # --- Bloque Izquierdo: RECIBIDO DE ---
        left_text = [
            Paragraph("RECIBIDO DE:", style_label_head),
            Paragraph(f"<b>{data['arrendatario']}</b>", style_body),
            Paragraph(data.get('arrendatario_doc', ''), style_body),
            Paragraph(data.get('telefono', ''), style_body),
            Paragraph(data.get('email', ''), style_body),
        ]

        # --- Bloque Derecho:        # --- Caja Propiedad ---
        periodo_fmt = self._format_periodo_es(data.get('periodo')).capitalize()
        
        propiedad_content = [
            [Paragraph("PROPIEDAD / CONTRATO:", style_label_head)],
            [Paragraph(data.get('propiedad', 'N/A').upper(), style_val_bold)], # Dirección en negrita
            [Paragraph(f"Municipio: {data.get('municipio', 'ARMENIA')} | Dept: {data.get('departamento', 'QUINDÍO')}", style_val)],
            [Paragraph(f"Período Facturado: {periodo_fmt}", style_val)],
        ]
        
        right_text = Table(propiedad_content, colWidths=[3.8*inch])
        right_text.setStyle(TableStyle([
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ]))

        # Tabla contenedora de los dos bloques
        tbl = Table([[left_text, right_text]], colWidths=[3.8*inch, 3.8*inch])
        tbl.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LINEABOVE', (0,0), (-1,0), 2, Colors.to_reportlab(Colors.GRAY_DARKEST)), # Línea dorada superior
            ('TOPPADDING', (0,0), (-1,-1), 12),
        ]))
        
        self.story.append(tbl)
        self.story.append(Spacer(1, 0.8*cm))

    def _layout_table(self, data: Dict[str, Any]):
        """
        Tabla central de items estilo 'Invoice'
        Encabezados coloreados, filas alternas.
        """
        headers = ["DESCRIPCIÓN / CONCEPTO", "PERÍODO", "VALOR"]
        
        # Preparar filas
        rows = []
        conceptos = data.get("conceptos", [])
        
        if not conceptos:
             # Default row if no concepts
             periodo_fmt = self._format_periodo_es(data.get('periodo')).capitalize()
             rows.append([
                "Canon de Arrendamiento",
                periodo_fmt,
                f"${data['valor_total']:,.0f}"
            ])
        else:
            for c in conceptos:
                # Manejo robusto de dict u objeto
                if isinstance(c, dict):
                    tipo = c.get('tipo', 'Concepto')
                    per = c.get('periodo', data.get('periodo'))
                    val = c.get('valor', 0)
                else:
                    tipo = getattr(c, 'tipo_concepto', 'Concepto')
                    per = getattr(c, 'periodo', data.get('periodo'))
                    val = getattr(c, 'valor', 0)
                
                # Formatear periodo fila
                per_fmt = self._format_periodo_es(per).capitalize()
                rows.append([tipo, per_fmt, f"${val:,.0f}"])

        # Construir tabla
        table_data = [headers] + rows
        t = Table(table_data, colWidths=[4.2*inch, 1.5*inch, 1.8*inch])
        
        # Estilos de tabla
        colors_obj = Colors()
        primary_col = colors_obj.to_reportlab(Colors.PRIMARY) # Azul corporativo
        accent_col = colors_obj.to_reportlab(Colors.GRAY_MEDIUM) # Dorado
        
        style = [
            # Header
            ('BACKGROUND', (0,0), (-1,0), accent_col), # Encabezado Dorado según referencia LOGOPET
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), Fonts.MAIN_BOLD),
            ('FONTSIZE', (0,0), (-1,0), 10),
            ('ALIGN', (0,0), (-1,0), 'CENTER'),
            ('BOTTOMPADDING', (0,0), (-1,0), 10),
            ('TOPPADDING', (0,0), (-1,0), 10),
            
            # Rows
            ('ALIGN', (0,1), (0,-1), 'LEFT'),   # Desc izquierda
            ('ALIGN', (1,1), (-1,-1), 'CENTER'), # Resto centro/derecha
            ('ALIGN', (2,1), (2,-1), 'RIGHT'),   # Valor derecha
            ('FONTNAME', (0,1), (-1,-1), Fonts.MAIN),
            ('FONTSIZE', (0,1), (-1,-1), 10),
            ('BOTTOMPADDING', (0,1), (-1,-1), 8),
            ('TOPPADDING', (0,1), (-1,-1), 8),
            
            # Grid
            ('LINEBELOW', (0,0), (-1,-1), 0.5, colors.lightgrey),
            ('LINEBEFORE', (1,0), (1,-1), 0.5, colors.lightgrey), # Líneas verticales internas
            ('LINEBEFORE', (2,0), (2,-1), 0.5, colors.lightgrey),
        ]
        
        # Zebra striping suave
        for i, _ in enumerate(rows):
             if i % 2 == 0:
                style.append(('BACKGROUND', (0, i+1), (-1, i+1), colors.whitesmoke))

        t.setStyle(TableStyle(style))
        self.story.append(t)
        self.story.append(Spacer(1, 0.5*cm))

    def _layout_footer_totals(self, data: Dict[str, Any]):
        """
        Sección inferior dividida:
        [ Info Pago / Notas ]       [ Subtotal / Total ]
        """
        # --- Lado Izquierdo: Info Pago ---
        style_bold = self.styles["BodyBold"]
        style_normal = self.styles["Body"]
        
        left_content = [
            Paragraph("INFORMACIÓN DE PAGO:", self.styles["Heading2"]),
            Paragraph(f"<b>Método:</b> {data.get('metodo_pago', 'N/A')}", style_normal),
            Paragraph(f"<b>Referencia:</b> {data.get('referencia_pago', 'N/A')}", style_normal),
            Paragraph(f"<b>Banco/Cuenta:</b> {data.get('banco', 'N/A')} - {data.get('tipo_cuenta', '')}", style_normal),
            Spacer(1, 0.2*cm),
        ]
        
        if data.get("observaciones"):
            left_content.append(Paragraph("OBSERVACIONES:", self.styles["Heading2"]))
            left_content.append(Paragraph(data["observaciones"], self.styles["Small"]))

        # --- Lado Derecho: Totales ---
        # Estilo "Caja Negra" para el Total según referencia LOGOPET
        total_val = f"${data['valor_total']:,.0f}"
        
        # Tabla de totales
        totals_data = [
            ["SUBTOTAL", total_val],
            ["DESCUENTOS", "$0"], # Placeholder
            ["TOTAL", total_val]
        ]
        
        t_totals = Table(totals_data, colWidths=[1.2*inch, 1.3*inch])
        
        # Estilos Totales
        black_col = Colors.to_reportlab(Colors.GRAY_LIGHTEST)
        accent_col = Colors.to_reportlab(Colors.GRAY_DARKEST)
        
        t_totals.setStyle(TableStyle([
            ('FONTNAME', (0,0), (-1,-1), Fonts.MAIN_BOLD),
            ('ALIGN', (0,0), (0,-1), 'LEFT'),  # Labels left
            ('ALIGN', (1,0), (1,-1), 'RIGHT'), # Values right
            ('PADDING', (0,0), (-1,-1), 6),
            
            # Row Subtotal
            ('BACKGROUND', (0,0), (-1,0), colors.whitesmoke),
            
            # Row Total (Fondo oscuro, texto dorado/claro)
            ('BACKGROUND', (0,2), (-1,2), black_col),
            ('TEXTCOLOR', (0,2), (-1,2), accent_col),
            ('FONTSIZE', (0,2), (-1,2), 12),
            ('TOPPADDING', (0,2), (-1,2), 10),
            ('BOTTOMPADDING', (0,2), (-1,2), 10),
        ]))

        # Grid Contenedor
        main_footer = Table([[left_content, t_totals]], colWidths=[4.5*inch, 3.0*inch])
        main_footer.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('ALIGN', (1,0), (1,0), 'RIGHT'), # Tabla de totales a la derecha
        ]))
        
        self.story.append(main_footer)
        self.story.append(Spacer(1, 1.0*cm))

    def _layout_contact_footer(self, data: Dict[str, Any]):
        """Pie de página con contacto y términos"""
        style_center = self.styles["Small"]
        style_center.alignment = TA_CENTER
        
        text = [
            Paragraph("TÉRMINOS Y CONDICIONES:", self.styles["Heading2"]),
            Paragraph("Este recibo constituye prueba de pago. Consérvelo para sus registros.", self.styles["Small"]),
        ]
        
        for item in text:
            self.story.append(item)

__all__ = ["ReciboRecaudoElite"]
