
import sys
import os
import shutil
from pathlib import Path
from unittest.mock import MagicMock
from datetime import datetime, timedelta

# MOCK FLET
sys.modules['flet'] = MagicMock()

# PATH SETUP
current_dir = Path(__file__).parent
root_dir = current_dir.parent
sys.path.append(str(root_dir))
sys.path.insert(0, str(root_dir)) # Priority

print(f"ROOT: {root_dir}")

try:
    from src.infraestructura.persistencia.database import DatabaseManager
    from src.aplicacion.servicios.servicio_financiero import ServicioFinanciero
except ImportError as e:
    print(f"FATAL IMPORT ERROR: {e}")
    sys.exit(1)

DB_PATH = "test_manual.db"
DOCS_DIR = "test_manual_docs"
SCHEMA_PATH = root_dir / "DB_Inmo_Velar.txt"

def setup():
    print("SETUP...")
    global DB_PATH
    if os.path.exists(DB_PATH):
        try:
            os.remove(DB_PATH)
        except PermissionError:
            print("WARN: Cannot remove old DB file (locked). Using new name.")
            DB_PATH = f"test_manual_{os.getpid()}.db"

    if os.path.exists(DOCS_DIR):
        shutil.rmtree(DOCS_DIR)
        
    # Inicializar Singleton sin argumentos
    db_manager = DatabaseManager()
    # Sobrescribir path
    db_manager.database_path = Path(DB_PATH)
    # Reset connection pool just in case
    db_manager.cerrar_todas_conexiones()
    
    print(f"DB Path: {db_manager.database_path}")
    
    # Inicializar Schema
    if not SCHEMA_PATH.exists():
        print(f"ERROR: Schema not found at {SCHEMA_PATH}")
        sys.exit(1)
        
    db_manager.inicializar_base_datos(SCHEMA_PATH)
    
    servicio = ServicioFinanciero(db_manager)
    servicio.pdf_service.output_dir = Path(DOCS_DIR)
    servicio.pdf_service.output_dir.mkdir(exist_ok=True)
    
    # Insertar Datos de Prueba
    with db_manager.obtener_conexion() as conn:
        cursor = conn.cursor()
        
        # 1. Municipio (FK constraint)
        cursor.execute("INSERT OR IGNORE INTO MUNICIPIOS (ID_MUNICIPIO, NOMBRE_MUNICIPIO, DEPARTAMENTO) VALUES (1, 'Bogotá', 'Cundinamarca')")
        
        # 2. Personas
        cursor.execute("INSERT INTO PERSONAS (NOMBRE_COMPLETO, TIPO_DOCUMENTO, NUMERO_DOCUMENTO) VALUES ('Juan Propietario', 'CC', '1000')")
        id_prop = cursor.lastrowid
        cursor.execute("INSERT INTO PROPIETARIOS (ID_PERSONA) VALUES (?)", (id_prop,))
        id_propietario = cursor.lastrowid
        
        cursor.execute("INSERT INTO PERSONAS (NOMBRE_COMPLETO, TIPO_DOCUMENTO, NUMERO_DOCUMENTO) VALUES ('Pedro Inquilino', 'CC', '2000')")
        id_inq = cursor.lastrowid
        cursor.execute("INSERT INTO ARRENDATARIOS (ID_PERSONA) VALUES (?)", (id_inq,))
        id_arrendatario = cursor.lastrowid

        # 2b. Asesor
        cursor.execute("INSERT INTO PERSONAS (NOMBRE_COMPLETO, TIPO_DOCUMENTO, NUMERO_DOCUMENTO) VALUES ('Ana Asesor', 'CC', '3000')")
        id_asesor_p = cursor.lastrowid
        cursor.execute("INSERT INTO ASESORES (ID_PERSONA, COMISION_PORCENTAJE_VENTA, COMISION_PORCENTAJE_ARRIENDO) VALUES (?, 0, 0)", (id_asesor_p,))
        id_asesor = cursor.lastrowid

        # 3. Propiedad
        # Aseguramos columnas correctas según schema
        cursor.execute("""
            INSERT INTO PROPIEDADES (
                DIRECCION_PROPIEDAD, MATRICULA_INMOBILIARIA, AREA_M2, 
                CANON_ARRENDAMIENTO_ESTIMADO, ID_MUNICIPIO,
                TIPO_PROPIEDAD, ESTRATO, HABITACIONES, BANO, PARQUEADERO,
                VALOR_ADMINISTRACION, VALOR_VENTA_PROPIEDAD, COMISION_VENTA_PROPIEDAD,
                ESTADO_REGISTRO
            ) VALUES (
                'Calle Test 123', 'MAT-001', 50, 
                1000000, 1,
                'Apartamento', 3, 2, 1, 0,
                100000, 0, 0,
                1
            )
        """)
        id_propiedad = cursor.lastrowid
        
        today = datetime.now().strftime('%Y-%m-%d')
        next_year = (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d')

        # 4. Contrato Mandato
        cursor.execute("""
            INSERT INTO CONTRATOS_MANDATOS (
                ID_PROPIEDAD, ID_PROPIETARIO, ID_ASESOR,
                FECHA_INICIO_CONTRATO_M, FECHA_FIN_CONTRATO_M, DURACION_CONTRATO_M,
                ESTADO_CONTRATO_M, CANON_MANDATO, COMISION_PORCENTAJE_CONTRATO_M,
                IVA_CONTRATO_M
            ) VALUES (?, ?, ?, ?, ?, 12, 'Activo', 75000000, 1000, 0)
        """, (id_propiedad, id_propietario, id_asesor, today, next_year))
        id_contrato_m = cursor.lastrowid
        
        # 5. Contrato Arrendamiento
        # ID_CODEUDOR is nullable usually, we can skip or pass NULL
        cursor.execute("""
            INSERT INTO CONTRATOS_ARRENDAMIENTOS (
                ID_PROPIEDAD, ID_ARRENDATARIO,
                FECHA_INICIO_CONTRATO_A, FECHA_FIN_CONTRATO_A, DURACION_CONTRATO_A,
                ESTADO_CONTRATO_A,
                CANON_ARRENDAMIENTO, DEPOSITO
            ) VALUES (?, ?, ?, ?, 12, 'Activo', 75000000, 500000)
        """, (id_propiedad, id_arrendatario, today, next_year))
        id_contrato_a = cursor.lastrowid
        
        conn.commit()
        
    return servicio, id_contrato_a, id_contrato_m

def run_tests():
    servicio, id_a, id_m = setup()
    
    # TEST 1: MORA
    print("TEST 1: MORA...")
    mora = servicio.calcular_mora(id_a, "2024-02-05", "2024-02-15", 1000000)
    assert mora > 0, f"Mora deberia ser > 0, fue {mora}"
    print(f"  OK (Mora={mora})")
    
    # TEST 2: RECAUDO
    print("TEST 2: RECAUDO...")
    datos = {
        'id_contrato_a': id_a,
        'fecha_pago': '2024-02-05',
        'valor_total': 1000000,
        'metodo_pago': 'Transferencia',
        'referencia_bancaria': 'REF-123456'
    }
    conceptos = [{'tipo_concepto': 'Canon', 'periodo': '2024-02', 'valor': 1000000}]
    recaudo = servicio.registrar_recaudo(datos, conceptos, "TEST")
    assert recaudo.id_recaudo is not None
    print(f"  OK (ID={recaudo.id_recaudo})")
    
    # TEST 3: COMPROBANTE
    print("TEST 3: PDF RECAUDO...")
    path = servicio.generar_comprobante_pago(recaudo.id_recaudo)
    assert os.path.exists(path)
    print(f"  OK ({path})")
    
    # TEST 4: LIQUIDACION
    print("TEST 4: LIQUIDACION...")
    # Generar
    liq = servicio.generar_liquidacion_mensual(id_m, "2024-02", {'observaciones': 'Test'}, "TEST")
    print(f"  Liquidacion generada ID={liq.id_liquidacion}")
    assert liq.estado_liquidacion == 'En Proceso'
    
    # Aprobar
    servicio.aprobar_liquidacion(liq.id_liquidacion, "ADMIN")
    print("  Liquidacion aprobada")
    
    # Pagar
    servicio.marcar_liquidacion_pagada(liq.id_liquidacion, "2024-02-10", "Transf", "REF", "TESORERO")
    print("  Liquidacion pagada")
    
    # PDF
    path_liq = servicio.generar_estado_cuenta_pdf(liq.id_liquidacion)
    assert os.path.exists(path_liq)
    print(f"  OK ({path_liq})")
    
    print("\nALL TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    try:
        run_tests()
    except Exception as e:
        print(f"\nFAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
