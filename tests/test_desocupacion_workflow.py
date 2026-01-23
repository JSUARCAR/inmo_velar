"""
Test de Integración: Workflow de Desocupación Completo
Valida que al completar una desocupación:
1. El estado de la desocupación cambie a 'Completada'
2. El contrato cambie a 'Finalizado'
3. La propiedad cambie a 'Disponible'
"""

import pytest
import sqlite3
from datetime import datetime, date
import os
import sys

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tests.integration.test_database_manager import TestDatabaseManager
from src.aplicacion.servicios.servicio_desocupaciones import ServicioDesocupaciones


@pytest.fixture
def db_manager(tmp_path):
    """Fixture que crea una base de datos temporal para tests."""
    db_file = tmp_path / "test_desocupacion.db"
    manager = TestDatabaseManager(str(db_file))
    
    # Crear esquema básico
    with manager.obtener_conexion() as conn:
        cursor = conn.cursor()
        
        # Tabla MUNICIPIOS
        cursor.execute("""
            CREATE TABLE MUNICIPIOS (
                ID_MUNICIPIO INTEGER PRIMARY KEY,
                NOMBRE_MUNICIPIO TEXT
            )
        """)
        cursor.execute("INSERT INTO MUNICIPIOS VALUES (1, 'Bogotá')")
        
        # Tabla PROPIEDADES
        cursor.execute("""
            CREATE TABLE PROPIEDADES (
                ID_PROPIEDAD INTEGER PRIMARY KEY AUTOINCREMENT,
                MATRICULA_INMOBILIARIA TEXT UNIQUE,
                ID_MUNICIPIO INTEGER,
                DIRECCION_PROPIEDAD TEXT,
                TIPO_PROPIEDAD TEXT,
                DISPONIBILIDAD_PROPIEDAD INTEGER DEFAULT 0,
                AREA_M2 REAL,
                HABITACIONES INTEGER DEFAULT 0,
                BANO INTEGER DEFAULT 0,
                PARQUEADERO INTEGER DEFAULT 0,
                ESTRATO INTEGER,
                VALOR_ADMINISTRACION INTEGER DEFAULT 0,
                CANON_ARRENDAMIENTO_ESTIMADO INTEGER DEFAULT 0,
                VALOR_VENTA_PROPIEDAD INTEGER DEFAULT 0,
                COMISION_VENTA_PROPIEDAD INTEGER DEFAULT 0,
                OBSERVACIONES_PROPIEDAD TEXT,
                CODIGO_ENERGIA TEXT,
                CODIGO_AGUA TEXT,
                CODIGO_GAS TEXT,
                TELEFONO_ADMINISTRACION TEXT,
                TIPO_CUENTA_ADMINISTRACION TEXT,
                NUMERO_CUENTA_ADMINISTRACION TEXT,
                FECHA_INGRESO_PROPIEDAD TEXT,
                ESTADO_REGISTRO INTEGER DEFAULT 1,
                MOTIVO_INACTIVACION TEXT,
                CREATED_AT TEXT,
                CREATED_BY TEXT,
                UPDATED_AT TEXT,
                UPDATED_BY TEXT
            )
        """)
        
        # Tabla PERSONAS
        cursor.execute("""
            CREATE TABLE PERSONAS (
                ID_PERSONA INTEGER PRIMARY KEY AUTOINCREMENT,
                TIPO_PERSONA TEXT,
                NOMBRE_COMPLETO TEXT,
                NUMERO_DOCUMENTO TEXT,
                ESTADO_REGISTRO INTEGER DEFAULT 1
            )
        """)
        
        # Tabla ARRENDATARIOS
        cursor.execute("""
            CREATE TABLE ARRENDATARIOS (
                ID_ARRENDATARIO INTEGER PRIMARY KEY AUTOINCREMENT,
                ID_PERSONA INTEGER,
                FECHA_INGRESO TEXT
            )
        """)
        
        # Tabla CONTRATOS_ARRENDAMIENTOS
        cursor.execute("""
            CREATE TABLE CONTRATOS_ARRENDAMIENTOS (
                ID_CONTRATO_A INTEGER PRIMARY KEY AUTOINCREMENT,
                ID_PROPIEDAD INTEGER,
                ID_ARRENDATARIO INTEGER,
                FECHA_INICIO_CONTRATO_A TEXT,
                FECHA_FIN_CONTRATO_A TEXT,
                ESTADO_CONTRATO_A TEXT,
                CANON_MENSUAL REAL,
                MOTIVO_CANCELACION TEXT,
                CREATED_AT TEXT,
                CREATED_BY TEXT,
                UPDATED_AT TEXT,
                UPDATED_BY TEXT
            )
        """)
        
        # Tabla DESOCUPACIONES
        cursor.execute("""
            CREATE TABLE DESOCUPACIONES (
                ID_DESOCUPACION INTEGER PRIMARY KEY AUTOINCREMENT,
                ID_CONTRATO INTEGER,
                FECHA_SOLICITUD TEXT,
                FECHA_PROGRAMADA TEXT,
                FECHA_REAL TEXT,
                ESTADO TEXT,
                OBSERVACIONES TEXT,
                CREATED_AT TEXT,
                CREATED_BY TEXT,
                UPDATED_AT TEXT,
                UPDATED_BY TEXT
            )
        """)
        
        # Tabla TAREAS_DESOCUPACION
        cursor.execute("""
            CREATE TABLE TAREAS_DESOCUPACION (
                ID_TAREA INTEGER PRIMARY KEY AUTOINCREMENT,
                ID_DESOCUPACION INTEGER,
                DESCRIPCION TEXT,
                ORDEN INTEGER,
                COMPLETADA INTEGER DEFAULT 0,
                FECHA_COMPLETADA TEXT,
                RESPONSABLE TEXT,
                OBSERVACIONES TEXT
            )
        """)
        
        conn.commit()
    
    return manager


def test_finalizar_desocupacion_actualiza_propiedad(db_manager):
    """
    Test: Verificar que al finalizar una desocupación, la propiedad se marca como Disponible.
    """
    servicio = ServicioDesocupaciones(db_manager)
    
    # SETUP: Crear datos de prueba
    with db_manager.obtener_conexion() as conn:
        cursor = conn.cursor()
        
        # 1. Crear propiedad (OCUPADA inicialmente)
        cursor.execute("""
            INSERT INTO PROPIEDADES 
            (MATRICULA_INMOBILIARIA, ID_MUNICIPIO, DIRECCION_PROPIEDAD, 
             TIPO_PROPIEDAD, DISPONIBILIDAD_PROPIEDAD, AREA_M2, CREATED_BY)
            VALUES ('MAT-001', 1, 'Calle 123 #45-67', 'Apartamento', 0, 80.5, 'test')
        """)
        id_propiedad = cursor.lastrowid
        
        # 2. Crear persona/arrendatario
        cursor.execute("""
            INSERT INTO PERSONAS (TIPO_PERSONA, NOMBRE_COMPLETO, NUMERO_DOCUMENTO)
            VALUES ('Natural', 'Juan Pérez', '1234567890')
        """)
        id_persona = cursor.lastrowid
        
        cursor.execute("""
            INSERT INTO ARRENDATARIOS (ID_PERSONA, FECHA_INGRESO)
            VALUES (?, ?)
        """, (id_persona, date.today().isoformat()))
        id_arrendatario = cursor.lastrowid
        
        # 3. Crear contrato ACTIVO
        cursor.execute("""
            INSERT INTO CONTRATOS_ARRENDAMIENTOS 
            (ID_PROPIEDAD, ID_ARRENDATARIO, FECHA_INICIO_CONTRATO_A, 
             FECHA_FIN_CONTRATO_A, ESTADO_CONTRATO_A, CANON_MENSUAL, CREATED_BY)
            VALUES (?, ?, ?, ?, 'Activo', 1000000, 'test')
        """, (id_propiedad, id_arrendatario, '2024-01-01', '2025-01-01'))
        id_contrato = cursor.lastrowid
        
        # 4. Crear desocupación EN PROCESO
        cursor.execute("""
            INSERT INTO DESOCUPACIONES 
            (ID_CONTRATO, FECHA_SOLICITUD, FECHA_PROGRAMADA, ESTADO, CREATED_BY)
            VALUES (?, ?, ?, 'En Proceso', 'test')
        """, (id_contrato, date.today().isoformat(), date.today().isoformat()))
        id_desocupacion = cursor.lastrowid
        
        # 5. Crear tareas completadas (todas)
        tareas = [
            "Inspección inicial del inmueble",
            "Verificación de servicios públicos",
            "Revisión de inventario",
            "Acta de entrega firmada"
        ]
        for i, desc in enumerate(tareas, 1):
            cursor.execute("""
                INSERT INTO TAREAS_DESOCUPACION 
                (ID_DESOCUPACION, DESCRIPCION, ORDEN, COMPLETADA, RESPONSABLE)
                VALUES (?, ?, ?, 1, 'test')
            """, (id_desocupacion, desc, i))
        
        conn.commit()
    
    # VERIFICAR ESTADO INICIAL
    with db_manager.obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT DISPONIBILIDAD_PROPIEDAD FROM PROPIEDADES WHERE ID_PROPIEDAD = ?", (id_propiedad,))
        assert cursor.fetchone()[0] == 0, "Propiedad debe estar OCUPADA (0) inicialmente"
    
    # ACTION: Finalizar desocupación
    servicio.finalizar_desocupacion(id_desocupacion, usuario="test_user")
    
    # ASSERTIONS: Verificar resultados
    with db_manager.obtener_conexion() as conn:
        cursor = conn.cursor()
        
        # 1. Verificar que desocupación está Completada
        cursor.execute("SELECT ESTADO FROM DESOCUPACIONES WHERE ID_DESOCUPACION = ?", (id_desocupacion,))
        estado_desocupacion = cursor.fetchone()[0]
        assert estado_desocupacion == "Completada", f"Desocupación debe estar 'Completada', pero está '{estado_desocupacion}'"
        
        # 2. Verificar que contrato está Finalizado
        cursor.execute("SELECT ESTADO_CONTRATO_A FROM CONTRATOS_ARRENDAMIENTOS WHERE ID_CONTRATO_A = ?", (id_contrato,))
        estado_contrato = cursor.fetchone()[0]
        assert estado_contrato == "Finalizado", f"Contrato debe estar 'Finalizado', pero está '{estado_contrato}'"
        
        # 3. Verificar que propiedad está DISPONIBLE ✅ (ESTE ES EL FIX)
        cursor.execute("SELECT DISPONIBILIDAD_PROPIEDAD FROM PROPIEDADES WHERE ID_PROPIEDAD = ?", (id_propiedad,))
        disponibilidad = cursor.fetchone()[0]
        assert disponibilidad == 1, f"Propiedad debe estar DISPONIBLE (1), pero está {disponibilidad}"
        
        # 4. Verificar que el updated_by se registró correctamente
        cursor.execute("SELECT UPDATED_BY FROM PROPIEDADES WHERE ID_PROPIEDAD = ?", (id_propiedad,))
        updated_by = cursor.fetchone()[0]
        assert updated_by == "test_user", f"UPDATED_BY debe ser 'test_user', pero es '{updated_by}'"
    
    print("[OK] Test PASSED: La propiedad se marcó correctamente como Disponible")


if __name__ == "__main__":
    # Ejecutar test directamente
    import sys
    sys.exit(pytest.main([__file__, "-v", "-s"]))
