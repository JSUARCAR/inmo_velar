from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from src.presentacion_reflex.state.auth_state import AuthState


def obtener_usuario_actual() -> str:
    return "sistema"


async def obtener_usuario_actual_async() -> str:
    return "sistema"


async def obtener_usuario_desde_state(state: "AuthState") -> str:
    if state.is_authenticated and state.user_nombre:
        return state.user_nombre
    return "sistema"


async def obtener_usuario_en_event(state_instance) -> str:
    """
    Obtiene el usuario actual en el contexto de un event handler.
    Intenta obtener AuthState y retornar el usuario autenticado.
    Fallback a 'sistema' si no hay sesion.
    """
    try:
        auth_state = await state_instance.get_state(
            state_instance.__class__.get_app_state().substates["auth"]
        )
        if hasattr(auth_state, "is_authenticated") and auth_state.is_authenticated:
            if hasattr(auth_state, "user_nombre") and auth_state.user_nombre:
                return auth_state.user_nombre
    except Exception:
        pass
    return "sistema"
