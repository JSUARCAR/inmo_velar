import pytest
from src.dominio.excepciones.excepciones_base import (
    ErrorCredencialesInvalidas,
    ErrorUsuarioInactivo,
    ErrorRecurso,
    ErrorPoliticaIntentos,
)

def test_mensajes_error_canonicos():
    assert ErrorCredencialesInvalidas().mensaje == "Credenciales inválidas. Verifique usuario y contraseña."
    assert ErrorUsuarioInactivo().mensaje == "El usuario se encuentra inactivo."
    assert ErrorPoliticaIntentos().mensaje == "Demasiados intentos. Intente de nuevo en 15 minutos."
    
    # ErrorRecurso
    err_bd = ErrorRecurso(codigo_recurso="BD")
    assert err_bd.mensaje == "Error de recurso"
    assert err_bd.codigo_recurso == "BD"
