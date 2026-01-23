"""
Repositorio para ConfiguracionEmpresa.
Gestiona el acceso a la tabla configuracion_sistema.
"""

from typing import Optional
from datetime import datetime
import json

from src.dominio.entidades.configuracion_empresa import ConfiguracionEmpresa
from src.infraestructura.persistencia.database import DatabaseManager

class RepositorioConfiguracionEmpresa:
    """Repositorio para gestionar la configuración de la empresa."""

    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def _row_to_entity(self, row) -> ConfiguracionEmpresa:
        """Convierte fila de BD a entidad."""
        if not row:
            return None
        
        # Manejo flexible de diccionarios (PostgreSQL/SQLite)
        row_dict = dict(row) if hasattr(row, 'keys') else row

        return ConfiguracionEmpresa(
            id=row_dict.get('id') or row_dict.get('ID'),
            nombre_empresa=row_dict.get('nombre_empresa') or row_dict.get('NOMBRE_EMPRESA'),
            nit=row_dict.get('nit') or row_dict.get('NIT'),
            email=row_dict.get('email') or row_dict.get('EMAIL'),
            telefono=row_dict.get('telefono') or row_dict.get('TELEFONO'),
            direccion=row_dict.get('direccion') or row_dict.get('DIRECCION'),
            ubicacion=row_dict.get('ubicacion') or row_dict.get('UBICACION'),
            website=row_dict.get('website') or row_dict.get('WEBSITE'),
            redes_sociales=row_dict.get('redes_sociales') or row_dict.get('REDES_SOCIALES'),
            representante_legal=row_dict.get('representante_legal') or row_dict.get('REPRESENTANTE_LEGAL') or "",
            cedula_representante=row_dict.get('cedula_representante') or row_dict.get('CEDULA_REPRESENTANTE') or "",
            logo_base64=row_dict.get('logo_base64') or row_dict.get('LOGO_BASE64') or "",
            logo_filename=row_dict.get('logo_filename') or row_dict.get('LOGO_FILENAME') or "",
            created_at=str(row_dict.get('created_at') or row_dict.get('CREATED_AT')),
            updated_at=str(row_dict.get('updated_at') or row_dict.get('UPDATED_AT'))
        )

    def obtener_configuracion(self) -> ConfiguracionEmpresa:
        """
        Obtiene la configuración actual (ID=1).
        Si no existe, retorna una instancia vacía o crea una por defecto.
        """
        conn = self.db.obtener_conexion()
        cursor = self.db.get_dict_cursor(conn)
        placeholder = self.db.get_placeholder()

        cursor.execute(
            f"SELECT * FROM configuracion_sistema WHERE id = {placeholder}", 
            (1,)
        )
        row = cursor.fetchone()
        
        if row:
            return self._row_to_entity(row)
        
        # Si no existe, crear registro por defecto
        default_config = ConfiguracionEmpresa(
            id=1,
            nombre_empresa="Inmobiliaria Default",
            nit="",
            email="",
            telefono="",
            direccion="",
            ubicacion="",
            website="",
            representante_legal="",
            cedula_representante="",
            redes_sociales="{}"
        )
        # Intentar crearlo (puede fallar si hay condiciones de carrera, pero es poco probable aquí)
        # O simplemente retornarlo vacío
        return default_config

    def guardar_configuracion(self, config: ConfiguracionEmpresa) -> bool:
        """
        Guarda (Actualiza) la configuración de le empresa (ID=1).
        Siempre actualiza el registro con ID=1.
        """
        with self.db.transaccion() as conn:
            cursor = conn.cursor()
            placeholder = self.db.get_placeholder()
            
            # Upsert logic (Intentar UPDATE, si no afecta filas, INSERT)
            # Como sabemos que trabajamos sobre ID=1, podemos hacer UPDATE directo si existe
            
            # Primero intentar UPDATE
            query_update = f"""
                UPDATE configuracion_sistema SET
                    nombre_empresa = {placeholder},
                    nit = {placeholder},
                    email = {placeholder},
                    telefono = {placeholder},
                    direccion = {placeholder},
                    ubicacion = {placeholder},
                    website = {placeholder},
                    redes_sociales = {placeholder},
                    representante_legal = {placeholder},
                    cedula_representante = {placeholder},
                    logo_base64 = {placeholder},
                    logo_filename = {placeholder},
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = 1
            """
            params = (
                config.nombre_empresa,
                config.nit,
                config.email,
                config.telefono,
                config.direccion,
                config.ubicacion,
                config.website,
                config.redes_sociales,
                config.representante_legal,
                config.cedula_representante,
                config.logo_base64,
                config.logo_filename
            )
            
            cursor.execute(query_update, params)
            
            if cursor.rowcount == 0:
                # Si no actualizó nada, intentar INSERT con ID=1 especificado
                query_insert = f"""
                    INSERT INTO configuracion_sistema (
                        id, nombre_empresa, nit, email, telefono, 
                        direccion, ubicacion, website, redes_sociales,
                        representante_legal, cedula_representante,
                        logo_base64, logo_filename
                    ) VALUES (1, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
                """
                cursor.execute(query_insert, params)
                
            return True
