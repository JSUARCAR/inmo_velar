#!/usr/bin/env python3
"""
Generador de PDF para Propuesta Comercial
Usa fpdf2 con fuente Unicode
"""

from fpdf import FPDF
import re
import os

# Rutas
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_FILE = os.path.join(BASE_DIR, "docs", "propuesta-comercial-inmobiliaria-velar.md")
OUTPUT_FILE = os.path.join(BASE_DIR, "docs", "propuesta-comercial-inmobiliaria-velar.pdf")


class PropuestaPDF(FPDF):
    """Clase personalizada para generar PDF de propuesta comercial"""
    
    def __init__(self):
        super().__init__('P', 'mm', 'Letter')
        self.set_auto_page_break(auto=True, margin=25)
        # Usar fuente built-in que soporte caracteres básicos
        self.set_font('Helvetica', '', 10)
        
    def header(self):
        """Encabezado de cada pagina"""
        self.set_font('Helvetica', 'B', 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, 'Propuesta Comercial - Inmobiliaria Velar SAS', 0, 0, 'L')
        self.cell(0, 8, f'Pagina {self.page_no()}', 0, 1, 'R')
        self.line(10, 15, 200, 15)
        self.ln(5)
        
    def footer(self):
        """Pie de pagina"""
        self.set_y(-20)
        self.set_font('Helvetica', 'I', 7)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, 'Documento generado automaticamente - Version 1.4', 0, 0, 'C')
        
    def chapter_title(self, title, level=1):
        """ titulo de capitulo"""
        if level == 1:
            self.set_font('Helvetica', 'B', 18)
            self.set_text_color(26, 54, 93)
            self.ln(5)
            self.cell(0, 12, title, 0, 1, 'L')
            self.set_draw_color(43, 108, 176)
            self.set_line_width(0.8)
            self.line(10, self.get_y(), 200, self.get_y())
            self.ln(6)
        elif level == 2:
            self.set_font('Helvetica', 'B', 14)
            self.set_text_color(43, 108, 176)
            self.ln(4)
            self.cell(0, 10, title, 0, 1, 'L')
            self.set_draw_color(190, 227, 248)
            self.set_line_width(0.4)
            self.line(10, self.get_y(), 150, self.get_y())
            self.ln(4)
        elif level == 3:
            self.set_font('Helvetica', 'B', 12)
            self.set_text_color(44, 82, 130)
            self.ln(3)
            self.cell(0, 8, title, 0, 1, 'L')
            self.ln(2)
            
    def paragraph(self, text):
        """Parrafo normal"""
        self.set_font('Helvetica', '', 10)
        self.set_text_color(51, 51, 51)
        # Limpiar caracteres Unicode problematicos
        text = clean_text(text)
        self.multi_cell(0, 6, text)
        self.ln(2)
        
    def bold_paragraph(self, text):
        """Parrafo en negrita"""
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(26, 54, 93)
        text = clean_text(text)
        self.multi_cell(0, 6, text)
        self.ln(2)
        
    def bullet_item(self, text):
        """Elemento de lista con viñeta"""
        self.set_font('Helvetica', '', 10)
        self.set_text_color(51, 51, 51)
        text = clean_text(text)
        x = self.get_x()
        self.cell(8, 6, '-', 0, 0)  # Guión como viñeta
        self.multi_cell(0, 6, text)
        self.ln(1)
        
    def add_table(self, headers, data, col_widths=None):
        """Agregar tabla formateada"""
        if not col_widths:
            num_cols = len(headers)
            col_widths = [190 / num_cols] * num_cols
            
        # Encabezados
        self.set_font('Helvetica', 'B', 8)
        self.set_fill_color(43, 108, 176)
        self.set_text_color(255, 255, 255)
        
        for i, header in enumerate(headers):
            header_clean = clean_text(header)
            self.cell(col_widths[i], 8, header_clean, 1, 0, 'C', True)
        self.ln()
        
        # Datos
        self.set_text_color(51, 51, 51)
        
        for row_idx, row in enumerate(data):
            is_summary = row_idx == len(data) - 1 and any(
                word in str(row[0]).lower() for word in ['total', 'subtotal', 'valor final']
            )
            
            if is_summary:
                self.set_font('Helvetica', 'B', 8)
                self.set_fill_color(226, 232, 240)
                fill = True
            else:
                self.set_font('Helvetica', '', 8)
                if row_idx % 2 == 0:
                    self.set_fill_color(247, 250, 252)
                    fill = True
                else:
                    fill = False
            
            for i, cell in enumerate(row):
                cell_clean = clean_text(str(cell))
                if i == len(row) - 1 and '$' in str(cell):
                    self.cell(col_widths[i], 7, cell_clean, 1, 0, 'R', fill)
                elif i == len(row) - 2 and str(cell).isdigit():
                    self.cell(col_widths[i], 7, cell_clean, 1, 0, 'C', fill)
                else:
                    self.cell(col_widths[i], 7, cell_clean, 1, 0, 'L', fill)
            self.ln()
            
        self.ln(4)


def clean_text(text):
    """Limpiar caracteres Unicode problemáticos"""
    replacements = {
        '\u2022': '-',  # Viñeta
        '\u2018': "'",  # Comilla izquierda
        '\u2019': "'",  # Comilla derecha
        '\u201c': '"',  # Comilla doble izquierda
        '\u201d': '"',  # Comilla doble derecha
        '\u2013': '-',  # Guión medio
        '\u2014': '--', # Guión largo
        '\u2026': '...', # Puntos suspensivos
        '\u00e7': 'c',  # cedilla
        '\u00f1': 'n',  # ñ
        '\u00d1': 'N',  # Ñ
        '\u00e1': 'a',  # a acento
        '\u00e9': 'e',  # e acento
        '\u00ed': 'i',  # i acento
        '\u00f3': 'o',  # o acento
        '\u00fa': 'u',  # u acento
        '\u00c1': 'A',  # A acento
        '\u00c9': 'E',  # E acento
        '\u00cd': 'I',  # I acento
        '\u00d3': 'O',  # O acento
        '\u00da': 'U',  # U acento
        '\u00dc': 'U',  # U diéresis
        '\u00fc': 'u',  # u diéresis
    }
    
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    
    # Para caracteres restantes, usar replace silencioso
    result = ''
    for char in text:
        try:
            char.encode('latin-1')
            result += char
        except UnicodeEncodeError:
            result += ' '
    
    return result


def parse_markdown_table(lines, start_idx):
    """Parsear tabla Markdown"""
    headers = []
    data = []
    idx = start_idx
    
    if idx < len(lines) and '|' in lines[idx]:
        header_line = lines[idx].strip()
        headers = [h.strip() for h in header_line.split('|')[1:-1] if h.strip()]
        idx += 1
        
        if idx < len(lines) and '---' in lines[idx]:
            idx += 1
            
        while idx < len(lines) and '|' in lines[idx] and lines[idx].strip():
            row_line = lines[idx].strip()
            row = [cell.strip() for cell in row_line.split('|')[1:-1] if cell.strip()]
            if row:
                data.append(row)
            idx += 1
            
    return headers, data, idx


def generate_pdf(md_file, pdf_file):
    """Generar PDF desde archivo Markdown"""
    
    with open(md_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    pdf = PropuestaPDF()
    pdf.add_page()
    
    idx = 0
    while idx < len(lines):
        line = lines[idx].strip()
        
        if not line:
            idx += 1
            continue
            
        # Titulos
        if line.startswith('# ') and not line.startswith('## '):
            title = clean_text(line[2:].strip())
            pdf.chapter_title(title, level=1)
            idx += 1
            continue
            
        if line.startswith('## ') and not line.startswith('### '):
            title = clean_text(line[3:].strip())
            pdf.chapter_title(title, level=2)
            idx += 1
            continue
            
        if line.startswith('### ') and not line.startswith('#### '):
            title = clean_text(line[4:].strip())
            pdf.chapter_title(title, level=3)
            idx += 1
            continue
            
        if line.startswith('#### '):
            title = clean_text(line[5:].strip())
            pdf.set_font('Helvetica', 'B', 11)
            pdf.set_text_color(45, 55, 72)
            pdf.ln(2)
            pdf.cell(0, 8, title, 0, 1, 'L')
            pdf.ln(1)
            idx += 1
            continue
            
        # Tablas
        if line.startswith('|') and idx + 1 < len(lines) and '---' in lines[idx + 1]:
            headers, data, next_idx = parse_markdown_table(lines, idx)
            if headers and data:
                num_cols = len(headers)
                if num_cols <= 3:
                    col_widths = [70, 60, 60]
                elif num_cols <= 4:
                    col_widths = [50, 45, 50, 45]
                elif num_cols <= 5:
                    col_widths = [40, 35, 40, 35, 40]
                elif num_cols <= 6:
                    col_widths = [35, 30, 35, 30, 30, 30]
                else:
                    col_widths = [190 / num_cols] * num_cols
                    
                pdf.add_table(headers, data, col_widths[:num_cols])
            idx = next_idx
            continue
            
        # Viñetas
        if line.startswith('- ') or line.startswith('* '):
            text = line[2:].strip()
            text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
            text = re.sub(r'\*(.*?)\*', r'\1', text)
            pdf.bullet_item(text)
            idx += 1
            continue
            
        # Listas numeradas
        if re.match(r'^\d+\.\s', line):
            text = re.sub(r'^\d+\.\s', '', line).strip()
            text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
            pdf.bullet_item(text)
            idx += 1
            continue
            
        # Separadores
        if line.startswith('---') or line.startswith('***'):
            pdf.ln(3)
            pdf.set_draw_color(200, 200, 200)
            pdf.set_line_width(0.3)
            pdf.line(10, pdf.get_y(), 200, pdf.get_y())
            pdf.ln(3)
            idx += 1
            continue
            
        # Negrita
        if line.startswith('**') and line.endswith('**'):
            text = line[2:-2].strip()
            pdf.bold_paragraph(text)
            idx += 1
            continue
            
        # Parrafos
        if line:
            text = line
            text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
            text = re.sub(r'\*(.*?)\*', r'\1', text)
            text = re.sub(r'`(.*?)`', r'\1', text)
            
            if any(keyword in text.upper() for keyword in ['VALOR FINAL', 'VALOR TOTAL', 'RESUMEN']):
                pdf.bold_paragraph(text)
            else:
                pdf.paragraph(text)
                
        idx += 1
    
    pdf.output(pdf_file)
    return os.path.getsize(pdf_file)


if __name__ == "__main__":
    try:
        print(f"Generando PDF desde: {INPUT_FILE}")
        size = generate_pdf(INPUT_FILE, OUTPUT_FILE)
        print(f"PDF generado exitosamente: {OUTPUT_FILE}")
        print(f"Tamano: {size:,} bytes ({size/1024:.1f} KB)")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
