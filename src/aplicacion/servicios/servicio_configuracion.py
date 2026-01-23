"""
Servicio de Configuración del Sistema.
Gestiona usuarios, IPC y parámetros del sistema.
"""

import hashlib
from typing import Optional, List, Dict, Any
from datetime import datetime

from src.dominio.entidades.usuario import Usuario
from src.dominio.entidades.ipc import IPC
from src.dominio.entidades.parametro_sistema import ParametroSistema
from src.infraestructura.persistencia.repositorio_usuario_sqlite import RepositorioUsuarioSQLite
from src.infraestructura.persistencia.repositorio_ipc_sqlite import RepositorioIPCSQLite
from src.infraestructura.persistencia.repositorio_parametro_sqlite import RepositorioParametroSQLite
from src.infraestructura.persistencia.repositorio_auditoria_sqlite import RepositorioAuditoriaSQLite
from src.dominio.entidades.auditoria_cambio import AuditoriaCambio
from src.infraestructura.persistencia.database import DatabaseManager


class ServicioConfiguracion:
    """
    Servicio unificado para gestión de configuración del sistema.
    Incluye gestión de usuarios, IPC y parámetros del sistema.
    """
    
    ROLES_DISPONIBLES = ['Administrador', 'Asesor']
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.repo_usuario = RepositorioUsuarioSQLite(db_manager)
        self.repo_ipc = RepositorioIPCSQLite(db_manager)
        self.repo_parametro = RepositorioParametroSQLite(db_manager)
        self.repo_auditoria = RepositorioAuditoriaSQLite(db_manager)
        
        # Nuevo Repositorio para Configuración de Empresa
        from src.infraestructura.persistencia.repositorio_configuracion_empresa import RepositorioConfiguracionEmpresa
        self.repo_empresa = RepositorioConfiguracionEmpresa(db_manager)
    
    # ========================================
    # GESTIÓN DE CONFIGURACIÓN DE EMPRESA
    # ========================================

    def obtener_configuracion_empresa(self):
        """Obtiene la configuración de la empresa."""
        return self.repo_empresa.obtener_configuracion()

    def guardar_configuracion_empresa(self, config, usuario_sistema: str = "SISTEMA") -> bool:
        """
        Guarda la configuración de la empresa.
        
        Args:
            config: Entidad ConfiguracionEmpresa
            usuario_sistema: Usuario que realiza la acción (para logs futuros)
        """
        # Aquí se podría agregar auditoría si se desea
        return self.repo_empresa.guardar_configuracion(config)
    
    # ========================================
    # GESTIÓN DE USUARIOS
    # ========================================
    
    def listar_usuarios(self, incluir_inactivos: bool = False) -> List[Usuario]:
        """
        Lista todos los usuarios del sistema.
        
        Args:
            incluir_inactivos: Si True, incluye usuarios desactivados
            
        Returns:
            Lista de usuarios
        """
        todos = self.repo_usuario.listar_todos()
        if incluir_inactivos:
            return todos
        return [u for u in todos if u.es_activo()]
    
    def obtener_usuario(self, id_usuario: int) -> Optional[Usuario]:
        """Obtiene un usuario por su ID."""
        return self.repo_usuario.obtener_por_id(id_usuario)
    
    def crear_usuario(
        self,
        nombre_usuario: str,
        contrasena: str,
        rol: str,
        usuario_sistema: str
    ) -> Usuario:
        """
        Crea un nuevo usuario con contraseña hasheada.
        
        Args:
            nombre_usuario: Nombre de usuario único
            contrasena: Contraseña en texto plano
            rol: Rol del sistema (Administrador, Asesor)
            usuario_sistema: Usuario que ejecuta la operación
            
        Returns:
            Usuario creado
            
        Raises:
            ValueError: Si los datos son inválidos
        """
        # Validar nombre de usuario único
        existente = self.repo_usuario.obtener_por_nombre(nombre_usuario)
        if existente:
            raise ValueError(f"El nombre de usuario '{nombre_usuario}' ya existe")
        
        # Validar contraseña
        if len(contrasena) < 6:
            raise ValueError("La contraseña debe tener al menos 6 caracteres")
        
        # Validar rol
        if rol not in self.ROLES_DISPONIBLES:
            raise ValueError(f"Rol inválido. Valores permitidos: {', '.join(self.ROLES_DISPONIBLES)}")
        
        # Hashear contraseña
        contrasena_hash = hashlib.sha256(contrasena.encode('utf-8')).hexdigest()
        
        # Crear usuario
        usuario = Usuario(
            nombre_usuario=nombre_usuario,
            contrasena_hash=contrasena_hash,
            rol=rol,
            estado_usuario=1,
            fecha_creacion=datetime.now().isoformat()
        )
        
        return self.repo_usuario.crear(usuario, usuario_sistema)
    
    def actualizar_usuario(
        self,
        id_usuario: int,
        rol: Optional[str] = None,
        usuario_sistema: str = "SISTEMA"
    ) -> bool:
        """
        Actualiza los datos de un usuario (rol).
        
        Args:
            id_usuario: ID del usuario a actualizar
            rol: Nuevo rol (opcional)
            usuario_sistema: Usuario que ejecuta la operación
            
        Returns:
            True si se actualizó correctamente
        """
        usuario = self.repo_usuario.obtener_por_id(id_usuario)
        if not usuario:
            raise ValueError(f"Usuario con ID {id_usuario} no encontrado")
        
        if rol:
            if rol not in self.ROLES_DISPONIBLES:
                raise ValueError(f"Rol inválido. Valores permitidos: {', '.join(self.ROLES_DISPONIBLES)}")
            usuario.rol = rol
        
        return self.repo_usuario.actualizar(usuario, usuario_sistema)
    
    def desactivar_usuario(self, id_usuario: int, usuario_sistema: str) -> bool:
        """
        Desactiva un usuario (soft delete).
        
        Args:
            id_usuario: ID del usuario a desactivar
            usuario_sistema: Usuario que ejecuta la operación
            
        Returns:
            True si se desactivó correctamente
        """
        usuario = self.repo_usuario.obtener_por_id(id_usuario)
        if not usuario:
            raise ValueError(f"Usuario con ID {id_usuario} no encontrado")
        
        if not usuario.es_activo():
            raise ValueError("El usuario ya está desactivado")
        
        return self.repo_usuario.eliminar(id_usuario)
    
    def reactivar_usuario(self, id_usuario: int, usuario_sistema: str) -> bool:
        """
        Reactiva un usuario previamente desactivado.
        
        Args:
            id_usuario: ID del usuario a reactivar
            usuario_sistema: Usuario que ejecuta la operación
            
        Returns:
            True si se reactivó correctamente
        """
        usuario = self.repo_usuario.obtener_por_id(id_usuario)
        if not usuario:
            raise ValueError(f"Usuario con ID {id_usuario} no encontrado")
        
        if usuario.es_activo():
            raise ValueError("El usuario ya está activo")
        
        usuario.estado_usuario = 1
        return self.repo_usuario.actualizar(usuario, usuario_sistema)
    
    def resetear_contrasena(
        self,
        id_usuario: int,
        nueva_contrasena: str,
        usuario_sistema: str
    ) -> bool:
        """
        Resetea la contraseña de un usuario.
        
        Args:
            id_usuario: ID del usuario
            nueva_contrasena: Nueva contraseña en texto plano
            usuario_sistema: Usuario que ejecuta la operación
            
        Returns:
            True si se reseteo correctamente
        """
        usuario = self.repo_usuario.obtener_por_id(id_usuario)
        if not usuario:
            raise ValueError(f"Usuario con ID {id_usuario} no encontrado")
        
        if len(nueva_contrasena) < 6:
            raise ValueError("La contraseña debe tener al menos 6 caracteres")
        
        usuario.contrasena_hash = hashlib.sha256(nueva_contrasena.encode('utf-8')).hexdigest()
        return self.repo_usuario.actualizar(usuario, usuario_sistema)
    
    # ========================================
    # GESTIÓN DE IPC
    # ========================================
    
    def listar_ipc(self) -> List[IPC]:
        """Lista todos los valores IPC registrados."""
        return self.repo_ipc.listar_todos()
    
    def obtener_ipc_actual(self) -> Optional[IPC]:
        """Obtiene el IPC del año más reciente."""
        return self.repo_ipc.obtener_ultimo()
    
    def obtener_ipc_por_anio(self, anio: int) -> Optional[IPC]:
        """Obtiene el IPC de un año específico."""
        return self.repo_ipc.obtener_por_anio(anio)
    
    def agregar_ipc(
        self,
        anio: int,
        valor_ipc: int,
        fecha_publicacion: Optional[str] = None,
        usuario_sistema: str = "SISTEMA"
    ) -> IPC:
        """
        Agrega un nuevo registro de IPC.
        
        Args:
            anio: Año del IPC (ej: 2025)
            valor_ipc: Valor en base 100 (ej: 800 = 8%)
            fecha_publicacion: Fecha de publicación (opcional)
            usuario_sistema: Usuario que ejecuta la operación
            
        Returns:
            IPC creado
            
        Raises:
            ValueError: Si el año ya tiene un IPC registrado
        """
        # Validar que no exista IPC para ese año
        existente = self.repo_ipc.obtener_por_anio(anio)
        if existente:
            raise ValueError(f"Ya existe un IPC para el año {anio}")
        
        # Validar rango
        if valor_ipc < 0 or valor_ipc > 10000:
            raise ValueError("El valor IPC debe estar entre 0 y 10000 (0% - 100%)")
        
        ipc = IPC(
            anio=anio,
            valor_ipc=valor_ipc,
            fecha_publicacion=fecha_publicacion or datetime.now().isoformat(),
            estado_registro=1
        )
        
        return self.repo_ipc.crear(ipc, usuario_sistema)
    
    def actualizar_ipc(
        self,
        id_ipc: int,
        valor_ipc: int,
        fecha_publicacion: Optional[str] = None,
        usuario_sistema: str = "SISTEMA"
    ) -> bool:
        """
        Actualiza un registro de IPC existente.
        
        Args:
            id_ipc: ID del IPC a actualizar
            valor_ipc: Nuevo valor
            fecha_publicacion: Nueva fecha de publicación (opcional)
            usuario_sistema: Usuario que ejecuta la operación
            
        Returns:
            True si se actualizó correctamente
        """
        ipc = self.repo_ipc.obtener_por_id(id_ipc)
        if not ipc:
            raise ValueError(f"IPC con ID {id_ipc} no encontrado")
        
        if valor_ipc < 0 or valor_ipc > 10000:
            raise ValueError("El valor IPC debe estar entre 0 y 10000 (0% - 100%)")
        
        ipc.valor_ipc = valor_ipc
        if fecha_publicacion:
            ipc.fecha_publicacion = fecha_publicacion
        
        return self.repo_ipc.actualizar(ipc, usuario_sistema)
    
    # ========================================
    # GESTIÓN DE PARÁMETROS
    # ========================================
    
    def listar_parametros(self) -> List[ParametroSistema]:
        """Lista todos los parámetros del sistema."""
        return self.repo_parametro.listar_todos()
    
    def listar_categorias(self) -> List[str]:
        """Lista todas las categorías de parámetros disponibles."""
        return self.repo_parametro.listar_categorias()
    
    def listar_por_categoria(self, categoria: str) -> List[ParametroSistema]:
        """Lista todos los parámetros de una categoría específica."""
        return self.repo_parametro.obtener_por_categoria(categoria)
    
    def obtener_parametro(self, nombre: str) -> Optional[ParametroSistema]:
        """Obtiene un parámetro por su nombre."""
        return self.repo_parametro.obtener_por_nombre(nombre)
    
    def obtener_valor_parametro(self, nombre: str, default: Any = None) -> Any:
        """
        Obtiene el valor de un parámetro de forma directa.
        
        Args:
            nombre: Nombre del parámetro
            default: Valor por defecto si no existe
            
        Returns:
            Valor del parámetro convertido según su tipo, o default si no existe
        """
        parametro = self.repo_parametro.obtener_por_nombre(nombre)
        if not parametro:
            return default
        
        try:
            if parametro.tipo_dato == 'INTEGER':
                return parametro.valor_como_int
            elif parametro.tipo_dato == 'DECIMAL':
                return parametro.valor_como_decimal
            elif parametro.tipo_dato == 'BOOLEAN':
                return parametro.valor_como_bool
            else:
                return parametro.valor_parametro
        except Exception:
            return default
    
    def actualizar_parametro(
        self,
        id_parametro: int,
        nuevo_valor: str,
        usuario_sistema: str
    ) -> bool:
        """
        Actualiza el valor de un parámetro.
        
        Args:
            id_parametro: ID del parámetro
            nuevo_valor: Nuevo valor como string
            usuario_sistema: Usuario que ejecuta la operación
            
        Returns:
            True si se actualizó correctamente
            
        Raises:
            PermissionError: Si el parámetro no es modificable
            ValueError: Si el valor no es válido para el tipo de dato
        """
        parametro = self.repo_parametro.obtener_por_id(id_parametro)
        if not parametro:
            raise ValueError(f"Parámetro con ID {id_parametro} no encontrado")
        
        # Validar tipo antes de actualizar
        parametro.actualizar_valor(nuevo_valor, usuario_sistema)
        
        return self.repo_parametro.actualizar(parametro, usuario_sistema)
    
    def actualizar_parametros_por_categoria(
        self,
        categoria: str,
        valores: Dict[int, str],
        usuario_sistema: str
    ) -> int:
        """
        Actualiza múltiples parámetros de una categoría.
        
        Args:
            categoria: Categoría de los parámetros
            valores: Diccionario {id_parametro: nuevo_valor}
            usuario_sistema: Usuario que ejecuta la operación
            
        Returns:
            Número de parámetros actualizados
        """
        actualizados = 0
        for id_parametro, nuevo_valor in valores.items():
            try:
                if self.actualizar_parametro(id_parametro, nuevo_valor, usuario_sistema):
                    actualizados += 1
            except PermissionError:
                # Ignorar parámetros no modificables
                continue
            except ValueError:
                # Re-lanzar errores de validación
                raise
        
        return actualizados

    # ========================================
    # GESTIÓN DE AUDITORÍA
    # ========================================

    def listar_auditoria(self, limit: int = 100, offset: int = 0) -> List[AuditoriaCambio]:
        """Lista registros de auditoría."""
        return self.repo_auditoria.listar_todos(limit, offset)

    def buscar_auditoria_por_tabla(self, tabla: str, limit: int = 100) -> List[AuditoriaCambio]:
        """Busca auditoría filtrando por tabla."""
        return self.repo_auditoria.buscar_por_tabla(tabla, limit)
