#!/usr/bin/env python3
"""
Generador de PDF para Propuesta Comercial
Usa Markdown → HTML → PDF con WeasyPrint
"""

import markdown
from weasyprint import HTML
import os

# Rutas
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_FILE = os.path.join(BASE_DIR, "docs", "propuesta-comercial-inmobiliaria-velar.md")
OUTPUT_FILE = os.path.join(BASE_DIR, "docs", "propuesta-comercial-inmobiliaria-velar.pdf")

# CSS profesional para tablas y documentos
CSS_STYLE = """
@page {
    size: letter;
    margin: 2cm;
    @bottom-center {
        content: "Propuesta Comercial - Inmobiliaria Velar SAS | Página " counter(page) " de " counter(pages);
        font-size: 8pt;
        color: #666;
    }
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    font-size: 10pt;
    line-height: 1.6;
    color: #333;
}

h1 {
    color: #1a365d;
    font-size: 24pt;
    border-bottom: 3px solid #2b6cb0;
    padding-bottom: 10px;
    margin-top: 30px;
}

h2 {
    color: #2b6cb0;
    font-size: 16pt;
    border-bottom: 2px solid #bee3f8;
    padding-bottom: 8px;
    margin-top: 25px;
}

h3 {
    color: #2c5282;
    font-size: 13pt;
    margin-top: 20px;
}

h4 {
    color: #2d3748;
    font-size: 11pt;
    margin-top: 15px;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin: 15px 0;
    font-size: 9pt;
    page-break-inside: avoid;
}

thead {
    background-color: #2b6cb0;
    color: white;
}

th {
    padding: 10px 8px;
    text-align: left;
    font-weight: bold;
    border: 1px solid #2c5282;
}

td {
    padding: 8px;
    border: 1px solid #e2e8f0;
}

tr:nth-child(even) {
    background-color: #f7fafc;
}

tr:hover {
    background-color: #ebf8ff;
}

tr:last-child td {
    font-weight: bold;
    background-color: #e2e8f0;
}

strong {
    color: #1a365d;
}

ul, ol {
    margin-left: 20px;
    margin-bottom: 15px;
}

li {
    margin-bottom: 5px;
}

hr {
    border: none;
    border-top: 2px solid #e2e8f0;
    margin: 20px 0;
}

p {
    margin-bottom: 10px;
}

/* Estilos para énfasis */
em {
    font-style: italic;
    color: #4a5568;
}

/* Código */
code {
    background-color: #edf2f7;
    padding: 2px 6px;
    border-radius: 4px;
    font-family: 'Consolas', monospace;
    font-size: 9pt;
}
"""

def markdown_to_pdf(md_file, pdf_file):
    """Convierte Markdown a PDF con estilos profesionales"""
    
    # Leer archivo Markdown
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()
    
    # Convertir Markdown a HTML
    html_body = markdown.markdown(
        md_content,
        extensions=['tables', 'fenced_code', 'toc', 'nl2br']
    )
    
    # Crear HTML completo con CSS
    html_full = f"""
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <title>Propuesta Comercial - Inmobiliaria Velar SAS</title>
        <style>
        {CSS_STYLE}
        </style>
    </head>
    <body>
        {html_body}
    </body>
    </html>
    """
    
    # Generar PDF
    HTML(string=html_full).write_pdf(pdf_file)
    
    return os.path.getsize(pdf_file)

if __name__ == "__main__":
    try:
        print(f"Generando PDF desde: {md_file}")
        size = markdown_to_pdf(INPUT_FILE, OUTPUT_FILE)
        print(f"PDF generado exitosamente: {OUTPUT_FILE}")
        print(f"Tamaño: {size:,} bytes ({size/1024:.1f} KB)")
    except Exception as e:
        print(f"Error: {e}")
        raise
