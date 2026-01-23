
import sys
import unittest
from unittest.mock import MagicMock
from pathlib import Path
import os
import shutil
from datetime import datetime

# MOCK FLET BEFORE ANYTHING ELSE
sys.modules['flet'] = MagicMock()

# Add root to path
current_dir = Path(__file__).parent
root_dir = current_dir.parent
sys.path.append(str(root_dir))

print(f"ROOT DIR: {root_dir}")

try:
    from src.infraestructura.persistencia.database import DatabaseManager
    from src.aplicacion.servicios.servicio_financiero import ServicioFinanciero
    # Recaudo/Liquidacion imports might be needed for assertions?
    # from src.dominio.entidades.recaudo import Recaudo
except ImportError as e:
    print(f"FATAL IMPORT ERROR: {e}")
    sys.exit(1)

# Configuración de prueba
DB_PATH = "test_financiero_v2.db"
DOCS_DIR = "test_documentos_v2"

class TestFinancieroIntegration(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        print("SETTING UP TEST CLASS...")
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
        if os.path.exists(DOCS_DIR):
            shutil.rmtree(DOCS_DIR)
            
        cls.db_manager = DatabaseManager(DB_PATH)
        cls.servicio = ServicioFinanciero(cls.db_manager)
        
        # Redireccionar salida de PDFs
        cls.servicio.pdf_service.output_dir = Path(DOCS_DIR)
        cls.servicio.pdf_service.output_dir.mkdir(exist_ok=True)
        
        cls._poblar_datos_base()
        print("SETUP COMPLETE.")

    @classmethod
    def _poblar_datos_base(cls):
        with cls.db_manager.obtener_conexion() as conn:
            cursor = conn.cursor()
            
            # 1. Personas
            cursor.execute("INSERT INTO PERSONAS (NOMBRES, APELLIDOS, TIPO_DOCUMENTO, NUMERO_DOCUMENTO) VALUES ('Juan', 'Propietario', 'CC', '1000')")
            id_prop = cursor.lastrowid
            cursor.execute("INSERT INTO PROPIETARIOS (ID_PERSONA) VALUES (?)", (id_prop,))
            id_propietario = cursor.lastrowid
            
            cursor.execute("INSERT INTO PERSONAS (NOMBRES, APELLIDOS, TIPO_DOCUMENTO, NUMERO_DOCUMENTO) VALUES ('Pedro', 'Inquilino', 'CC', '2000')")
            id_inq = cursor.lastrowid
            cursor.execute("INSERT INTO ARRENDATARIOS (ID_PERSONA) VALUES (?)", (id_inq,))
            id_arrendatario = cursor.lastrowid

            # 2. Propiedad
            cursor.execute("INSERT INTO PROPIEDADES (DIRECCION_PROPIEDAD, MATRICULA_INMOBILIARIA, AREA, CANON_ARRENDAMIENTO, ID_MUNICIPIO) VALUES ('Calle Test 123', 'MAT-001', 50, 1000000, 1)")
            id_propiedad = cursor.lastrowid
            
            # 3. Contrato Mandato
            cursor.execute("""
                INSERT INTO CONTRATOS_MANDATOS (
                    ID_PROPIEDAD, ID_PROPIETARIO, FECHA_INICIO, FECHA_FIN, 
                    ESTADO, CANON_MANDATO, COMISION_PORCENTAJE
                ) VALUES (?, ?, '2024-01-01', '2025-01-01', 'Activo', 1000000, 1000)
            """, (id_propiedad, id_propietario))
            cls.id_contrato_m = cursor.lastrowid
            
            # 4. Contrato Arrendamiento
            cursor.execute("""
                INSERT INTO CONTRATOS_ARRENDAMIENTOS (
                    ID_PROPIEDAD, ID_ARRENDATARIO, ID_PROPIETARIO,
                    FECHA_INICIO, FECHA_FIN, ESTADO_CONTRATO_A,
                    CANON_ARRENDAMIENTO, DIA_PAGO
                ) VALUES (?, ?, ?, '2024-01-01', '2025-01-01', 'ACTIVO', 1000000, 5)
            """, (id_propiedad, id_arrendatario, id_propietario))
            cls.id_contrato_a = cursor.lastrowid
            
            conn.commit()

    def test_01_calculo_mora(self):
        print("Running test_01_calculo_mora...")
        mora = self.servicio.calcular_mora(
            id_contrato_a=self.id_contrato_a,
            fecha_limite="2024-02-05",
            fecha_pago="2024-02-15",
            valor_canon=1000000
        )
        self.assertTrue(mora > 0)
        print(f"Mora calculada: {mora}")

    def test_02_registrar_recaudo(self):
        print("Running test_02_registrar_recaudo...")
        datos = {
            'id_contrato_a': self.id_contrato_a,
            'fecha_pago': '2024-02-05',
            'valor_total': 1000000,
            'metodo_pago': 'Transferencia'
        }
        conceptos = [{'tipo_concepto': 'Canon', 'periodo': '2024-02', 'valor': 1000000}]
        
        recaudo = self.servicio.registrar_recaudo(datos, conceptos, "TEST")
        self.__class__.id_recaudo = recaudo.id_recaudo
        self.assertIsNotNone(recaudo.id_recaudo)
    
    def test_03_generar_pdf_recaudo(self):
        # Asegurar que existe el recaudo
        path = self.servicio.generar_comprobante_pago(self.__class__.id_recaudo)
        print(f"PDF Recaudo generado en: {path}")
        self.assertTrue(os.path.exists(path))

    def test_04_liquidacion_completa(self):
        print("Running test_04_liquidacion_completa...")
        # Generar
        liq = self.servicio.generar_liquidacion_mensual(
            self.id_contrato_m, "2024-02", {'observaciones': 'Test'}, "TEST"
        )
        # Aprobar
        self.servicio.aprobar_liquidacion(liq.id_liquidacion, "ADMIN")
        # Pagar
        self.servicio.marcar_liquidacion_pagada(liq.id_liquidacion, "2024-02-10", "Transf", "REF", "TESORERO")
        
        # PDF
        path = self.servicio.generar_estado_cuenta_pdf(liq.id_liquidacion)
        print(f"PDF Liquidacion generado: {path}")
        self.assertTrue(os.path.exists(path))

if __name__ == '__main__':
    unittest.main()
