import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.infraestructura.persistencia.database import db_manager
from src.aplicacion.servicios.servicio_contratos import ServicioContratos

def test_cascada_full_dict():
    servicio = ServicioContratos(db_manager)
    arriendos = servicio.listar_arrendamientos()
    if not arriendos:
        print("No hay arriendos")
        return

    arriendo = arriendos[0]
    id_arriendo = arriendo["id"]
    canon_anterior = int(arriendo["canon"])
    print(f"Probando con contrato arriendo ID: {id_arriendo}, canon actual: {canon_anterior}")

    # Obtener el contrato completo de la bd
    contrato = servicio.servicio_arriendo.obtener_arrendamiento(id_arriendo)

    nuevo_canon = canon_anterior + 10000
    print(f"Actualizando a nuevo canon: {nuevo_canon}")

    datos = {
        "id_propiedad": contrato.id_propiedad,
        "id_arrendatario": contrato.id_arrendatario,
        "id_codeudor": contrato.id_codeudor,
        "fecha_inicio": contrato.fecha_inicio_contrato_a,
        "fecha_fin": contrato.fecha_fin_contrato_a,
        "canon": nuevo_canon,
        "deposito": contrato.deposito,
        "duracion_meses": contrato.duracion_contrato_a,
        "fecha_pago": contrato.fecha_pago,
    }
    
    try:
        servicio.actualizar_arrendamiento(id_arriendo, datos, "test_admin")
        print("Actualizacion exitosa.")
    except Exception as e:
        print(f"Error al actualizar: {e}")

    # Verificar cambios
    propiedad_despues = servicio.repo_propiedad.obtener_por_id(contrato.id_propiedad)
    mandato_despues = servicio.repo_mandato.obtener_activo_por_propiedad(contrato.id_propiedad)

    print(f"Propiedad despues: {propiedad_despues.canon_arrendamiento_estimado if propiedad_despues else 'None'}")
    print(f"Mandato despues: {mandato_despues.canon_mandato if mandato_despues else 'None'}")
    
    # Revertir cambios
    datos_revertir = datos.copy()
    datos_revertir["canon"] = canon_anterior
    servicio.actualizar_arrendamiento(id_arriendo, datos_revertir, "test_admin")

if __name__ == "__main__":
    test_cascada_full_dict()
