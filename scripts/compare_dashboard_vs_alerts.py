import os
import sys
from datetime import datetime

# Add root directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.infraestructura.persistencia.database import db_manager
from src.aplicacion.servicios.servicio_alertas import ServicioAlertas

def compare_data():
    print("=== Comparando Dashboard vs Alertas ===")
    
    try:
        # 1. Get data from VW_ALERTA_VENCIMIENTO_CONTRATOS (Dashboard source)
        print("\n[INFO] Datos de la VISTA (Dashboard):")
        with db_manager.obtener_conexion() as conn:
            cursor = db_manager.get_dict_cursor(conn)
            cursor.execute("SELECT * FROM VW_ALERTA_VENCIMIENTO_CONTRATOS")
            vista_rows = cursor.fetchall()
            print(f"Total en vista: {len(vista_rows)}")
            for r in vista_rows:
                print(f"  - {r['TIPO_CONTRATO']}: {r['DIRECCION']} | Vence: {r['FECHA_FIN']} | Dias: {r['DIAS_RESTANTES']}")

        # 2. Get data from ServicioAlertas (Notifications source)
        print("\n[INFO] Datos de ServicioAlertas (Notificaciones):")
        servicio = ServicioAlertas(db_manager)
        alertas = servicio.obtener_alertas()
        print(f"Total en alertas: {len(alertas)}")
        for a in alertas:
            if "Contrato" in a['tipo']:
                print(f"  - {a['tipo']}: {a['mensaje']} | Vence: {a['fecha']}")

        # 3. Analyze differences
        print("\n[ANALYSIS]")
        print("Checking Arrendamientos in ServicioContratos directly (90 days)...")
        # Ensure we are using 90 days as per my latest fix
        arr_vencen = servicio.servicio_contratos.listar_arrendamientos_por_vencer(90)
        print(f"Arrendamientos via Query (90 days): {len(arr_vencen)}")
        for i in arr_vencen:
             print(f"  - ID {i['id']}: {i['propiedad']} | Fin: {i['fecha_fin']}")

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    compare_data()
