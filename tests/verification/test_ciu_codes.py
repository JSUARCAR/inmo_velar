
import sqlite3
import unittest
import sys
import os
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(PROJECT_ROOT))

# Imports after path setup
from src.aplicacion.servicios.servicio_propiedades import ServicioPropiedades
from src.infraestructura.persistencia.database import DatabaseManager

class TestVerificacionCIU(unittest.TestCase):
    def setUp(self):
        # Create in-memory DB
        self.conn = sqlite3.connect(":memory:")
        self.conn.row_factory = sqlite3.Row
        
        # Enable FKs
        self.conn.execute("PRAGMA foreign_keys = ON")
        
        # Create Tables
        self.crear_tablas()
        
        # Setup Dependency Injection
        self.db_manager = DatabaseManager()
        # Mock connection to return our in-memory connection
        # We need to monkeypatch the instance that ServicioPropiedades will use
        self.db_manager.obtener_conexion = lambda: self.conn
        
        self.servicio = ServicioPropiedades(self.db_manager)

    def tearDown(self):
        self.conn.close()

    def crear_tablas(self):
        # MUNICIPIOS
        self.conn.execute("""
            CREATE TABLE MUNICIPIOS (
                ID_MUNICIPIO INTEGER PRIMARY KEY AUTOINCREMENT,
                NOMBRE_MUNICIPIO TEXT NOT NULL,
                DEPARTAMENTO TEXT NOT NULL,
                ESTADO_REGISTRO INTEGER DEFAULT 1
            )
        """)
        self.conn.execute("INSERT INTO MUNICIPIOS (NOMBRE_MUNICIPIO, DEPARTAMENTO) VALUES ('Medellín', 'Antioquia')")
        
        # PROPIEDADES with new columns
        self.conn.execute("""
            CREATE TABLE PROPIEDADES (
                ID_PROPIEDAD INTEGER PRIMARY KEY AUTOINCREMENT,
                MATRICULA_INMOBILIARIA TEXT NOT NULL UNIQUE,
                ID_MUNICIPIO INTEGER NOT NULL,
                DIRECCION_PROPIEDAD TEXT NOT NULL,
                TIPO_PROPIEDAD TEXT NOT NULL,
                DISPONIBILIDAD_PROPIEDAD INTEGER DEFAULT 1,
                AREA_M2 REAL NOT NULL,
                HABITACIONES INTEGER DEFAULT 0,
                BANO INTEGER DEFAULT 0,
                PARQUEADERO INTEGER DEFAULT 0,
                ESTRATO INTEGER,
                VALOR_ADMINISTRACION INTEGER DEFAULT 0,
                CANON_ARRENDAMIENTO_ESTIMADO INTEGER DEFAULT 0,
                VALOR_VENTA_PROPIEDAD INTEGER DEFAULT 0,
                COMISION_VENTA_PROPIEDAD INTEGER DEFAULT 0,
                OBSERVACIONES_PROPIEDAD TEXT,
                FECHA_INGRESO_PROPIETARIO TEXT,
                FECHA_INGRESO_PROPIEDAD TEXT DEFAULT (date('now')),
                ESTADO_REGISTRO INTEGER DEFAULT 1,
                MOTIVO_INACTIVACION TEXT,
                CREATED_AT TEXT DEFAULT (datetime('now')),
                CREATED_BY TEXT,
                UPDATED_AT TEXT DEFAULT (datetime('now')),
                UPDATED_BY TEXT,
                CODIGO_ENERGIA TEXT,
                CODIGO_AGUA TEXT,
                CODIGO_GAS TEXT,
                FOREIGN KEY (ID_MUNICIPIO) REFERENCES MUNICIPIOS(ID_MUNICIPIO)
            )
        """)

    def test_creacion_sin_ciu(self):
        print("\nCaso 1: Creación sin CIU")
        datos = {
            "matricula_inmobiliaria": "001-TEST",
            "id_municipio": 1,
            "direccion_propiedad": "Calle Test 123",
            "tipo_propiedad": "Apartamento",
            "area_m2": 50,
            "estrato": 3
        }
        propiedad = self.servicio.crear_propiedad(datos)
        self.assertIsNone(propiedad.codigo_energia)
        self.assertIsNone(propiedad.codigo_agua)
        self.assertIsNone(propiedad.codigo_gas)
        print("✅ Propiedad creada sin códigos correctamente")
        
        # Verify DB
        cursor = self.conn.execute("SELECT CODIGO_ENERGIA, CODIGO_AGUA, CODIGO_GAS FROM PROPIEDADES WHERE ID_PROPIEDAD = ?", (propiedad.id_propiedad,))
        row = cursor.fetchone()
        self.assertIsNone(row["CODIGO_ENERGIA"])
        print("✅ DB verificada: Valores NULL")

    def test_creacion_con_ciu(self):
        print("\nCaso 2: Creación con CIU")
        datos = {
            "matricula_inmobiliaria": "002-TEST",
            "id_municipio": 1,
            "direccion_propiedad": "Carrera Test 456",
            "tipo_propiedad": "Casa",
            "area_m2": 100,
            "estrato": 4,
            "codigo_energia": "E-123",
            "codigo_agua": "A-456",
            "codigo_gas": "G-789"
        }
        propiedad = self.servicio.crear_propiedad(datos)
        self.assertEqual(propiedad.codigo_energia, "E-123")
        self.assertEqual(propiedad.codigo_agua, "A-456")
        self.assertEqual(propiedad.codigo_gas, "G-789")
        print("✅ Propiedad creada con códigos correctamente")
        
        # Verify DB
        cursor = self.conn.execute("SELECT CODIGO_ENERGIA, CODIGO_AGUA, CODIGO_GAS FROM PROPIEDADES WHERE ID_PROPIEDAD = ?", (propiedad.id_propiedad,))
        row = cursor.fetchone()
        self.assertEqual(row["CODIGO_ENERGIA"], "E-123")
        self.assertEqual(row["CODIGO_AGUA"], "A-456")
        self.assertEqual(row["CODIGO_GAS"], "G-789")
        print("✅ DB verificada: Valores guardados")

    def test_edicion_agregar_ciu(self):
        print("\nCaso 3: Edición agregando CIU")
        # Create without
        datos = {
            "matricula_inmobiliaria": "003-TEST",
            "id_municipio": 1,
            "direccion_propiedad": "Transversal Test 789",
            "tipo_propiedad": "Local Comercial",
            "area_m2": 30
        }
        propiedad = self.servicio.crear_propiedad(datos)
        
        # Edit to add
        nuevo_datos = {"codigo_energia": "ADDED-E"}
        updated = self.servicio.actualizar_propiedad(propiedad.id_propiedad, nuevo_datos)
        self.assertEqual(updated.codigo_energia, "ADDED-E")
        print("✅ Propiedad actualizada con código agregado")
        
        # Verify DB
        cursor = self.conn.execute("SELECT CODIGO_ENERGIA FROM PROPIEDADES WHERE ID_PROPIEDAD = ?", (propiedad.id_propiedad,))
        row = cursor.fetchone()
        self.assertEqual(row["CODIGO_ENERGIA"], "ADDED-E")
        print("✅ DB verificada: Valor agregado")

    def test_edicion_modificar_ciu(self):
        print("\nCaso 4: Edición modificando CIU")
         # Create with
        datos = {
            "matricula_inmobiliaria": "004-TEST",
            "id_municipio": 1,
            "direccion_propiedad": "Diagonal Test 101",
            "tipo_propiedad": "Oficina",
            "area_m2": 40,
            "codigo_agua": "OLD-A"
        }
        propiedad = self.servicio.crear_propiedad(datos)
        
        # Edit
        updated = self.servicio.actualizar_propiedad(propiedad.id_propiedad, {"codigo_agua": "NEW-A"})
        self.assertEqual(updated.codigo_agua, "NEW-A")
        print("✅ Propiedad actualizada con código modificado")

    def test_edicion_borrar_ciu(self):
        print("\nCaso 5: Edición borrando CIU")
         # Create with
        datos = {
            "matricula_inmobiliaria": "005-TEST",
            "id_municipio": 1,
            "direccion_propiedad": "Circular Test 202",
            "tipo_propiedad": "Bodega",
            "area_m2": 200,
            "codigo_gas": "TO-DELETE"
        }
        propiedad = self.servicio.crear_propiedad(datos)
        
        # Edit to delete (set to None)
        updated = self.servicio.actualizar_propiedad(propiedad.id_propiedad, {"codigo_gas": None})
        self.assertIsNone(updated.codigo_gas)
        print("✅ Propiedad actualizada con código borrado (None)")
        
        # Verify DB
        cursor = self.conn.execute("SELECT CODIGO_GAS FROM PROPIEDADES WHERE ID_PROPIEDAD = ?", (propiedad.id_propiedad,))
        row = cursor.fetchone()
        self.assertIsNone(row["CODIGO_GAS"])
        print("✅ DB verificada: Valor es NULL")

if __name__ == "__main__":
    unittest.main()
