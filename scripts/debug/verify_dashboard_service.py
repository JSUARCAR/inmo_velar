"""
Verification script to test ServicioDashboard methods return correct data.
Writes output to a file to avoid truncation.
"""
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.infraestructura.persistencia.database import DatabaseManager
from src.aplicacion.servicios.servicio_dashboard import ServicioDashboard

def main():
    output_file = "verify_dashboard_output.txt"
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("=== VERIFICACIÓN SERVICIO DASHBOARD ===\n\n")
        
        db = DatabaseManager()
        f.write(f"Database Path: {db.database_path}\n\n")
        
        svc = ServicioDashboard(db)
        
        # 1. Contratos Activos
        contratos = svc.obtener_total_contratos_activos()
        f.write(f"1. Contratos Activos: {contratos}\n")
        
        # 2. Tasa de Ocupación
        ocupacion = svc.obtener_tasa_ocupacion()
        f.write(f"2. Tasa de Ocupación: {ocupacion}\n")
        
        # 3. Flujo Caja Mes
        flujo = svc.obtener_flujo_caja_mes()
        f.write(f"3. Flujo Caja Mes: {flujo}\n")
        
        # 4. Cartera en Mora
        mora = svc.obtener_cartera_mora()
        f.write(f"4. Cartera en Mora: {mora}\n")
        
        # 5. Comisiones Pendientes
        comisiones = svc.obtener_comisiones_pendientes()
        f.write(f"5. Comisiones Pendientes: {comisiones}\n")
        
        # 6. Contratos por Vencer
        vencer = svc.obtener_contratos_por_vencer()
        f.write(f"6. Contratos por Vencer: {vencer}\n")
        
        # 7. Recibos Vencidos
        recibos = svc.obtener_recibos_vencidos_resumen()
        f.write(f"7. Recibos Vencidos: {recibos}\n")
        
        # 8. Evolución Recaudo
        evolucion = svc.obtener_evolucion_recaudo()
        f.write(f"8. Evolución Recaudo: {evolucion}\n")
        
        f.write("\n=== FIN VERIFICACIÓN ===\n")
    
    print(f"Output written to {output_file}")

if __name__ == "__main__":
    main()
