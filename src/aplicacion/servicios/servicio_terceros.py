"""
Servicio de Aplicación: Gestión de Terceros (Party Model).
Coordina la creación de personas y sus roles asociados.
"""

from typing import Optional, List
from datetime import datetime

from src.dominio.entidades.persona import Persona
from src.dominio.entidades.asesor import Asesor
from src.dominio.entidades.propietario import Propietario
from src.dominio.entidades.arrendatario import Arrendatario
from src.dominio.entidades.codeudor import Codeudor
from src.infraestructura.persistencia.repositorio_persona_sqlite import RepositorioPersonaSQLite
from src.infraestructura.persistencia.repositorio_asesor_sqlite import RepositorioAsesorSQLite
from src.infraestructura.persistencia.repositorio_propietario_sqlite import RepositorioPropietarioSQLite
from src.infraestructura.persistencia.repositorio_arrendatario_sqlite import RepositorioArrendatarioSQLite
from src.infraestructura.persistencia.repositorio_codeudor_sqlite import RepositorioCodeudorSQLite
from src.infraestructura.persistencia.database import DatabaseManager


class ServicioTerceros:
    """
    Servicio para gestión de terceros (Personas y sus roles).
    Implementa el Party Model con composición 1:N.
    """
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.repo_persona = RepositorioPersonaSQLite(db_manager)
        self.repo_asesor = RepositorioAsesorSQLite(db_manager)
        self.repo_propietario = RepositorioPropietarioSQLite(db_manager)
        self.repo_arrendatario = RepositorioArrendatarioSQLite(db_manager)
        self.repo_codeudor = RepositorioCodeudorSQLite(db_manager)
    
    def crear_persona_con_roles(
        self,
        persona: Persona,
        roles: List[str],
        usuario_sistema: str,
        **kwargs
    ) -> dict:
        """
        Crea una persona y le asigna uno o más roles.
        
        Args:
            persona: Entidad Persona
            roles: Lista de roles ('ASESOR', 'PROPIETARIO', 'ARRENDATARIO', 'CODEUDOR')
            usuario_sistema: Usuario que ejecuta la operación
            **kwargs: Datos adicionales específicos de cada rol
            
        Returns:
            Diccionario con persona y roles creados
        """
        # Crear persona base
        persona_creada = self.repo_persona.crear(persona, usuario_sistema)
        
        resultado = {
            'persona': persona_creada,
            'roles': {}
        }
        
        # Asignar roles
        if 'ASESOR' in roles:
            asesor = Asesor(
                id_persona=persona_creada.id_persona,
                comision_porcentaje_arriendo=kwargs.get('comision_arriendo', 10),
                comision_porcentaje_venta=kwargs.get('comision_venta', 50)
            )
            resultado['roles']['asesor'] = self.repo_asesor.crear(asesor, usuario_sistema)
        
        if 'PROPIETARIO' in roles:
            propietario = Propietario(
                id_persona=persona_creada.id_persona,
                banco_propietario=kwargs.get('banco'),
                numero_cuenta_propietario=kwargs.get('numero_cuenta'),
                tipo_cuenta=kwargs.get('tipo_cuenta')
            )
            resultado['roles']['propietario'] = self.repo_propietario.crear(propietario, usuario_sistema)
        
        if 'ARRENDATARIO' in roles:
            arrendatario = Arrendatario(
                id_persona=persona_creada.id_persona,
                id_seguro=kwargs.get('id_seguro'),
                codigo_aprobacion_seguro=kwargs.get('codigo_seguro')
            )
            resultado['roles']['arrendatario'] = self.repo_arrendatario.crear(arrendatario, usuario_sistema)
        
        if 'CODEUDOR' in roles:
            codeudor = Codeudor(
                id_persona=persona_creada.id_persona
            )
            resultado['roles']['codeudor'] = self.repo_codeudor.crear(codeudor, usuario_sistema)
        
        return resultado
    
    def obtener_persona_con_roles(self, id_persona: int) -> Optional[dict]:
        """
        Obtiene una persona y todos sus roles.
        
        Args:
            id_persona: ID de la persona
            
        Returns:
            Diccionario con persona y roles
        """
        persona = self.repo_persona.obtener_por_id(id_persona)
        
        if not persona:
            return None
        
        resultado = {
            'persona': persona,
            'roles': {}
        }
        
        # Buscar roles
        asesor = self.repo_asesor.obtener_por_persona(id_persona)
        if asesor:
            resultado['roles']['asesor'] = asesor
        
        propietario = self.repo_propietario.obtener_por_persona(id_persona)
        if propietario:
            resultado['roles']['propietario'] = propietario
        
        arrendatario = self.repo_arrendatario.obtener_por_persona(id_persona)
        if arrendatario:
            resultado['roles']['arrendatario'] = arrendatario
        
        codeudor = self.repo_codeudor.obtener_por_persona(id_persona)
        if codeudor:
            resultado['roles']['codeudor'] = codeudor
        
        return resultado
    
    def persona_tiene_multiples_roles(self, id_persona: int) -> bool:
        """
        Verifica si una persona tiene más de un rol (validación Party Model).
        
        Args:
            id_persona: ID de la persona
            
        Returns:
            True si tiene múltiples roles
        """
        info = self.obtener_persona_con_roles(id_persona)
        
        if not info:
            return False
        
        return len(info['roles']) > 1
