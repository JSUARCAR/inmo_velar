from typing import Dict, List, Optional

from src.aplicacion.servicios.servicio_autenticacion import ServicioAutenticacion
from src.dominio.entidades.usuario import Usuario
from src.infraestructura.persistencia.database import DatabaseManager
from src.infraestructura.persistencia.repositorio_usuario_sqlite import RepositorioUsuarioSQLite


class ServicioUsuarios:
    """
    Servicio para la gestión administrativa de usuarios (CRUD).
    """

    def __init__(
        self, db_manager: DatabaseManager, auth_service: Optional[ServicioAutenticacion] = None
    ):
        self.db = db_manager
        self.repo = RepositorioUsuarioSQLite(db_manager)

        if auth_service:
            self.auth_service = auth_service
        else:
            from src.infraestructura.persistencia.repositorio_sesion_sqlite import (
                RepositorioSesionSQLite,
            )

            repo_sesion = RepositorioSesionSQLite(db_manager)
            self.auth_service = ServicioAutenticacion(self.repo, repo_sesion)

    def listar_usuarios(self) -> List[Usuario]:
        """Obtiene todos los usuarios registrados."""
        return self.repo.listar_todos()

    def obtener_usuario(self, id_usuario: int) -> Optional[Usuario]:
        """Obtiene un usuario por ID."""
        return self.repo.obtener_por_id(id_usuario)

    def crear_usuario(
        self, nombre_usuario: str, contrasena: str, rol: str, creador: str
    ) -> Usuario:
        """
        Crea un nuevo usuario usando la lógica de hasheo segura.
        Delega en ServicioAutenticacion para garantizar consistencia en hashes.
        """
        if self.repo.obtener_por_nombre(nombre_usuario):
            raise ValueError(f"El usuario '{nombre_usuario}' ya existe.")

        return self.auth_service.crear_usuario(nombre_usuario, contrasena, rol, creador)

    def actualizar_usuario(self, id_usuario: int, datos: Dict, editor: str) -> bool:
        """
        Actualiza datos del usuario (Rol, Estado).
        NO actualiza contraseña aquí (usar metodo especifico).
        """
        usuario = self.repo.obtener_por_id(id_usuario)
        if not usuario:
            raise ValueError("Usuario no encontrado")

        if "rol" in datos:
            usuario.rol = datos["rol"]

        if "estado_usuario" in datos:
            # Convertir a boolean si es necesario
            if isinstance(datos["estado_usuario"], bool):
                usuario.estado_usuario = datos["estado_usuario"]
            else:
                usuario.estado_usuario = bool(datos["estado_usuario"])

        return self.repo.actualizar(usuario, editor)

    def cambiar_estado(self, id_usuario: int, activo: bool, editor: str) -> bool:
        """Activa o desactiva un usuario."""
        usuario = self.repo.obtener_por_id(id_usuario)
        if not usuario:
            raise ValueError("Usuario no encontrado")

        # Usar directamente el valor boolean
        usuario.estado_usuario = activo
        return self.repo.actualizar(usuario, editor)

    def restablecer_contrasena(self, id_usuario: int, nueva_contrasena: str, editor: str) -> bool:
        """Restablece la contraseña de un usuario (Admin action)."""
        usuario = self.repo.obtener_por_id(id_usuario)
        if not usuario:
            raise ValueError("Usuario no encontrado")

        # Reutilizamos lógica de validación y hash de auth_service
        # Corrección: hashear_contraseña devuelve string (hash bcrypt), no tupla.
        if len(nueva_contrasena) < 6:
            raise ValueError("La contraseña debe tener al menos 6 caracteres")

        from src.infraestructura.logging.logger import logger
        try:
            # Debugging: Ensure hashear_contraseña returns string
            nuevo_hash = self.auth_service.hashear_contraseña(nueva_contrasena)
            
            # If accidentally returned tuple (hash, salt), this log will reveal it
            if not isinstance(nuevo_hash, str):
                logger.error(f"CRITICAL: hashear_contraseña returned {type(nuevo_hash)}: {nuevo_hash}")
                # Fallback if it is a tuple (just in case of weird environment)
                if isinstance(nuevo_hash, tuple):
                    nuevo_hash = nuevo_hash[0]

            usuario.contrasena_hash = nuevo_hash

        except Exception as e:
            logger.error(f"Error hashing password in restablecer_contrasena: {e}")
            raise e

        return self.repo.actualizar(usuario, editor)
