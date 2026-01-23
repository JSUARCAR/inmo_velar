import reflex as rx
from typing import List, Dict, Any
from src.aplicacion.servicios.servicio_configuracion import ServicioConfiguracion
from src.infraestructura.persistencia.database import db_manager
from src.dominio.entidades.parametro_sistema import ParametroSistema
from src.dominio.entidades.configuracion_empresa import ConfiguracionEmpresa

class ConfiguracionState(rx.State):
    """Estado para la página de configuración."""
    
    # Datos de Empresa
    empresa: Dict[str, str] = {
        "nombre_empresa": "",
        "nit": "",
        "representante_legal": "",
        "cedula_representante": "",
        "email": "",
        "telefono": "",
        "direccion": "",
        "ubicacion": "",
        "website": "",
        "facebook": "",
        "instagram": "",
        "tiktok": "",
    }
    
    # Logo
    logo_preview: str = ""  # URL data: para preview
    logo_base64: str = ""  # Base64 del logo cargado
    logo_filename: str = ""  # Nombre del archivo
    
    # Parámetros del Sistema
    parametros: List[ParametroSistema] = []
    
    def on_load(self):
        """Carga los datos al iniciar la página."""
        self.cargar_datos_empresa()
        self.cargar_parametros()

    def cargar_datos_empresa(self):
        """Carga la configuración de la empresa desde BD."""
        servicio = ServicioConfiguracion(db_manager)
        config = servicio.obtener_configuracion_empresa()
        
        if config:
            # Parse social media JSON
            redes = config.redes_sociales_dict
            self.empresa = {
                "nombre_empresa": config.nombre_empresa or "",
                "nit": config.nit or "",
                "representante_legal": config.representante_legal or "",
                "cedula_representante": config.cedula_representante or "",
                "email": config.email or "",
                "telefono": config.telefono or "",
                "direccion": config.direccion or "",
                "ubicacion": config.ubicacion or "",
                "website": config.website or "",
                "facebook": redes.get("facebook", ""),
                "instagram": redes.get("instagram", ""),
                "tiktok": redes.get("tiktok", ""),
            }
            
            # Cargar logo si existe
            if config.logo_base64:
                self.logo_base64 = config.logo_base64
                self.logo_filename = config.logo_filename
                self.logo_preview = f"data:image/png;base64,{config.logo_base64}"

    def cargar_parametros(self):
        """Carga la lista de parámetros."""
        servicio = ServicioConfiguracion(db_manager)
        self.parametros = servicio.listar_parametros()

    def set_empresa_field(self, field: str, value: str):
        """Actualiza un campo específico de la empresa."""
        self.empresa[field] = value
    
    async def handle_upload_logo(self, files: list[rx.UploadFile]):
        """Maneja la subida del logo."""
        if not files:
            return rx.toast.error("No se seleccionó ningún archivo")
        
        file = files[0]
        
        # Validar tipo de archivo
        valid_types = ["image/png", "image/jpeg", "image/jpg"]
        if file.content_type not in valid_types:
            return rx.toast.error("Tipo de archivo no válido. Use PNG o JPG.")
        
        # Leer contenido
        import base64
        content = await file.read()
        
        # Validar tamaño (máximo 1MB)
        if len(content) > 1024 * 1024:
            return rx.toast.error("El archivo es demasiado grande (máximo 1MB)")
        
        # Convertir a base64
        self.logo_base64 = base64.b64encode(content).decode('utf-8')
        self.logo_filename = file.filename
        self.logo_preview = f"data:{file.content_type};base64,{self.logo_base64}"
        
        return rx.toast.success(f"Logo cargado: {file.filename}")
    
    def clear_logo(self):
        """Limpia el logo actual."""
        self.logo_base64 = ""
        self.logo_filename = ""
        self.logo_preview = ""
        return rx.toast.info("Logo eliminado. No olvides guardar los cambios.")

    def guardar_empresa_click(self):
        """Guarda los cambios en la configuración de la empresa usando el estado actual."""
        try:
            servicio = ServicioConfiguracion(db_manager)
            
            # Combine social media fields into JSON
            redes_dict = {
                "facebook": self.empresa.get("facebook", ""),
                "instagram": self.empresa.get("instagram", ""),
                "tiktok": self.empresa.get("tiktok", "")
            }
            
            nueva_config = ConfiguracionEmpresa(
                nombre_empresa=self.empresa.get("nombre_empresa", ""),
                nit=self.empresa.get("nit", ""),
                representante_legal=self.empresa.get("representante_legal", ""),
                cedula_representante=self.empresa.get("cedula_representante", ""),
                email=self.empresa.get("email", ""),
                telefono=self.empresa.get("telefono", ""),
                direccion=self.empresa.get("direccion", ""),
                ubicacion=self.empresa.get("ubicacion", ""),
                website=self.empresa.get("website", ""),
                logo_base64=self.logo_base64,
                logo_filename=self.logo_filename
            )
            nueva_config.set_redes_sociales_from_dict(redes_dict)
            
            servicio.guardar_configuracion_empresa(nueva_config, "USUARIO_WEB")
            
            # Recargar estado
            self.cargar_datos_empresa()
            return rx.toast.success("Información de empresa actualizada correctamente.")
            
        except Exception as e:
            return rx.toast.error(f"Error al guardar: {str(e)}")

    def actualizar_parametro(self, id_parametro: int, nuevo_valor: str):
        """Actualiza un parámetro del sistema."""
        try:
            servicio = ServicioConfiguracion(db_manager)
            servicio.actualizar_parametro(id_parametro, nuevo_valor, "USUARIO_WEB")
            self.cargar_parametros()
            return rx.toast.success("Parámetro actualizado.")
        except Exception as e:
            return rx.toast.error(f"Error al actualizar parámetro: {str(e)}")
