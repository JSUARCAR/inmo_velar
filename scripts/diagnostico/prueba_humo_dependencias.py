"""Pruebas de humo de dependencias (spec 080).

Verifica que los saltos mayores de versión (Plotly, ReportLab, bcrypt, qrcode,
Pillow) siguen funcionando. Se ejecuta con datos sintéticos, sin base de datos.

Uso:
    python scripts/diagnostico/prueba_humo_dependencias.py
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path
from typing import Callable

RAIZ_PROYECTO: Path = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ_PROYECTO))

CABECERA_PDF: bytes = b"%PDF"
CABECERA_PNG: bytes = b"\x89PNG"


def prueba_pdf_contrato_pdf_elite(directorio: Path) -> str:
    """Genera un PDF de contrato de arrendamiento con pdf_elite (ReportLab)."""
    from src.infraestructura.servicios.pdf_elite.templates.contrato_template import (
        ContratoArrendamientoElite,
    )

    datos = {
        "contrato_id": 123,
        "fecha": "2026-01-18",
        "arrendador": {"nombre": "Juan Pérez", "documento": "123456", "telefono": "555-1234"},
        "arrendatario": {
            "nombre": "María López",
            "documento": "789012",
            "telefono": "555-5678",
            "email": "maria@example.com",
        },
        "codeudor": {
            "nombre": "Pedro Gómez",
            "documento": "123",
            "direccion": "Calle 123",
            "telefono": "555-1234",
            "email": "pedro@example.com",
        },
        "inmueble": {
            "direccion": "Calle 123 #45-67",
            "tipo": "Apartamento",
            "matricula_inmobiliaria": "123",
        },
        "condiciones": {"canon": 1000000, "duracion_meses": 12},
        "fecha_inicio": "2026-01-01",
        "fecha_fin": "2026-12-31",
    }
    ruta = ContratoArrendamientoElite(output_dir=directorio).generate(datos)
    contenido = Path(ruta).read_bytes()
    assert contenido.startswith(CABECERA_PDF), "El contrato no es un PDF válido"
    return f"{Path(ruta).name} ({len(contenido)} bytes)"


def prueba_pdf_fpdf2(directorio: Path) -> str:
    """Genera un PDF simple con fpdf2."""
    from fpdf import FPDF

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", size=12)
    pdf.cell(text="Prueba de humo fpdf2 - Inmobiliaria Velar")
    contenido = bytes(pdf.output())
    (directorio / "fpdf2.pdf").write_bytes(contenido)
    assert contenido.startswith(CABECERA_PDF), "fpdf2 no generó un PDF válido"
    return f"{len(contenido)} bytes"


def prueba_qr() -> str:
    """Genera un QR (qrcode + Pillow) y uno de verificación con pdf_elite."""
    import qrcode

    from src.infraestructura.servicios.pdf_elite.utils.qr_generator import QRGenerator

    imagen = qrcode.make("https://example.com")
    assert imagen.size[0] > 0, "qrcode devolvió una imagen vacía"
    buffer = QRGenerator.generate_verification_qr("contrato", 12345)
    assert buffer.getvalue().startswith(CABECERA_PNG), "El QR no es PNG"
    return f"qrcode.make OK, QR verificación {len(buffer.getvalue())} bytes"


def prueba_codigo_barras() -> str:
    """Genera un código de barras (python-barcode + Pillow)."""
    from src.infraestructura.servicios.pdf_elite.utils.barcode_generator import (
        BarcodeGenerator,
    )

    buffer = BarcodeGenerator.generate_document_barcode(12345, prefix="DOC")
    assert buffer.getvalue(), "Código de barras vacío"
    return f"{len(buffer.getvalue())} bytes"


def prueba_bcrypt() -> str:
    """Hashea y verifica con bcrypt vía ServicioAutenticacion."""
    from src.aplicacion.servicios.servicio_autenticacion import ServicioAutenticacion

    clave = "ClaveDePrueba-080"
    hash_clave = ServicioAutenticacion.hashear_contraseña(clave)
    servicio = ServicioAutenticacion(repo_usuario=None, repo_sesion=None)  # type: ignore[arg-type]
    assert servicio.verificar_contraseña(clave, hash_clave) is True
    assert servicio.verificar_contraseña("otra", hash_clave) is False
    return f"hash {hash_clave[:7]}… verificado"


def prueba_plotly() -> str:
    """Construye y serializa una figura Plotly."""
    import plotly.graph_objects as go

    figura = go.Figure(go.Bar(x=["Ene", "Feb", "Mar"], y=[1, 3, 2]))
    figura.update_layout(title="Prueba de humo")
    json_figura = figura.to_json()
    assert '"bar"' in json_figura, "La figura no serializó el trazo de barras"
    return f"figura serializada ({len(json_figura)} chars)"


def prueba_plotly_a_imagen() -> str:
    """Exporta una figura a PNG vía kaleido (requiere Chrome/Chromium)."""
    import plotly.graph_objects as go

    from src.infraestructura.servicios.pdf_elite.utils.chart_converter import (
        ChartConverter,
    )

    figura = go.Figure(go.Bar(x=["a", "b"], y=[1, 2]))
    buffer = ChartConverter.plotly_to_image(figura, width=300, height=200, scale=1.0)
    assert buffer.getvalue().startswith(CABECERA_PNG), "kaleido no devolvió PNG"
    return f"{len(buffer.getvalue())} bytes"


def main() -> int:
    """Ejecuta todas las pruebas y devuelve 1 si alguna obligatoria falla."""
    resultados: list[tuple[str, bool, str]] = []
    with tempfile.TemporaryDirectory(prefix="humo_deps_") as tmp:
        directorio = Path(tmp)
        pruebas: list[tuple[str, Callable[[], str], bool]] = [
            ("PDF contrato pdf_elite (ReportLab)", lambda: prueba_pdf_contrato_pdf_elite(directorio), True),
            ("PDF fpdf2", lambda: prueba_pdf_fpdf2(directorio), True),
            ("QR (qrcode + Pillow)", prueba_qr, True),
            ("Código de barras (python-barcode)", prueba_codigo_barras, True),
            ("bcrypt hash/verificación", prueba_bcrypt, True),
            ("Figura Plotly", prueba_plotly, True),
            ("Plotly -> PNG (kaleido, informativa)", prueba_plotly_a_imagen, False),
        ]
        for nombre, funcion, obligatoria in pruebas:
            try:
                detalle = funcion()
                resultados.append((nombre, True, detalle))
            except (AssertionError, ImportError, OSError, RuntimeError, ValueError, KeyError, TypeError) as error:
                etiqueta = "" if obligatoria else " [no obligatoria]"
                resultados.append((nombre + etiqueta, False, f"{type(error).__name__}: {error}"))

    fallo_obligatorio = False
    for nombre, ok, detalle in resultados:
        estado = "OK   " if ok else "FALLA"
        print(f"[{estado}] {nombre}: {detalle[:300]}")
        if not ok and "[no obligatoria]" not in nombre:
            fallo_obligatorio = True
    return 1 if fallo_obligatorio else 0


if __name__ == "__main__":
    sys.exit(main())
