"""
Servicio para asociación de incidentes a liquidaciones.
Implementa la lógica de negocio para asociar incidentes con liquidaciones.

Feature: 003-integracion-incidentes-liquidaciones
Date: 2026-06-30
"""

import logging
from typing import Dict, Optional, Any

from src.dominio.entidades.incidente_liquidacion import IncidenteLiquidacion
from src.dominio.interfaces.repositorio_incidente_liq import RepositorioIncidenteLiquidacion
from src.dominio.interfaces.repositorio_cuota import RepositorioCuota
from src.dominio.interfaces.repositorio_plan_pago import RepositorioPlanPago
from src.dominio.interfaces.repositorio_liquidacion import IRepositorioLiquidacion
from src.dominio.interfaces.repositorio_incidentes import RepositorioIncidentes
from src.infraestructura.persistencia.database import db_manager

logger = logging.getLogger(__name__)

# Constantes para manejo de observaciones
MAX_LONGITUD_OBSERVACIONES = 500
PREFIJO_INCIDENTE = "Inc #"


def agregar_id_incidente_observaciones(
    observaciones: Optional[str],
    id_incidente: int,
) -> str:
    """
    Agrega ID de incidente a observaciones existentes.
    
    Args:
        observaciones: Observaciones actuales (puede ser None o vacío)
        id_incidente: ID del incidente a agregar
    
    Returns:
        str con observaciones actualizadas
    
    Note:
        - Preserva observaciones existentes del usuario
        - No duplica IDs ya existentes
        - Formato: "Inc #{id}"
    """
    nuevo_id = f"{PREFIJO_INCIDENTE}{id_incidente}"
    
    if not observaciones:
        return nuevo_id
    
    # Verificar si el ID ya existe
    if nuevo_id in observaciones:
        return observaciones
    
    # Append con newline
    return f"{observaciones}\n{nuevo_id}"


def remover_id_incidente_observaciones(
    observaciones: str,
    id_incidente: int,
) -> str:
    """
    Remueve ID de incidente de observaciones.
    
    Args:
        observaciones: Observaciones actuales
        id_incidente: ID del incidente a remover
    
    Returns:
        str con observaciones actualizadas
    
    Note:
        - Solo remueve la línea específica del incidente
        - Preserva otras observaciones
        - Si no quedan IDs, retorna observaciones originales sin la línea
    """
    if not observaciones:
        return ""
    
    id_a_remover = f"{PREFIJO_INCIDENTE}{id_incidente}"
    lineas = observaciones.split('\n')
    
    # Filtrar la línea del incidente a remover
    lineas_filtradas = [linea for linea in lineas if linea.strip() != id_a_remover]
    
    return '\n'.join(lineas_filtradas) if lineas_filtradas else ""


def truncar_observaciones(
    observaciones: str,
    max_longitud: int = MAX_LONGITUD_OBSERVACIONES,
) -> str:
    """
    Trunca observaciones manteniendo IDs más recientes.
    
    Args:
        observaciones: Observaciones a truncar
        max_longitud: Longitud máxima permitida
    
    Returns:
        str con observaciones truncadas
    
    Note:
        - Mantiene observaciones del usuario
        - Mantiene IDs de incidentes más recientes
        - Descarta IDs más antiguos si es necesario
    """
    if not observaciones or len(observaciones) <= max_longitud:
        return observaciones
    
    lineas = observaciones.split('\n')
    
    # Separar IDs de incidentes de otras observaciones
    ids_incidentes = [linea for linea in lineas if linea.strip().startswith(PREFIJO_INCIDENTE)]
    otros = [linea for linea in lineas if not linea.strip().startswith(PREFIJO_INCIDENTE)]
    
    # Reconstruir con IDs más recientes primero
    resultado = '\n'.join(otros)
    
    for id_inc in reversed(ids_incidentes):
        candidato = f"{id_inc}\n{resultado}" if resultado else id_inc
        if len(candidato) <= max_longitud:
            resultado = candidato
        else:
            break
    
    return resultado


class ServicioIncidenteLiquidacion:
    """
    Servicio para gestionar la asociación de incidentes a liquidaciones.
    
    Responsibilities:
    - Asociar incidentes con liquidaciones
    - Desasociar incidentes de liquidaciones
    - Calcular totales de descuentos
    - Actualizar estado de pago de incidentes
    """

    def __init__(
        self,
        repositorio_relacion: RepositorioIncidenteLiquidacion,
        repositorio_cuota: RepositorioCuota,
        repositorio_plan: RepositorioPlanPago,
        repositorio_liquidacion: IRepositorioLiquidacion,
        repositorio_incidentes: RepositorioIncidentes,
    ):
        self.repositorio_relacion = repositorio_relacion
        self.repositorio_cuota = repositorio_cuota
        self.repositorio_plan = repositorio_plan
        self.repositorio_liquidacion = repositorio_liquidacion
        self.repositorio_incidentes = repositorio_incidentes

    def asociar_incidente(
        self,
        id_incidente: int,
        id_liquidacion: int,
        numero_cuota: int,
        valor_descuento: int,
        asociado_por: str,
        justificacion: str,
    ) -> Dict[str, Any]:
        """
        Asocia un incidente a una liquidación.
        
        Args:
            id_incidente: ID del incidente
            id_liquidacion: ID de la liquidación
            numero_cuota: Número de cuota del incidente
            valor_descuento: Valor del descuento
            asociado_por: Usuario que asocia
            justificacion: Justificación de la asociación
            
        Returns:
            Dict con resultado de la operación
        """
        try:
            with db_manager.transaccion():
                # 0. Validar justificación
                if not justificacion or not justificacion.strip():
                    return {
                        "success": False,
                        "error": "JUSTIFICACION_REQUERIDA",
                        "message": "Se requiere una justificación para asociar el incidente",
                    }
                    
                    # 1. Validar que el incidente existe y está calificado
                incidente = self.repositorio_incidentes.obtener_por_id(id_incidente)
                if not incidente:
                    return {
                        "success": False,
                        "error": "INCIDENTE_NO_ENCONTRADO",
                        "message": "El incidente no existe",
                    }
                
                if incidente.estado not in ["Aprobado", "En Reparacion", "Finalizado"]:
                    return {
                        "success": False,
                        "error": "INCIDENTE_NO_CALIFICADO",
                        "message": f"El incidente no está en un estado válido (estado actual: {incidente.estado})",
                    }
                
                if incidente.estado_pago == "Pagado":
                    return {
                        "success": False,
                        "error": "INCIDENTE_PAGADO",
                        "message": "El incidente ya está pagado completamente",
                    }
                
                # 2. Verificar que el incidente tenga un plan de pago activo
                plan = self.repositorio_plan.obtener_por_incidente(id_incidente)
                if not plan or not plan.esta_activo():
                    return {
                        "success": False,
                        "error": "PLAN_NO_EXISTE",
                        "message": "El incidente no tiene un plan de pago activo",
                    }
                
                # 3. Validar que la liquidación existe y está calificada
                liquidacion = self.repositorio_liquidacion.obtener_por_id(id_liquidacion)
                if not liquidacion:
                    return {
                        "success": False,
                        "error": "LIQUIDACION_NO_ENCONTRADA",
                        "message": "La liquidación no existe",
                    }
                
                if liquidacion.estado_liquidacion not in ["En Proceso", "Aprobada"]:
                    return {
                        "success": False,
                        "error": "LIQUIDACION_NO_CALIFICADA",
                        "message": f"La liquidación no está en un estado válido (estado actual: {liquidacion.estado_liquidacion})",
                    }
                
                # 4. Validar que la cuota exista y esté pendiente
                cuotas = self.repositorio_cuota.obtener_por_plan(plan.id_plan_pago)
                cuota = next((c for c in cuotas if c.numero_cuota == numero_cuota), None)
                
                if not cuota:
                    return {
                        "success": False,
                        "error": "CUOTA_NO_ENCONTRADA",
                        "message": f"No se encontró la cuota número {numero_cuota}",
                    }
                
                if not cuota.puede_asociarse():
                    return {
                        "success": False,
                        "error": "CUOTA_YA_ASOCIADA",
                        "message": "La cuota ya está asociada a una liquidación",
                    }
                
                # 5. Validar que no exista una asociación duplicada
                relaciones_existentes = self.repositorio_relacion.obtener_por_incidente(id_incidente)
                duplicado = next(
                    (
                        r
                        for r in relaciones_existentes
                        if r.id_liquidacion == id_liquidacion
                        and r.numero_cuota == numero_cuota
                    ),
                    None,
                )
                
                if duplicado:
                    # Idempotency check: Return success if it's already associated
                    total_descuentos = self.repositorio_relacion.calcular_total_descuentos(id_liquidacion)
                    return {
                        "success": True,
                        "data": {
                            "relacion": duplicado.to_dict(),
                            "total_descuentos_liquidacion": total_descuentos,
                        },
                        "message": "Esta cuota ya está asociada a esta liquidación",
                    }
                
                # 6. Validar valor del descuento
                if valor_descuento <= 0:
                    return {
                        "success": False,
                        "error": "VALOR_INVALIDO",
                        "message": "El valor del descuento debe ser mayor a 0",
                    }
                
                # 7. Crear la relación
                relacion = IncidenteLiquidacion.crear(
                    id_incidente=id_incidente,
                    id_liquidacion=id_liquidacion,
                    numero_cuota=numero_cuota,
                    valor_descuento=valor_descuento,
                    asociado_por=asociado_por,
                )
                relacion = self.repositorio_relacion.crear(relacion)
                
                # 8. Actualizar estado de la cuota
                cuota.asociar_a_liquidacion(id_liquidacion)
                self.repositorio_cuota.actualizar(cuota)
                
                # 9. Actualizar observaciones con ID del incidente (append, no reemplazo)
                liquidacion.observaciones = agregar_id_incidente_observaciones(
                    liquidacion.observaciones,
                    id_incidente,
                )
                
                # 10. Obtener VALOR_INCIDENTES fresco de BD (post-trigger)
                total_descuentos = self.repositorio_relacion.calcular_total_descuentos(
                    id_liquidacion
                )
                
                # 11. Asignar valor fresco y recalcular totales
                liquidacion.valor_incidentes = total_descuentos
                liquidacion.calcular_totales()
                
                # 12. Persistir cambios en liquidación
                self.repositorio_liquidacion.actualizar(liquidacion, asociado_por)
                
                # 13. Auditar la acción (T082, T083)
                if hasattr(self, "servicio_auditoria") and self.servicio_auditoria:
                    self.servicio_auditoria.auditar_accion(
                        tabla="INCIDENTE_LIQUIDACION",
                        id_registro=relacion.id_relacion,
                        accion="INSERT",
                        usuario=asociado_por,
                        valores_nuevos=relacion.to_dict(),
                        ip_origen="127.0.0.1",
                        sesion_id="SYSTEM"
                    )
                
                logger.info(
                    f"Incidente {id_incidente} asociado a liquidación {id_liquidacion} "
                    f"(cuota {numero_cuota}, descuento ${valor_descuento})"
                )
                
                return {
                    "success": True,
                    "data": {
                        "relacion": relacion.to_dict(),
                        "total_descuentos_liquidacion": total_descuentos,
                    },
                    "message": "Incidente asociado exitosamente",
                }
            
        except Exception as e:
            logger.error(f"Error al asociar incidente: {e}")
            return {
                "success": False,
                "error": "ERROR_INESPERADO",
                "message": f"Error al asociar incidente: {str(e)}",
            }

    def desasociar_incidente(
        self,
        id_relacion: int,
        desasociado_por: str,
        justificacion: str = "",
    ) -> Dict[str, Any]:
        """
        Desasocia un incidente de una liquidación.
        
        Args:
            id_relacion: ID de la relación a eliminar
            desasociado_por: Usuario que desasocia
            justificacion: Justificación de la desasociación
            
        Returns:
            Dict con resultado de la operación
        """
        try:
            with db_manager.transaccion():
                # 0. Validar justificación
                if not justificacion or not justificacion.strip():
                    return {
                        "success": False,
                        "error": "JUSTIFICACION_REQUERIDA",
                        "message": "Se requiere una justificación para desasociar el incidente",
                    }
                    
                # 1. Obtener la relación
                relacion = self.repositorio_relacion.obtener_por_id(id_relacion)
                
                if not relacion:
                    return {
                        "success": True,
                        "data": {"id_relacion_eliminada": id_relacion},
                        "message": "La relación ya no existe o fue desasociada previamente",
                    }
                
                valores_anteriores = relacion.to_dict()
                
                # 2. Verificar que la liquidación no esté pagada
                liquidacion = self.repositorio_liquidacion.obtener_por_id(
                    relacion.id_liquidacion
                )
                
                if liquidacion and liquidacion.estado_liquidacion == "Pagada":
                    return {
                        "success": False,
                        "error": "LIQUIDACION_PAGADA",
                        "message": "No se puede desasociar de una liquidación pagada",
                    }
                
                if liquidacion and liquidacion.estado_liquidacion == "Cancelada":
                    return {
                        "success": False,
                        "error": "LIQUIDACION_ANULADA",
                        "message": "No se puede desasociar de una liquidación cancelada",
                    }
                
                # 3. Obtener y actualizar la cuota
                plan = self.repositorio_plan.obtener_por_incidente(relacion.id_incidente)
                if plan:
                    cuotas = self.repositorio_cuota.obtener_por_plan(plan.id_plan_pago)
                    cuota = next(
                        (
                            c
                            for c in cuotas
                            if c.numero_cuota == relacion.numero_cuota
                            and c.id_liquidacion == relacion.id_liquidacion
                        ),
                        None,
                    )
                    
                    if cuota:
                        cuota.desasociar_de_liquidacion()
                        self.repositorio_cuota.actualizar(cuota)
                
                # 4. Eliminar la relación
                self.repositorio_relacion.eliminar(id_relacion)
                
                # 5. Actualizar observaciones (remover solo el ID del incidente)
                if liquidacion:
                    liquidacion.observaciones = remover_id_incidente_observaciones(
                        liquidacion.observaciones,
                        relacion.id_incidente,
                    )
                
                # 6. Obtener VALOR_INCIDENTES fresco de BD (post-trigger)
                if liquidacion:
                    total_descuentos = self.repositorio_relacion.calcular_total_descuentos(
                        relacion.id_liquidacion
                    )
                    
                    # 7. Asignar valor fresco y recalcular totales
                    liquidacion.valor_incidentes = total_descuentos
                    liquidacion.calcular_totales()
                    
                    # 8. Persistir cambios en liquidación
                    self.repositorio_liquidacion.actualizar(liquidacion, desasociado_por)
                
                # 9. Auditar (T082)
                if hasattr(self, "servicio_auditoria") and self.servicio_auditoria:
                    self.servicio_auditoria.auditar_accion(
                        tabla="INCIDENTE_LIQUIDACION",
                        id_registro=id_relacion,
                        accion="DELETE",
                        usuario=desasociado_por,
                        valores_anteriores=valores_anteriores,
                        ip_origen="127.0.0.1",
                        sesion_id="SYSTEM"
                    )
                
                logger.info(
                    f"Relación {id_relacion} eliminada por {desasociado_por}"
                )
                
                return {
                    "success": True,
                    "data": {
                        "id_relacion_eliminada": id_relacion,
                        "total_descuentos_liquidacion": total_descuentos
                    },
                    "message": "Incidente desasociado correctamente",
                }
            
        except Exception as e:
            logger.error(f"Error al desasociar incidente: {e}")
            return {
                "success": False,
                "error": "ERROR_INESPERADO",
                "message": f"Error al desasociar incidente: {str(e)}",
            }

    def obtener_incidentes_por_liquidacion(
        self, id_liquidacion: int
    ) -> Dict[str, Any]:
        """
        Obtiene todos los incidentes asociados a una liquidación.
        
        Args:
            id_liquidacion: ID de la liquidación
            
        Returns:
            Dict con la lista de incidentes asociados
        """
        try:
            relaciones = self.repositorio_relacion.obtener_por_liquidacion(id_liquidacion)
            
            incidentes = []
            for relacion in relaciones:
                incidente = self.repositorio_incidentes.obtener_por_id(
                    relacion.id_incidente
                )
                if incidente:
                    incidentes.append(
                        {
                            "relacion": relacion.to_dict(),
                            "incidente": {
                                "id": incidente.id_incidente,
                                "descripcion": incidente.descripcion_incidente,
                                "costo": incidente.costo_incidente,
                                "estado": incidente.estado,
                                "estado_pago": incidente.estado_pago,
                            },
                        }
                    )
            
            total_descuentos = sum(r.valor_descuento for r in relaciones)
            
            return {
                "success": True,
                "data": {
                    "incidentes": incidentes,
                    "total_descuentos": total_descuentos,
                    "num_incidentes": len(incidentes),
                },
            }
            
        except Exception as e:
            logger.error(f"Error al obtener incidentes por liquidación: {e}")
            return {
                "success": False,
                "error": "ERROR_INESPERADO",
                "message": f"Error al obtener incidentes: {str(e)}",
            }

    def obtener_liquidaciones_por_incidente(
        self, id_incidente: int
    ) -> Dict[str, Any]:
        """
        Obtiene todas las liquidaciones asociadas a un incidente.
        
        Args:
            id_incidente: ID del incidente
            
        Returns:
            Dict con la lista de liquidaciones asociadas
        """
        try:
            relaciones = self.repositorio_relacion.obtener_por_incidente(id_incidente)
            
            liquidaciones = []
            for relacion in relaciones:
                liquidacion = self.repositorio_liquidacion.obtener_por_id(
                    relacion.id_liquidacion
                )
                if liquidacion:
                    liquidaciones.append(
                        {
                            "relacion": relacion.to_dict(),
                            "liquidacion": {
                                "id": liquidacion.id_liquidacion,
                                "periodo": liquidacion.periodo,
                                "estado": liquidacion.estado_liquidacion,
                                "neto_a_pagar": liquidacion.neto_a_pagar,
                            },
                        }
                    )
            
            total_descuentos = sum(r.valor_descuento for r in relaciones)
            
            return {
                "success": True,
                "data": {
                    "liquidaciones": liquidaciones,
                    "total_descuentos": total_descuentos,
                    "num_liquidaciones": len(liquidaciones),
                },
            }
            
        except Exception as e:
            logger.error(f"Error al obtener liquidaciones por incidente: {e}")
            return {
                "success": False,
                "error": "ERROR_INESPERADO",
                "message": f"Error al obtener liquidaciones: {str(e)}",
            }

    def calcular_total_descuentos(self, id_liquidacion: int) -> int:
        """
        Calcula el total de descuentos para una liquidación.
        
        Args:
            id_liquidacion: ID de la liquidación
            
        Returns:
            Total de descuentos
        """
        return self.repositorio_relacion.calcular_total_descuentos(id_liquidacion)
