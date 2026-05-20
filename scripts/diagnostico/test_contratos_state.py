import sys
import os
import asyncio
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.infraestructura.persistencia.database import db_manager
from src.aplicacion.servicios.servicio_contratos import ServicioContratos
from src.presentacion_reflex.state.contratos_state import ContratosState
import reflex as rx

async def test_ui_edit():
    state = ContratosState()
    # Mocking some basic stuff if necessary
    
    # 1. Fetch valid arrendamiento
    servicio = ServicioContratos(db_manager)
    arriendos = servicio.listar_arrendamientos()
    if not arriendos:
        print("No hay arriendos")
        return
    id_arriendo = arriendos[0]["id"]
    
    # 2. Simulate open_edit_modal
    print(f"Abriendo modal para ID: {id_arriendo}")
    try:
        await state.open_edit_modal(id_arriendo, "Arrendamiento")
        print("open_edit_modal exitoso")
    except Exception as e:
        print(f"Error en open_edit_modal: {e}")
        import traceback
        traceback.print_exc()
        return

    # 3. Simulate save_contrato
    print("Simulando save_contrato...")
    state.form_data["canon"] = str(int(float(state.form_data["canon"])) + 5000)
    
    try:
        # save_contrato es un generator porque tiene yields
        generator = state.save_contrato(state.form_data)
        async for item in generator:
            print(f"Yield: {item}")
        print("save_contrato exitoso")
    except Exception as e:
        print(f"Error en save_contrato: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_ui_edit())
