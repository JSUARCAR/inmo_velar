
import sys
import os
import sqlite3
from datetime import datetime

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from src.infraestructura.configuracion.settings import obtener_configuracion
from src.infraestructura.persistencia.database import DatabaseManager
from src.aplicacion.servicios.servicio_contratos import ServicioContratos

def reproduce():
    try:
        config = obtener_configuracion()
        print(f"DB: {config.database_path}")
        db = DatabaseManager()
        servicio = ServicioContratos(db)
        
        # 1. Crear propiedad dummy
        print("Creando propiedad dummy...")
        with db.obtener_conexion() as conn:
            c = conn.cursor()
            c.execute("INSERT OR IGNORE INTO MUNICIPIOS (ID_MUNICIPIO, NOMBRE_MUNICIPIO, DEPARTAMENTO, ESTADO_REGISTRO) VALUES (88888, 'MUNI DEBUG', 'DEP DEBUG', 1)")
            c.execute("INSERT OR IGNORE INTO PROPIEDADES (MATRICULA_INMOBILIARIA, DIRECCION_PROPIEDAD, ESTADO_REGISTRO, ID_MUNICIPIO, TIPO_PROPIEDAD, AREA_M2, ESTRATO, DISPONIBILIDAD_PROPIEDAD, CANON_ARRENDAMIENTO_ESTIMADO) VALUES ('DEBUG-IPC', 'Calle Debug IPC', 1, 88888, 'Apartamento', 50, 3, 1, 1000000)")
            conn.commit()
            c.execute("SELECT ID_PROPIEDAD FROM PROPIEDADES WHERE MATRICULA_INMOBILIARIA='DEBUG-IPC'")
            id_propiedad = c.fetchone()[0]
            
            # Limpiar contratos viejos
            c.execute("UPDATE CONTRATOS_ARRENDAMIENTOS SET ESTADO_CONTRATO_A='Cancelado', MOTIVO_CANCELACION='Limpieza Debug' WHERE ID_PROPIEDAD=? AND ESTADO_CONTRATO_A='Activo'", (id_propiedad,))
            conn.commit()

            # Arrendatario
            c.execute("INSERT OR IGNORE INTO PERSONAS (NUMERO_DOCUMENTO, NOMBRE_COMPLETO) VALUES ('DEBUG-DOC', 'Pepe Debug')")
            conn.commit()
            c.execute("SELECT ID_PERSONA FROM PERSONAS WHERE NUMERO_DOCUMENTO='DEBUG-DOC'")
            id_persona = c.fetchone()[0]
            c.execute("INSERT OR IGNORE INTO ARRENDATARIOS (ID_PERSONA) VALUES (?)", (id_persona,))
            conn.commit()
            c.execute("SELECT ID_ARRENDATARIO FROM ARRENDATARIOS WHERE ID_PERSONA=?", (id_persona,))
            id_arrendatario = c.fetchone()[0]

        # 2. Crear Contrato con Canon 1.000.000
        datos = {
            "id_propiedad": id_propiedad,
            "id_arrendatario": id_arrendatario,
            "fecha_inicio": "2024-01-01",
            "fecha_fin": "2025-01-01",
            "duracion_meses": 12,
            "canon": 1000000,
            "deposito": 0
        }
        print("Creando contrato...")
        contrato = servicio.crear_arrendamiento(datos, "debug_script")
        print(f"Contrato creado ID: {contrato.id_contrato_a}, Canon: {contrato.canon_arrendamiento}")
        
        # 3. Renovar
        print("Ejecutando servicio.renovar_arrendamiento...")
        servicio.renovar_arrendamiento(contrato.id_contrato_a, "debug_script")
        
        # 4. Verificar en BD (bypass object cache)
        with db.obtener_conexion() as conn:
            c = conn.cursor()
            c.execute("SELECT CANON_ARRENDAMIENTO FROM CONTRATOS_ARRENDAMIENTOS WHERE ID_CONTRATO_A=?", (contrato.id_contrato_a,))
            canon_db = c.fetchone()[0]
            print(f"Canon en BD tras renovación: {canon_db}")
            
            if canon_db > 1000000:
                print(">>> SUCCESS: El canon aumentó.")
            else:
                print(">>> FAILURE: El canon NO aumentó.")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    reproduce()
