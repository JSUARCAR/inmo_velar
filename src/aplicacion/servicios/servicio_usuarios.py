
from typing import List, Optional, Dict
from src.dominio.entidades.usuario import Usuario
from src.infraestructura.persistencia.database import DatabaseManager
from src.infraestructura.persistencia.repositorio_usuario_sqlite import RepositorioUsuarioSQLite
from src.aplicacion.servicios.servicio_autenticacion import ServicioAutenticacion

class ServicioUsuarios:
    """
    Servicio para la gestión administrativa de usuarios (CRUD).
    """
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.repo = RepositorioUsuarioSQLite(db_manager)
        self.auth_service = ServicioAutenticacion(db_manager)

    def listar_usuarios(self) -> List[Usuario]:
        """Obtiene todos los usuarios registrados."""
        return self.repo.listar_todos()

    def obtener_usuario(self, id_usuario: int) -> Optional[Usuario]:
        """Obtiene un usuario por ID."""
        return self.repo.obtener_por_id(id_usuario)

    def crear_usuario(self, nombre_usuario: str, contrasena: str, rol: str, creador: str) -> Usuario:
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
        # Pero como auth_service.cambiar_contraseña pide la actual para verificación,
        # aquí hacemos la asignación directa del hash validado.
        
        if len(nueva_contrasena) < 6:
            raise ValueError("La contraseña debe tener al menos 6 caracteres")
            
        hash_nuevo, _ = self.auth_service.hashear_contraseña(nueva_contrasena)
        
        # OJO: ServicioAutenticacion.hashear_contraseña devuelve (hash, salt) pero el método actual del servicio 
        # en `crear_usuario` usa hashlib directo sin salt separado en la implementación actual de autenticación.
        # Revisando servicio_autenticacion.py:
        # L86: hash_ingresado = hashlib.sha256(contraseña.encode('utf-8')).hexdigest()
        # L172: contraseña_hash = hashlib.sha256(contraseña.encode('utf-8')).hexdigest()
        # Por consistencia con FASE 0, usaremos hashlib directo aquí también hasta que se migre todo a sal.
        
        import hashlib
        usuario.contrasena_hash = hashlib.sha256(nueva_contrasena.encode('utf-8')).hexdigest()
        
        return self.repo.actualizar(usuario, editor)
