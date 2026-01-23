"""
Servicio de Aplicación: Gestión de Permisos por Rol
"""

from typing import List, Dict, Optional
from datetime import datetime

from src.dominio.entidades.permiso import Permiso, RolPermiso
from src.infraestructura.persistencia.repositorio_permisos import RepositorioPermisos
from src.infraestructura.persistencia.database import DatabaseManager


class ServicioPermisos:
    """
    Servicio para gestionar permisos del sistema y asignaciones a roles.
    """
    
    def __init__(self, db_manager: DatabaseManager):
        self.repo = RepositorioPermisos(db_manager)
    
    # ===== GESTIÓN DE PERMISOS =====
    
    def listar_todos_permisos(self) -> List[Permiso]:
        """Lista todos los permisos disponibles en el sistema."""
        return self.repo.listar_permisos()
    
    def obtener_permisos_agrupados_por_categoria(self) -> Dict[str, List[Permiso]]:
        """
        Obtiene los permisos agrupados por categoría para facilitar la UI.
        
        Returns:
            Dict con categorías como keys y listas de permisos como values
        """
        permisos = self.repo.listar_permisos()
        agrupados = {}
        
        for permiso in permisos:
            categoria = permiso.categoria or "Otros"
            if categoria not in agrupados:
                agrupados[categoria] = []
            agrupados[categoria].append(permiso)
        
        return agrupados
    
    # ===== GESTIÓN DE PERMISOS POR ROL =====
    
    def obtener_permisos_rol(self, rol: str) -> List[Permiso]:
        """Obtiene todos los permisos asignados a un rol."""
        # Administrador siempre tiene todos los permisos
        if rol == "Administrador":
            return self.repo.listar_permisos()
        
        return self.repo.obtener_permisos_por_rol(rol)
    
    def obtener_ids_permisos_rol(self, rol: str) -> List[int]:
        """Obtiene solo los IDs de permisos asignados a un rol."""
        permisos = self.obtener_permisos_rol(rol)
        return [p.id_permiso for p in permisos if p.id_permiso]
    
    def actualizar_permisos_rol(
        self, 
        rol: str, 
        ids_permisos: List[int], 
        usuario: str
    ) -> bool:
        """
        Actualiza los permisos de un rol. Reemplaza todos los permisos existentes.
        
        Args:
            rol: Nombre del rol
            ids_permisos: Lista de IDs de permisos a asignar
            usuario: Usuario que realiza la operación
            
        Returns:
            True si la actualización fue exitosa
        """
        # No permitir modificar permisos de Administrador
        if rol == "Administrador":
            raise ValueError("No se pueden modificar los permisos del rol Administrador")
        
        try:
            # 1. Limpiar permisos existentes
            self.repo.limpiar_permisos_rol(rol)
            
            # 2. Asignar nuevos permisos
            for id_permiso in ids_permisos:
                self.repo.asignar_permiso_a_rol(rol, id_permiso, usuario)
            
            return True
        except Exception as e:
            raise Exception(f"Error al actualizar permisos: {str(e)}")
    
    def asignar_permiso(self, rol: str, id_permiso: int, usuario: str) -> bool:
        """Asigna un permiso individual a un rol."""
        if rol == "Administrador":
            raise ValueError("No se pueden modificar los permisos del rol Administrador")
        
        self.repo.asignar_permiso_a_rol(rol, id_permiso, usuario)
        return True
    
    def revocar_permiso(self, rol: str, id_permiso: int, usuario: str) -> bool:
        """Revoca un permiso individual de un rol."""
        if rol == "Administrador":
            raise ValueError("No se pueden modificar los permisos del rol Administrador")
        
        return self.repo.revocar_permiso_de_rol(rol, id_permiso, usuario)
    
    # ===== VERIFICACIÓN DE ACCESO =====
    
    def verificar_acceso(self, rol: str, modulo: str, accion: str) -> bool:
        """
        Verifica si un rol tiene permiso para realizar una acción en un módulo.
        
        Args:
            rol: Nombre del rol
            modulo: Nombre del módulo
            accion: Acción a verificar (VER, CREAR, EDITAR, ELIMINAR)
            
        Returns:
            True si el rol tiene el permiso
        """
        # Administrador siempre tiene acceso
        if rol == "Administrador":
            return True
        
        return self.repo.verificar_permiso(rol, modulo, accion)
    
    def verificar_acceso_multiple(
        self, 
        rol: str, 
        verificaciones: List[Dict[str, str]]
    ) -> Dict[str, bool]:
        """
        Verifica múltiples permisos de una vez.
        
        Args:
            rol: Nombre del rol
            verificaciones: Lista de dicts con 'modulo' y 'accion'
            
        Returns:
            Dict con resultados de cada verificación
        """
        resultados = {}
        for v in verificaciones:
            key = f"{v['modulo']}:{v['accion']}"
            resultados[key] = self.verificar_acceso(rol, v['modulo'], v['accion'])
        return resultados
    
    # ===== PRESETS DE PERMISOS =====
    
    def aplicar_preset_asesor(self, usuario: str) -> bool:
        """
        Aplica un conjunto predefinido de permisos típico para el rol Asesor.
        
        Permisos incluidos:
        - Personas: Ver, Crear, Editar
        - Propiedades: Ver, Crear, Editar
        - Contratos: Ver, Crear
        - Dashboard: Ver
        - Liquidación Asesores: Ver
        - Incidentes: Ver, Crear
        - Recibos Públicos: Ver
        """
        # Obtener todos los permisos
        todos_permisos = self.repo.listar_permisos()
        
        # Definir preset
        preset_config = {
            "Personas": ["VER", "CREAR", "EDITAR"],
            "Propiedades": ["VER", "CREAR", "EDITAR"],
            "Contratos": ["VER", "CREAR"],
            "Dashboard": ["VER"],
            "Liquidación Asesores": ["VER"],
            "Incidentes": ["VER", "CREAR"],
            "Recibos Públicos": ["VER"],
        }
        
        # Filtrar IDs de permisos según preset
        ids_permisos = []
        for permiso in todos_permisos:
            if permiso.modulo in preset_config:
                if permiso.accion in preset_config[permiso.modulo]:
                    if permiso.id_permiso:
                        ids_permisos.append(permiso.id_permiso)
        
        # Aplicar permisos
        return self.actualizar_permisos_rol("Asesor", ids_permisos, usuario)
    
    def aplicar_preset_operativo(self, usuario: str) -> bool:
        """
        Aplica un conjunto predefinido de permisos típico para el rol Operativo.
        
        Permisos incluidos:
        - Incidentes: Ver, Crear, Editar
        - Desocupaciones: Ver, Crear, Editar
        - Seguros: Ver, Editar
        - Recaudos: Ver, Editar
        - Dashboard: Ver
        - Personas: Ver
        - Propiedades: Ver
        - Contratos: Ver
        """
        todos_permisos = self.repo.listar_permisos()
        
        preset_config = {
            "Incidentes": ["VER", "CREAR", "EDITAR"],
            "Desocupaciones": ["VER", "CREAR", "EDITAR"],
            "Seguros": ["VER", "EDITAR"],
            "Recaudos": ["VER", "EDITAR"],
            "Dashboard": ["VER"],
            "Personas": ["VER"],
            "Propiedades": ["VER"],
            "Contratos": ["VER"],
        }
        
        ids_permisos = []
        for permiso in todos_permisos:
            if permiso.modulo in preset_config:
                if permiso.accion in preset_config[permiso.modulo]:
                    if permiso.id_permiso:
                        ids_permisos.append(permiso.id_permiso)
        
        return self.actualizar_permisos_rol("Operativo", ids_permisos, usuario)
    
    def aplicar_preset_solo_lectura(self, rol: str, usuario: str) -> bool:
        """
        Aplica permisos de solo lectura (VER) a todos los módulos.
        """
        todos_permisos = self.repo.listar_permisos()
        
        # Solo permisos de VER
        ids_permisos = [
            p.id_permiso for p in todos_permisos 
            if p.accion == "VER" and p.id_permiso
        ]
        
        return self.actualizar_permisos_rol(rol, ids_permisos, usuario)
