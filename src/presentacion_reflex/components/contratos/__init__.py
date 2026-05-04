"""Exports de componentes de contratos."""

from .formulario_contrato_arrendamiento import formulario_contrato_arrendamiento
from .tarjeta_contrato import tarjeta_contrato
from .modal_detalle_contrato import modal_detalle_contrato
from .formulario_contrato_mandato import formulario_contrato_mandato
from .modal_incremento_ipc import modal_incremento_ipc
from .modal_renovacion_contrato import modal_renovacion_contrato

__all__ = [
    "formulario_contrato_arrendamiento",
    "formulario_contrato_mandato",
    "modal_detalle_contrato",
    "modal_incremento_ipc",
    "tarjeta_contrato",
    "modal_renovacion_contrato",
]
