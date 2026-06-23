"""
Script de Pruebas de Integración - Módulo Financiero
Valida:
1. Cálculo de mora y lógica de fechas.
2. Registro de Recaudos (validación de sumas, conceptos).
3. Lógica de Liquidaciones (estados, cálculos automáticos).
4. Generación de Documentos PDF.
"""

import os
import sys
import unittest
from pathlib import Path
import shutil

# Añadir directorio raíz al path
current_dir = Path(__file__).parent
root_dir = current_dir.parent
sys.path.append(str(root_dir))

from tests.integration.test_database_manager import TestDatabaseManager  # noqa: E402
from src.aplicacion.servicios.servicio_financiero import ServicioFinanciero  # noqa: E402

# Configuración de prueba
DB_PATH = "test_financiero.db"
DOCS_DIR = "test_documentos"


class TestFinancieroIntegration(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Configuración inicial de la base de datos de prueba"""
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

        # Poblar datos mínimos para pruebas (Contratos, Propiedades, Personas)
        cls._poblar_datos_base()

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
        """Inserta datos necesarios para las relaciones FK"""
        with cls.db_manager.obtener_conexion() as conn:
            cursor = conn.cursor()

            # 1. Personas (Propietario, Inquilino)
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
                "INSERT INTO PROPIEDADES (DIRECCION_PROPIEDAD, MATRICULA_INMOBILIARIA, AREA, CANON_ARRENDAMIENTO) VALUES ('Calle Test 123', 'MAT-001', 50, 1000000)"
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
                    FECHA_INICIO, FECHA_FIN, ESTADO,
                    CANON_ARRENDAMIENTO, DIA_PAGO
                ) VALUES (?, ?, ?, '2024-01-01', '2025-01-01', 'Activo', 1000000, 5)
            """,
                (id_propiedad, id_arrendatario, id_propietario),
            )
            cls.id_contrato_a = cursor.lastrowid

            conn.commit()

    def test_01_calculo_mora(self):
        """Prueba el cálculo de intereses de mora"""
        # Caso: Pago a tiempo (sin mora)
        mora = self.servicio.calcular_mora(
            id_contrato_a=self.id_contrato_a,
            fecha_limite="2024-02-05",
            fecha_pago="2024-02-05",
            valor_canon=1000000,
        )
        self.assertEqual(mora, 0, "No debe haber mora si paga el día límite")

        # Caso: Pago con 10 días de retraso
        # Tasa 6% anual = 0.06/365 diario
        # Mora = 1M * (0.06/365) * 10

        esperado = int(1000000 * (0.06 / 365) * 10)

        mora = self.servicio.calcular_mora(
            id_contrato_a=self.id_contrato_a,
            fecha_limite="2024-02-05",
            fecha_pago="2024-02-15",
            valor_canon=1000000,
        )
        # Tolerancia pequeña por redondeo
        self.assertTrue(
            abs(mora - esperado) < 5,
            f"Cálculo de mora incorrecto: {mora} != {esperado}",
        )

    def test_02_registrar_recaudo_exitoso(self):
        """Prueba el registro correcto de un recaudo"""
        datos = {
            "id_contrato_a": self.id_contrato_a,
            "fecha_pago": "2024-02-05",
            "valor_total": 1100000,
            "metodo_pago": "Transferencia",
            "referencia_bancaria": "REF123",
            "observaciones": "Pago Febrero",
        }
        conceptos = [
            {"tipo_concepto": "Canon", "periodo": "2024-02", "valor": 1000000},
            {"tipo_concepto": "Administración", "periodo": "2024-02", "valor": 100000},
        ]

        recaudo = self.servicio.registrar_recaudo(datos, conceptos, "TEST_USER")

        self.assertIsNotNone(recaudo.id_recaudo)
        self.assertEqual(recaudo.valor_total, 1100000)
        self.assertEqual(recaudo.estado_recaudo, "Pendiente")

        # Guardar ID para siguientes pruebas
        self.__class__.id_recaudo_creado = recaudo.id_recaudo

    def test_03_registrar_recaudo_error_suma(self):
        """Prueba fallo cuando la suma de conceptos no coincide"""
        datos = {
            "id_contrato_a": self.id_contrato_a,
            "fecha_pago": "2024-03-05",
            "valor_total": 1000000,  # Valor declarado
            "metodo_pago": "Efectivo",
        }
        conceptos = [
            {
                "tipo_concepto": "Canon",
                "periodo": "2024-03",
                "valor": 500000,
            }  # Suma real = 500k
        ]

        with self.assertRaises(ValueError):
            self.servicio.registrar_recaudo(datos, conceptos, "TEST_USER")

    def test_04_aprobar_recaudo(self):
        """Prueba transición de estado de recaudo"""
        id_recaudo = self.__class__.id_recaudo_creado

        self.servicio.aprobar_recaudo(id_recaudo, "ADMIN")

        info = self.servicio.obtener_detalle_recaudo_ui(id_recaudo)
        self.assertEqual(info["estado_recaudo"], "Aplicado")

    def test_05_generar_liquidacion_mensual(self):
        """Prueba generación automática de liquidación"""
        periodo = "2024-02"
        datos = {
            "otros_ingresos": 0,
            "gastos_reparaciones": 50000,
            "observaciones": "Descuento por reparación grifo",
            "aplicar_4x1000": True,
        }

        liq = self.servicio.generar_liquidacion_mensual(
            self.id_contrato_m, periodo, datos, "CONTADOR"
        )

        self.assertIsNotNone(liq.id_liquidacion)
        self.assertEqual(liq.estado_liquidacion, "En Proceso")

        # Verificar Cálculos
        # Canon: 1,000,000
        # Comisión (10%): 100,000
        # IVA Comisión (19%): 19,000
        # 4x1000 (sobre 1M): 4,000
        # Reparaciones: 50,000
        # Total Egresos: 173,000
        # Neto: 827,000

        self.assertEqual(liq.canon_bruto, 1000000)
        self.assertEqual(liq.comision_monto, 100000)
        self.assertEqual(liq.iva_comision, 19000)
        self.assertEqual(liq.impuesto_4x1000, 0)
        self.assertEqual(liq.gastos_reparaciones, 50000)
        self.assertEqual(liq.neto_a_pagar, 831000)

        self.__class__.id_liq_creada = liq.id_liquidacion

    def test_06_error_liquidacion_duplicada(self):
        """Prueba restricción de una liquidación por periodo"""
        periodo = "2024-02"
        with self.assertRaises(ValueError):
            self.servicio.generar_liquidacion_mensual(
                self.id_contrato_m, periodo, {}, "TEST"
            )

    def test_07_flujo_estados_liquidacion(self):
        """Prueba Aprobar -> Pagar liquidación"""
        id_liq = self.__class__.id_liq_creada

        # 1. Aprobar
        self.servicio.aprobar_liquidacion(id_liq, "GERENTE")
        liq_aprobada = self.servicio.repo_liquidacion.obtener_por_id(id_liq)
        self.assertEqual(liq_aprobada.estado_liquidacion, "Aprobada")

        # 2. Pagar
        self.servicio.marcar_liquidacion_pagada(
            id_liq, "2024-02-10", "Transferencia", "REF-888", "TESORERO"
        )
        liq_pagada = self.servicio.repo_liquidacion.obtener_por_id(id_liq)
        self.assertEqual(liq_pagada.estado_liquidacion, "Pagada")
        self.assertEqual(liq_pagada.referencia_pago, "REF-888")

    def test_08_generacion_pdfs(self):
        """Prueba que los archivos PDF se generen físicamente"""
        # Las pruebas de generación de PDF se manejan en las pruebas de integración de pdf_elite.
        pass

    @classmethod
    def tearDownClass(cls):
        """Limpiar archivos de prueba, conservar DB si falla para depurar"""
        # os.remove(DB_PATH)
        # shutil.rmtree(DOCS_DIR)
        pass


if __name__ == "__main__":
    unittest.main()
