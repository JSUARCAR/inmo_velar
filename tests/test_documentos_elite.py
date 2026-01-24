
import unittest
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.dominio.servicios.validador_documentos import ValidadorDocumentos
from src.aplicacion.servicios.servicio_documental import ServicioDocumentalElite

class TestDocumentosElite(unittest.TestCase):
    
    def test_validacion_extensiones(self):
        """Prueba que se acepten/rechacen extensiones según módulo."""
        print("\n--- Test Validación Extensiones ---")
        
        # Caso 1: Desocupación permite PDF (checklist) y JPG (fotos)
        res_ok_pdf = ValidadorDocumentos.validar_archivo_generico(
            "DESOCUPACION", "archivo.pdf", 1024
        )
        self.assertTrue(res_ok_pdf['valido'], "Debería aceptar PDF en Desocupación")
        print("✓ PDF aceptado en Desocupación")

        res_ok_jpg = ValidadorDocumentos.validar_archivo_generico(
            "DESOCUPACION", "foto.jpg", 1024
        )
        self.assertTrue(res_ok_jpg['valido'], "Debería aceptar JPG en Desocupación")
        print("✓ JPG aceptado en Desocupación")

        # Caso 2: Rechazar EXE
        res_fail_exe = ValidadorDocumentos.validar_archivo_generico(
            "DESOCUPACION", "virus.exe", 1024
        )
        self.assertFalse(res_fail_exe['valido'], "Debería rechazar EXE")
        print("✓ EXE rechazado correctamente")

    def test_validacion_tamano(self):
        """Prueba validación de límites de tamaño."""
        print("\n--- Test Validación Tamaño ---")
        
        # Límite Desocupación ~3MB para fotos
        limit_bytes = 3 * 1024 * 1024
        
        # Caso Ok
        res_ok = ValidadorDocumentos.validar_archivo_generico(
            "DESOCUPACION", "foto.jpg", limit_bytes - 100
        )
        self.assertTrue(res_ok['valido'])
        print("✓ Archivo bajo límite aceptado")

        # Caso Fail
        res_fail = ValidadorDocumentos.validar_archivo_generico(
            "DESOCUPACION", "foto.jpg", limit_bytes + 1000
        )
        self.assertFalse(res_fail['valido'])
        self.assertIn("excede el tamaño", res_fail['mensaje'])
        print("✓ Archivo sobre límite rechazado")

    def test_generacion_thumbnail(self):
        """Prueba generación de thumbnails (Requiere PIL/Pillow)."""
        print("\n--- Test Generación Thumbnail ---")
        try:
            from PIL import Image
            import io
            
            # Crear imagen dummy en memoria
            img = Image.new('RGB', (500, 500), color='red')
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='JPEG')
            img_bytes = img_byte_arr.getvalue()
            
            servicio = ServicioDocumentalElite()
            thumb = servicio.generar_thumbnail(img_bytes, "image/jpeg")
            
            self.assertIsNotNone(thumb)
            
            # Verificar tamaño reducido
            thumb_img = Image.open(io.BytesIO(thumb))
            self.assertTrue(thumb_img.width <= 200)
            self.assertTrue(thumb_img.height <= 200)
            print(f"✓ Thumbnail generado: {thumb_img.size} (Original: 500x500)")
            
        except ImportError:
            print("! Skipped: PIL no instalado")

    def test_validacion_propiedades(self):
        """Prueba reglas específicas del módulo Propiedades."""
        print("\n--- Test Validación Propiedades ---")
        
        # Caso 1: Video mp4 permitido (hasta 50MB)
        res_video = ValidadorDocumentos.validar_archivo_generico(
            "PROPIEDAD", "recorrido.mp4", 45 * 1024 * 1024
        )
        self.assertTrue(res_video['valido'], "Debería aceptar MP4 de 45MB")
        print("✓ Video MP4 aceptado")

        # Caso 2: Video muy grande rechazado
        res_video_fail = ValidadorDocumentos.validar_archivo_generico(
            "PROPIEDAD", "recorrido.mp4", 55 * 1024 * 1024
        )
        self.assertFalse(res_video_fail['valido'], "Debería rechazar MP4 de 55MB")
        print("✓ Video MP4 excedido rechazado")

        # Caso 3: Escritura pública (PDF) aceptada
        res_escritura = ValidadorDocumentos.validar_archivo_generico(
            "PROPIEDAD", "escritura.pdf", 15 * 1024 * 1024
        )
        self.assertTrue(res_escritura['valido'], "Debería aceptar Escritura PDF de 15MB")
        print("✓ Escritura PDF aceptada")

if __name__ == '__main__':
    unittest.main()
