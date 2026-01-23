
import sys
import os
from datetime import datetime, timedelta

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.infraestructura.persistencia.database import DatabaseManager
from src.aplicacion.servicios.servicio_contratos import ServicioContratos

def test_ipc_alert_update_strategy():
    print(">>> INICIANDO TEST DE ALERTAS IPC (Update Encuesta) <<<")
    
    db = DatabaseManager()
    servicio = ServicioContratos(db)
    
    with db.obtener_conexion() as conn:
        cursor = conn.cursor()
        
        # 1. Buscar un contrato activo
        cursor.execute("""
            SELECT ID_CONTRATO_A, FECHA_INICIO_CONTRATO_A 
            FROM CONTRATOS_ARRENDAMIENTOS 
            WHERE ESTADO_CONTRATO_A = 'Activo'
            LIMIT 1
        """)
        row = cursor.fetchone()
        
        if not row:
            print("⚠️ SKIPPING: No hay contratos activos para probar.")
            return

        id_contrato = row[0]
        fecha_inicio_original = row[1]
        print(f"DEBUG: Contrato encontrado {id_contrato} con inicio {fecha_inicio_original}")

        # 2. Calcular fecha objetivo para triggers (en 60 dias)
        # Queremos que (Hoy + 60) == MM-DD de Fecha Inicio
        # Hoy = 2024-X-Y. Target = Hoy + 60.
        # Ajustamos la fecha de inicio del contrato para que su mes/dia coincida con Target
        
        target_date = datetime.now() + timedelta(days=60)
        # Forzar año anterior para que no sea futuro
        new_start_date = target_date.replace(year=datetime.now().year - 1)
        new_start_str = new_start_date.strftime("%Y-%m-%d")
        
        print(f"DEBUG: Actualizando contrato para iniciar en {new_start_str} (Target 60 dias: {target_date.strftime('%Y-%m-%d')})")
        
        try:
            # 3. UPDATE temporal
            cursor.execute("UPDATE CONTRATOS_ARRENDAMIENTOS SET FECHA_INICIO_CONTRATO_A = ? WHERE ID_CONTRATO_A = ?", (new_start_str, id_contrato))
            conn.commit()
            
            # 4. Ejecutar verificación
            servicio.verificar_vencimientos("test_script")
            
            # 5. Check Alerta
            cursor.execute("""
                SELECT TIPO_ALERTA, DESCRIPCION_ALERTA, CREATED_AT
                FROM ALERTAS 
                WHERE ID_ENTIDAD_RELACIONADA = ? 
                  AND TIPO_ENTIDAD = 'CONTRATO_ARRENDAMIENTO'
                  AND TIPO_ALERTA = 'Incremento IPC Anual'
                  AND date(CREATED_AT) = date('now')
            """, (id_contrato,))
            
            alerta = cursor.fetchone() # fetchone is distinct from existing ones if logic implies distinctness or we filter by time
            
            if alerta:
                print(f"✅ EXITO: Alerta generada: {alerta[0]} - {alerta[1]}")
            else:
                print("❌ FALLO: No se generó alerta.")
                
        finally:
            # 6. RESTORE
            print(f"DEBUG: Restaurando fecha original {fecha_inicio_original}")
            cursor.execute("UPDATE CONTRATOS_ARRENDAMIENTOS SET FECHA_INICIO_CONTRATO_A = ? WHERE ID_CONTRATO_A = ?", (fecha_inicio_original, id_contrato))
            # Limpiar alerta de prueba para no ensuciar
            cursor.execute("DELETE FROM ALERTAS WHERE ID_ENTIDAD_RELACIONADA = ? AND TIPO_ALERTA = 'Incremento IPC Anual' AND CREATED_BY = 'test_script'", (id_contrato,))
            conn.commit()

if __name__ == "__main__":
    test_ipc_alert_update_strategy()
