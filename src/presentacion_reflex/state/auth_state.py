import reflex as rx
from typing import Optional, Dict, Any, List
from src.dominio.entidades.usuario import Usuario
from src.infraestructura.persistencia.database import db_manager
from src.aplicacion.servicios.servicio_autenticacion import ServicioAutenticacion
from src.aplicacion.servicios.servicio_permisos import ServicioPermisos

class AuthState(rx.State):
    """
    Estado de Autenticación Global.
    Maneja la sesión del usuario, login y logout.
    """
    
    # Usuario autenticado
    # Usuario autenticado
    user: Optional[Dict[str, Any]] = None
    allowed_modules: List[str] = []  # Lista de módulos que el usuario puede VER
    permissions_map: Dict[str, List[str]] = {} # Mapa {Modulo: [Lista de Acciones]}
    
    # Estado de UX
    is_loading: bool = False
    error_message: str = ""
    
    @rx.var(cache=True)
    def is_authenticated(self) -> bool:
        """Verifica si hay un usuario autenticado."""
        return self.user is not None

    def login(self, form_data: dict):
        """
        Procesa el inicio de sesión.
        
        Args:
            form_data: Diccionario con 'username' y 'password'
        """
        self.is_loading = True
        self.error_message = ""
        
        username = form_data.get("username")
        password = form_data.get("password")
        
        if not username or not password:
            self.error_message = "Por favor ingrese usuario y contraseña."
            self.is_loading = False
            return
            
        try:
            # Inicializar servicio (DB Manager ya está configurado globalmente)
            servicio_auth = ServicioAutenticacion(db_manager)
            
            # Autenticar
            usuario_autenticado = servicio_auth.autenticar(username, password)
            
            if usuario_autenticado:
                # Serializar usuario para el estado
                self.user = {
                    "id_usuario": usuario_autenticado.id_usuario,
                    "nombre_usuario": usuario_autenticado.nombre_usuario,
                    "rol": usuario_autenticado.rol,
                    "ultimo_acceso": usuario_autenticado.ultimo_acceso,
                }
                # Cargar permisos del usuario
                servicio_permisos = ServicioPermisos(db_manager)
                permisos = servicio_permisos.obtener_permisos_rol(usuario_autenticado.rol)
                
                # Construir mapa de permisos granular {Modulo: [Acciones]}
                permits_map = {}
                allowed_mods = set()
                
                for p in permisos:
                    if p.modulo not in permits_map:
                        permits_map[p.modulo] = []
                    permits_map[p.modulo].append(p.accion)
                    
                    if p.accion == "VER":
                        allowed_mods.add(p.modulo)
                
                self.permissions_map = permits_map
                self.allowed_modules = list(allowed_mods)
                
                # Si es Admin, asegurar que tiene acceso a todo (aunque el servicio lo haga, un fallback)
                if usuario_autenticado.rol == "Administrador":
                     # Hardcoded list of all known modules if dynamic fetch fails or for safety
                     pass # Service already returns all permissions for Admin
                
                self.error_message = ""
                # Redirigir al dashboard
                return rx.redirect("/")
            else:
                self.error_message = "Credenciales incorrectas o usuario inactivo."
                
        except Exception as e:
            print(f"Error login reflex: {e}")
            self.error_message = f"Error del sistema: {str(e)}"
        finally:
            self.is_loading = False

    def logout(self):
        """Cierra la sesión del usuario."""
        self.user = None
        self.allowed_modules = []
        self.permissions_map = {}
        return rx.redirect("/login")
    
    @classmethod
    def check_module_access(cls, module_name: str) -> rx.Var:
        """Verifica si el usuario tiene acceso a un módulo (Frontend safe)."""
        # Admin siempre tiene acceso
        is_admin = cls.user["rol"] == "Administrador"
        # Verificar en lista de permitidos
        has_access = cls.allowed_modules.contains(module_name)
        
        return is_admin | has_access
    
    @classmethod
    def check_action(cls, module_name: str, action: str) -> rx.Var:
        """
        Verifica si el usuario tiene permiso para una acción específica en un módulo.
        Retorna un rx.Var booleano compatible con rx.cond().
        """
        # Admin siempre tiene acceso
        is_admin = cls.user["rol"] == "Administrador"
            
        # Verificar si el módulo existe y si la acción está permitida
        # Usamos lógica booleana de Vars: (Existe Modulo) AND (Existe Accion en Modulo)
        # cls.permissions_map[module_name] retorna un Var (lista) si existe
        
        module_exists = cls.permissions_map.contains(module_name)
        
        # Para evitar error JS si el modulo no existe (undefined.includes...), usamos short-circuit AND (&)
        # Nota: Reflex evalúa '&' como logic AND en JS si son vars
        
        action_allowed = cls.permissions_map[module_name].contains(action)
        
        return is_admin | (module_exists & action_allowed)

    def require_login(self):
        """Protector de rutas. Redirige a login si no está autenticado."""
        if not self.is_authenticated:
            return rx.redirect("/login")
