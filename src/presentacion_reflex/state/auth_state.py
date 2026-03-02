import sys
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

# ─── Constante de versión para confirmar que el nuevo código se ejecuta ───────
_AUTH_STATE_VERSION = "2026-02-25-v3-DEBUG"


def _debug(msg: str, **kwargs):
    """Imprime un mensaje de debug con prefijo claro a stderr."""
    extra = " | ".join(f"{k}={v!r}" for k, v in kwargs.items())
    line = f"[AUTH_DEBUG] {msg}" + (f" | {extra}" if extra else "")
    print(line, file=sys.stderr, flush=True)


class AuthState(rx.State):
    """
    Estado de Autenticación Global.
    Maneja la sesión del usuario, login y logout.

    VERSION: 2026-02-25-v3-DEBUG
    CAMBIOS CLAVE vs v2:
      - user_info ya NO es @rx.var — es un campo de estado normal (_user_data).
      - La validación del token se hace SÓLO en event handlers (require_login,
        redirect_to_dashboard, _validate_session), nunca en una computed var.
      - Esto elimina la mutación de estado dentro de @rx.var que causaba el
        comportamiento indefinido en Reflex.
      - Se agrega logging diagnóstico detallado para confirmar el flujo real.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _debug("AuthState.__init__", version=_AUTH_STATE_VERSION)

    # ── Variables de Estado ────────────────────────────────────────────────────

    # Token de Sesión (Persistente en Cookie)
    session_token: str = rx.Cookie(name="session_token", secure=False)

    # Datos del usuario autenticado (se llenan en event handlers, no en vars)
    _user_data: Optional[Dict[str, Any]] = None

    # Info pública del usuario (campos individuales para evitar problemas de var)
    user_nombre: str = ""
    user_rol: str = ""
    user_id: int = 0
    is_authenticated: bool = False

    allowed_modules: List[str] = []
    permissions_map: Dict[str, List[str]] = {}

    # Estado de UX
    is_loading: bool = False
    error_message: str = ""

    # ── Computed Vars (sin efectos secundarios) ────────────────────────────────

    # @rx.var
    # def user_info(self) -> Optional[Dict[str, Any]]:
    #     """Retorna los datos del usuario en memoria (SIN tocar la BD, SIN mutar estado)."""
    #     return self._user_data

    # ── Event Handlers ─────────────────────────────────────────────────────────

    def _validate_session(self) -> bool:
        """
        Valida el session_token contra la BD y actualiza el estado interno.
        Retorna True si la sesión es válida, False en caso contrario.
        Debe llamarse SÓLO desde event handlers.
        """
        _debug(
            "_validate_session START",
            token_present=bool(self.session_token),
            token_prefix=self.session_token[:8] if self.session_token else "N/A",
            user_data_cached=bool(self._user_data),
        )

        # Si ya tenemos datos en memoria, confiar en ellos
        if self._user_data and self.is_authenticated:
            _debug("_validate_session → HIT CACHE, usuario ya autenticado")
            return True

        # Sin token = sin sesión
        if not self.session_token:
            _debug("_validate_session → NO TOKEN, sesión inválida")
            self._user_data = None
            self.is_authenticated = False
            self.user_nombre = ""
            self.user_rol = ""
            self.user_id = 0
            return False

        # Validar contra BD
        try:
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
            self.is_authenticated = True
            self.user_nombre = usuario.nombre_usuario
            self.user_rol = usuario.rol
            self.user_id = usuario.id_usuario

            _debug(
                "_validate_session → BD OK",
                usuario=usuario.nombre_usuario,
                rol=usuario.rol,
            )
            return True

        except SesionInvalida as e:
            _debug("_validate_session → SESIÓN INVÁLIDA (BD)", error=str(e))
            self.session_token = ""
            self._user_data = None
            self.is_authenticated = False
            self.user_nombre = ""
            self.user_rol = ""
            self.user_id = 0
            return False

        except Exception as e:
            import traceback
            _debug("_validate_session → EXCEPCIÓN INESPERADA", error=str(e))
            traceback.print_exc(file=sys.stderr)
            try:
                db_manager.obtener_conexion().rollback()
            except Exception:
                pass
            # En caso de error de BD transitorio, NO invalidar sesión —
            # retornar False solo para esta llamada sin borrar el token
            return False

    def require_login(self):
        """
        Protector de rutas. Se ejecuta en on_load de páginas protegidas.
        Valida la sesión; si no es válida, redirige a /login.
        """
        import threading
        _debug(
            "require_login CALLED",
            route=getattr(self.router, "page", {}).path if hasattr(self, "router") else "unknown",
            thread=threading.current_thread().name,
            token_present=bool(self.session_token),
        )

        valid = self._validate_session()

        _debug("require_login → valid=%s" % valid)

        if not valid:
            _debug("require_login → REDIRECT a /login")
            return rx.redirect("/login")

        _debug("require_login → ACCESO PERMITIDO")
        # Sincronizar permisos si están vacíos (F5 reinicia el estado en memoria)
        if not self.allowed_modules:
            _debug("require_login → sincronizando permisos")
            self._sync_permissions()

    def redirect_to_dashboard(self):
        """
        Usado por la página raíz '/'.
        Redirige a /dashboard si autenticado, o a /login si no.
        """
        _debug(
            "redirect_to_dashboard CALLED",
            token_present=bool(self.session_token),
        )
        valid = self._validate_session()
        _debug("redirect_to_dashboard → valid=%s" % valid)

        if valid:
            _debug("redirect_to_dashboard → REDIRECT a /dashboard")
            return rx.redirect("/dashboard")

        _debug("redirect_to_dashboard → REDIRECT a /login")
        return rx.redirect("/login")

    def login(self, form_data: dict):
        """Procesa el inicio de sesión."""
        _debug("login CALLED", username=form_data.get("username"))
        self.is_loading = True
        self.error_message = ""

        username = form_data.get("username")
        password = form_data.get("password")

        if not username or not password:
            self.error_message = "Por favor ingrese usuario y contraseña."
            self.is_loading = False
            return

        try:
            repo_u = RepositorioUsuarioSQLite(db_manager)
            repo_s = RepositorioSesionSQLite(db_manager)
            servicio_auth = ServicioAutenticacion(repo_u, repo_s)

            usuario_autenticado = servicio_auth.autenticar(username, password)
            sesion = servicio_auth.crear_sesion(usuario_autenticado)

            # Guardar token en cookie
            self.session_token = sesion.token_sesion

            # Llenar estado en memoria
            user_dict = {
                "id_usuario": usuario_autenticado.id_usuario,
                "nombre_usuario": usuario_autenticado.nombre_usuario,
                "rol": usuario_autenticado.rol,
                "ultimo_acceso": usuario_autenticado.ultimo_acceso,
            }
            self._user_data = user_dict
            self.is_authenticated = True
            self.user_nombre = usuario_autenticado.nombre_usuario
            self.user_rol = usuario_autenticado.rol
            self.user_id = usuario_autenticado.id_usuario

            # Cargar permisos
            self._sync_permissions(usuario_autenticado.rol)
            self.error_message = ""

            _debug("login → ÉXITO, redirigiendo a /dashboard", usuario=username)
            return rx.redirect("/dashboard")

        except ErrorAutenticacion as e:
            _debug("login → ERROR_AUTH", error=str(e))
            self.error_message = str(e)
        except ExcepcionDominio as e:
            self.error_message = f"Error de negocio: {str(e)}"
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            _debug("login → EXCEPCIÓN", error=str(e))
            print(f"LOGIN ERROR: {str(e)}", file=sys.stderr)
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
        _debug("logout CALLED")
        self.session_token = ""
        self._user_data = None
        self.is_authenticated = False
        self.user_nombre = ""
        self.user_rol = ""
        self.user_id = 0
        self.allowed_modules = []
        self.permissions_map = {}
        return rx.redirect("/login")

    @classmethod
    def check_module_access(cls, module_name: str) -> rx.Var:
        """Verifica si el usuario tiene acceso a un módulo (Frontend safe)."""
        return rx.cond(
            cls.user_rol == "Administrador",
            True,
            cls.allowed_modules.contains(module_name)
        )

    @classmethod
    def check_action(cls, module_name: str, action: str) -> rx.Var:
        """
        Verifica si el usuario tiene permiso para una acción específica en un módulo.
        Retorna un rx.Var booleano compatible con rx.cond().
        """
        # Usar rx.cond y manejo seguro para evitar VarAttributeError durante la compilación
        is_admin = (cls.user_rol == "Administrador")
        
        # Comprobar si el módulo existe primero
        module_exists = cls.permissions_map.contains(module_name)
        
        # Obtener la lista de acciones de forma segura. 
        # Si el módulo existe, comprobar la acción. Si no, False.
        return rx.cond(
            is_admin,
            True,
            rx.cond(
                module_exists,
                cls.permissions_map[module_name].contains(action),
                False
            )
        )

    def _sync_permissions(self, rol: str = None):
        """Recarga los permisos del usuario desde la base de datos."""
        try:
            target_rol = rol or self.user_rol or None
            if not target_rol:
                _debug("_sync_permissions → sin rol, abortando")
                return

            _debug("_sync_permissions START", rol=target_rol)
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
            _debug(
                "_sync_permissions OK",
                modulos_count=len(allowed_mods),
            )
        except Exception as e:
            _debug("_sync_permissions → ERROR", error=str(e))
