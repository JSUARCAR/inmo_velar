from typing import Any, Dict, List, Optional

import reflex as rx

from src.aplicacion.servicios.servicio_autenticacion import ServicioAutenticacion
from src.aplicacion.servicios.servicio_permisos import ServicioPermisos
from src.dominio.excepciones.excepciones_base import (
    ErrorAutenticacion,
    ExcepcionDominio,
    SesionInvalida,
)
from src.infraestructura.logging.logger import logger
from src.infraestructura.persistencia.database import db_manager
from src.infraestructura.persistencia.repositorio_sesion_sqlite import (
    RepositorioSesionSQLite,
)
from src.infraestructura.persistencia.repositorio_usuario_sqlite import (
    RepositorioUsuarioSQLite,
)


class AuthState(rx.State):
    """
    Estado de Autenticación Global.
    Maneja la sesión del usuario, login y logout.
    """

    # Token de Sesión (Persistente)
    # En producción cambiar secure=True
    session_token: str = rx.Cookie(name="session_token", secure=False)

    # Legacy: user cookie removed
    # user: str = rx.Cookie(name="user_data", secure=False)

    # In-memory parsed user data for easier access
    _user_data: Optional[Dict[str, Any]] = None

    allowed_modules: List[str] = []  # Lista de módulos que el usuario puede VER
    permissions_map: Dict[str, List[str]] = {}  # Mapa {Modulo: [Lista de Acciones]}

    # Estado de UX
    is_loading: bool = False
    error_message: str = ""

    @rx.var(cache=False)
    def user_info(self) -> Optional[Dict[str, Any]]:
        """Recupera la información del usuario validando el token de sesión."""
        if self._user_data:
            return self._user_data

        if self.session_token:
            try:
                # Validar token contra BD
                repo_u = RepositorioUsuarioSQLite(db_manager)
                repo_s = RepositorioSesionSQLite(db_manager)
                servicio_auth = ServicioAutenticacion(repo_u, repo_s)
                usuario = servicio_auth.validar_sesion(self.session_token)

                user_dict = {
                    "id_usuario": usuario.id_usuario,
                    "nombre_usuario": usuario.nombre_usuario,
                    "rol": usuario.rol,
                    "ultimo_acceso": usuario.ultimo_acceso,
                }
                self._user_data = user_dict
                return user_dict
            except SesionInvalida:
                self.session_token = ""
                return None
            except Exception as e:
                logger.error("Error validando sesión en AuthState", error=e)
                try:
                    db_manager.obtener_conexion().rollback()
                except Exception:
                    pass
                return None
        return None

    @rx.var(cache=True)
    def is_authenticated(self) -> bool:
        """Verifica si hay un usuario autenticado."""
        return self.user_info is not None

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
            # Inicializar servicio con repositorios inyectados
            repo_u = RepositorioUsuarioSQLite(db_manager)
            repo_s = RepositorioSesionSQLite(db_manager)
            servicio_auth = ServicioAutenticacion(repo_u, repo_s)

            # Autenticar
            usuario_autenticado = servicio_auth.autenticar(username, password)

            # Crear sesión persistente
            sesion = servicio_auth.crear_sesion(usuario_autenticado)

            # Guardar token en cookie
            self.session_token = sesion.token_sesion

            # Cache local para esta ejecución
            user_dict = {
                "id_usuario": usuario_autenticado.id_usuario,
                "nombre_usuario": usuario_autenticado.nombre_usuario,
                "rol": usuario_autenticado.rol,
                "ultimo_acceso": usuario_autenticado.ultimo_acceso,
            }
            self._user_data = user_dict

            # Cargar permisos y módulos permitidos
            self._sync_permissions(usuario_autenticado.rol)

            self.error_message = ""

            # Redirigir al dashboard
            return rx.redirect("/dashboard")

        except ErrorAutenticacion as e:
            self.error_message = str(e)
        except ExcepcionDominio as e:
            self.error_message = f"Error de negocio: {str(e)}"
        except Exception as e:
            import sys
            import traceback
            error_trace = traceback.format_exc()
            print(f"LOGIN ERROR: {str(e)}", file=sys.stderr)
            print(f"TRACEBACK: {error_trace}", file=sys.stderr)
            print(f"TRACEBACK: {error_trace}", file=sys.stderr)
            logger.error("Error inesperado en login", error=e)
            try:
                db_manager.obtener_conexion().rollback()
            except Exception:
                pass
            self.error_message = "Ocurrió un error inesperado. Intente de nuevo."
        finally:
            self.is_loading = False

    def logout(self):
        """Cierra la sesión del usuario."""
        self.session_token = ""  # Clear cookie
        self._user_data = None
        self.allowed_modules = []
        self.permissions_map = {}
        return rx.redirect("/login")

    @classmethod
    def check_module_access(cls, module_name: str) -> rx.Var:
        """Verifica si el usuario tiene acceso a un módulo (Frontend safe)."""
        # Admin siempre tiene acceso
        # Access the computed user_info var
        is_admin = cls.user_info["rol"] == "Administrador"
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
        is_admin = cls.user_info["rol"] == "Administrador"

        # Verificar si el módulo existe y si la acción está permitida
        # Usamos lógica booleana de Vars: (Existe Modulo) AND (Existe Accion en Modulo)
        # cls.permissions_map[module_name] retorna un Var (lista) si existe

        module_exists = cls.permissions_map.contains(module_name)

        # Para evitar error JS si el modulo no existe (undefined.includes...), usamos short-circuit AND (&)
        # Nota: Reflex evalúa '&' como logic AND en JS si son vars

        action_allowed = cls.permissions_map[module_name].contains(action)

        return is_admin | (module_exists & action_allowed)

    def _sync_permissions(self, rol: str = None):
        """Recarga los permisos del usuario desde la base de datos."""
        try:
            target_rol = rol or (self.user_info["rol"] if self.user_info else None)
            if not target_rol:
                return

            servicio_permisos = ServicioPermisos(db_manager)
            permisos = servicio_permisos.obtener_permisos_rol(target_rol)

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
        except Exception:
            pass  # print(f"Error syncing permissions: {e}") [OpSec Removed]

    def require_login(self):
        """Protector de rutas. Redirige a login si no está autenticado."""
        if not self.is_authenticated:
            return rx.redirect("/login")

        # Sincronizar permisos si el estado está vacío (ej. después de un F5)
        if not self.allowed_modules and self.user_info:
            self._sync_permissions()
