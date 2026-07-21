import pytest
from datetime import datetime
from src.infraestructura.persistencia.database import DatabaseManager
from src.infraestructura.persistencia.repositorio_contrato_mandato_postgres import RepositorioContratoMandatoPostgres
from src.infraestructura.persistencia.repositorio_contrato_arrendamiento_postgres import RepositorioContratoArrendamientoPostgres
from src.dominio.entidades.contrato_mandato import ContratoMandato
from src.dominio.entidades.contrato_arrendamiento import ContratoArrendamiento

TEST_MUNICIPIO_ID = 999998
TEST_PROPIEDAD_ID = 999998
TEST_PERSONA_ID = 999998
TEST_PERSONA_ASESOR_ID = 999999
TEST_PROPIETARIO_ID = 999998
TEST_ASESOR_ID = 999998

@pytest.fixture(scope="module")
def db():
    manager = DatabaseManager()
    yield manager

@pytest.fixture(scope="module")
def setup_data(db):
    conn = db.obtener_conexion()
    c = conn.cursor()
    
    # Limpiar datos anteriores
    c.execute("DELETE FROM CONTRATOS_ARRENDAMIENTOS WHERE ID_PROPIEDAD = %s", (TEST_PROPIEDAD_ID,))
    c.execute("DELETE FROM CONTRATOS_MANDATOS WHERE ID_PROPIEDAD = %s", (TEST_PROPIEDAD_ID,))
    
    # Crear Municipio
    c.execute("SELECT ID_MUNICIPIO FROM MUNICIPIOS WHERE ID_MUNICIPIO = %s", (TEST_MUNICIPIO_ID,))
    if not c.fetchone():
        c.execute("INSERT INTO MUNICIPIOS (ID_MUNICIPIO, NOMBRE_MUNICIPIO, DEPARTAMENTO, ESTADO_REGISTRO) VALUES (%s, 'MUNI TEST', 'DEP TEST', True)", (TEST_MUNICIPIO_ID,))
    
    # Crear Propiedad
    c.execute("SELECT ID_PROPIEDAD FROM PROPIEDADES WHERE ID_PROPIEDAD = %s", (TEST_PROPIEDAD_ID,))
    if not c.fetchone():
        c.execute("INSERT INTO PROPIEDADES (ID_PROPIEDAD, MATRICULA_INMOBILIARIA, DIRECCION_PROPIEDAD, ESTADO_REGISTRO, ID_MUNICIPIO, TIPO_PROPIEDAD, AREA_M2, ESTRATO, CANON_ARRENDAMIENTO_ESTIMADO) VALUES (%s, 'TEST-MAT', 'Calle Test', True, %s, 'Casa', 100, 4, 2000000)", (TEST_PROPIEDAD_ID, TEST_MUNICIPIO_ID))
    
    # Crear Persona Propietario
    c.execute("SELECT ID_PERSONA FROM PERSONAS WHERE ID_PERSONA = %s", (TEST_PERSONA_ID,))
    if not c.fetchone():
        c.execute("INSERT INTO PERSONAS (ID_PERSONA, NUMERO_DOCUMENTO, NOMBRE_COMPLETO) VALUES (%s, 'DOC-TEST-PROP', 'Prop Test')", (TEST_PERSONA_ID,))
        
    # Crear Propietario
    c.execute("SELECT ID_PROPIETARIO FROM PROPIETARIOS WHERE ID_PROPIETARIO = %s", (TEST_PROPIETARIO_ID,))
    if not c.fetchone():
        c.execute("INSERT INTO PROPIETARIOS (ID_PROPIETARIO, ID_PERSONA) VALUES (%s, %s)", (TEST_PROPIETARIO_ID, TEST_PERSONA_ID))
        
    # Crear Persona Asesor
    c.execute("SELECT ID_PERSONA FROM PERSONAS WHERE ID_PERSONA = %s", (TEST_PERSONA_ASESOR_ID,))
    if not c.fetchone():
        c.execute("INSERT INTO PERSONAS (ID_PERSONA, NUMERO_DOCUMENTO, NOMBRE_COMPLETO) VALUES (%s, 'DOC-TEST-ASE', 'Asesor Test')", (TEST_PERSONA_ASESOR_ID,))
        
    # Crear Asesor
    c.execute("SELECT ID_ASESOR FROM ASESORES WHERE ID_ASESOR = %s", (TEST_ASESOR_ID,))
    if not c.fetchone():
        c.execute("INSERT INTO ASESORES (ID_ASESOR, ID_PERSONA, COMISION_PORCENTAJE_ARRIENDO, COMISION_PORCENTAJE_VENTA) VALUES (%s, %s, 8, 3)", (TEST_ASESOR_ID, TEST_PERSONA_ASESOR_ID))

    conn.commit()
    
    yield {
        "id_propiedad": TEST_PROPIEDAD_ID,
        "id_propietario": TEST_PROPIETARIO_ID,
        "id_asesor": TEST_ASESOR_ID,
        "id_arrendatario": TEST_PERSONA_ID, # reused for arrendatario tests
        "id_codeudor": TEST_PERSONA_ASESOR_ID,
    }
    
    # Cleanup post-test
    c.execute("DELETE FROM CONTRATOS_ARRENDAMIENTOS WHERE ID_PROPIEDAD = %s", (TEST_PROPIEDAD_ID,))
    c.execute("DELETE FROM CONTRATOS_MANDATOS WHERE ID_PROPIEDAD = %s", (TEST_PROPIEDAD_ID,))
    conn.commit()

@pytest.fixture
def repo_mandato(db):
    return RepositorioContratoMandatoPostgres(db)

@pytest.fixture
def repo_arrendamiento(db):
    return RepositorioContratoArrendamientoPostgres(db)

def test_mandato_create_recovers_all_fields(repo_mandato, setup_data):
    """T010 [US1] Escribir test test_mandato_create_recovers_all_fields"""
    contrato = ContratoMandato(
        id_contrato_m=None,
        id_propiedad=setup_data["id_propiedad"],
        id_propietario=setup_data["id_propietario"],
        id_asesor=setup_data["id_asesor"],
        fecha_inicio_contrato_m="2024-01-01",
        fecha_fin_contrato_m="2025-01-01",
        duracion_contrato_m=12,
        canon_mandato=1000000,
        comision_porcentaje_contrato_m=10,
        iva_contrato_m=19,
        estado_contrato_m="Activo",
        banco_propietario="Bancolombia",
        numero_cuenta_propietario="123456789",
        tipo_cuenta="Ahorros",
        consignatario="Juan Perez",
        documento_consignatario="123456",
        enlace_video="https://youtube.com/test",
        motivo_cancelacion=None,
        alerta_vencimiento_contrato_m=True,
        fecha_renovacion_contrato_m=None,
        fecha_pago="10",
        grupo_operativo=1
    )
    nuevo = repo_mandato.crear(contrato, "test")
    assert nuevo.id_contrato_m is not None
    
    recuperado = repo_mandato.obtener_por_id(nuevo.id_contrato_m)
    assert recuperado.banco_propietario == "Bancolombia"
    assert recuperado.numero_cuenta_propietario == "123456789"
    assert recuperado.tipo_cuenta == "Ahorros"
    assert recuperado.consignatario == "Juan Perez"
    assert recuperado.documento_consignatario == "123456"
    assert recuperado.enlace_video == "https://youtube.com/test"

def test_mandato_update_persists_all_fields(repo_mandato, setup_data):
    """T011 [US1] Escribir test test_mandato_update_persists_all_fields"""
    contrato = ContratoMandato(
        id_contrato_m=None,
        id_propiedad=setup_data["id_propiedad"],
        id_propietario=setup_data["id_propietario"],
        id_asesor=setup_data["id_asesor"],
        fecha_inicio_contrato_m="2024-01-01",
        fecha_fin_contrato_m="2025-01-01",
        duracion_contrato_m=12,
        canon_mandato=1000000,
        comision_porcentaje_contrato_m=10,
        iva_contrato_m=19,
        estado_contrato_m="Activo",
        motivo_cancelacion=None,
        alerta_vencimiento_contrato_m=True,
        fecha_renovacion_contrato_m=None,
        fecha_pago="10",
        grupo_operativo=1,
        banco_propietario="Banco 1",
        numero_cuenta_propietario="000",
        tipo_cuenta="Corriente",
        consignatario="Inicial",
        documento_consignatario="000",
        enlace_video="https://vimeo.com/test"
    )
    nuevo = repo_mandato.crear(contrato, "test")
    
    # Update fields
    nuevo.banco_propietario = "Davivienda"
    nuevo.consignatario = "Maria Gomez"
    nuevo.enlace_video = "https://youtube.com/updated"
    
    res = repo_mandato.actualizar(nuevo, "test")
    assert res is True
    
    recuperado = repo_mandato.obtener_por_id(nuevo.id_contrato_m)
    assert recuperado.banco_propietario == "Davivienda"
    assert recuperado.consignatario == "Maria Gomez"
    assert recuperado.enlace_video == "https://youtube.com/updated"

def test_mandato_read_uppercase_columns(db, repo_mandato, setup_data):
    """T012 [US1] Escribir test test_mandato_read_uppercase_columns"""
    conn = db.obtener_conexion()
    c = conn.cursor()
    # Insert directly with specific uppercase columns to mock old records or strange cases
    c.execute("""
        INSERT INTO CONTRATOS_MANDATOS (
            ID_PROPIEDAD, ID_PROPIETARIO, ID_ASESOR, FECHA_INICIO_CONTRATO_M,
            FECHA_FIN_CONTRATO_M, DURACION_CONTRATO_M, CANON_MANDATO,
            COMISION_PORCENTAJE_CONTRATO_M, IVA_CONTRATO_M, ESTADO_CONTRATO_M,
            CONSIGNATARIO, DOCUMENTO_CONSIGNATARIO, ENLACE_VIDEO
        ) VALUES (
            %s, %s, %s, '2024-01-01', '2025-01-01', 12, 1000, 10, 19, 'Activo',
            'UPPERCASE CONSIG', '111222', 'https://upper.com'
        ) RETURNING ID_CONTRATO_M
    """, (setup_data["id_propiedad"], setup_data["id_propietario"], setup_data["id_asesor"]))
    row = c.fetchone()
    # Check if we got a dict or tuple
    if hasattr(row, 'keys'):
        new_id = row.get('id_contrato_m') or row.get('ID_CONTRATO_M') or (list(row.values())[0] if row else row[0])
    else:
        new_id = row[0]
    conn.commit()
    
    recuperado = repo_mandato.obtener_por_id(new_id)
    assert recuperado.consignatario == 'UPPERCASE CONSIG'
    assert recuperado.documento_consignatario == '111222'
    assert recuperado.enlace_video == 'https://upper.com'

def test_arrendamiento_create_recovers_all_fields(repo_arrendamiento, setup_data):
    """T013 [US2] Escribir test test_arrendamiento_create_recovers_all_fields"""
    contrato = ContratoArrendamiento(
        id_contrato_a=None,
        id_propiedad=setup_data["id_propiedad"],
        id_arrendatario=setup_data["id_arrendatario"],
        id_codeudor=setup_data["id_codeudor"],
        fecha_inicio_contrato_a="2024-01-01",
        fecha_fin_contrato_a="2025-01-01",
        duracion_contrato_a=12,
        canon_arrendamiento=1000000,
        deposito=500000,
        fecha_pago="5",
        grupo_operativo=1,
        estado_contrato_a="Vigente",
        alerta_vencimiento_contrato_a=True,
        alerta_ipc=True,
        fecha_renovacion_contrato_a=None,
        fecha_incremento_ipc=None,
        fecha_ultimo_incremento_ipc=None,
        motivo_cancelacion=None,
        enlace_video="https://youtube.com/arriendo",
        responsable_deposito_id=setup_data["id_asesor"]
    )
    nuevo = repo_arrendamiento.crear(contrato, "test")
    assert nuevo.id_contrato_a is not None
    
    recuperado = repo_arrendamiento.obtener_por_id(nuevo.id_contrato_a)
    assert recuperado.enlace_video == "https://youtube.com/arriendo"
    assert recuperado.responsable_deposito_id == setup_data["id_asesor"]

def test_arrendamiento_update_persists_all_fields(repo_arrendamiento, setup_data):
    """T014 [US2] Escribir test test_arrendamiento_update_persists_all_fields"""
    contrato = ContratoArrendamiento(
        id_contrato_a=None,
        id_propiedad=setup_data["id_propiedad"],
        id_arrendatario=setup_data["id_arrendatario"],
        id_codeudor=setup_data["id_codeudor"],
        fecha_inicio_contrato_a="2024-01-01",
        fecha_fin_contrato_a="2025-01-01",
        duracion_contrato_a=12,
        canon_arrendamiento=1000000,
        deposito=500000,
        fecha_pago="5",
        grupo_operativo=1,
        estado_contrato_a="Vigente",
        alerta_vencimiento_contrato_a=True,
        alerta_ipc=True,
        fecha_renovacion_contrato_a=None,
        fecha_incremento_ipc=None,
        fecha_ultimo_incremento_ipc=None,
        motivo_cancelacion=None,
        enlace_video="https://vimeo.com/arriendo",
        responsable_deposito_id=setup_data["id_asesor"]
    )
    nuevo = repo_arrendamiento.crear(contrato, "test")
    
    # Update fields
    nuevo.enlace_video = "https://youtube.com/updated-arriendo"
    nuevo.responsable_deposito_id = None
    
    res = repo_arrendamiento.actualizar(nuevo, "test")
    assert res is True
    
    recuperado = repo_arrendamiento.obtener_por_id(nuevo.id_contrato_a)
    assert recuperado.enlace_video == "https://youtube.com/updated-arriendo"
    assert recuperado.responsable_deposito_id is None

