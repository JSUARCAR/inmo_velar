"""
Servicio de Aplicación: Autenticación de Usuarios.
Implementa lógica de autenticación, hash de contraseñas y gestión de sesiones.
"""

import hashlib
import secrets
from datetime import datetime
from typing import Optional

import bcrypt

from src.aplicacion.esquemas import CambioPassword, UsuarioCreate
from src.dominio.entidades.sesion_usuario import SesionUsuario
from src.dominio.entidades.usuario import Usuario
from src.dominio.excepciones.excepciones_base import (
    ErrorAutenticacion,
    ErrorValidacion,
    SesionInvalida,
)
from src.dominio.repositorios.interfaces import RepositorioSesion, RepositorioUsuario
from src.infraestructura.logging.logger import logger


class ServicioAutenticacion:
    """
    Servicio de autenticación de usuarios.
    Maneja login, logout, hash de contraseñas y sesiones.
    """

    def __init__(self, repo_usuario: RepositorioUsuario, repo_sesion: RepositorioSesion):
        self.repo_usuario = repo_usuario
        self.repo_sesion = repo_sesion

    @staticmethod
    def hashear_contraseña(contraseña_plana: str) -> str:
        """
        Hashea una contraseña usando Bcrypt.

        Args:
            contraseña_plana: Contraseña en texto plano

        Returns:
            Hash Bcrypt (incluye salt)
        """
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(contraseña_plana.encode("utf-8"), salt)
        return hashed.decode("utf-8")

    def verificar_contraseña(self, contraseña_plana: str, contraseña_hash: str) -> bool:
        """
        Verifica si una contraseña plana coincide con el hash almacenado.
        Soporta migración transparente de SHA256 a Bcrypt.
        """
        try:
            # Intentar verificar como Bcrypt
            return bcrypt.checkpw(contraseña_plana.encode("utf-8"), contraseña_hash.encode("utf-8"))
        except ValueError:
            # Fallback a SHA256 (Legacy)
            # Asumimos que el hash SHA256 almacenado no tiene salt o es hash simple
            hash_sha256 = hashlib.sha256(contraseña_plana.encode("utf-8")).hexdigest()
            return hash_sha256 == contraseña_hash

    def autenticar(self, nombre_usuario: str, contraseña: str) -> Usuario:
        """
        Autentica un usuario.

        Args:
            nombre_usuario: Nombre de usuario
            contraseña: Contraseña en texto plano

        Returns:
            Usuario si la autenticación es exitosa

        Raises:
            ErrorAutenticacion: si las credenciales son inválidas o el usuario no existe
        """
        # Obtener usuario
        usuario = self.repo_usuario.obtener_por_nombre(nombre_usuario)

        if not usuario:
            logger.warning("Intento de login fallido: usuario no encontrado", user=nombre_usuario)
            raise ErrorAutenticacion("Usuario o contraseña incorrectos")

        # Verificar que esté activo
        if not usuario.es_activo():
            logger.warning("Intento de login fallido: usuario inactivo", user=nombre_usuario)
            raise ErrorAutenticacion("El usuario se encuentra inactivo")

        # Verificar contraseña (automigración incluida)
        es_valida = self.verificar_contraseña(contraseña, usuario.contrasena_hash)

        if es_valida:
            # Si el hash era SHA256 (no empieza con $2b$), actualizar a Bcrypt
            if not usuario.contrasena_hash.startswith("$2b$"):
                nuevo_hash = self.hashear_contraseña(contraseña)
                usuario.contrasena_hash = nuevo_hash
                # Guardar actualización de hash
                self.repo_usuario.actualizar(usuario, nombre_usuario)
                logger.info("Hash de contraseña actualizado a Bcrypt", user=nombre_usuario)

            # Actualizar último acceso
            usuario.ultimo_acceso = datetime.now().isoformat()
            self.repo_usuario.actualizar(usuario, nombre_usuario)
            logger.info("Usuario autenticado exitosamente", user=nombre_usuario)
            return usuario

        logger.warning("Intento de login fallido: contraseña incorrecta", user=nombre_usuario)
        raise ErrorAutenticacion("Usuario o contraseña incorrectos")

    def crear_sesion(self, usuario: Usuario) -> SesionUsuario:
        """
        Crea una nueva sesión para un usuario autenticado.

        Args:
            usuario: Usuario autenticado

        Returns:
            Sesión creada
        """
        sesion = SesionUsuario(
            id_usuario=usuario.id_usuario,
            fecha_inicio=datetime.now().isoformat(),
            token_sesion=secrets.token_urlsafe(32),
        )

        # Guardar en BD
        return self.repo_sesion.guardar(sesion)

    def validar_sesion(self, token_sesion: str) -> Usuario:
        """
        Valida un token de sesión y retorna el usuario asociado.

        Args:
            token_sesion: Token de la cookie

        Returns:
            Usuario si corresponde a una sesión válida

        Raises:
            SesionInvalida: si el token no es válido o la sesión expiró
        """
        sesion = self.repo_sesion.obtener_por_token(token_sesion)

        if not sesion:
            raise SesionInvalida("Token de sesión no encontrado")

        # Verificar si está finalizada (active check)
        if not sesion.esta_activa():
            logger.warning("Intento de uso de sesión inactiva", token=token_sesion)
            raise SesionInvalida("La sesión ha finalizado")

        usuario = self.repo_usuario.obtener_por_id(sesion.id_usuario)
        if not usuario:
            raise SesionInvalida("Usuario de sesión no encontrado")

        return usuario

    def cambiar_contraseña(
        self, usuario: Usuario, contraseña_actual: str, contraseña_nueva: str
    ) -> bool:
        """
        Cambia la contraseña de un usuario.

        Args:
            usuario: Usuario
            contraseña_actual: Contraseña actual
            contraseña_nueva: Nueva contraseña

        Returns:
            True si se cambió exitosamente
        """
        # Validar usando Esquema Pydantic
        datos = CambioPassword(
            password_actual=contraseña_actual, password_nueva=contraseña_nueva
        )

        # Verificar contraseña actual
        if not self.verificar_contraseña(datos.password_actual, usuario.contrasena_hash):
            return False

        # Hashear nueva contraseña
        nuevo_hash = self.hashear_contraseña(datos.password_nueva)
        usuario.contrasena_hash = nuevo_hash

        # Actualizar en BD
        return self.repo_usuario.actualizar(usuario, usuario.nombre_usuario)

    def crear_usuario(
        self, nombre_usuario: str, contraseña: str, rol: str, usuario_sistema: str
    ) -> Usuario:
        """
        Crea un nuevo usuario con contraseña hasheada.

        Args:
            nombre_usuario: Nombre de usuario único
            contraseña: Contraseña en texto plano
            rol: Rol del sistema
            usuario_sistema: Usuario que ejecuta la operación

        Returns:
            Usuario creado
        """
        # Validar usando Esquema Pydantic
        datos = UsuarioCreate(
            nombre_usuario=nombre_usuario,
            contraseña=contraseña,
            rol=rol,
            usuario_sistema=usuario_sistema,
        )

        # Hashear contraseña
        contraseña_hash = self.hashear_contraseña(datos.contraseña)

        # Crear usuario
        usuario = Usuario(
            nombre_usuario=datos.nombre_usuario,
            contrasena_hash=contraseña_hash,
            rol=datos.rol,
            estado_usuario=True,
            fecha_creacion=datetime.now().isoformat(),
        )

        return self.repo_usuario.crear(usuario, datos.usuario_sistema)
