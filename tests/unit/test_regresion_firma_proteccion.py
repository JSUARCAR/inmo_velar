import pytest
from unittest.mock import patch, PropertyMock
from src.presentacion_reflex.state.auth_state import AuthState


@pytest.fixture
def auth_state():
    return AuthState()


def patch_session_token(auth_state):
    if hasattr(type(auth_state), "session_token") and isinstance(
        getattr(type(auth_state), "session_token"), property
    ):
        return patch(
            "src.presentacion_reflex.state.auth_state.AuthState.session_token",
            new_callable=PropertyMock,
            return_value="token_valido",
        )
    return patch(
        "src.presentacion_reflex.state.auth_state.AuthState.session_token",
        new="token_valido",
    )


@pytest.mark.asyncio
async def test_require_login_background_acceso_permitido(auth_state):
    """(1) acceso permitido (_validate_session -> True): termina sin TypeError, is_loading == False"""
    original_fn = AuthState.require_login_background.fn

    with patch_session_token(auth_state):
        with patch(
            "src.presentacion_reflex.state.auth_state.AuthState._validate_session",
            return_value=True,
        ):
            with patch(
                "src.presentacion_reflex.state.auth_state.AuthState._sync_permissions"
            ):
                with patch(
                    "src.presentacion_reflex.state.navigation_mixin.NavigationGenerationMixin.validate_generation",
                    return_value=True,
                ):

                    generador = original_fn(auth_state, "test-gen-1")
                    async for _ in generador:
                        pass

                    assert auth_state.is_loading is False


@pytest.mark.asyncio
async def test_require_login_background_acceso_denegado(auth_state):
    """(2) acceso denegado (_validate_session -> False, redirección a /login): termina sin TypeError, is_loading == False"""
    original_fn = AuthState.require_login_background.fn

    with patch_session_token(auth_state):
        with patch(
            "src.presentacion_reflex.state.auth_state.AuthState._validate_session",
            return_value=False,
        ):
            with patch(
                "src.presentacion_reflex.state.navigation_mixin.NavigationGenerationMixin.validate_generation",
                return_value=True,
            ):

                generador = original_fn(auth_state, "test-gen-2")
                async for _ in generador:
                    pass

                assert auth_state.is_loading is False


@pytest.mark.asyncio
async def test_require_login_background_generacion_obsoleta(auth_state):
    """(3) generación obsoleta (validate_generation -> False -> DROP): termina sin TypeError, is_loading == False"""
    original_fn = AuthState.require_login_background.fn

    with patch(
        "src.presentacion_reflex.state.navigation_mixin.NavigationGenerationMixin.validate_generation",
        return_value=False,
    ):

        generador = original_fn(auth_state, "test-gen-3")
        async for _ in generador:
            pass

        assert auth_state.is_loading is False


@pytest.mark.asyncio
async def test_require_login_background_error_transitorio(auth_state):
    """T014: Error transitorio en _validate_session (retorna False) -> termina sin TypeError."""
    original_fn = AuthState.require_login_background.fn

    with patch_session_token(auth_state):
        with patch(
            "src.presentacion_reflex.state.auth_state.AuthState._validate_session",
            return_value=False,
        ):
            with patch(
                "src.presentacion_reflex.state.navigation_mixin.NavigationGenerationMixin.validate_generation",
                return_value=True,
            ):

                generador = original_fn(auth_state, "test-gen-4")
                async for _ in generador:
                    pass

                assert auth_state.is_loading is False
