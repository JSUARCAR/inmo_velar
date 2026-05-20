"""
Diagnóstico: Verificar que save_contrato + repo actualizar funciona
Simula exactamente el flujo que haría la UI al editar un arrendamiento.
"""
import sys
import os
# Agregar raíz del proyecto al path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))

import logging
logging.basicConfig(level=logging.DEBUG, format='%(name)s - %(levelname)s - %(message)s')

from src.infraestructura.persistencia.database import db_manager
from src.aplicacion.servicios.servicio_contratos import ServicioContratos


def test_diagnóstico_save_contrato():
    """Simula el flujo EXACTO de save_contrato para arrendamiento."""
    servicio = ServicioContratos(db_manager)
    
    # 1. Obtener un contrato de arrendamiento existente
    contratos = servicio.listar_arrendamientos_paginado(page=1, page_size=1)
    if not contratos.items:
        print("❌ No hay contratos de arrendamiento")
        return
    
    item = contratos.items[0]
    id_contrato = item["id_contrato"]
    print(f"\n{'='*60}")
    print(f"📋 Contrato seleccionado: ID={id_contrato}")
    
    # 2. Obtener entidad completa
    arriendo = servicio.obtener_arrendamiento_por_id(id_contrato)
    if not arriendo:
        print("❌ No se pudo obtener el contrato")
        return
    
    canon_original = arriendo.canon_arrendamiento
    print(f"   Canon actual en BD: {canon_original} (tipo: {type(canon_original).__name__})")
    
    # 3. Simular EXACTAMENTE lo que hace save_contrato L793-804
    # Simulamos que el form_data HTML trae el canon con +10000
    nuevo_canon = canon_original + 10000
    
    # Así se construye 'datos' en save_contrato
    full_data = {
        "id_propiedad": str(arriendo.id_propiedad),
        "id_arrendatario": str(arriendo.id_arrendatario),
        "id_codeudor": str(arriendo.id_codeudor or ""),
        "fecha_inicio": arriendo.fecha_inicio_contrato_a,
        "fecha_fin": arriendo.fecha_fin_contrato_a,
        "duracion_meses": str(arriendo.duracion_contrato_a),
        "canon": str(nuevo_canon),  # El HTML siempre envía strings
        "deposito": str(arriendo.deposito),
        "fecha_pago": arriendo.fecha_pago or "",
    }
    
    # Construir 'datos' exactamente como save_contrato L793-804
    datos = {
        "id_propiedad": int(full_data["id_propiedad"]),
        "id_arrendatario": int(full_data["id_arrendatario"]),
        "id_codeudor": int(full_data["id_codeudor"])
        if full_data.get("id_codeudor")
        else None,
        "fecha_inicio": full_data["fecha_inicio"],
        "fecha_fin": full_data["fecha_fin"],
        "canon": int(full_data.get("canon") or 0),
        "deposito": int(full_data.get("deposito") or 0),
        "duracion_meses": int(full_data.get("duracion_meses") or 12),
        "fecha_pago": full_data.get("fecha_pago", ""),
    }
    
    print(f"\n🔧 Datos construidos (como save_contrato):")
    for k, v in datos.items():
        print(f"   {k}: {v} ({type(v).__name__})")
    
    # 4. Llamar al servicio
    print(f"\n🚀 Llamando servicio.actualizar_arrendamiento({id_contrato}, datos, 'admin')")
    try:
        servicio.actualizar_arrendamiento(id_contrato, datos, "admin")
        print("✅ Actualización exitosa")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 5. Verificar que el canon se actualizó
    arriendo_despues = servicio.obtener_arrendamiento_por_id(id_contrato)
    canon_despues = arriendo_despues.canon_arrendamiento if arriendo_despues else None
    
    print(f"\n📊 RESULTADO:")
    print(f"   Canon ANTES:   {canon_original}")
    print(f"   Canon DESPUÉS: {canon_despues}")
    print(f"   ¿Se actualizó? {'✅ SÍ' if canon_despues == nuevo_canon else '❌ NO'}")
    
    # 6. Revertir
    print(f"\n🔄 Revirtiendo canon a: {canon_original}")
    datos_revertir = {
        "id_propiedad": arriendo.id_propiedad,
        "id_arrendatario": arriendo.id_arrendatario,
        "id_codeudor": arriendo.id_codeudor,
        "fecha_inicio": arriendo.fecha_inicio_contrato_a,
        "fecha_fin": arriendo.fecha_fin_contrato_a,
        "duracion_meses": arriendo.duracion_contrato_a,
        "canon": canon_original,
        "deposito": arriendo.deposito,
        "fecha_pago": arriendo.fecha_pago or "",
    }
    servicio.actualizar_arrendamiento(id_contrato, datos_revertir, "admin")
    
    # Verificar reversión
    arriendo_final = servicio.obtener_arrendamiento_por_id(id_contrato)
    print(f"   Canon final: {arriendo_final.canon_arrendamiento}")
    print(f"   ¿Revertido? {'✅' if arriendo_final.canon_arrendamiento == canon_original else '❌'}")


if __name__ == "__main__":
    test_diagnóstico_save_contrato()
