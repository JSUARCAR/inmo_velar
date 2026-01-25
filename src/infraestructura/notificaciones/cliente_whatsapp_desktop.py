import logging
import os
import time
import urllib.parse
import webbrowser

import pyautogui


class ClienteWhatsAppDesktop:
    """
    Cliente para automatización de WhatsApp Desktop.
    Utiliza webbrowser para abrir el protocolo whatsapp:// y pyautogui para enviar.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        # Tiempo de espera por defecto (segundos) para que cargue la app
        self.wait_time = float(os.getenv("WA_AUTOSEND_DELAY", "4.0"))

    def enviar_mensaje(self, telefono: str, mensaje: str) -> bool:
        """
        Abre WhatsApp Desktop y envía un mensaje automáticamente.

        Args:
            telefono: Número de teléfono con código de país (ej: 573001234567).
            mensaje: Texto del mensaje a enviar.

        Returns:
            True si se ejecutó el comando de envío (no garantiza entrega), False si falló.
        """
        try:
            # Limpiar teléfono (quitar + si existe)
            telefono = telefono.replace("+", "").strip()

            # Codificar mensaje para URL
            mensaje_encoded = urllib.parse.quote(mensaje)

            # Construir URL protocolar
            # Usamos whatsapp://send en lugar de https://wa.me para forzar app de escritorio si es posible
            url = f"whatsapp://send?phone={telefono}&text={mensaje_encoded}"

            self.logger.info(f"Abriendo WhatsApp Desktop para número {telefono}...")

            # Abrir URL (El SO debería preguntar o abrir la App)
            webbrowser.open(url)

            # Esperar a que cargue la aplicación
            # CRÍTICO: Si el PC es lento, este tiempo debe aumentar
            time.sleep(self.wait_time)

            # Simular ENTER para enviar
            # pyautogui funciona sobre la ventana activa
            self.logger.info("Enviando mensaje (Simulando ENTER)...")
            pyautogui.press("enter")

            # Opcional: Esperar un momento para asegurar que salió
            time.sleep(1)

            # Opcional: Cerrar ventana o minimizar (Alt+F4 o Win+Down)
            # pyautogui.hotkey('alt', 'f4')

            return True

        except Exception as e:
            self.logger.error(f"Error automatizando WhatsApp: {e}")
            return False
