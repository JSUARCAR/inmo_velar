"""
Template para Incidentes Élite
==============================
Reporte dinámico que cambia según el estado del incidente:
- Reportado/Revisión -> Reporte de Incidente
- Cotizado -> Comparativo de Cotizaciones
- Aprobado/Reparación -> Orden de Trabajo
- Finalizado -> Acta de Finalización

Autor: Sistema de Gestión Inmobiliaria
Fecha: 2026-02-04
"""

from pathlib import Path
from typing import Any, Dict, List

from reportlab.lib import colors
from reportlab.lib.units import inch, cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Table, TableStyle, Paragraph, Spacer, KeepTogether
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT, TA_JUSTIFY

from ..components.tables import AdvancedTable
from .base_template import BaseDocumentTemplate
from ..core.config import Colors, Fonts


class IncidenteTemplateElite(BaseDocumentTemplate):
    """
    Generador PDF multifuncional para el ciclo de vida de incidentes.
    """

    def __init__(self, output_dir: Path = None):
        super().__init__(output_dir)
        self.titulo_documento = "REPORTE DE INCIDENTE"
        self.color_estado = Colors.PRIMARY

    def validate_data(self, data: Dict[str, Any]) -> bool:
        self._require_fields(data, "id", "descripcion", "estado", "propiedad")
        return True

    def _determinar_tipo_documento(self, estado: str):
        """Configura títulos y colores según el estado"""
        estado = estado.lower()
        if estado in ["finalizado"]:
            self.titulo_documento = "ACTA DE FINALIZACIÓN"
            self.color_estado = Colors.SUCCESS
        elif estado in ["aprobado", "en reparacion", "en reparación"]:
            self.titulo_documento = "ORDEN DE TRABAJO"
            self.color_estado = Colors.WARNING  # O un color distintivo para OT
        elif estado in ["cotizado"]:
            self.titulo_documento = "SOLICITUD DE APROBACIÓN"
        elif estado in ["cancelado"]:
            self.titulo_documento = "REPORTE DE INCIDENTE (CANCELADO)"
            self.color_estado = Colors.DANGER
        else:
            self.titulo_documento = "REPORTE DE INCIDENTE"
            self.color_estado = Colors.PRIMARY

    def generate(self, data: Dict[str, Any]) -> Path:
        self.empresa_config = data.get("empresa", {})
        self.data_source = data
        self.enable_verification_qr("incidente", data["id"])
        
        self._determinar_tipo_documento(data.get("estado", ""))
        
        filename = self._generate_filename(f"incidente_{data.get('estado','').lower()}", data["id"])
        self.create_document(filename, self.titulo_documento)

        # Márgenes
        self.doc.leftMargin = 1.0 * cm
        self.doc.rightMargin = 1.0 * cm
        self.doc.topMargin = 1.0 * cm
        
        # --- ESTRUCTURA ---
        
        # 1. HEADER (Logo, Título y Metadatos)
        self._layout_header(data)
        
        # 2. INFORMACIÓN GENERAL (Propiedad, Reportante)
        self._layout_info_general(data)
        
        # 3. DETALLE DEL PROBLEMA
        self._layout_detalle_problema(data)
        
        # 4. SECCIONES DINÁMICAS SEGÚN ESTADO
        estado = data.get("estado", "").lower()
        
        if estado == "cotizado":
            self._layout_cotizaciones(data)
            
        elif estado in ["aprobado", "en reparacion", "en reparación"]:
            self._layout_orden_trabajo(data)
            
        elif estado == "finalizado":
             # Mostrar historial de cotización aprobada si existe + cierre
            self._layout_orden_trabajo(data, titulo="EJECUCIÓN")
            self._layout_cierre_final(data)

        # 5. FOOTER FIRMAS (Solo para OT y Acta)
        if estado in ["aprobado", "en reparacion", "en reparación", "finalizado"]:
            self._layout_firmas()
            
        return self.build()

    # ================= LAYOUT COMPONENTS =================

    def _default_header_footer(self, canvas_obj, doc):
        """Footer estándar con paginación y contacto"""
        canvas_obj.saveState()
        page_width = doc.width + doc.leftMargin + doc.rightMargin
        
        # Footer Contacto
        txt_footer = [
            "Calle 19 No. 16 – 44 Centro Comercial Manhatan Local 15 Armenia, Quindío.",
            "Contacto: +57 (6) 735 9999 | mantenimiento@inmovelar.com"
        ]
        
        canvas_obj.setFont(Fonts.MAIN_BOLD, 8)
        canvas_obj.setFillColor(Colors.to_reportlab(Colors.GRAY_DARK))
        
        y_pos = 1.8 * cm
        center_x = page_width / 2
        
        for line in txt_footer:
            canvas_obj.drawCentredString(center_x, y_pos, line)
            y_pos -= 10
            
        # Paginación
        canvas_obj.setFont(Fonts.MAIN, 8)
        canvas_obj.setFillColor(Colors.to_reportlab(Colors.GRAY_MEDIUM))
        canvas_obj.drawCentredString(center_x, 0.8 * cm, f"Página {doc.page} | Gestión de Incidentes Velar")

        # Restaurar
        canvas_obj.restoreState()
        
        # Dibujar Logo si existe (Misma lógica que Recibo)
        logo_data = self.empresa_config.get("logo_base64")
        if not logo_data and hasattr(self, 'data_source'): 
             logo_data = self.data_source.get("logo_base64")
             
        if logo_data:
            try:
                import base64
                import io
                from reportlab.lib.utils import ImageReader
                if "," in logo_data: logo_data = logo_data.split(",")[1]
                logo_bytes = base64.b64decode(logo_data)
                img = ImageReader(io.BytesIO(logo_bytes))
                
                logo_w, logo_h = 2.0*inch, 0.8*inch
                # Centrar Logo
                x = (page_width - logo_w) / 2
                y = doc.height + doc.topMargin - logo_h + 0.95*inch
                canvas_obj.drawImage(img, x, y, width=logo_w, height=logo_h, mask='auto', preserveAspectRatio=True)
            except: pass

    def _layout_header(self, data):
        """Encabezado con Título Dinámico y Estado"""
        styles = self.styles
        
        # Estilos
        s_title = styles["Heading1"]
        s_title.alignment = TA_CENTER
        s_title.fontSize = 12  # Reducido de 20
        s_title.textColor = Colors.to_reportlab(Colors.GRAY_DARKEST)
        
        s_meta = ParagraphStyle(
            "MetaCentered",
            parent=styles["Heading2"],
            alignment=TA_CENTER,
            fontSize=8,
            textColor=Colors.to_reportlab(Colors.GRAY_DARK),
            spaceBefore=6
        )
        
        # Prioridad con color
        prioridad_color = "black"
        prio = data.get('prioridad', 'Media').upper()
        if prio == 'ALTA': prioridad_color = "red"
        elif prio == 'BAJA': prioridad_color = "green"
        
        # Formato lineal separado por pipes
        # INCIDENTE NO: 000123 | FECHA: 2023-01-01 | PRIORIDAD: ALTA | ESTADO: REPORTADO
        detalles = f"""
        INCIDENTE NO: <b>{data['id']:06d}</b> &nbsp;|&nbsp; 
        FECHA: {self._format_date(data.get('fecha_reporte'))} &nbsp;|&nbsp; 
        PRIORIDAD: <font color='{prioridad_color}'>{prio}</font> &nbsp;|&nbsp; 
        ESTADO: <b>{data.get('estado', '').upper()}</b>
        """
        
        # Layout Secuencial:
        # 1. Espacio para logo (arriba centro)
        # 2. Título (A la izquierda)
        # 3. Detalles (Debajo, Centrado, Una sola línea)
        
        self.story.append(Spacer(1, 0.5*cm))
        self.story.append(Paragraph(self.titulo_documento, s_title))
        self.story.append(Paragraph(detalles, s_meta))
        #self.story.append(Spacer(1, 0.5*cm))

    def _layout_info_general(self, data):
        """Bloques de Propiedad y Solicitante"""
        s_label = self.styles["Heading2"]
        s_label.fontSize = 10
        s_label.textColor = Colors.to_reportlab(Colors.PRIMARY)
        
        s_val = self.styles["Body"]
        s_val.fontSize = 10
        
        # Propiedad
        prop_block = [
            Paragraph("UBICACIÓN / PROPIEDAD", s_label),
            Paragraph(f"<b>{data.get('direccion', 'N/A')}</b>", s_val),
            Paragraph(f"Propiedad ID: {data.get('id_propiedad', '')}", s_val),
            Paragraph("Tipo: Residencial", s_val) # Placeholder o data real
        ]
        
        # Solicitante
        sol_block = [
            Paragraph("REPORTADO POR", s_label),
            Paragraph(f"<b>{data.get('origen_reporte', 'Inquilino')}</b>", s_val),
            Paragraph(f"Responsable Pago: <b>{data.get('responsable_pago', 'Por definir')}</b>", s_val),
        ]
        
        tbl = Table([[prop_block, sol_block]], colWidths=[4.0*inch, 3.5*inch])
        tbl.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LINEABOVE', (0,0), (-1,0), 1.5, Colors.to_reportlab(Colors.GRAY_LIGHT)),
            ('TOPPADDING', (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 10),
        ]))
        self.story.append(tbl)
        self.story.append(Spacer(1, 0.3*cm))

    def _layout_detalle_problema(self, data):
        """Descripción del incidente"""
        self.story.append(Paragraph("DETALLE DEL REPORTE", self.styles["Heading2"]))
        
        desc = data.get('descripcion', 'Sin descripción.')
        
        # Caja gris con la descripción
        tbl = Table([[Paragraph(desc, self.styles["Body"])]], colWidths=[7.5*inch])
        tbl.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.whitesmoke),
            ('BOX', (0,0), (-1,-1), 0.5, Colors.to_reportlab(Colors.GRAY_LIGHT)),
            ('PADDING', (0,0), (-1,-1), 10),
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ]))
        self.story.append(tbl)
        self.story.append(Spacer(1, 0.5*cm))

    def _layout_cotizaciones(self, data):
        """Tabla de cotizaciones para comparar"""
        self.story.append(Paragraph("RESUMEN DE COTIZACIONES", self.styles["Heading2"]))
        
        cots = data.get('cotizaciones', [])
        if not cots:
            self.story.append(Paragraph("No hay cotizaciones registradas.", self.styles["Body"]))
            return

        headers = ["PROVEEDOR", "DESCRIPCIÓN", "DÍAS", "M.OBRA", "MAT.", "TOTAL"]
        rows = []
        for c in cots:
            rows.append([
                c.get('proveedor', 'N/A'),
                Paragraph(c.get('descripcion', '')[:50]+"...", self.styles["Small"]),
                str(c.get('dias', 0)),
                f"${c.get('mano_obra', 0):,.0f}",
                f"${c.get('materiales', 0):,.0f}",
                f"${c.get('valor_total', 0):,.0f}"
            ])
            
        t = Table([headers] + rows, colWidths=[1.8*inch, 2.2*inch, 0.6*inch, 1.0*inch, 0.9*inch, 1.0*inch])
        
        # Estilo tabla profesional
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), Colors.to_reportlab(Colors.GRAY_DARKEST)),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('FONTNAME', (0,0), (-1,0), Fonts.MAIN_BOLD),
            ('FONTSIZE', (0,0), (-1,0), 8), # Header Size
            ('FONTSIZE', (0,1), (-1,-1), 7), # Body Size
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('ALIGN', (0,1), (1,-1), 'LEFT'), # Texto col 1 y 2 izq
            ('ALIGN', (3,1), (-1,-1), 'RIGHT'), # Valores der
            ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
            ('PADDING', (0,0), (-1,-1), 6),
        ]))
        self.story.append(t)

    def _layout_orden_trabajo(self, data, titulo="DATOS DE EJECUCIÓN"):
        """Datos del proveedor y trabajo aprobado"""
        self.story.append(Paragraph(titulo, self.styles["Heading2"]))
        
        prov_name = data.get('nombre_proveedor', 'No Asignado')
        fecha_arreglo = self._format_date(data.get('fecha_arreglo'))
        costo = f"${data.get('costo_incidente', 0):,.0f}"
        
        # Grid layout
        info = [
            [
                Paragraph(f"<b>PROVEEDOR ASIGNADO:</b><br/>{prov_name}", self.styles["Body"]),
                Paragraph(f"<b>FECHA PROGRAMADA/EJECUCIÓN:</b><br/>{fecha_arreglo}", self.styles["Body"]),
                Paragraph(f"<b>VALOR APROBADO:</b><br/>{costo}", self.styles["Heading2"])
            ]
        ]
        
        t = Table(info, colWidths=[2.5*inch, 2.5*inch, 2.5*inch])
        t.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOX', (0,0), (-1,-1), 1, Colors.to_reportlab(Colors.GRAY_MEDIUM)),
            ('BACKGROUND', (0,0), (-1,-1), colors.aliceblue),
            ('PADDING', (0,0), (-1,-1), 8),
        ]))
        self.story.append(t)
        self.story.append(Spacer(1, 0.5*cm))

    def _layout_cierre_final(self, data):
        """Observaciones finales y cierre"""
        self.story.append(Paragraph("CIERRE Y CONFORMIDAD", self.styles["Heading2"]))
        
        obs = data.get('observaciones_final', 'La reparación ha sido completada satisfactoriamente.')
        if not obs: obs = "Sin observaciones adicionales."
        
        self.story.append(Paragraph(f"<b>Observaciones Finales:</b> {obs}", self.styles["Body"]))
        self.story.append(Spacer(1, 0.2*cm))
        self.story.append(Paragraph("<i>Se certifica que el trabajo ha sido recibido a entera satisfacción y cumple con los estándares de calidad requeridos.</i>", self.styles["Small"]))

    def _layout_firmas(self):
        """Espacios para firmas"""
        self.story.append(Spacer(1, 1.5*cm))
        
        s_centered = ParagraphStyle(
            "Centered",
            parent=self.styles["Body"],
            alignment=TA_CENTER
        )
        
        line = "____________________________________"
        firmas = [
            [
                Paragraph(f"{line}<br/>FIRMA PROVEEDOR", s_centered),
                Paragraph(f"{line}<br/>FIRMA RECIBIDO (Inquilino/Admin)", s_centered)
            ]
        ]
        
        t = Table(firmas, colWidths=[3.7*inch, 3.7*inch])
        self.story.append(t)

    def _format_date(self, date_val):
        """Helper fecha"""
        if not date_val: return "N/A"
        if hasattr(date_val, 'strftime'):
            return date_val.strftime("%Y-%m-%d")
        return str(date_val).split(" ")[0]

