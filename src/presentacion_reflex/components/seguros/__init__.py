"""
Exports para componentes de seguros
"""

from .detail_modal import modal_detalle_seguro
from .modal_form import modal_seguro
from .poliza_modal import modal_poliza

__all__ = [
    "modal_seguro",
    "modal_poliza",
    "modal_detalle_seguro",
]
