"""
Interface Repository: CuotaIncidente
Define el contrato para operaciones de cuotas de incidentes.

Feature: 003-integracion-incidentes-liquidaciones
Date: 2026-06-30
"""

from typing import List, Optional, Protocol

from ..entidades.cuota_incidente import CuotaIncidente


class RepositorioCuota(Protocol):
    """
    Interface para operaciones de cuotas de incidentes.
    
    Methods:
        crear: Crea una nueva cuota
        crear_desde_plan: Crea todas las cuotas para un plan
        obtener_por_id: Obtiene una cuota por su ID
        obtener_por_plan: Obtiene todas las cuotas de un plan
        obtener_por_liquidacion: Obtiene cuotas asociadas a una liquidación
        actualizar: Actualiza una cuota existente
        eliminar: Elimina una cuota
    """
    
    def crear(self, cuota: CuotaIncidente) -> CuotaIncidente:
        """
        Crea una nueva cuota.
        
        Args:
            cuota: Cuota a crear
            
        Returns:
            Cuota creada con ID asignado
        """
        ...
    
    def crear_desde_plan(self, id_plan_pago: int, num_cuotas: int, 
                         valor_cuota: int) -> List[CuotaIncidente]:
        """
        Crea todas las cuotas para un plan.
        
        Args:
            id_plan_pago: ID del plan de pago
            num_cuotas: Número de cuotas a crear
            valor_cuota: Valor de cada cuota
            
        Returns:
            Lista de cuotas creadas
        """
        ...
    
    def obtener_por_id(self, id_cuota: int) -> Optional[CuotaIncidente]:
        """
        Obtiene una cuota por su ID.
        
        Args:
            id_cuota: ID de la cuota
            
        Returns:
            Cuota encontrada o None
        """
        ...
    
    def obtener_por_plan(self, id_plan_pago: int) -> List[CuotaIncidente]:
        """
        Obtiene todas las cuotas de un plan.
        
        Args:
            id_plan_pago: ID del plan
            
        Returns:
            Lista de cuotas del plan
        """
        ...
    
    def obtener_por_liquidacion(self, id_liquidacion: int) -> List[CuotaIncidente]:
        """
        Obtiene todas las cuotas asociadas a una liquidación.
        
        Args:
            id_liquidacion: ID de la liquidación
            
        Returns:
            Lista de cuotas asociadas
        """
        ...
    
    def actualizar(self, cuota: CuotaIncidente) -> CuotaIncidente:
        """
        Actualiza una cuota existente.
        
        Args:
            cuota: Cuota con datos actualizados
            
        Returns:
            Cuota actualizada
        """
        ...
    
    def eliminar(self, id_cuota: int) -> bool:
        """
        Elimina una cuota.
        
        Args:
            id_cuota: ID de la cuota a eliminar
            
        Returns:
            True si se eliminó correctamente
        """
        ...

    def contar_estado_liquidaciones_por_plan(self, id_plan_pago: int) -> tuple[int, int]:
        """
        Calcula la cantidad de cuotas con liquidación y cuántas están pagadas 
        para un plan de pago específico en una sola consulta optimizada.
        
        Args:
            id_plan_pago: ID del plan
            
        Returns:
            Tuple[int, int]: (total_cuotas_con_liq, total_cuotas_pagadas)
        """
        ...

    def obtener_cuotas_pendientes_por_propiedad(self, id_propiedad: int) -> List[CuotaIncidente]:
        """
        Obtiene las cuotas pendientes que no están asociadas a ninguna liquidación para una propiedad dada.
        
        Args:
            id_propiedad: ID de la propiedad
            
        Returns:
            Lista de cuotas pendientes
        """
        ...
