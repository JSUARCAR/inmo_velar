"""
Servicio de Aplicación: Autenticación de Usuarios.
Implementa lógica de autenticación, hash de contraseñas y gestión de sesiones.
"""

import hashlib
import secrets
from typing import Optional, Tuple
from datetime import datetime

from src.dominio.entidades.usuario import Usuario
from src.dominio.entidades.sesion_usuario import SesionUsuario
from src.infraestructura.persistencia.repositorio_usuario_sqlite import RepositorioUsuarioSQLite
from src.infraestructura.persistencia.database import DatabaseManager


class ServicioAutenticacion:
    """
    Servicio de autenticación de usuarios.
    Maneja login, logout, hash de contraseñas y sesiones.
    """
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.repo_usuario = RepositorioUsuarioSQLite(db_manager)
    
    @staticmethod
    def hashear_contraseña(contraseña_plana: str, sal: Optional[str] = None) -> Tuple[str, str]:
        """
        Hashea una contraseña usando SHA256 + salt.
        
        Args:
            contraseña_plana: Contraseña en texto plano
            sal: Salt opcional (se genera si no se provee)
            
        Returns:
            Tupla (hash, sal)
        """
        if not sal:
            sal = secrets.token_hex(16)
        
        combinacion = f"{contraseña_plana}{sal}".encode('utf-8')
        hash_obj = hashlib.sha256(combinacion)
        
        return hash_obj.hexdigest(), sal
    
    def verificar_contraseña(self, contraseña_plana: str, contraseña_hash: str, sal: str) -> bool:
        """
        Verifica si una contraseña plana coincide con el hash almacenado.
        
        Args:
            contraseña_plana: Contraseña a verificar
            contraseña_hash: Hash almacenado
            sal: Salt del usuario
            
        Returns:
            True si la contraseña es correcta
        """
        hash_calculado, _ = self.hashear_contraseña(contraseña_plana, sal)
        return hash_calculado == contraseña_hash
    
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
        
        # Nota: El hash en BD no tiene sal separada, necesitamos ajustar la estrategia
        # Para simplificar en esta fase, asumimos que la BD ya tiene contraseña hasheada
        # y hacemos comparación directa con hash simple
        hash_ingresado = hashlib.sha256(contraseña.encode('utf-8')).hexdigest()
        
        if hash_ingresado == usuario.contrasena_hash:
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
        
        # Aquí iría la lógica para guardar en BD si tuviéramos repo de sesiones
        return sesion
    
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
        hash_actual = hashlib.sha256(contraseña_actual.encode('utf-8')).hexdigest()
        if hash_actual != usuario.contrasena_hash:
            return False
        
        # Validar nueva contraseña
        if len(contraseña_nueva) < 6:
            raise ValueError("La nueva contraseña debe tener al menos 6 caracteres")
        
        # Hashear nueva contraseña
        nuevo_hash = hashlib.sha256(contraseña_nueva.encode('utf-8')).hexdigest()
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
        if len(contraseña) < 6:
            raise ValueError("La contraseña debe tener al menos 6 caracteres")
        
        # Hashear contraseña
        contraseña_hash = hashlib.sha256(contraseña.encode('utf-8')).hexdigest()
        
        # Crear usuario
        usuario = Usuario(
            nombre_usuario=nombre_usuario,
            contrasena_hash=contraseña_hash,
            rol=rol,
            estado_usuario=True,  # Usar boolean en lugar de int
            fecha_creacion=datetime.now().isoformat()
        )
        
        return self.repo_usuario.crear(usuario, usuario_sistema)
