import os
import sys
import logging
from dotenv import load_dotenv

# Agregar raíz del proyecto al path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.aplicacion.servicios.servicio_notificaciones import ServicioNotificaciones

# Configurar Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_whatsapp():
    load_dotenv()
    
    servicio = ServicioNotificaciones()
    
    # Mock de Recibo
    class MockRecibo:
        tipo_servicio = "Energía Varia"
        valor_recibo = 150000.0
        fecha_vencimiento = "2025-01-15"
    
    print("\n--- PRUEBA DE NOTIFICACIÓN WHATSAPP ---")
    print("El sistema intentará abrir WhatsApp Desktop.")
    print("Asegúrate de tener la sesión iniciada y el PC desbloqueado.")
    telefono = input("Ingresa un número de celular para la prueba (ej: 573xxxxxxxxx): ").strip()
    
    if not telefono:
        logger.warning("Prueba cancelada.")
        return

    logger.info(f"📱 Enviando mensaje de prueba a: {telefono}...")
    
    try:
        resultado = servicio.notificar_recibo_vencido_whatsapp(
            recibo=MockRecibo(),
            telefono_inquilino=telefono,
            nombre_inquilino="Usuario de Prueba"
        )
        
        if resultado:
            logger.info("✅ Comando de envío ejecutado. Verifica si se envió el mensaje en WhatsApp.")
        else:
            logger.error("❌ FALLO: El comando no se ejecutó correctamente.")
            
    except Exception as e:
        logger.error(f"❌ Error crítico: {e}")

if __name__ == "__main__":
    test_whatsapp()
