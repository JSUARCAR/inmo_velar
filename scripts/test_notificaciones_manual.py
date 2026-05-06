import os
import sys
import logging
from dotenv import load_dotenv

# Agregar raíz del proyecto al path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.aplicacion.servicios.servicio_notificaciones import ServicioNotificaciones
from src.dominio.entidades.liquidacion_asesor import LiquidacionAsesor

# Configurar Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_email():
    load_dotenv()
    
    servicio = ServicioNotificaciones()
    destinatario = os.getenv("SMTP_USER") # Autenvío para probar
    
    if not destinatario or "your-email" in destinatario:
        logger.error("❌ ERROR: Configura SMTP_USER en .env antes de probar.")
        return

    logger.info(f"📧 Probando envío de correo a: {destinatario}...")
    
    # Mock de Liquidación
    class MockLiquidacion:
        periodo_liquidacion = "2025-01 (TEST)"
        valor_neto_asesor = 1234567.0
    
    resultado = servicio.notificar_liquidacion_asesor(
        liquidacion=MockLiquidacion(),
        email_asesor=destinatario,
        nombre_asesor="Administrador (Test)"
    )
    
    if resultado:
        logger.info("✅ ÉXITO: Correo enviado correctamente. Revisa tu bandeja de entrada.")
    else:
        logger.error("❌ FALLO: El correo no se pudo enviar. Revisa los logs.")

if __name__ == "__main__":
    test_email()
