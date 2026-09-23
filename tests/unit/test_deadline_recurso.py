import pytest
import asyncio
from src.aplicacion.servicios.servicio_autenticacion import operacion_con_deadline
from src.dominio.excepciones.excepciones_base import ErrorRecurso

@pytest.mark.asyncio
async def test_deadline_operacion_expirado():
    """Test que verifica que el deadline de operacion expirado produce ErrorRecurso(BACKEND)"""
    with pytest.raises(ErrorRecurso) as exc_info:
        async with operacion_con_deadline(segundos=1):
            await asyncio.sleep(2)
            
    assert exc_info.value.codigo_recurso == "BACKEND"
    assert exc_info.value.mensaje == "La operación ha excedido el tiempo límite"

@pytest.mark.asyncio
async def test_deadline_operacion_exito():
    """Test que verifica que si termina a tiempo no hay error"""
    async with operacion_con_deadline(segundos=2):
        await asyncio.sleep(0.5)
    # Si llega aca sin excepcion, paso
    assert True
