
import os
import sys
from pathlib import Path
from typing import Any, Dict
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent))

from src.infraestructura.servicios.pdf_elite.templates.contrato_template_mandato import ContratoMandatoElite

def get_datos_dummy():
    return {
        "contrato_id": 70,
        "tipo_contrato": "MANDATO",
        "fecha": datetime.now().strftime("%Y-%m-%d"),
        "fecha_inicio": "2026-03-01",
        "fecha_fin": "2027-03-01",
        "estado": "oficial",
        "mandante": {
            "nombre": "YESID BEDOYA RAMIREZ",
            "documento": "1097721326",
            "telefono": "3183864675",
            "email": "YESIDBEDOYA@HOTMAIL.COM",
            "banco": "BANCOLOMBIA",
            "tipo_cuenta": "Ahorros",
            "numero_cuenta": "86500004079",
        },
        "inmueble": {
            "direccion": "BRR LA PATRIA MZ 29 CS 38",
            "matricula_inmobiliaria": "280-105975",
            "municipio": "ARMENIA",
            "departamento": "QUINDÍO",
            "tipo": "Casa",
        },
        "condiciones": {
            "valor_canon_sugerido": 850000,
            "comision": 10,
            "duracion_meses": 12,
            "fecha_pago": 5,
        }
    }

def test_without_image():
    # Parchear ContratoMandatoElite._header_footer_with_features para no poner la imagen
    orig_header = ContratoMandatoElite._header_footer_with_features
    
    def patched_header(self, canvas_obj, doc):
        # Skip image drawing
        print("v Patched header: skipping image")
        pass # Just do nothing or some simple text
        
    ContratoMandatoElite._header_footer_with_features = patched_header
    
    try:
        gen = ContratoMandatoElite()
        datos = get_datos_dummy()
        pdf_path = gen.generate(datos)
        print(f"v PDF sin imagen generado en: {pdf_path}")
    except Exception as e:
        print(f"x ERROR: {e}")
    finally:
        ContratoMandatoElite._header_footer_with_features = orig_header

if __name__ == "__main__":
    test_without_image()
