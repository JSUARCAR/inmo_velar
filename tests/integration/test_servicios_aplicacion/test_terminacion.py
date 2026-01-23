
import sys
import os
import sqlite3
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.infraestructura.configuracion.settings import obtener_configuracion
from src.infraestructura.persistencia.database import DatabaseManager
from src.aplicacion.servicios.servicio_contratos import ServicioContratos
from src.dominio.entidades.contrato_arrendamiento import ContratoArrendamiento

def test_terminacion_arriendo():
    try:
        config = obtener_configuracion()
        print(f"DB: {config.database_path}")
        db = DatabaseManager()
        servicio = ServicioContratos(db)
        
        # 1. SETUP: Borrar datos de prueba
        with db.obtener_conexion() as conn:
            c = conn.cursor()
            c.execute("DELETE FROM CONTRATOS_ARRENDAMIENTOS WHERE ID_PROPIEDAD=88888")
            # Restaurar propiedad disponible=0 (Ocupada)
            c.execute("UPDATE PROPIEDADES SET DISPONIBILIDAD_PROPIEDAD=0 WHERE ID_PROPIEDAD=88888")
            conn.commit()
            
            # Verificar propiedad dummy (del test anterior)
            c.execute("SELECT ID_PROPIEDAD, DISPONIBILIDAD_PROPIEDAD FROM PROPIEDADES WHERE MATRICULA_INMOBILIARIA='DEBUG-IPC'")
            row = c.fetchone()
            if not row:
                 # Crear si no existe
                 pass # Asumimos existe del script reproduce_issue.py
            else:
                 id_propiedad = row[0]
                 # Forzar ocupada (temporalmente)
                 c.execute("UPDATE PROPIEDADES SET DISPONIBILIDAD_PROPIEDAD=0 WHERE ID_PROPIEDAD=?", (id_propiedad,))
                 # CANCELAR contratos activos previos (Requiere motivo por trigger)
                 c.execute("UPDATE CONTRATOS_ARRENDAMIENTOS SET ESTADO_CONTRATO_A='Cancelado', MOTIVO_CANCELACION='Limpieza Test Script' WHERE ID_PROPIEDAD=?", (id_propiedad,))
                 conn.commit()
                 print(f"Propiedad {id_propiedad} limpiada (Cancelados previos).")

            # Arrendatario dummy
            c.execute("SELECT ID_ARRENDATARIO FROM ARRENDATARIOS LIMIT 1")
            id_arrendatario = c.fetchone()[0]

        # 2. CREAR CONTRATO ARRIENDO ACTIVO
        datos = {
            "id_propiedad": id_propiedad,
            "id_arrendatario": id_arrendatario,
            "fecha_inicio": "2024-01-01",
            "fecha_fin": "2025-01-01",
            "duracion_meses": 12,
            "canon": 1500000,
            "deposito": 0
        }
        print("Creando contrato arriendo...")
        contrato = servicio.crear_arrendamiento(datos, "test_term")
        print(f"Contrato creado ID: {contrato.id_contrato_a}, Estado: {contrato.estado_contrato_a}")

        # 3. TERMINAR CONTRATO
        motivo = "Terminación Anticipada TestScript"
        print(f"Terminando contrato con motivo: {motivo}...")
        servicio.terminar_arrendamiento(contrato.id_contrato_a, motivo, "test_term")
        
        # 4. VERIFICAR
        # A. Contrato
        c_fin = servicio.repo_arriendo.obtener_por_id(contrato.id_contrato_a)
        print(f"Estado Final: {c_fin.estado_contrato_a}")
        print(f"Motivo Final: {c_fin.motivo_cancelacion}")
        print(f"Fecha Fin Final: {c_fin.fecha_fin_contrato_a}")
        
        if c_fin.estado_contrato_a == 'Cancelado':
             print(">>> SUCCESS: Estado Cancelado.")
        else:
             print(">>> FAILURE: Estado incorrecto.")

        if c_fin.fecha_fin_contrato_a == datetime.now().strftime("%Y-%m-%d"):
             print(">>> SUCCESS: Fecha fin es HOY.")
        else:
             print(f">>> FAILURE: Fecha fin incorrecta {c_fin.fecha_fin_contrato_a}")
             
        # B. Propiedad Liberada
        p_fin = servicio.repo_propiedad.obtener_por_id(id_propiedad)
        print(f"Disponibilidad Propiedad: {p_fin.disponibilidad_propiedad}")
        
        if p_fin.disponibilidad_propiedad == 1:
             print(">>> SUCCESS: Propiedad LIBERADA.")
        else:
             print(">>> FAILURE: Propiedad sigue ocupada.")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_terminacion_arriendo()
