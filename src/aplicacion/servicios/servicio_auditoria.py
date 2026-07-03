"""
Servicio para gestión de auditoría en la aplicación.
Centraliza el registro de auditoría, incluyendo captura de IP y sesión.

Feature: 003-integracion-incidentes-liquidaciones
"""
import logging
from typing import Optional, Dict, Any

from src.dominio.interfaces.repositorio_auditoria import RepositorioAuditoria

logger = logging.getLogger(__name__)

class ServicioAuditoria:
    """
    Servicio de aplicación para registrar eventos de auditoría.
    Maneja la captura de contexto adicional como IP y sesión.
    """
    
    def __init__(self, repositorio: RepositorioAuditoria):
        self.repositorio = repositorio
        
    def auditar_accion(
        self,
        tabla: str,
        id_registro: int,
        accion: str,
        usuario: str,
        motivo: str = "",
        valor_anterior: Optional[str] = None,
        valor_nuevo: Optional[str] = None,
        campo: Optional[str] = None,
        ip_origen: Optional[str] = None,
        sesion_id: Optional[str] = None
    ) -> bool:
        """
        Registra una acción en la auditoría con información de contexto.
        """
        try:
            contexto_extra = []
            if ip_origen:
                contexto_extra.append(f"IP: {ip_origen}")
            if sesion_id:
                contexto_extra.append(f"Sesión: {sesion_id}")
                
            if contexto_extra:
                info_extra = " [" + ", ".join(contexto_extra) + "]"
                motivo = f"{motivo}{info_extra}"
                
            self.repositorio.guardar_cambio(
                tabla=tabla,
                id_registro=id_registro,
                tipo_operacion=accion,
                valor_anterior=valor_anterior,
                valor_nuevo=valor_nuevo,
                usuario=usuario,
                motivo_cambio=motivo,
                campo_modificado=campo
            )
            return True
        except Exception as e:
            logger.error(f"Error al auditar acción: {e}")
            return False
