"""
Servicio de Infraestructura: Generación de Documentos PDF
Utiliza fpdf2 para crear comprobantes de recaudo y estados de cuenta.
"""

from fpdf import FPDF
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
import os

class PDFGenerator(FPDF):
    """Clase base personalizada para PDFs de la inmobiliaria"""
    
    def __init__(self, title: str):
        super().__init__()
        self.title_doc = title
        self.set_auto_page_break(auto=True, margin=15)
        
    def header(self):
        # Logo (si existe)
        # self.image('logo.png', 10, 8, 33)
        
        # Título Empresa
        self.set_font('helvetica', 'B', 15)
        self.cell(0, 10, 'INMOBILIARIA VELAR SAS', align='C', new_x="LMARGIN", new_y="NEXT")
        
        # Subtítulo Dirección/NIT
        self.set_font('helvetica', '', 9)
        self.cell(0, 5, 'NIT: 900.123.456-7 | Dirección: Calle 100 # 15-20, Bogotá', align='C', new_x="LMARGIN", new_y="NEXT")
        self.cell(0, 5, 'Teléfono: (601) 555-5555 | Email: contacto@inmovelar.com', align='C', new_x="LMARGIN", new_y="NEXT")
        
        # Línea separadora
        self.ln(5)
        self.line(10, 35, 200, 35)
        self.ln(5)
        
        # Título del Documento
        self.set_font('helvetica', 'B', 14)
        self.cell(0, 10, self.title_doc, align='C', new_x="LMARGIN", new_y="NEXT")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.cell(0, 10, f'Página {self.page_no()}/{{nb}} - Generado el {datetime.now().strftime("%Y-%m-%d %H:%M")}', align='C')


class ServicioDocumentosPDF:
    """Implementa la generación de documentos oficiales"""
    
    def __init__(self, output_dir: str = "documentos_generados"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
    def generar_comprobante_recaudo(self, datos: Dict[str, Any]) -> str:
        """
        Genera el PDF del comprobante de recaudo.
        
        Args:
            datos: Diccionario con info del recaudo, contrato y conceptos.
            
        Returns:
            Ruta absoluta del archivo generado.
        """
        pdf = PDFGenerator("COMPROBANTE DE PAGO")
        pdf.add_page()
        
        # --- Información General ---
        pdf.set_font('helvetica', 'B', 10)
        pdf.cell(40, 7, f"Comprobante No:", border=0)
        pdf.set_font('helvetica', '', 10)
        pdf.cell(60, 7, f"{datos['id_recaudo']}", border=0)
        
        pdf.set_font('helvetica', 'B', 10)
        pdf.cell(30, 7, f"Fecha Pago:", border=0)
        pdf.set_font('helvetica', '', 10)
        pdf.cell(60, 7, f"{datos['fecha_pago']}", border=0, new_x="LMARGIN", new_y="NEXT")
        
        # Fila 2
        pdf.set_font('helvetica', 'B', 10)
        pdf.cell(40, 7, f"Contrato:", border=0)
        pdf.set_font('helvetica', '', 10)
        pdf.cell(150, 7, f"{datos['id_contrato_a']} - {datos.get('direccion_propiedad', 'N/A')}", border=0, new_x="LMARGIN", new_y="NEXT")
        
        # Fila 3
        pdf.set_font('helvetica', 'B', 10)
        pdf.cell(40, 7, f"Método Pago:", border=0)
        pdf.set_font('helvetica', '', 10)
        pdf.cell(60, 7, f"{datos['metodo_pago']}", border=0)
        
        pdf.set_font('helvetica', 'B', 10)
        pdf.cell(30, 7, f"Referencia:", border=0)
        pdf.set_font('helvetica', '', 10)
        pdf.cell(60, 7, f"{datos.get('referencia_bancaria', 'N/A')}", border=0, new_x="LMARGIN", new_y="NEXT")
        
        pdf.ln(10)
        
        # --- Tabla de Conceptos ---
        pdf.set_font('helvetica', 'B', 10)
        pdf.set_fill_color(240, 240, 240)
        
        # Encabezados
        pdf.cell(80, 8, "Concepto", border=1, fill=True)
        pdf.cell(60, 8, "Período", border=1, fill=True)
        pdf.cell(50, 8, "Valor", border=1, fill=True, new_x="LMARGIN", new_y="NEXT")
        
        # Filas
        pdf.set_font('helvetica', '', 10)
        total_calculado = 0
        
        for c in datos.get('conceptos', []):
            pdf.cell(80, 7, str(c['tipo_concepto']), border=1)
            pdf.cell(60, 7, str(c['periodo']), border=1)
            pdf.cell(50, 7, f"${c['valor']:,}", border=1, align='R', new_x="LMARGIN", new_y="NEXT")
            total_calculado += c['valor']
            
        pdf.ln(5)
        
        # --- Totales ---
        pdf.set_font('helvetica', 'B', 11)
        pdf.cell(140, 8, "TOTAL PAGADO", border=1, align='R')
        pdf.cell(50, 8, f"${datos['valor_total']:,}", border=1, align='R', fill=True, new_x="LMARGIN", new_y="NEXT")
        
        pdf.ln(20)
        
        # --- Pie / Firma ---
        pdf.set_font('helvetica', '', 9)
        pdf.cell(0, 5, f"Observaciones: {datos.get('observaciones', 'Ninguna')}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(20)
        
        pdf.line(70, pdf.get_y(), 140, pdf.get_y())
        pdf.cell(0, 5, "Firma Autorizada", align='C', new_x="LMARGIN", new_y="NEXT")
        pdf.cell(0, 5, "Departamento de Tesorería", align='C', new_x="LMARGIN", new_y="NEXT")
        
        # Guardar
        filename = f"recaudo_{datos['id_recaudo']}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
        output_path = self.output_dir / filename
        pdf.output(str(output_path))
        
        return str(output_path.absolute())

    def generar_estado_cuenta(self, datos: Dict[str, Any]) -> str:
        """
        Genera el PDF del estado de cuenta de liquidación.
        
        Args:
            datos: Diccionario con info de la liquidación, propiedad y totales.
            
        Returns:
            Ruta absoluta del archivo generado.
        """
        pdf = PDFGenerator("ESTADO DE CUENTA - PROPIETARIO")
        pdf.add_page()
        
        # --- Información Propietario ---
        pdf.set_font('helvetica', 'B', 10)
        pdf.cell(100, 7, f"Propietario: {datos['propietario']}", border=0, new_x="LMARGIN", new_y="NEXT")
        pdf.set_font('helvetica', '', 10)
        pdf.cell(100, 7, f"Documento: {datos['documento']} | Matrícula: {datos['matricula']}", border=0, new_x="LMARGIN", new_y="NEXT")
        pdf.cell(190, 7, f"Propiedad: {datos['propiedad']}", border="B", new_x="LMARGIN", new_y="NEXT")
        
        pdf.ln(5)
        
        # Periodo
        pdf.set_font('helvetica', 'B', 11)
        pdf.cell(95, 8, f"Período Liquidado: {datos['periodo']}", border=1)
        pdf.cell(95, 8, f"ID Liquidación: {datos['id']}", border=1, new_x="LMARGIN", new_y="NEXT")
        
        pdf.ln(10)
        
        # --- Ingresos ---
        pdf.set_font('helvetica', 'B', 12)
        pdf.cell(0, 8, "INGRESOS", new_x="LMARGIN", new_y="NEXT")
        
        pdf.set_font('helvetica', '', 10)
        pdf.cell(140, 7, "Canon de Arrendamiento", border=1)
        pdf.cell(50, 7, f"${datos['canon']:,}", border=1, align='R', new_x="LMARGIN", new_y="NEXT")
        
        if datos['otros_ingresos'] > 0:
            pdf.cell(140, 7, "Otros Ingresos", border=1)
            pdf.cell(50, 7, f"${datos['otros_ingresos']:,}", border=1, align='R', new_x="LMARGIN", new_y="NEXT")
            
        pdf.set_font('helvetica', 'B', 10)
        pdf.cell(140, 7, "TOTAL INGRESOS", border=1, align='R')
        pdf.cell(50, 7, f"${datos['total_ingresos']:,}", border=1, align='R', fill=True, new_x="LMARGIN", new_y="NEXT")
        
        pdf.ln(5)
        
        # --- Egresos ---
        pdf.set_font('helvetica', 'B', 12)
        pdf.cell(0, 8, "EGRESOS Y DEDUCCIONES", new_x="LMARGIN", new_y="NEXT")
        
        pdf.set_font('helvetica', '', 10)
        
        egresos_items = [
            (f"Comisión de Administración ({int(datos['comision_pct'])/100}%)", datos['comision_monto']),
            ("IVA Comisión (19%)", datos['iva_comision']),
            ("Gravamen Financiero (4x1000)", datos['impuesto_4x1000']),
            ("Gastos Administrativos", datos['gastos_admin']),
            ("Reparaciones y Mantenimiento", datos['gastos_rep']),
            ("Servicios Públicos", datos['gastos_serv']),
            ("Otros Egresos", datos['otros_egr']),
        ]
        
        for desc, valor in egresos_items:
            if valor > 0:
                pdf.cell(140, 7, desc, border=1)
                pdf.cell(50, 7, f"${valor:,}", border=1, align='R', new_x="LMARGIN", new_y="NEXT")
                
        pdf.set_font('helvetica', 'B', 10)
        pdf.cell(140, 7, "TOTAL EGRESOS", border=1, align='R')
        pdf.cell(50, 7, f"${datos['total_egresos']:,}", border=1, align='R', fill=True, new_x="LMARGIN", new_y="NEXT")
        
        pdf.ln(10)
        
        # --- NETO A PAGAR ---
        pdf.set_font('helvetica', 'B', 14)
        pdf.set_fill_color(220, 230, 255) # Azul claro
        pdf.cell(140, 12, "NETO A PAGAR AL PROPIETARIO", border=1, fill=True, align='R')
        pdf.cell(50, 12, f"${datos['neto_pagar']:,}", border=1, fill=True, align='R', new_x="LMARGIN", new_y="NEXT")
        
        pdf.ln(10)
        
        # --- Información de Transferencia (si aplica) ---
        if datos['estado'] == 'Pagada':
            pdf.set_font('helvetica', 'B', 11)
            pdf.cell(0, 8, "INFORMACIÓN DE PAGO REALIZADO", border="B", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font('helvetica', '', 10)
            pdf.ln(2)
            pdf.cell(60, 6, f"Fecha: {datos['fecha_pago']}", border=0)
            pdf.cell(60, 6, f"Método: {datos['metodo_pago']}", border=0)
            pdf.cell(60, 6, f"Referencia: {datos['referencia_pago']}", border=0, new_x="LMARGIN", new_y="NEXT")
        
        # Guardar
        filename = f"liquidacion_{datos['id']}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
        output_path = self.output_dir / filename
        pdf.output(str(output_path))
        
        return str(output_path.absolute())

    def generar_cuenta_cobro_asesor(self, datos: Dict[str, Any]) -> str:
        """
        Genera el PDF de la cuenta de cobro / liquidación para asesor.
        
        Args:
            datos: Diccionario con info de la liquidación, asesor y contratos.
            
        Returns:
            Ruta absoluta del archivo generado.
        """
        pdf = PDFGenerator("CUENTA DE COBRO - ASESOR")
        pdf.add_page()
        
        # --- Información Asesor ---
        pdf.set_font('helvetica', 'B', 10)
        pdf.cell(100, 7, f"Asesor: {datos['nombre_asesor']}", border=0, new_x="LMARGIN", new_y="NEXT")
        pdf.set_font('helvetica', '', 10)
        pdf.cell(100, 7, f"Documento: {datos['documento_asesor']}", border=0, new_x="LMARGIN", new_y="NEXT")
        
        pdf.ln(5)
        
        # Periodo e ID
        pdf.set_font('helvetica', 'B', 11)
        pdf.cell(95, 8, f"Período Liquidado: {datos['periodo']}", border=1)
        pdf.cell(95, 8, f"Liquidación #: {datos['id_liquidacion']}", border=1, new_x="LMARGIN", new_y="NEXT")
        
        pdf.ln(10)
        
        # --- Detalle de Contratos (Base Comisional) ---
        pdf.set_font('helvetica', 'B', 12)
        pdf.cell(0, 8, "DETALLE DE CONTRATOS GESTIONADOS", new_x="LMARGIN", new_y="NEXT")
        
        pdf.set_font('helvetica', 'B', 9)
        pdf.set_fill_color(240, 240, 240)
        pdf.cell(30, 8, "Contrato", border=1, fill=True)
        pdf.cell(100, 8, "Dirección Inmueble", border=1, fill=True)
        pdf.cell(30, 8, "Canon", border=1, fill=True)
        pdf.cell(30, 8, "Comisión", border=1, fill=True, new_x="LMARGIN", new_y="NEXT")
        
        pdf.set_font('helvetica', '', 9)
        
        total_canon = 0
        contratos = datos.get('contratos', [])
        
        # Si no hay contratos detallados (legacy), intentamos mostrar el contrato único si existe
        if not contratos and datos.get('id_contrato_legacy'):
            contratos = [{
                'id_contrato': datos['id_contrato_legacy'],
                'direccion': datos.get('direccion_legacy', 'N/A'),
                'canon_incluido': datos.get('canon_legacy', 0)
            }]
            
        for c in contratos:
            canon = c.get('canon_incluido', 0)
            # Calcular comision individual estimada
            com_ind = int(canon * datos['porcentaje_comision'] / 100)
            
            pdf.cell(30, 6, f"#{c.get('id_contrato')}", border=1)
            pdf.cell(100, 6, str(c.get('direccion'))[:50], border=1)
            pdf.cell(30, 6, f"${canon:,}", border=1, align='R')
            pdf.cell(30, 6, f"${com_ind:,}", border=1, align='R', new_x="LMARGIN", new_y="NEXT")
            total_canon += canon
            
        # Total Canones
        pdf.set_font('helvetica', 'B', 9)
        pdf.cell(130, 7, "TOTAL BASE COMISIONAL", border=1, align='R')
        pdf.cell(60, 7, f"${total_canon:,}", border=1, align='R', fill=True, new_x="LMARGIN", new_y="NEXT")
        
        pdf.ln(5)
        
        # --- Liquidación Final ---
        pdf.set_font('helvetica', 'B', 12)
        pdf.cell(0, 8, "LIQUIDACIÓN DE COMISIONES", new_x="LMARGIN", new_y="NEXT")
        
        pdf.set_font('helvetica', '', 10)
        
        # Comisión Bruta
        pdf.cell(140, 7, f"Comisión Bruta ({datos['porcentaje_real']}%)", border=1)
        pdf.cell(50, 7, f"${datos['comision_bruta']:,}", border=1, align='R', new_x="LMARGIN", new_y="NEXT")
        
        # Descuentos
        if datos['total_descuentos'] > 0:
            pdf.set_font('helvetica', 'B', 10)
            pdf.cell(0, 7, "Menos Descuentos y Deducciones:", border=0, new_x="LMARGIN", new_y="NEXT")
            pdf.set_font('helvetica', '', 9)
            
            for desc in datos.get('descuentos_lista', []):
                pdf.cell(140, 6, f"- {desc['tipo_descuento']}: {desc['descripcion_descuento']}", border=1)
                pdf.cell(50, 6, f"${desc['valor_descuento']:,}", border=1, align='R', new_x="LMARGIN", new_y="NEXT")
                
            pdf.set_font('helvetica', 'B', 10)
            pdf.cell(140, 7, "TOTAL DESCUENTOS", border=1, align='R')
            pdf.cell(50, 7, f"${datos['total_descuentos']:,}", border=1, align='R', fill=True, new_x="LMARGIN", new_y="NEXT")
        
        pdf.ln(5)
        
        # --- NETO A PAGAR ---
        pdf.set_font('helvetica', 'B', 14)
        pdf.set_fill_color(220, 255, 220) # Verde claro
        pdf.cell(140, 12, "NETO A PAGAR AL ASESOR", border=1, fill=True, align='R')
        pdf.cell(50, 12, f"${datos['valor_neto']:,}", border=1, fill=True, align='R', new_x="LMARGIN", new_y="NEXT")
        
        pdf.ln(20)
        
        # --- Observaciones ---
        if datos.get('observaciones'):
            pdf.set_font('helvetica', '', 9)
            pdf.multi_cell(0, 5, f"Observaciones: {datos['observaciones']}")
            pdf.ln(10)

        # --- Firmas ---
        curr_y = pdf.get_y()
        # Verificar espacio
        if curr_y > 230:
            pdf.add_page()
            curr_y = pdf.get_y()
            
        pdf.ln(20)
        
        y_sig = pdf.get_y()
        pdf.line(20, y_sig, 80, y_sig)
        pdf.line(110, y_sig, 170, y_sig)
        
        pdf.set_xy(20, y_sig + 2)
        pdf.set_font('helvetica', 'B', 9)
        pdf.cell(60, 5, "AUTORIZADO POR", align='C')
        
        pdf.set_xy(110, y_sig + 2)
        pdf.cell(60, 5, "RECIBIDO POR (ASESOR)", align='C')
        
        pdf.set_xy(110, y_sig + 7)
        pdf.set_font('helvetica', '', 9)
        pdf.cell(60, 5, f"C.C. {datos['documento_asesor']}", align='C')
        
        # Guardar
        filename = f"cuenta_cobro_{datos['id_liquidacion']}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
        output_path = self.output_dir / filename
        pdf.output(str(output_path))
        
        return str(output_path.absolute())

    def generar_checklist_desocupacion(self, datos: Dict[str, Any]) -> str:
        """
        Genera el PDF del checklist de desocupación.
        
        Args:
            datos: Diccionario con info recuperada por obtener_datos_para_checklist.
            
        Returns:
            Ruta absoluta del archivo generado.
        """
        print(f"[DEBUG PDF] Generando PDF para Desocupación {datos.get('id_desocupacion')}")
        pdf = PDFGenerator("CHECKLIST DE ENTREGA DE INMUEBLE")
        pdf.add_page()
        
        # --- Información General ---
        pdf.set_font('helvetica', 'B', 9)
        
        # Fila 1: Fecha y ID
        pdf.cell(30, 6, "Fecha:", border=0)
        pdf.set_font('helvetica', '', 9)
        pdf.cell(70, 6, f"{datetime.now().strftime('%Y-%m-%d')}", border=0)
        
        pdf.set_font('helvetica', 'B', 9)
        pdf.cell(40, 6, "Desocupación #:", border=0)
        pdf.set_font('helvetica', '', 9)
        pdf.cell(40, 6, f"{datos['id_desocupacion']}", border=0, new_x="LMARGIN", new_y="NEXT")
        
        # Fila 2: Inmueble
        pdf.set_font('helvetica', 'B', 9)
        pdf.cell(30, 6, "Inmueble:", border=0)
        pdf.set_font('helvetica', '', 9)
        pdf.cell(160, 6, f"{datos['direccion']}", border=0, new_x="LMARGIN", new_y="NEXT")
        
        # Fila 3: Inquilino
        pdf.set_font('helvetica', 'B', 9)
        pdf.cell(30, 6, "Inquilino:", border=0)
        pdf.set_font('helvetica', '', 9)
        pdf.cell(100, 6, f"{datos['inquilino']}", border=0)
        
        pdf.set_font('helvetica', 'B', 9)
        pdf.cell(20, 6, "Tel:", border=0)
        pdf.set_font('helvetica', '', 9)
        pdf.cell(40, 6, f"{datos['telefono']}", border=0, new_x="LMARGIN", new_y="NEXT")
        
        pdf.line(10, pdf.get_y()+2, 200, pdf.get_y()+2)
        pdf.ln(4)
        
        # --- Checklist ---
        pdf.ln(3)
        pdf.set_font('helvetica', 'B', 11)
        pdf.cell(0, 8, "INVENTARIO Y ESTADO DEL INMUEBLE", new_x="LMARGIN", new_y="NEXT")
        
        # Definir items del checklist
        items = [
            "Entrega de llaves (Total juegos: ____)",
            "Estado de pintura (Muros y techos)",
            "Pisos y guardescobas",
            "Estado de puertas y cerraduras",
            "Ventanas y vidrios",
            "Cocina (Estufa, Gabinetes, Lavaplatos)",
            "Baños (Lavamanos, Inodoro, Ducha, Accesorios)",
            "Carpintería de madera (Closets)",
            "Instalaciones eléctricas (Tomas, Interruptores, Lámparas)",
            "Instalaciones hidráulicas y sanitarias",
            "Paz y salvo Servicios Públicos (Agua)",
            "Paz y salvo Servicios Públicos (Luz)",
            "Paz y salvo Servicios Públicos (Gas)",
            "Paz y salvo Administración (Si aplica)"
        ]
        
        # Encabezados tabla
        pdf.set_font('helvetica', 'B', 8)
        pdf.set_fill_color(240, 240, 240)
        
        col_item = 110
        col_est = 25
        col_obs = 55
        row_height = 6
        
        pdf.cell(col_item, row_height, "Item / Descripción", border=1, fill=True)
        pdf.cell(col_est, row_height, "Estado", border=1, fill=True) # B/R/M
        pdf.cell(col_obs, row_height, "Observaciones", border=1, fill=True, new_x="LMARGIN", new_y="NEXT")
        
        pdf.set_font('helvetica', '', 8)
        
        for item in items:
            pdf.cell(col_item, row_height, item, border=1)
            pdf.cell(col_est, row_height, "[ ] B  [ ] M", border=1, align='C')
            pdf.cell(col_obs, row_height, "", border=1, new_x="LMARGIN", new_y="NEXT")
            
        pdf.ln(3)
        
        # --- Observaciones Finales ---
        pdf.set_font('helvetica', 'B', 9)
        pdf.cell(0, 6, "OBSERVACIONES GENERALES:", new_x="LMARGIN", new_y="NEXT")
        pdf.rect(pdf.get_x(), pdf.get_y(), 190, 15)
        pdf.ln(18)
        
        # --- Firmas ---
        pdf.ln(5)
        
        y_sig = pdf.get_y() + 15
        
        # Verificar si cabe en la página, si no, nueva página
        if y_sig + 20 > 270: # A4 height approx 297, margin 15 bottom
             pdf.add_page()
             y_sig = pdf.get_y() + 15

        pdf.line(20, y_sig, 80, y_sig)
        pdf.line(110, y_sig, 170, y_sig)
        
        pdf.set_xy(20, y_sig + 2)
        pdf.set_font('helvetica', 'B', 8)
        pdf.cell(60, 4, "RECIBE (INMOBILIARIA)", align='C', new_x="LMARGIN", new_y="NEXT")
        
        pdf.set_xy(110, y_sig + 2)
        pdf.cell(60, 4, "ENTREGA (ARRENDATARIO)", align='C', new_x="LMARGIN", new_y="NEXT")
        
        pdf.set_xy(110, y_sig + 6)
        pdf.set_font('helvetica', '', 8)
        pdf.cell(60, 4, f"C.C. {datos.get('documento', '')}", align='C')
        
        # Guardar
        filename = f"checklist_desocupacion_{datos['id_desocupacion']}_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
        output_path = self.output_dir / filename
        pdf.output(str(output_path))
        
        return str(output_path.absolute())
