"""
Interface Repository: PlanPagoIncidente
Define el contrato para operaciones de planes de pago de incidentes.

Feature: 003-integracion-incidentes-liquidaciones
Date: 2026-06-30
"""

from typing import List, Optional, Protocol

from ..entidades.plan_pago_incidente import PlanPagoIncidente


class RepositorioPlanPago(Protocol):
    """
    Interface para operaciones de planes de pago de incidentes.
    
    Methods:
        crear: Crea un nuevo plan de pago
        obtener_por_id: Obtiene un plan por su ID
        obtener_por_incidente: Obtiene el plan activo de un incidente
        actualizar: Actualiza un plan existente
        eliminar: Elimina un plan (soft delete)
    """
    
    def crear(self, plan: PlanPagoIncidente) -> PlanPagoIncidente:
        """
        Crea un nuevo plan de pago.
        
        Args:
            plan: Plan de pago a crear
            
        Returns:
            Plan creado con ID asignado
        """
        ...
    
    def obtener_por_id(self, id_plan_pago: int) -> Optional[PlanPagoIncidente]:
        """
        Obtiene un plan de pago por su ID.
        
        Args:
            id_plan_pago: ID del plan
            
        Returns:
            Plan encontrado o None
        """
        ...
    
    def obtener_por_incidente(self, id_incidente: int) -> Optional[PlanPagoIncidente]:
        """
        Obtiene el plan activo de pago para un incidente.
        
        Args:
            id_incidente: ID del incidente
            
        Returns:
            Plan activo o None
        """
        ...
    
    def actualizar(self, plan: PlanPagoIncidente) -> PlanPagoIncidente:
        """
        Actualiza un plan de pago existente.
        
        Args:
            plan: Plan con datos actualizados
            
        Returns:
            Plan actualizado
        """
        ...
    
    def eliminar(self, id_plan_pago: int) -> bool:
        """
        Elimina un plan de pago (soft delete).
        
        Args:
            id_plan_pago: ID del plan a eliminar
            
        Returns:
            True si se eliminó correctamente
        """
        ...
