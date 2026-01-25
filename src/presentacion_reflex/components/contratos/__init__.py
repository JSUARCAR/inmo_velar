"""Exports de componentes de contratos."""

from .contrato_arrendamiento_form import contrato_arrendamiento_form
from .contrato_card import contrato_card
from .contrato_detail_modal import contrato_detail_modal
from .contrato_mandato_form import contrato_mandato_form
from .ipc_increment_modal import ipc_increment_modal

__all__ = [
    "contrato_arrendamiento_form",
    "contrato_mandato_form",
    "contrato_detail_modal",
    "ipc_increment_modal",
    "contrato_card",
]
