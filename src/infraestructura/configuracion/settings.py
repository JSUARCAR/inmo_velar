"""
Configuración del Sistema usando Pydantic Settings

Gestiona las variables de entorno y configuración de la aplicación.
"""

from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional
from pathlib import Path


class Settings(BaseSettings):
    """
    Configuración de la aplicación.
    
    Lee automáticamente desde variables de entorno o archivo .env
    """
    
    # === Base de Datos ===
    database_path: str = Field(
        default="migraciones/DB_Inmo_Velar.db",
        description="Ruta al archivo SQLite"
    )

    # === PostgreSQL ===
    db_host: str = Field(
        default="localhost",
        description="Host de PostgreSQL"
    )
    db_port: int = Field(
        default=5432,
        description="Puerto de PostgreSQL"
    )
    db_user: str = Field(
        default="postgres",
        description="Usuario de PostgreSQL"
    )
    db_password: str = Field(
        default="",
        description="Contraseña de PostgreSQL"
    )
    db_name: str = Field(
        default="db_inmo_velar",
        description="Nombre de la base de datos PostgreSQL"
    )
    
    # === Aplicación ===
    app_name: str = Field(
        default="Sistema de Gestión Inmobiliaria",
        description="Nombre de la aplicación"
    )
    
    app_version: str = Field(
        default="1.0.0",
        description="Versión de la aplicación"
    )
    
    debug: bool = Field(
        default=False,
        description="Modo de depuración"
    )
    
    # === Logging ===
    log_level: str = Field(
        default="INFO",
        description="Nivel de logging (DEBUG, INFO, WARNING, ERROR)"
    )
    
    log_file: Optional[str] = Field(
        default="logs/app.log",
        description="Archivo de log"
    )
    
    # === Seguridad ===
    secret_key: str = Field(
        default="CHANGE_ME_IN_PRODUCTION",
        description="Clave secreta para encriptación"
    )
    
    # === Negocio ===
    moneda_default: str = Field(
        default="COP",
        description="Moneda por defecto"
    )
    
    comision_default_porcentaje: float = Field(
        default=10.0,
        description="Porcentaje de comisión por defecto"
    )

    # === Notificaciones (Email Office 365) ===
    smtp_server: str = Field(
        default="smtp.office365.com",
        description="Servidor SMTP"
    )
    
    smtp_port: int = Field(
        default=587,
        description="Puerto SMTP"
    )
    
    smtp_user: Optional[str] = Field(
        default=None,
        description="Usuario SMTP (Email)"
    )
    
    smtp_password: Optional[str] = Field(
        default=None,
        description="Contraseña SMTP (App Password)"
    )
    
    # === Notificaciones (WhatsApp) ===
    wa_autosend_delay: float = Field(
        default=3.5,
        description="Tiempo de espera para envío automático WhatsApp"
    )
    
    class Config:
        """Configuración de Pydantic."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


# Singleton de configuración
_settings_instance: Optional[Settings] = None


def obtener_configuracion() -> Settings:
    """
    Obtiene la instancia singleton de configuración.
    
    Returns:
        Configuración de la aplicación
    """
    global _settings_instance
    
    if _settings_instance is None:
        _settings_instance = Settings()
    
    return _settings_instance
