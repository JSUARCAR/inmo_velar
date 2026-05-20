"""
Script de Prueba Élite: Verificación de Sincronización en Cascada y Transaccionalidad
Garantiza que Arrendamiento -> Propiedad -> Mandato funcionen como un átomo.
"""
import os
import sys
from datetime import datetime

# Añadir raíz al path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.infraestructura.persistencia.database import db_manager
from src.aplicacion.servicios.servicio_contratos import ServicioContratos
from src.infraestructura.persistencia.repositorio_contrato_arrendamiento_postgres import RepositorioContratoArrendamientoPostgres
from src.infraestructura.persistencia.repositorio_contrato_mandato_postgres import RepositorioContratoMandatoPostgres
from src.infraestructura.persistencia.repositorio_propiedad_postgres import RepositorioPropiedadPostgres
from src.infraestructura.persistencia.repositorio_renovacion_postgres import RepositorioRenovacionPostgres
from src.infraestructura.persistencia.repositorio_ipc_postgres import RepositorioIPCPostgres
from src.infraestructura.persistencia.repositorio_arrendatario_postgres import RepositorioArrendatarioPostgres
from src.infraestructura.persistencia.repositorio_codeudor_postgres import RepositorioCodeudorPostgres

def test_sincronizacion_cascada():
    print("\n🚀 INICIANDO TEST DE SINCRONIZACIÓN EN CASCADA...")
    
    # 1. Setup inicial (buscar una propiedad con arriendo y mandato activos)
    repo_m = RepositorioContratoMandatoPostgres(db_manager)
    repo_a = RepositorioContratoArrendamientoPostgres(db_manager)
    repo_p = RepositorioPropiedadPostgres(db_manager)
    
    servicio = ServicioContratos(
        db_manager, repo_m, repo_a, repo_p, 
        RepositorioRenovacionPostgres(db_manager),
        RepositorioIPCPostgres(db_manager),
        RepositorioArrendatarioPostgres(db_manager),
        RepositorioCodeudorPostgres(db_manager)
    )

    # Buscar un arriendo activo para probar
    with db_manager.obtener_conexion() as conn:
        cursor = db_manager.get_dict_cursor(conn)
        cursor.execute("SELECT ID_CONTRATO_A, ID_PROPIEDAD FROM CONTRATOS_ARRENDAMIENTOS WHERE ESTADO_CONTRATO_A = 'Activo' LIMIT 1")
        row = cursor.fetchone()
        
    if not row:
        print("❌ ERROR: No se encontró ningún contrato de arrendamiento activo para la prueba.")
        return

    id_arriendo = row['ID_CONTRATO_A']
    id_propiedad = row['ID_PROPIEDAD']
    
    print(f"🔹 Usando Arriendo ID: {id_arriendo} en Propiedad ID: {id_propiedad}")

    # Verificar si tiene mandato activo
    mandato = repo_m.obtener_activo_por_propiedad(id_propiedad)
    if not mandato:
        print("⚠️ Advertencia: No hay mandato activo para esta propiedad. La cascada hacia mandato no se probará.")
    else:
        print(f"🔹 Mandato Asociado Encontrado: {mandato.id_contrato_m} (Canon: {mandato.canon_mandato})")

    # 2. PROBAR ACTUALIZACIÓN DE CANON
    nuevo_canon = 1500000 + (id_arriendo % 100) # Valor determinístico para el test
    print(f"🛠️ Aplicando nuevo canon: ${nuevo_canon}...")
    
    try:
        servicio.actualizar_arrendamiento(id_arriendo, {"canon": nuevo_canon}, "test_user")
        
        # Validar Arriendo
        a_updated = repo_a.obtener_por_id(id_arriendo)
        print(f"✅ Arriendo actualizado: {a_updated.canon_arrendamiento == nuevo_canon}")
        
        # Validar Propiedad
        p_updated = repo_p.obtener_por_id(id_propiedad)
        print(f"✅ Propiedad sincronizada: {p_updated.canon_arrendamiento_estimado == nuevo_canon}")
        
        # Validar Mandato
        if mandato:
            m_updated = repo_m.obtener_por_id(mandato.id_contrato_m)
            print(f"✅ Mandato sincronizado: {m_updated.canon_mandato == nuevo_canon}")
            
    except Exception as e:
        print(f"❌ FALLO EN ACTUALIZACIÓN: {e}")

    # 3. PROBAR ACTUALIZACIÓN DE FECHAS
    nueva_f_inicio = "2026-01-01"
    nueva_f_fin = "2026-12-31"
    print(f"🛠️ Sincronizando fechas: {nueva_f_inicio} -> {nueva_f_fin}...")
    
    try:
        servicio.actualizar_arrendamiento(id_arriendo, {
            "fecha_inicio": nueva_f_inicio,
            "fecha_fin": nueva_f_fin,
            "duracion_meses": 12
        }, "test_user")
        
        if mandato:
            m_updated = repo_m.obtener_por_id(mandato.id_contrato_m)
            check = (m_updated.fecha_inicio_contrato_m == nueva_f_inicio and 
                     m_updated.fecha_fin_contrato_m == nueva_f_fin)
            print(f"✅ Fechas Mandato sincronizadas: {check}")
            if not check:
                print(f"   (Esperado: {nueva_f_inicio}/{nueva_f_fin}, Obtenido: {m_updated.fecha_inicio_contrato_m}/{m_updated.fecha_fin_contrato_m})")
    except Exception as e:
        print(f"❌ FALLO EN FECHAS: {e}")

    # 4. PROBAR TRANSACCIONALIDAD (ROLLBACK)
    print("🛠️ Probando atomicidad (Rollback inducido)...")
    try:
        # Intentar actualizar con una fecha inválida (provocará error en validación coherencia)
        # Esto debería revertir cualquier cambio (si lo hubiéramos hecho antes del error)
        # Pero mejor probamos inyectando un error después de un update exitoso si pudiéramos.
        
        # Simulamos un error de BD mediante un ID de propiedad inexistente en un update manual
        with db_manager.transaccion() as conn:
            # Update 1: Exitoso
            cursor = conn.cursor()
            cursor.execute("UPDATE CONTRATOS_ARRENDAMIENTOS SET CANON_ARRENDAMIENTO = 999999 WHERE ID_CONTRATO_A = %s", (id_arriendo,))
            
            print("   -> Update 1 ejecutado (canon temporal 999999)")
            
            # Update 2: FALLO (Violación de FK o error sintáctico)
            print("   -> Induciendo error SQL...")
            cursor.execute("UPDATE TABLA_QUE_NO_EXISTE SET X = 1")
            
    except Exception as e:
        print(f"✅ Capturado error esperado: {str(e)[:50]}...")
        
        # Verificar que el canon NO es 999999 (Rollback funcionó)
        a_final = repo_a.obtener_por_id(id_arriendo)
        if a_final.canon_arrendamiento != 999999:
            print("✅ TEST DE ROLLBACK EXITOSO: El canon no cambió permanentemente.")
        else:
            print("❌ FALLO DE TRANSACCIONALIDAD: El cambio se persistió a pesar del error.")

    print("\n🏁 TEST FINALIZADO.")

if __name__ == "__main__":
    test_sincronizacion_cascada()
