"""
Verificación integral de todos los templates de PDF Elite.
"""
import sys
import os
from pathlib import Path
from datetime import datetime

# Añadir raíz del proyecto al path
sys.path.insert(0, os.getcwd())

def test_all_templates():
    from src.infraestructura.servicios.pdf_elite.templates.contrato_template import ContratoArrendamientoElite
    from src.infraestructura.servicios.pdf_elite.templates.contrato_template_local import ContratoArrendamientoElite as ContratoLocal
    from src.infraestructura.servicios.pdf_elite.templates.contrato_template_mandato import ContratoMandatoElite
    from src.infraestructura.servicios.pdf_elite.templates.certificado_template import CertificadoTemplate
    from src.infraestructura.servicios.pdf_elite.templates.estado_cuenta_elite import EstadoCuentaElite
    from src.infraestructura.servicios.pdf_elite.templates.incidente_template_elite import IncidenteTemplateElite

    output_dir = Path("outputs/tests/full_verify")
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Contrato Arrendamiento
    print("⏳ Generando Contrato Arrendamiento...")
    data_arriendo = {
        "contrato_id": 1, "fecha": "2026-05-10", "fecha_inicio": "2026-06-01", "fecha_fin": "2027-05-31",
        "inmueble": {"direccion": "Calle 1", "matricula_inmobiliaria": "123"},
        "arrendatario": {"nombre": "Juan", "documento": "1", "telefono": "1", "email": "j@t.com"},
        "codeudor": {"nombre": "Maria", "documento": "2", "direccion": "D2", "telefono": "2", "email": "m@t.com"},
        "condiciones": {"canon": 1000, "duracion_meses": 12, "fecha_pago": 5}
    }
    ContratoArrendamientoElite(output_dir).generate(data_arriendo)

    # 2. Contrato Local
    print("⏳ Generando Contrato Local...")
    ContratoLocal(output_dir).generate(data_arriendo)

    # 3. Contrato Mandato
    print("⏳ Generando Contrato Mandato...")
    data_mandato = {
        "contrato_id": 3, "fecha": "2026-05-10", "fecha_inicio": "2026-06-01", "fecha_fin": "2027-05-31",
        "inmueble": {"direccion": "Calle 3"},
        "mandante": {"nombre": "Pedro", "documento": "3", "telefono": "3", "email": "p@t.com"},
        "condiciones": {"valor_canon_sugerido": 2000, "duracion_meses": 12, "comision": 10}
    }
    ContratoMandatoElite(output_dir).generate(data_mandato)

    # 4. Certificado
    print("⏳ Generando Certificado...")
    data_cert = {
        "certificado_id": 4, "tipo": "paz_y_salvo", "fecha": "2026-05-10",
        "beneficiario": {"nombre": "Luis", "documento": "4"},
        "contenido": "Luis está al día.",
        "firmante": {"nombre": "Gerente"}
    }
    CertificadoTemplate(output_dir).generate(data_cert)

    # 5. Estado de Cuenta
    print("⏳ Generando Estado de Cuenta...")
    data_ec = {
        "estado_id": 5, "periodo": "2026-05", "fecha_generacion": "2026-05-10",
        "propietario": {"nombre": "Prop", "documento": "5"},
        "inmueble": {"direccion": "Inm 5"},
        "detalle_propiedades": [],
        "resumen": {"valor_neto": 100}
    }
    EstadoCuentaElite(output_dir).generate(data_ec)

    # 6. Incidente
    print("⏳ Generando Incidente...")
    data_inc = {
        "id": 6, "descripcion": "Tubo roto", "estado": "Reportado", "fecha_reporte": "2026-05-10",
        "propiedad": {"direccion": "Inm 6"}, "direccion": "Calle 6"
    }
    IncidenteTemplateElite(output_dir).generate(data_inc)

    print("✅ Todas las generaciones completadas.")

if __name__ == "__main__":
    test_all_templates()
