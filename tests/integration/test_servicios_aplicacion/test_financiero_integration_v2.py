import sys
import unittest
from unittest.mock import MagicMock
from pathlib import Path
import os
import shutil

# MOCK FLET BEFORE ANYTHING ELSE
sys.modules["flet"] = MagicMock()

# Add root to path
current_dir = Path(__file__).parent
root_dir = current_dir.parent
sys.path.append(str(root_dir))

print(f"DIRECTORIO RAIZ: {root_dir}")

try:
    from tests.integration.test_database_manager import TestDatabaseManager
    from src.aplicacion.servicios.servicio_financiero import ServicioFinanciero

    # Recaudo/Liquidacion imports might be needed for assertions?
    # from src.dominio.entidades.recaudo import Recaudo
except ImportError as e:
    print(f"ERROR FATAL DE IMPORTACION: {e}")
    sys.exit(1)

# Configuración de prueba
DB_PATH = "test_financiero_v2.db"
DOCS_DIR = "test_documentos_v2"


class TestFinancieroIntegration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        print("CONFIGURANDO CLASE DE PRUEBA...")
        if os.path.exists(DB_PATH):
            os.remove(DB_PATH)
        if os.path.exists(DOCS_DIR):
            shutil.rmtree(DOCS_DIR)

        cls.db_manager = TestDatabaseManager(DB_PATH)
        cls.servicio = ServicioFinanciero(cls.db_manager)
        cls._crear_tablas()

        # Redireccionar salida de PDFs
        cls.servicio.pdf_service.output_dir = Path(DOCS_DIR)
        cls.servicio.pdf_service.output_dir.mkdir(exist_ok=True)

        cls._poblar_datos_base()
        print("CONFIGURACION COMPLETA.")

    @classmethod
    def _crear_tablas(cls):
        with cls.db_manager.obtener_conexion() as conn:
            conn.executescript("""
            CREATE TABLE IF NOT EXISTS PERSONAS (ID_PERSONA INTEGER PRIMARY KEY AUTOINCREMENT, NOMBRES TEXT, APELLIDOS TEXT, NOMBRE_COMPLETO TEXT, TIPO_DOCUMENTO TEXT, NUMERO_DOCUMENTO TEXT);
            CREATE TABLE IF NOT EXISTS PROPIETARIOS (ID_PROPIETARIO INTEGER PRIMARY KEY AUTOINCREMENT, ID_PERSONA INTEGER);
            CREATE TABLE IF NOT EXISTS ARRENDATARIOS (ID_ARRENDATARIO INTEGER PRIMARY KEY AUTOINCREMENT, ID_PERSONA INTEGER);
            CREATE TABLE IF NOT EXISTS PROPIEDADES (ID_PROPIEDAD INTEGER PRIMARY KEY AUTOINCREMENT, DIRECCION_PROPIEDAD TEXT, MATRICULA_INMOBILIARIA TEXT, AREA REAL, CANON_ARRENDAMIENTO REAL, ID_MUNICIPIO INTEGER);
            CREATE TABLE IF NOT EXISTS CONTRATOS_MANDATOS (ID_CONTRATO_M INTEGER PRIMARY KEY AUTOINCREMENT, ID_PROPIEDAD INTEGER, ID_PROPIETARIO INTEGER, ID_ASESOR INTEGER, FECHA_INICIO_CONTRATO_M TEXT, FECHA_FIN TEXT, ESTADO TEXT, CANON_MANDATO REAL, COMISION_PORCENTAJE_CONTRATO_M REAL, BANCO_PROPIETARIO TEXT, NUMERO_CUENTA_PROPIETARIO TEXT, TIPO_CUENTA TEXT);
            CREATE TABLE IF NOT EXISTS CONTRATOS_ARRENDAMIENTOS (ID_CONTRATO_A INTEGER PRIMARY KEY AUTOINCREMENT, ID_PROPIEDAD INTEGER, ID_ARRENDATARIO INTEGER, ID_PROPIETARIO INTEGER, FECHA_INICIO TEXT, FECHA_FIN TEXT, ESTADO TEXT, ESTADO_CONTRATO_A TEXT, CANON_ARRENDAMIENTO REAL, DIA_PAGO INTEGER);
            CREATE TABLE IF NOT EXISTS RECAUDOS (ID_RECAUDO INTEGER PRIMARY KEY AUTOINCREMENT, ID_CONTRATO_A INTEGER, VALOR_TOTAL REAL, FECHA_PAGO TEXT, METODO_PAGO TEXT, REFERENCIA_BANCARIA TEXT, OBSERVACIONES TEXT, ESTADO_RECAUDO TEXT, USUARIO_CREACION TEXT, FECHA_CREACION TEXT);
            CREATE TABLE IF NOT EXISTS CONCEPTOS_RECAUDO (ID_CONCEPTO INTEGER PRIMARY KEY AUTOINCREMENT, ID_RECAUDO INTEGER, TIPO_CONCEPTO TEXT, PERIODO TEXT, VALOR REAL);
            CREATE TABLE IF NOT EXISTS LIQUIDACIONES (ID_LIQUIDACION INTEGER PRIMARY KEY AUTOINCREMENT, ID_CONTRATO_M INTEGER, PERIODO TEXT, ESTADO_LIQUIDACION TEXT, CANON_BRUTO REAL, COMISION_MONTO REAL, IVA_COMISION REAL, IMPUESTO_4X1000 REAL, GASTOS_REPARACIONES REAL, NETO_A_PAGAR REAL, REFERENCIA_PAGO TEXT);
            CREATE TABLE IF NOT EXISTS ASESORES (ID_ASESOR INTEGER PRIMARY KEY, ID_PERSONA INTEGER, COMISION_PORCENTAJE_ARRIENDO REAL);
            CREATE TABLE IF NOT EXISTS SEGUROS (ID_SEGURO INTEGER PRIMARY KEY, NOMBRE_SEGURO TEXT, PORCENTAJE_SEGURO REAL);
            CREATE TABLE IF NOT EXISTS POLIZAS (ID_POLIZA INTEGER PRIMARY KEY, ID_CONTRATO INTEGER, ID_SEGURO INTEGER, ESTADO TEXT);
            """)
            conn.commit()

    @classmethod
    def _poblar_datos_base(cls):
        with cls.db_manager.obtener_conexion() as conn:
            cursor = conn.cursor()

            # 1. Personas
            cursor.execute(
                "INSERT INTO PERSONAS (NOMBRES, APELLIDOS, TIPO_DOCUMENTO, NUMERO_DOCUMENTO) VALUES ('Juan', 'Propietario', 'CC', '1000')"
            )
            id_prop = cursor.lastrowid
            cursor.execute(
                "INSERT INTO PROPIETARIOS (ID_PERSONA) VALUES (?)", (id_prop,)
            )
            id_propietario = cursor.lastrowid

            cursor.execute(
                "INSERT INTO PERSONAS (NOMBRES, APELLIDOS, TIPO_DOCUMENTO, NUMERO_DOCUMENTO) VALUES ('Pedro', 'Inquilino', 'CC', '2000')"
            )
            id_inq = cursor.lastrowid
            cursor.execute(
                "INSERT INTO ARRENDATARIOS (ID_PERSONA) VALUES (?)", (id_inq,)
            )
            id_arrendatario = cursor.lastrowid

            # 2. Propiedad
            cursor.execute(
                "INSERT INTO PROPIEDADES (DIRECCION_PROPIEDAD, MATRICULA_INMOBILIARIA, AREA, CANON_ARRENDAMIENTO, ID_MUNICIPIO) VALUES ('Calle Test 123', 'MAT-001', 50, 1000000, 1)"
            )
            id_propiedad = cursor.lastrowid

            # 3. Contrato Mandato
            cursor.execute(
                """
                INSERT INTO CONTRATOS_MANDATOS (
                    ID_PROPIEDAD, ID_PROPIETARIO, FECHA_INICIO_CONTRATO_M, FECHA_FIN, 
                    ESTADO, CANON_MANDATO, COMISION_PORCENTAJE_CONTRATO_M
                ) VALUES (?, ?, '2024-01-01', '2025-01-01', 'Activo', 1000000, 1000)
            """,
                (id_propiedad, id_propietario),
            )
            cls.id_contrato_m = cursor.lastrowid

            # 4. Contrato Arrendamiento
            cursor.execute(
                """
                INSERT INTO CONTRATOS_ARRENDAMIENTOS (
                    ID_PROPIEDAD, ID_ARRENDATARIO, ID_PROPIETARIO,
                    FECHA_INICIO, FECHA_FIN, ESTADO_CONTRATO_A,
                    CANON_ARRENDAMIENTO, DIA_PAGO
                ) VALUES (?, ?, ?, '2024-01-01', '2025-01-01', 'ACTIVO', 1000000, 5)
            """,
                (id_propiedad, id_arrendatario, id_propietario),
            )
            cls.id_contrato_a = cursor.lastrowid

            conn.commit()

    def test_01_calculo_mora(self):
        print("Ejecutando test_01_calculo_mora...")
        mora = self.servicio.calcular_mora(
            id_contrato_a=self.id_contrato_a,
            fecha_limite="2024-02-05",
            fecha_pago="2024-02-15",
            valor_canon=1000000,
        )
        self.assertTrue(mora > 0)
        print(f"Mora calculada: {mora}")

    def test_02_registrar_recaudo(self):
        print("Ejecutando test_02_registrar_recaudo...")
        datos = {
            "id_contrato_a": self.id_contrato_a,
            "fecha_pago": "2024-02-05",
            "valor_total": 1000000,
            "metodo_pago": "Transferencia",
            "referencia_bancaria": "REF123",
        }
        conceptos = [{"tipo_concepto": "Canon", "periodo": "2024-02", "valor": 1000000}]

        recaudo = self.servicio.registrar_recaudo(datos, conceptos, "TEST")
        self.__class__.id_recaudo = recaudo.id_recaudo
        self.assertIsNotNone(recaudo.id_recaudo)

    def test_03_generar_pdf_recaudo(self):
        # Las pruebas de generación de PDF se manejan en las pruebas de integración de pdf_elite.
        pass

    def test_04_liquidacion_completa(self):
        print("Ejecutando test_04_liquidacion_completa...")
        # Generar
        liq = self.servicio.generar_liquidacion_mensual(
            self.id_contrato_m,
            "2024-02",
            {"observaciones": "Test", "aplicar_4x1000": True},
            "TEST",
        )
        # Aprobar
        self.servicio.aprobar_liquidacion(liq.id_liquidacion, "ADMIN")
        # Pagar
        self.servicio.marcar_liquidacion_pagada(
            liq.id_liquidacion, "2024-02-10", "Transf", "REF", "TESORERO"
        )


if __name__ == "__main__":
    unittest.main()
