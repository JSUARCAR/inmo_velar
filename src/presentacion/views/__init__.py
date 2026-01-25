"""
Paquete de vistas de presentacion.
"""

from src.presentacion.views.alerts_view import AlertsView
from src.presentacion.views.configuracion_view import build_configuracion_view
from src.presentacion.views.contrato_arrendamiento_form_view import (
    crear_contrato_arrendamiento_form_view,
)
from src.presentacion.views.contrato_mandato_form_view import crear_contrato_mandato_form_view
from src.presentacion.views.contratos_list_view import crear_contratos_list_view
from src.presentacion.views.dashboard_view import crear_dashboard_view
from src.presentacion.views.login_view import crear_login_view
from src.presentacion.views.persona_form_view import crear_persona_form_view
from src.presentacion.views.personas_list_view import crear_personas_list_view
from src.presentacion.views.propiedad_form_view import crear_propiedad_form_view
from src.presentacion.views.propiedades_list_view import crear_propiedades_list_view
from src.presentacion.views.recibo_publico_form_view import crear_recibo_publico_form_view
from src.presentacion.views.recibos_publicos_list_view import crear_recibos_publicos_list_view
from src.presentacion.views.usuario_form_view import build_usuario_form_view

__all__ = [
    "crear_login_view",
    "crear_dashboard_view",
    "AlertsView",
    "crear_personas_list_view",
    "crear_persona_form_view",
    "crear_propiedades_list_view",
    "crear_propiedad_form_view",
    "crear_contratos_list_view",
    "crear_contrato_mandato_form_view",
    "crear_contrato_arrendamiento_form_view",
    "crear_recibos_publicos_list_view",
    "crear_recibo_publico_form_view",
    "build_configuracion_view",
    "build_usuario_form_view",
]
