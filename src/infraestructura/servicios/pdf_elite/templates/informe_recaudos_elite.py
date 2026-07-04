"""
Template para Informe de Recaudos Élite
======================================
Generador de informes de recaudos con análisis detallado.

Autor: Sistema de Gestión Inmobiliaria
Fecha: 2026-04-03
"""

from pathlib import Path
from typing import Any, Dict

from reportlab.lib import colors
from ..components.tables import AdvancedTable
from .base_template import BaseDocumentTemplate


class InformeRecaudosElite(BaseDocumentTemplate):
    """
    Generador élite de informes de recaudos.

    Características:
    - Tabla detallada de pagos recibidos
    - Resumen por método de pago
    - Totales consolidados
    - Estado de cuentas detallado
    - QR de verificación
    - Formato profesional

    Example:
        >>> gen = InformeRecaudosElite()
        >>> data = {
        ...     'informe_id': 1,
        ...     'periodo_inicio': '2026-01',
        ...     'periodo_fin': '2026-03',
        ...     'resumen': {...},
        ...     'detalles': [...],
        ...     'totales_metodo': {...}
        ... }
        >>> pdf_path = gen.generate(data)
    """

    def __init__(self, output_dir: Path = None):
        """Inicializa el generador de informes de recaudos."""
        super().__init__(output_dir)
        self.document_title = "INFORME DE RECAUDOS"

    def validate_data(self, data: Dict[str, Any]) -> bool:
        """Valida datos del informe de recaudos."""
        self._require_fields(
            data, "informe_id", "periodo_inicio", "periodo_fin", "resumen", "detalles"
        )
        return True

    def generate(self, data: Dict[str, Any]) -> Path:
        """
        Genera el informe de recaudos en PDF.

        Args:
            data: Diccionario con datos del informe

        Returns:
            Path del PDF generado
        """
        self.empresa_config = data.get("empresa", {})
        self.set_header_footer(
            self._header_footer_with_features, self._header_footer_with_features
        )
        self.enable_verification_qr("recaudos", data["informe_id"])

        filename = self._generate_filename("informe_recaudos", data["informe_id"])
        self.create_document(filename, self.document_title)

        self._add_informacion_general(data)
        self._add_resumen_ejecutivo(data)
        self._add_tabla_detalle_recaudos(data)
        self._add_resumen_metodo_pago(data)
        self._add_pie_legal()

        return self.build()

    def _header_footer_with_features(self, canvas_obj, doc):
        """Header y footer con Membrete."""
        current_dir = Path(__file__).parent
        membrete_path = current_dir / "VELAR INMOBILIARIA_membrete_modificada.png"

        try:
            if membrete_path.exists():
                page_width, page_height = doc.pagesize
                canvas_obj.drawImage(
                    str(membrete_path),
                    0,
                    0,
                    width=page_width,
                    height=page_height,
                    mask=None,
                    preserveAspectRatio=False,
                )
        except Exception as e:
            print(f"Advertencia: No se pudo cargar fondo {membrete_path}: {e}")

        if self.watermark_text:
            from ..components.watermarks import Watermark

            Watermark.add_text_watermark(
                canvas_obj,
                text=self.watermark_text,
                opacity=self.watermark_opacity,
                position=self.watermark_style,
            )

        canvas_obj.saveState()

        page_num = canvas_obj.getPageNumber()
        canvas_obj.setFont("Helvetica", 8)
        canvas_obj.setFillColor(colors.gray)

        center_x = doc.pagesize[0] / 2
        canvas_obj.drawCentredString(center_x, 20, f"Página {page_num}")

        canvas_obj.setFont("Helvetica", 8)
        canvas_obj.setFillColor(colors.lightgrey)

        from datetime import datetime

        dt_str = datetime.now().strftime("%Y-%m-%d %H:%M")

        canvas_obj.saveState()
        canvas_obj.translate(30, 250)
        canvas_obj.rotate(90)
        canvas_obj.drawString(
            0,
            0,
            "Impreso por Inmobiliaria Velar SAS - NIT 901.703.515 - Correo: inmobiliariavelarsasaxm@gmail.com",
        )
        canvas_obj.restoreState()

        canvas_obj.saveState()
        canvas_obj.translate(doc.pagesize[0] - 30, 250)
        canvas_obj.rotate(90)
        canvas_obj.drawString(0, 0, f"Generado: {dt_str}")
        canvas_obj.restoreState()

        canvas_obj.restoreState()

    def _add_informacion_general(self, data: Dict[str, Any]) -> None:
        """Agrega información general del informe."""
        self.add_title_main(self.document_title)

        from reportlab.platypus import Table, TableStyle, Paragraph
        from ..core.config import Colors

        meses = {
            "01": "enero",
            "02": "febrero",
            "03": "marzo",
            "04": "abril",
            "05": "mayo",
            "06": "junio",
            "07": "julio",
            "08": "agosto",
            "09": "septiembre",
            "10": "octubre",
            "11": "noviembre",
            "12": "diciembre",
        }

        def format_periodo(periodo: str) -> str:
            if "-" in periodo:
                p_year, p_month = periodo.split("-")
                return f"{meses.get(p_month, p_month)} de {p_year}"
            return periodo

        info_style = self.styles["Body"]
        info_style.fontSize = 9
        info_style.leading = 12
        info_style.alignment = 0

        informe_id = f"{data['informe_id']:06d}"
        periodo_inicio = format_periodo(data["periodo_inicio"])
        periodo_fin = format_periodo(data["periodo_fin"])

        from datetime import datetime

        fecha_fmt = datetime.now().strftime("%d de %m de %Y")

        info_text = [
            f"<b>INFORME No:</b> {informe_id}",
            f"<b>PERÍODO:</b> {periodo_inicio} - {periodo_fin}",
            f"<b>FECHA DE GENERACIÓN:</b> {fecha_fmt}",
        ]

        info_content = [Paragraph(line, info_style) for line in info_text]

        table_data = [[info_content]]
        avail_width = self.doc.width

        t = Table(table_data, colWidths=[avail_width])
        t.setStyle(
            TableStyle(
                [
                    ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ("LEFTPADDING", (0, 0), (-1, -1), 0),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
                    (
                        "LINEABOVE",
                        (0, 0),
                        (-1, -1),
                        1,
                        Colors.to_reportlab(Colors.GRAY_LIGHT),
                    ),
                    (
                        "LINEBELOW",
                        (0, 0),
                        (-1, -1),
                        1,
                        Colors.to_reportlab(Colors.GRAY_LIGHT),
                    ),
                ]
            )
        )

        self.story.append(t)

    def _add_resumen_ejecutivo(self, data: Dict[str, Any]) -> None:
        """Agrega resumen ejecutivo del período."""
        self.add_heading("RESUMEN EJECUTIVO", level=3)

        resumen = data["resumen"]
        headers = ["Concepto", "Valor"]

        rows = [
            ["Total Recaudos", f"${resumen.get('total_recaudos', 0):,.0f}"],
            ["Total Aplicados", f"${resumen.get('total_aplicados', 0):,.0f}"],
            ["Total Pendientes", f"${resumen.get('total_pendientes', 0):,.0f}"],
            ["Total Reversados", f"${resumen.get('total_reversados', 0):,.0f}"],
            ["Total Registros", f"{resumen.get('cantidad_registros', 0)}"],
        ]

        table = AdvancedTable.create_data_table(headers, rows, zebra_stripe=True)
        self.story.append(table)
        self.add_spacer(0.15)

    def _add_tabla_detalle_recaudos(self, data: Dict[str, Any]) -> None:
        """Agrega tabla detallada de recaudos."""
        self.add_heading("DETALLE DE RECAUDOS", level=3)

        detalles = data.get("detalles", [])

        if not detalles:
            self.add_paragraph(
                "No hay registros de recaudos en el período seleccionado.",
                style_name="Body",
            )
            return

        headers = [
            "ID",
            "Fecha",
            "Inmueble",
            "Arrendatario",
            "Valor",
            "Método",
            "Estado",
            "Período",
        ]

        rows = []
        total_valor = 0

        for d in detalles:
            valor = d.get("valor_total", 0)
            total_valor += valor

            rows.append(
                [
                    str(d.get("id_recaudo", "")),
                    d.get("fecha_pago", ""),
                    d.get("direccion", "")[:30]
                    + ("..." if len(d.get("direccion", "")) > 30 else ""),
                    d.get("arrendatario", "")[:20]
                    + ("..." if len(d.get("arrendatario", "")) > 20 else ""),
                    f"${valor:,.0f}",
                    d.get("metodo_pago", ""),
                    d.get("estado", ""),
                    d.get("periodo", ""),
                ]
            )

        rows.append(["TOTAL", "", "", "", f"${total_valor:,.0f}", "", "", ""])

        table = AdvancedTable.create_data_table(
            headers, rows, zebra_stripe=True, font_size=7
        )
        self.story.append(table)
        self.add_spacer(0.15)

    def _add_resumen_metodo_pago(self, data: Dict[str, Any]) -> None:
        """Agrega resumen por método de pago."""
        totales_metodo = data.get("totales_metodo", {})

        if not totales_metodo:
            return

        self.add_heading("RESUMEN POR MÉTODO DE PAGO", level=3)

        headers = ["Método de Pago", "Cantidad", "Valor Total"]

        rows = []
        total_cantidad = 0
        total_valor = 0

        for metodo, datos in totales_metodo.items():
            cantidad = datos.get("cantidad", 0)
            valor = datos.get("valor", 0)
            total_cantidad += cantidad
            total_valor += valor

            rows.append([metodo, str(cantidad), f"${valor:,.0f}"])

        rows.append(["TOTAL", str(total_cantidad), f"${total_valor:,.0f}"])

        table = AdvancedTable.create_data_table(headers, rows, zebra_stripe=True)
        self.story.append(table)
        self.add_spacer(0.15)

    def _add_pie_legal(self) -> None:
        """Agrega pie legal del documento."""
        self.add_legal_footer_text(
            "Este informe ha sido generado electrónicamente. "
            "Para consultas contacte a Inmobiliaria Velar SAS."
        )


__all__ = ["InformeRecaudosElite"]
