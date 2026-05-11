"""
Template para Estados de Cuenta Élite
=====================================
Generador mejorado de estados de cuenta con gráficos y análisis.

Autor: Sistema de Gestión Inmobiliaria
Fecha: 2026-01-18
"""

from pathlib import Path
from typing import Any, Dict

from reportlab.lib import colors
from ..components.tables import AdvancedTable
from .base_template import BaseDocumentTemplate


class EstadoCuentaElite(BaseDocumentTemplate):
    """
    Generador élite de estados de cuenta

    Mejora sobre el estado de cuenta básico con:
    - Tabla de movimientos profesional
    - Resumen de totales destacado
    - Gráficos opcionales de evolución
    - QR de verificación
    - Formato profesional

    Example:
        >>> gen = EstadoCuentaElite()
        >>> data = {
        ...     'estado_id': 789,
        ...     'propietario': {...},
        ...     'inmueble': {...},
        ...     'periodo': '2026-01',
        ...     'movimientos': [...],
        ...     'resumen': {...}
        ... }
        >>> pdf_path = gen.generate(data)
    """

    def __init__(self, output_dir: Path = None):
        """Inicializa el generador de estados de cuenta"""
        super().__init__(output_dir)
        self.document_title = "ESTADO DE CUENTA - PROPIETARIO"

    def validate_data(self, data: Dict[str, Any]) -> bool:
        """Valida datos del estado de cuenta"""
        self._require_fields(
            data, "estado_id", "propietario", "inmueble", "periodo", "detalle_propiedades", "resumen"
        )
        return True

    def generate(self, data: Dict[str, Any]) -> Path:
        """
        Genera el estado de cuenta en PDF

        Args:
            data: Diccionario con datos del estado

        Returns:
            Path del PDF generado
        """
        # Guardar configuración de empresa para el header
        self.empresa_config = data.get("empresa", {})

        # Configurar Header/Footer con Membrete
        self.set_header_footer(self._header_footer_with_features, self._header_footer_with_features)

        # Determinar título dinámico según el modo
        modo = data.get("modo", "consolidado")
        if modo == "individual":
            self.document_title = "ESTADO DE CUENTA - LIQUIDACIÓN"
        else:
            self.document_title = "ESTADO DE CUENTA - PROPIETARIO"

        # Habilitar QR de verificación
        self.enable_verification_qr("estado", data["estado_id"])

        # Determinar descriptor para el nombre de archivo (Dirección de la propiedad)
        descriptor = "consolidado"
        if data.get("inmueble") and data["inmueble"].get("direccion"):
            descriptor = data["inmueble"]["direccion"]
        elif data.get("propiedad"): # Fallback por si acaso
            descriptor = data["propiedad"]

        # Crear documento con nomenclatura personalizada: estado_cuenta_[DIRECCION]_[DDMMAAAAHHMMSS]
        filename = self._generate_filename(
            prefix="estado_cuenta", 
            descriptor=descriptor,
            timestamp_format="%d%m%Y%H%M%S"
        )
        self.create_document(filename, self.document_title)

        # Construir contenido
        self._add_informacion_consolidada(data)
        self._add_tabla_propiedades(data) # Propiedades
        self._add_detalle_propiedades(data)
        self._add_resumen_financiero(data)
        self._add_notas(data)

        # Construir PDF
        return self.build()

    def _add_informacion_consolidada(self, data: Dict[str, Any]) -> None:
        """
        Agrega tabla consolidada de información (Propietario + Documento)
        Diseño compacto 2 columnas.
        """
        #self.add_spacer(0.1)
        self.add_title_main(self.document_title)
        #self.add_spacer(0.015) # Reducido para acercar al título

        prop = data["propietario"]
        
        # Estilos para celdas
        from reportlab.platypus import Table, TableStyle, Paragraph
        from reportlab.lib import colors as rl_colors
        from ..core.config import Colors, Fonts
        
        # Columna Izquierda: Información del Propietario
        # Usamos Paragraphs para formateo rico (Negritas/Normal)
        
        owner_style = self.styles["Body"]
        owner_style.fontSize = 8 # Reducido
        owner_style.leading = 10
        owner_style.alignment = 0 # TA_LEFT
        
        owner_text = [
            f"<b>PROPIETARIO:</b> {prop['nombre']}",
            f"<b>DOC:</b> {prop['documento']}",
            f"<b>TEL:</b> {prop.get('telefono', 'N/A')} | <b>EMAIL:</b> {prop.get('email', 'N/A')}"
        ]
        
        owner_content = [Paragraph(line, owner_style) for line in owner_text]
        
        # Columna Derecha: Información del Documento
        doc_style = self.styles["Body"]
        doc_style.fontSize = 8 # Reducido
        doc_style.leading = 10
        doc_style.alignment = 0 # TA_LEFT (User requested left align for the section)
        
        # Alineación derecha para texto de documento
        periodo_raw = data['periodo']
        periodo_fmt = periodo_raw
        
        # Formatear Periodo: "2025-07" -> "julio de 2025"
        meses = {
            "01": "enero", "02": "febrero", "03": "marzo", "04": "abril",
            "05": "mayo", "06": "junio", "07": "julio", "08": "agosto",
            "09": "septiembre", "10": "octubre", "11": "noviembre", "12": "diciembre"
        }
        
        try:
            if "-" in periodo_raw:
                p_year, p_month = periodo_raw.split("-")
                nombre_mes = meses.get(p_month, p_month)
                periodo_fmt = f"{nombre_mes} de {p_year}"
        except Exception:
            pass # Fallback to raw

        doc_id = f"{data['estado_id']:06d}"
        
        fecha_raw = data.get('fecha_generacion') 
        fecha_fmt = ""
        
        from datetime import datetime
        if not fecha_raw:
            fecha_dt = datetime.now()
        else:
            try:
                # Intentar parsear YYYY-MM-DD
                fecha_dt = datetime.strptime(fecha_raw, "%Y-%m-%d")
            except:
                fecha_dt = datetime.now()
        
        # Formatear Fecha: "03 de febrero de 2026"
        f_dia = fecha_dt.day
        f_mes = meses.get(f"{fecha_dt.month:02d}", "")
        f_year = fecha_dt.year
        fecha_fmt = f"{f_dia:02d} de {f_mes} de {f_year}"

        doc_text = [
            f"<b>PERÍODO:</b> {periodo_fmt}",
            f"<b>DOCUMENTO No:</b> {doc_id}",
            f"<b>FECHA:</b> {fecha_fmt}"
        ]
        
        # Para alinear a la derecha visualmente en la celda derecha, 
        # podríamos usar una tabla anidada o simplemente texto alineado.
        # Por simplicidad, texto normal.
        
        doc_content = [Paragraph(line, doc_style) for line in doc_text]

        # Construir Tabla Principal (1 Fila, 2 Columnas)
        # Hack: Unir la lista de parrafos en un solo contenido por celda? 
        # ReportLab acepta lista de flowables en celda.
        
        table_data = [[owner_content, doc_content]]
        
        # Anchos relativos: 60% Propietario, 40% Doc
        avail_width = self.doc.width
        col_widths = [avail_width * 0.6, avail_width * 0.4]
        
        t = Table(table_data, colWidths=col_widths)
        
        # Estilo Tabla: Linea superior e inferior negra delgada, sin bordes internos verticales
        t.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
            ('RIGHTPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 5),
            ('BOTTOMPADDING', (0,0), (-1,-1), 10),
            ('LINEABOVE', (0,0), (-1,-1), 1, Colors.to_reportlab(Colors.GRAY_LIGHT)),
            ('LINEBELOW', (0,0), (-1,-1), 1, Colors.to_reportlab(Colors.GRAY_LIGHT)),
        ]))
        
        self.story.append(t)
        #self.add_spacer(0.2)

    def _add_tabla_propiedades(self, data: Dict[str, Any]) -> None:
        """Agrega tabla de lista de propiedades"""
        if "lista_propiedades" not in data or not data["lista_propiedades"]:
            return

        self.add_heading("PROPIEDADES", level=3)

        # Headers
        headers = ["ID", "Dirección"]
        
        # Rows
        rows = []
        for prop in data["lista_propiedades"]:
            rows.append([str(prop.get("id", "")), prop.get("direccion", "")])

        # Crear tabla
        table = AdvancedTable.create_data_table(headers, rows, zebra_stripe=True)
        self.story.append(table)
        #self.add_spacer(0.1)

    def _add_detalle_propiedades(self, data: Dict[str, Any]) -> None:
        """Agrega tabla detallada de propiedades (Reemplaza movimientos)"""
        if "detalle_propiedades" not in data:
            return

        # Título dinámico para el detalle
        if data.get("modo") == "individual":
            self.add_heading("DETALLE FINANCIERO", level=3)
        else:
            self.add_heading("DETALLE POR PROPIEDAD", level=3)

        detalles = data["detalle_propiedades"]

        # Headers de la tabla detallada (Eliminados SEGURO y 4X1000)
        headers = ["ID", "CANON", "COMISIÓN", "IVA", "ADMIN", "SERV", "PREDIAL", "OTRO", "NETO"]

        # Convertir a filas
        rows = []
        
        # Totales columnas
        t_canon = t_comision = t_iva = t_admin = t_serv = t_predial = t_otro = t_total = 0

        for d in detalles:
            # Acumular
            t_canon += d["canon"]
            t_comision += d["comision"]
            t_iva += d["iva"]
            t_admin += d["admin"]
            t_serv += d["servicios"]
            t_predial += d["predial"]
            t_otro += d["incidente"]
            t_total += d["total"]
            
            # Formatear
            rows.append([
                str(d["id"]),
                f"${d['canon']:,.0f}",
                f"${d['comision']:,.0f}",
                f"${d['iva']:,.0f}",
                f"${d['admin']:,.0f}",
                f"${d['servicios']:,.0f}",
                f"${d['predial']:,.0f}",
                f"${d['incidente']:,.0f}",
                f"${d['total']:,.0f}"
            ])

        # Fila TOTAL FINAL
        rows.append([
            "TOTAL",
            f"${t_canon:,.0f}",
            f"${t_comision:,.0f}",
            f"${t_iva:,.0f}",
            f"${t_admin:,.0f}",
            f"${t_serv:,.0f}",
            f"${t_predial:,.0f}",
            f"${t_otro:,.0f}",
            f"${t_total:,.0f}"
        ])

        # Crear tabla
        table = AdvancedTable.create_data_table(
            headers, 
            rows, 
            zebra_stripe=True,
            font_size=7  # Se aumenta ligeramente la fuente al haber menos columnas
        )
        # Hack de estilo si AdvancedTable lo permite, si no confiamos en auto-fit
        
        self.story.append(table)
        #self.add_spacer(0.1)

    def _add_resumen_financiero(self, data: Dict[str, Any]) -> None:
        """Agrega resumen financiero"""
        self.add_heading("RESUMEN FINANCIERO", level=3)

        resumen = data["resumen"]

        # Tabla de resumen
        headers = ["Concepto", "Valor"]
        rows = [
            ["Total Ingresos", f"${resumen.get('total_ingresos', 0):,.2f}"],
            ["Total Egresos", f"${resumen.get('total_egresos', 0):,.2f}"],
            ["Honorarios Administración", f"${resumen.get('honorarios', 0):,.2f}"],
            ["Otros Descuentos", f"${resumen.get('otros_descuentos', 0):,.2f}"],
        ]

        # Valor neto
        valor_neto = resumen.get("valor_neto", 0)
        totals = {1: f"${valor_neto:,.2f}"}

        table = AdvancedTable.create_data_table(headers, rows, totals=totals, highlight_totals=True)
        self.story.append(table)

        # Información de transferencia si hay valor positivo
        # Información de transferencia si hay valor positivo
        if "cuenta_bancaria" in resumen and valor_neto > 0:
            self.add_spacer(0.1)
            self.add_paragraph(f"Valor a Transferir: ${valor_neto:,.2f} | Cuenta Bancaria: {resumen['cuenta_bancaria']}", style_name="Body")
            #self.add_paragraph(f"Cuenta Bancaria: {resumen['cuenta_bancaria']}", style_name="Body")

            if "fecha_pago" in resumen:
                self.add_paragraph(f"Fecha de Pago: {resumen['fecha_pago']}", style_name="Body")

        #self.add_spacer(0.1)

    def _add_notas(self, data: Dict[str, Any]) -> None:
        """Agrega notas y observaciones"""
        if "observaciones" in data and data["observaciones"]:
            self.add_spacer(0.1)
            self.add_heading("OBSERVACIONES", level=3)
            self.add_paragraph(data["observaciones"], style_name="Small")

        # Pie legal
        self.add_legal_footer_text(
            "Este estado de cuenta ha sido generado electrónicamente. "
            "Para consultas contacte a Inmobiliaria Velar SAS."
        )


__all__ = ["EstadoCuentaElite"]
