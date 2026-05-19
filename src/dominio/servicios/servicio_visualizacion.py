"""
Servicio de Dominio: Visualización de Grupos
Gestiona la representación visual de los grupos operativos de pago.
"""

from typing import Dict


class ServicioVisualizacion:
    # Mapeo de configuración visual por grupo
    # Estándar Claude Design System
    CONFIGURACION_GRUPOS: Dict[int, Dict[str, str]] = {
        1: {
            "color": "#C96442", 
            "label": "Grupo 1",
            "descripcion_larga": "Contratos iniciados entre día 1 y 5. Pago programado: 10 de cada mes."
        },
        2: {
            "color": "#D97757", 
            "label": "Grupo 2",
            "descripcion_larga": "Contratos iniciados entre día 6 y 15. Pago programado: 20 de cada mes."
        },
        3: {
            "color": "#87867F", 
            "label": "Grupo 3",
            "descripcion_larga": "Contratos iniciados entre día 16 y 24. Pago programado: 30 de cada mes."
        },
        4: {
            "color": "#5E5D59", 
            "label": "Grupo 4",
            "descripcion_larga": "Contratos iniciados entre día 25 y 31. Pago programado: 10 del mes siguiente."
        },
    }

    @staticmethod
    def obtener_configuracion_grupo(grupo_operativo: int) -> Dict[str, str]:
        """Retorna la configuración visual para un grupo dado."""
        return ServicioVisualizacion.CONFIGURACION_GRUPOS.get(
            grupo_operativo, 
            {"color": "#141413", "descripcion": "Sin grupo asignado"}
        )
