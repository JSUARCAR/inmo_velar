"""
Diagnóstico: Simula EXACTAMENTE el flujo de save_contrato de la UI
para depurar por qué la cascada no actualiza canon en Propiedad/Mandato.

Reproduce el diccionario `datos` tal como lo construye ContratosState.save_contrato.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.infraestructura.persistencia.database import db_manager
from src.aplicacion.servicios.servicio_contratos import ServicioContratos


def test_simular_flujo_ui():
    servicio = ServicioContratos(db_manager)
    
    # 1. Obtener un contrato de arrendamiento real
    arriendos = servicio.listar_arrendamientos()
    if not arriendos:
        print("❌ No hay arriendos disponibles")
        return

    arriendo_resumen = arriendos[0]
    id_contrato = arriendo_resumen["id"]
    print(f"📋 Contrato ID: {id_contrato}")

    # 2. Obtener el contrato completo (como hace open_edit_modal)
    contrato = servicio.obtener_arrendamiento_por_id(id_contrato)
    if not contrato:
        print(f"❌ No se encontró contrato {id_contrato}")
        return

    canon_original = contrato.canon_arrendamiento
    print(f"   Canon original: {canon_original} (tipo: {type(canon_original).__name__})")

    # 3. Obtener estado ANTES de la cascada
    propiedad_antes = servicio.repo_propiedad.obtener_por_id(contrato.id_propiedad)
    mandato_antes = servicio.repo_mandato.obtener_activo_por_propiedad(contrato.id_propiedad)
    
    canon_propiedad_antes = propiedad_antes.canon_arrendamiento_estimado if propiedad_antes else None
    canon_mandato_antes = mandato_antes.canon_mandato if mandato_antes else None
    
    print(f"   Canon Propiedad ANTES: {canon_propiedad_antes} (tipo: {type(canon_propiedad_antes).__name__ if canon_propiedad_antes is not None else 'None'})")
    print(f"   Canon Mandato ANTES:   {canon_mandato_antes} (tipo: {type(canon_mandato_antes).__name__ if canon_mandato_antes is not None else 'None'})")

    # 4. Simular form_data EXACTAMENTE como lo construye open_edit_modal
    # (líneas 706-716 de contratos_state.py)
    form_data_from_state = {
        "id_propiedad": str(contrato.id_propiedad),
        "id_arrendatario": str(contrato.id_arrendatario),
        "id_codeudor": str(contrato.id_codeudor or ""),
        "fecha_inicio": contrato.fecha_inicio_contrato_a,
        "fecha_fin": contrato.fecha_fin_contrato_a,
        "duracion_meses": str(contrato.duracion_contrato_a),
        "canon": str(contrato.canon_arrendamiento),
        "deposito": str(contrato.deposito),
        "fecha_pago": contrato.fecha_pago or "",
    }

    # Simular el HTML form_data (podría estar vacío o parcial)
    html_form_data = {}

    # 5. Merge tal como lo hace save_contrato (línea 763)
    full_data = {**form_data_from_state, **html_form_data}

    # 6. Simular cambio de canon (el usuario cambia el valor en el form)
    nuevo_canon = int(float(full_data["canon"])) + 10000
    full_data["canon"] = str(nuevo_canon)
    print(f"\n🔧 Simulando cambio de canon a: {nuevo_canon}")

    # 7. Construir `datos` EXACTAMENTE como lo hace save_contrato (líneas 793-805)
    datos = {
        "id_propiedad": int(full_data["id_propiedad"]),
        "id_arrendatario": int(full_data["id_arrendatario"]),
        "id_codeudor": int(full_data["id_codeudor"]) if full_data.get("id_codeudor") else None,
        "fecha_inicio": full_data["fecha_inicio"],
        "fecha_fin": full_data["fecha_fin"],
        "canon": int(full_data.get("canon") or 0),
        "deposito": int(full_data.get("deposito") or 0),
        "duracion_meses": int(full_data.get("duracion_meses") or 12),
        "fecha_pago": full_data.get("fecha_pago", ""),
    }

    print(f"\n📦 Diccionario 'datos' enviado al servicio:")
    for k, v in datos.items():
        print(f"   {k}: {v!r} (tipo: {type(v).__name__})")

    # 8. Llamar al servicio IGUAL que la UI
    print(f"\n🚀 Llamando servicio.actualizar_arrendamiento({id_contrato}, datos, 'admin')")
    try:
        servicio.actualizar_arrendamiento(id_contrato, datos, "admin")
        print("✅ Actualización completada sin errores")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return

    # 9. Verificar estado DESPUÉS
    contrato_despues = servicio.obtener_arrendamiento_por_id(id_contrato)
    propiedad_despues = servicio.repo_propiedad.obtener_por_id(contrato.id_propiedad)
    mandato_despues = servicio.repo_mandato.obtener_activo_por_propiedad(contrato.id_propiedad)

    canon_arr_despues = contrato_despues.canon_arrendamiento if contrato_despues else None
    canon_prop_despues = propiedad_despues.canon_arrendamiento_estimado if propiedad_despues else None
    canon_mand_despues = mandato_despues.canon_mandato if mandato_despues else None

    print(f"\n📊 RESULTADOS DE CASCADA:")
    print(f"   Canon Arrendamiento: {canon_original} → {canon_arr_despues} {'✅' if canon_arr_despues == nuevo_canon else '❌ NO SE ACTUALIZÓ'}")
    print(f"   Canon Propiedad:     {canon_propiedad_antes} → {canon_prop_despues} {'✅' if canon_prop_despues == nuevo_canon else '❌ NO SE ACTUALIZÓ'}")
    print(f"   Canon Mandato:       {canon_mandato_antes} → {canon_mand_despues} {'✅' if canon_mand_despues == nuevo_canon else '❌ NO SE ACTUALIZÓ'}")

    # 10. Debugging detallado: ¿Cuál fue la comparación exacta?
    print(f"\n🔍 DEBUGGING TIPOS DE COMPARACIÓN:")
    print(f"   canon_anterior (del repo) = {canon_original!r} (tipo: {type(canon_original).__name__})")
    print(f"   datos['canon'] = {datos['canon']!r} (tipo: {type(datos['canon']).__name__})")
    print(f"   ¿Son iguales? {datos['canon'] == canon_original} (== test)")
    print(f"   ¿Son distintos? {datos['canon'] != canon_original} (comparación que activa cascada)")

    # 11. REVERTIR cambios
    print(f"\n🔄 Revirtiendo canon a: {canon_original}")
    datos_revertir = datos.copy()
    datos_revertir["canon"] = canon_original
    servicio.actualizar_arrendamiento(id_contrato, datos_revertir, "admin")
    
    # Verificar reversión
    contrato_final = servicio.obtener_arrendamiento_por_id(id_contrato)
    print(f"   Canon final: {contrato_final.canon_arrendamiento if contrato_final else 'ERROR'}")
    print(f"\n✅ Test completado y datos revertidos")


if __name__ == "__main__":
    test_simular_flujo_ui()
