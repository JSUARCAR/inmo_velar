import logging
import os
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from src.infraestructura.configuracion.settings import obtener_configuracion


class ClienteEmailOffice365:
    """
    Cliente para envío de correos usando el servidor SMTP de Office 365.
    Usa la configuración centralizada (Settings).
    """

    def __init__(self):
        config = obtener_configuracion()
        self.smtp_server = config.smtp_server
        self.smtp_port = config.smtp_port
        self.email = config.smtp_user
        self.password = config.smtp_password
        self.logger = logging.getLogger(__name__)

        if not self.email or not self.password:
            self.logger.warning("Credenciales SMTP no configuradas (configuracion settings)")

    def enviar_correo(
        self, destinatario: str, asunto: str, cuerpo: str, adjunto_path: str = None
    ) -> bool:
        """
        Envía un correo electrónico a través de Office 365.

        Args:
            destinatario: Dirección de correo del destinatario.
            asunto: Asunto del correo.
            cuerpo: Contenido del correo en formato HTML o texto plano.
            adjunto_path: Ruta absoluta al archivo adjunto (opcional).

        Returns:
            True si el envío fue exitoso, False en caso contrario.
        """
        if not self.email or not self.password:
            self.logger.error("No se puede enviar correo: Credenciales faltantes.")
            return False

        try:
            # Configurar mensaje
            msg = MIMEMultipart()
            msg["From"] = self.email
            msg["To"] = destinatario
            msg["Subject"] = asunto

            # Agregar cuerpo del mensaje
            msg.attach(MIMEText(cuerpo, "html"))  # Asumimos HTML por defecto para formatting

            # Agregar adjunto si existe
            if adjunto_path:
                if os.path.exists(adjunto_path):
                    filename = os.path.basename(adjunto_path)
                    try:
                        with open(adjunto_path, "rb") as f:
                            part = MIMEApplication(f.read(), Name=filename)

                        part["Content-Disposition"] = f'attachment; filename="{filename}"'
                        msg.attach(part)
                    except Exception as e:
                        self.logger.error(f"Error leyendo adjunto {adjunto_path}: {e}")
                else:
                    self.logger.warning(f"Archivo adjunto no encontrado: {adjunto_path}")

            # Conectar al servidor SMTP
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()  # Importante para Office 365
                server.login(self.email, self.password)
                server.send_message(msg)

            self.logger.info(f"Correo enviado exitosamente a {destinatario}")
            return True

        except smtplib.SMTPAuthenticationError as e:
            # Log silently for debugging - don't alarm users with console errors
            self.logger.debug(f"SMTP Auth failed: {e}")
            return False
        except Exception as e:
            # Log connection/send errors silently
            self.logger.debug(f"Error enviando correo a {destinatario}: {e}")
            return False
