
import sys
import os
import sqlite3
from datetime import datetime, date

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.infraestructura.persistencia.database import DatabaseManager
from src.aplicacion.servicios.servicio_contratos import ServicioContratos
from src.dominio.entidades.contrato_arrendamiento import ContratoArrendamiento
from src.dominio.entidades.ipc import IPC
from src.infraestructura.persistencia.repositorio_ipc_sqlite import RepositorioIPCSQLite

def setup_test_data(db):
    """Crea datos de prueba: Propiedad, IPC y Contrato por vencer."""
    print("--- Configurando Datos de Prueba ---")
    
    # 1. IPC (Si no existe, crear uno alto para notar el cambio)
    repo_ipc = RepositorioIPCSQLite(db)
    ipc = IPC(anio=2024, valor_ipc=10, fecha_publicacion="2025-01-01") # 10% incremento
    try:
        repo_ipc.crear(ipc, "test_script")
        print(f"IPC Creado: 10%")
    except:
        print("IPC ya existe o error creando (ignorable si ya hay datos)")

    # 1.5. Municipio Dummy (FK para Propiedad)
    with db.obtener_conexion() as conn:
        cursor = conn.cursor()
        # En entidad Municipio, DEPARTAMENTO es string, no ID
        cursor.execute("INSERT OR IGNORE INTO MUNICIPIOS (ID_MUNICIPIO, NOMBRE_MUNICIPIO, DEPARTAMENTO, ESTADO_REGISTRO) VALUES (99999, 'MUNICIPIO TEST', 'DEPARTAMENTO TEST', 1)")
        conn.commit()
    
    # 2. Insertar Propiedad Dummy
    with db.obtener_conexion() as conn:
        cursor = conn.cursor()
        # ID_MUNICIPIO es requerido FK
        # Agregamos TIPO_PROPIEDAD, AREA_M2, ESTRATO, CANON ESTIMADO para evitar errores de constraints
        cursor.execute("""
            INSERT OR IGNORE INTO PROPIEDADES (
                MATRICULA_INMOBILIARIA, DIRECCION_PROPIEDAD, ESTADO_REGISTRO, ID_MUNICIPIO, 
                TIPO_PROPIEDAD, AREA_M2, ESTRATO, DISPONIBILIDAD_PROPIEDAD, CANON_ARRENDAMIENTO_ESTIMADO
            ) VALUES (
                'TEST-RENOV-001', 'Calle Falsa 123 - Test Renov', 1, 99999,
                'Apartamento', 60.0, 3, 1, 1000000
            )
        """)
        conn.commit()
        cursor.execute("SELECT ID_PROPIEDAD FROM PROPIEDADES WHERE MATRICULA_INMOBILIARIA = 'TEST-RENOV-001'")
        row = cursor.fetchone()
        if not row:
             raise Exception("No se pudo crear/encontrar la Propiedad de prueba")
        id_propiedad = row[0]
        
        # Arrendatario Dummy
        cursor.execute("INSERT OR IGNORE INTO PERSONAS (NUMERO_DOCUMENTO, NOMBRE_COMPLETO) VALUES ('TEST-DOC', 'Juan Test Renov')")
        conn.commit()
        cursor.execute("SELECT ID_PERSONA FROM PERSONAS WHERE NUMERO_DOCUMENTO = 'TEST-DOC'")
        id_persona = cursor.fetchone()[0]
        cursor.execute("INSERT OR IGNORE INTO ARRENDATARIOS (ID_PERSONA) VALUES (?)", (id_persona,))
        conn.commit()
        cursor.execute("SELECT ID_ARRENDATARIO FROM ARRENDATARIOS WHERE ID_PERSONA = ?", (id_persona,))
        id_arrendatario = cursor.fetchone()[0]

    # 3. Contrato por vencer
    servicio = ServicioContratos(db)
    
    # Limpiar contratos previos de esa propiedad para el test
    with db.obtener_conexion() as conn:
        # TRIGGER impide DELETE. Actualizamos a 'Cancelado' para permitir crear uno nuevo.
        # TRIGGER exige Motivo si es Cancelado
        conn.execute("UPDATE CONTRATOS_ARRENDAMIENTOS SET ESTADO_CONTRATO_A = 'Cancelado', MOTIVO_CANCELACION = 'Reinicio Test Script' WHERE ID_PROPIEDAD = ? AND ESTADO_CONTRATO_A = 'Activo'", (id_propiedad,))
        conn.commit()

    datos_contrato = {
        "id_propiedad": id_propiedad,
        "id_arrendatario": id_arrendatario,
        "fecha_inicio": "2024-01-01",
        "fecha_fin": "2025-01-01", # Vence pronto/ya
        "duracion_meses": 12,
        "canon": 1000000, # 1 millon
        "deposito": 0
    }
    
    contrato = servicio.crear_arrendamiento(datos_contrato, "test_script")
    print(f"Contrato Creado ID: {contrato.id_contrato_a}, Canon: {contrato.canon_arrendamiento}")
    return contrato.id_contrato_a

def test_renovacion():
    db = DatabaseManager()
    servicio = ServicioContratos(db)
    
    print(f"DB Path: {db.database_path}")
    with db.obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='trigger'")
        print("Triggers encontrados:", cursor.fetchall())
        
    id_contrato = setup_test_data(db)
    
    print("\n--- Ejecutando Renovación ---")
    try:
        contrato_renovado = servicio.renovar_arrendamiento(id_contrato, "test_runner")
        
        print(f"Renovación Exitosa!")
        print(f"Nuevo Canon: {contrato_renovado.canon_arrendamiento} (Esperado: 1.100.000 si IPC=10%)")
        print(f"Nueva Fecha Fin: {contrato_renovado.fecha_fin_contrato_a} (Esperado: 2026-01-01 aprox)")
        
        # Verificar Historial
        with db.obtener_conexion() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM RENOVACIONES_CONTRATOS WHERE ID_CONTRATO_A = ?", (id_contrato,))
            rows = cursor.fetchall()
            print(f"\nHistorial de Renovaciones ({len(rows)} registros):")
            for r in rows:
                print(f" - Fecha: {r['FECHA_RENOVACION']}, Canon Ant: {r['CANON_ANTERIOR']}, Nuevo: {r['CANON_NUEVO']}")
                
        if contrato_renovado.canon_arrendamiento == 1100000:
             print("\n>>> RESULTADO: PASS (Cálculo Correcto)")
        else:
             print("\n>>> RESULTADO: WARNING (Verificar IPC utilizado)")

    except Exception as e:
        print(f">>> RESULTADO: FAIL - Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_renovacion()
