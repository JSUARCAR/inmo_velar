import os
from typing import Optional
from pathlib import Path
import logging

from src.infraestructura.notificaciones.cliente_email_office365 import ClienteEmailOffice365
from src.infraestructura.notificaciones.cliente_whatsapp_desktop import ClienteWhatsAppDesktop
# Importar entidades para type hinting (ajustar paths según estructura real)
# from src.dominio.entidades.liquidacion_asesor import LiquidacionAsesor 
# from src.dominio.entidades.recibo_publico import ReciboPublico

class ServicioNotificaciones:
    """
    Servicio de dominio para la gestión de notificaciones.
    Orquesta el uso de clientes de Email y WhatsApp.
    """
    
    def __init__(self):
        self.email_client = ClienteEmailOffice365()
        self.whatsapp_client = ClienteWhatsAppDesktop()
        self.logger = logging.getLogger(__name__)
        self.template_path = Path(__file__).parent.parent.parent / "infraestructura" / "templates" / "email" / "base_notificacion.html"

    def _cargar_template(self, nombre_destinatario: str, mensaje_cuerpo: str, contenido_extra: str = "") -> str:
        """Carga y renderiza el template HTML básico."""
        from string import Template
        try:
            if self.template_path.exists():
                with open(self.template_path, "r", encoding="utf-8") as f:
                    html_content = f.read()
                
                template = Template(html_content)
                return template.safe_substitute(
                    nombre_destinatario=nombre_destinatario,
                    mensaje_cuerpo=mensaje_cuerpo,
                    contenido_extra=contenido_extra
                )
            else:
                return f"<p>{mensaje_cuerpo}</p>"
        except Exception as e:
            self.logger.error(f"Error cargando template: {e}")
            return mensaje_cuerpo

    def notificar_liquidacion_asesor(self, liquidacion, email_asesor: str, nombre_asesor: str, pdf_path: Optional[str] = None) -> bool:
        """
        Envía notificación de liquidación a un asesor por correo.
        
        Args:
            liquidacion: Objeto LiquidacionAsesor (o dict).
            email_asesor: Correo del asesor.
            nombre_asesor: Nombre del asesor.
            pdf_path: Ruta al archivo PDF generado.
        """
        if not email_asesor:
            self.logger.warning("No se puede notificar: Asesor sin email.")
            return False

        asunto = f"Comprobante de Liquidación - Período {liquidacion.periodo_liquidacion}"
        cuerpo_msg = (
            f"Adjunto encontrarás el comprobante de tu liquidación correspondiente al período <strong>{liquidacion.periodo_liquidacion}</strong>.<br>"
            f"Valor Neto a Pagar: <strong>${liquidacion.valor_neto_asesor:,.0f}</strong>"
        )
        
        html_content = self._cargar_template(nombre_asesor, cuerpo_msg)
        
        return self.email_client.enviar_correo(
            destinatario=email_asesor,
            asunto=asunto,
            cuerpo=html_content,
            adjunto_path=pdf_path
        )

    def notificar_recibo_vencido_whatsapp(self, recibo, telefono_inquilino: str, nombre_inquilino: str) -> bool:
        """
        Envía recordatorio de recibo público vencido por WhatsApp.
        
        Args:
            recibo: Objeto ReciboPublico.
            telefono_inquilino: Teléfono del inquilino (ej: 57300...).
            nombre_inquilino: Nombre del inquilino.
        """
        if not telefono_inquilino:
            self.logger.warning("No se puede notificar: Inquilino sin teléfono.")
            return False
            
        mensaje = (
            f"Hola {nombre_inquilino}, cordial saludo de Inmobiliaria Velar. "
            f"Le recordamos que el recibo de {recibo.tipo_servicio} por valor de ${recibo.valor_recibo:,.0f} "
            f"venció el día {recibo.fecha_vencimiento}. "
            f"Por favor gestionar el pago y enviar el comprobante. Gracias."
        )
        
        
        return self.whatsapp_client.enviar_mensaje(telefono_inquilino, mensaje)
    
    def notificar_liquidacion_asesor_whatsapp(self, liquidacion, telefono_asesor: str, nombre_asesor: str) -> bool:
        """
        Envía notificación de liquidación a un asesor por WhatsApp.
        
        Args:
            liquidacion: Objeto LiquidacionAsesor (o dict).
            telefono_asesor: Teléfono del asesor (ej: 573001234567).
            nombre_asesor: Nombre del asesor.
            
        Returns:
            True si se ejecutó el envío, False en caso contrario.
        """
        if not telefono_asesor:
            self.logger.warning("No se puede notificar: Asesor sin teléfono.")
            return False
            
        mensaje = (
            f"Hola {nombre_asesor}, cordial saludo de Inmobiliaria Velar. "
            f"Su liquidación del período {liquidacion.periodo_liquidacion} ha sido procesada. "
            f"Valor neto a pagar: ${liquidacion.valor_neto_asesor:,.0f}. "
            f"Por favor comuníquese con la administración para coordinar el pago. Gracias."
        )
        
        return self.whatsapp_client.enviar_mensaje(telefono_asesor, mensaje)

