"""
Servicio de Aplicación: Autenticación de Usuarios.
Implementa lógica de autenticación, hash de contraseñas y gestión de sesiones.
"""

import hashlib
import secrets
import bcrypt
from typing import Optional, Tuple
from datetime import datetime

from src.dominio.entidades.usuario import Usuario
from src.dominio.entidades.sesion_usuario import SesionUsuario
from src.infraestructura.persistencia.repositorio_usuario_sqlite import RepositorioUsuarioSQLite
from src.infraestructura.persistencia.repositorio_sesion_sqlite import RepositorioSesionSQLite
from src.infraestructura.persistencia.database import DatabaseManager


class ServicioAutenticacion:
    """
    Servicio de autenticación de usuarios.
    Maneja login, logout, hash de contraseñas y sesiones.
    """
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.repo_usuario = RepositorioUsuarioSQLite(db_manager)
        self.repo_sesion = RepositorioSesionSQLite(db_manager)
    
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
        hashed = bcrypt.hashpw(contraseña_plana.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verificar_contraseña(self, contraseña_plana: str, contraseña_hash: str) -> bool:
        """
        Verifica si una contraseña plana coincide con el hash almacenado.
        Soporta migración transparente de SHA256 a Bcrypt.
        """
        try:
            # Intentar verificar como Bcrypt
            return bcrypt.checkpw(contraseña_plana.encode('utf-8'), contraseña_hash.encode('utf-8'))
        except ValueError:
            # Fallback a SHA256 (Legacy)
            # Asumimos que el hash SHA256 almacenado no tiene salt o es hash simple
            hash_sha256 = hashlib.sha256(contraseña_plana.encode('utf-8')).hexdigest()
            return hash_sha256 == contraseña_hash
    

    
    def autenticar(self, nombre_usuario: str, contraseña: str) -> Optional[Usuario]:
        """
        Autentica un usuario.
        
        Args:
            nombre_usuario: Nombre de usuario
            contraseña: Contraseña en texto plano
            
        Returns:
            Usuario si la autenticación es exitosa, None si falla
        """
        # Obtener usuario
        usuario = self.repo_usuario.obtener_por_nombre(nombre_usuario)
        
        if not usuario:
            return None
        
        # Verificar que esté activo
        if not usuario.es_activo():
            return None
        
        # Verificar contraseña (automigración incluida)
        es_valida = self.verificar_contraseña(contraseña, usuario.contrasena_hash)
        
        if es_valida:
            # Si el hash era SHA256 (no empieza con $2b$), actualizar a Bcrypt
            if not usuario.contrasena_hash.startswith('$2b$'):
                nuevo_hash = self.hashear_contraseña(contraseña)
                usuario.contrasena_hash = nuevo_hash
                # Guardar actualización de hash
                self.repo_usuario.actualizar(usuario, nombre_usuario)

            # Actualizar último acceso
            usuario.ultimo_acceso = datetime.now().isoformat()
            self.repo_usuario.actualizar(usuario, nombre_usuario)
            return usuario
        
        return None
    
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
            token_sesion=secrets.token_urlsafe(32)
        )
        
        # Guardar en BD
        return self.repo_sesion.guardar(sesion)
    
    def validar_sesion(self, token_sesion: str) -> Optional[Usuario]:
        """
        Valida un token de sesión y retorna el usuario asociado.
        
        Args:
            token_sesion: Token de la cookie
            
        Returns:
            Usuario sicorresponde a una sesión válida
        """
        sesion = self.repo_sesion.obtener_por_token(token_sesion)
        
        if not sesion:
            return None
            
        # Verificar si está finalizada (active check)
        if not sesion.esta_activa():
            return None
            
        # (Opcional) Verificar timeout aquí si tuviéramos TTL
        
        return self.repo_usuario.obtener_por_id(sesion.id_usuario)
    
    def cambiar_contraseña(
        self,
        usuario: Usuario,
        contraseña_actual: str,
        contraseña_nueva: str
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
        # Verificar contraseña actual
        if not self.verificar_contraseña(contraseña_actual, usuario.contrasena_hash):
            return False
        
        # Validar nueva contraseña
        if len(contraseña_nueva) < 8:
            raise ValueError("La nueva contraseña debe tener al menos 8 caracteres")
        
        # Hashear nueva contraseña
        nuevo_hash = self.hashear_contraseña(contraseña_nueva)
        usuario.contrasena_hash = nuevo_hash
        
        # Actualizar en BD
        return self.repo_usuario.actualizar(usuario, usuario.nombre_usuario)
    
    def crear_usuario(
        self,
        nombre_usuario: str,
        contraseña: str,
        rol: str,
        usuario_sistema: str
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
        # Validar contraseña
        if len(contraseña) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        
        # Hashear contraseña
        # Hashear contraseña
        contraseña_hash = self.hashear_contraseña(contraseña)
        
        # Crear usuario
        usuario = Usuario(
            nombre_usuario=nombre_usuario,
            contrasena_hash=contraseña_hash,
            rol=rol,
            estado_usuario=True,  # Usar boolean en lugar de int
            fecha_creacion=datetime.now().isoformat()
        )
        
        return self.repo_usuario.crear(usuario, usuario_sistema)
