
import os
import sys
from pathlib import Path
from typing import Any, Dict
from datetime import datetime

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent))

from src.infraestructura.servicios.servicio_pdf_facade import ServicioPDFFacade

def repro_pdf_with_ampersand():
    try:
        datos = {
            "contrato_id": 999,
            "tipo_contrato": "MANDATO",
            "fecha": datetime.now().strftime("%Y-%m-%d"),
            "fecha_inicio": "2026-03-01",
            "fecha_fin": "2027-03-01",
            "estado": "oficial",
            "mandante": {
                "nombre": "YESID BEDOYA & CIA", # <--- AMPERSAND
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
        
        facade = ServicioPDFFacade()
        print("v Generando PDF con '&'...")
        pdf_path = facade.generar_contrato_elite(datos)
        print(f"v PDF generado en: {pdf_path}")
        
    except Exception as e:
        print(f"x ERROR ESPERADO: {e}")
        # import traceback
        # traceback.print_exc()

if __name__ == "__main__":
    repro_pdf_with_ampersand()
