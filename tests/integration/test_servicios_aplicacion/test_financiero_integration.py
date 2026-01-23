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
from datetime import datetime
from pathlib import Path
import shutil

# Añadir directorio raíz al path
current_dir = Path(__file__).parent
root_dir = current_dir.parent
sys.path.append(str(root_dir))

from src.infraestructura.persistencia.database import DatabaseManager
from src.aplicacion.servicios.servicio_financiero import ServicioFinanciero
from src.dominio.entidades.recaudo import Recaudo
from src.dominio.entidades.liquidacion import Liquidacion

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
            
        cls.db_manager = DatabaseManager(DB_PATH)
        cls.servicio = ServicioFinanciero(cls.db_manager)
        
        # Redireccionar salida de PDFs
        cls.servicio.pdf_service.output_dir = Path(DOCS_DIR)
        cls.servicio.pdf_service.output_dir.mkdir(exist_ok=True)
        
        # Poblar datos mínimos para pruebas (Contratos, Propiedades, Personas)
        cls._poblar_datos_base()

    @classmethod
    def _poblar_datos_base(cls):
        """Inserta datos necesarios para las relaciones FK"""
        with cls.db_manager.obtener_conexion() as conn:
            cursor = conn.cursor()
            
            # 1. Personas (Propietario, Inquilino)
            cursor.execute("INSERT INTO PERSONAS (NOMBRES, APELLIDOS, TIPO_DOCUMENTO, NUMERO_DOCUMENTO) VALUES ('Juan', 'Propietario', 'CC', '1000')")
            id_prop = cursor.lastrowid
            cursor.execute("INSERT INTO PROPIETARIOS (ID_PERSONA) VALUES (?)", (id_prop,))
            id_propietario = cursor.lastrowid
            
            cursor.execute("INSERT INTO PERSONAS (NOMBRES, APELLIDOS, TIPO_DOCUMENTO, NUMERO_DOCUMENTO) VALUES ('Pedro', 'Inquilino', 'CC', '2000')")
            id_inq = cursor.lastrowid
            cursor.execute("INSERT INTO ARRENDATARIOS (ID_PERSONA) VALUES (?)", (id_inq,))
            id_arrendatario = cursor.lastrowid

            # 2. Propiedad
            cursor.execute("INSERT INTO PROPIEDADES (DIRECCION_PROPIEDAD, MATRICULA_INMOBILIARIA, AREA, CANON_ARRENDAMIENTO) VALUES ('Calle Test 123', 'MAT-001', 50, 1000000)")
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
                    FECHA_INICIO, FECHA_FIN, ESTADO,
                    CANON_ARRENDAMIENTO, DIA_PAGO
                ) VALUES (?, ?, ?, '2024-01-01', '2025-01-01', 'Activo', 1000000, 5)
            """, (id_propiedad, id_arrendatario, id_propietario))
            cls.id_contrato_a = cursor.lastrowid
            
            conn.commit()

    def test_01_calculo_mora(self):
        """Prueba el cálculo de intereses de mora"""
        # Caso: Pago a tiempo (sin mora)
        mora = self.servicio.calcular_mora(
            id_contrato_a=self.id_contrato_a,
            fecha_limite="2024-02-05",
            fecha_pago="2024-02-05",
            valor_canon=1000000
        )
        self.assertEqual(mora, 0, "No debe haber mora si paga el día límite")
        
        # Caso: Pago con 10 días de retraso
        # Tasa 6% anual = 0.06/365 diario
        # Mora = 1M * (0.06/365) * 10
        import math
        esperado = int(1000000 * (0.06/365) * 10)
        
        mora = self.servicio.calcular_mora(
            id_contrato_a=self.id_contrato_a,
            fecha_limite="2024-02-05",
            fecha_pago="2024-02-15",
            valor_canon=1000000
        )
        # Tolerancia pequeña por redondeo
        self.assertTrue(abs(mora - esperado) < 5, f"Cálculo de mora incorrecto: {mora} != {esperado}")

    def test_02_registrar_recaudo_exitoso(self):
        """Prueba el registro correcto de un recaudo"""
        datos = {
            'id_contrato_a': self.id_contrato_a,
            'fecha_pago': '2024-02-05',
            'valor_total': 1100000,
            'metodo_pago': 'Transferencia',
            'referencia_bancaria': 'REF123',
            'observaciones': 'Pago Febrero'
        }
        conceptos = [
            {'tipo_concepto': 'Canon', 'periodo': '2024-02', 'valor': 1000000},
            {'tipo_concepto': 'Administración', 'periodo': '2024-02', 'valor': 100000}
        ]
        
        recaudo = self.servicio.registrar_recaudo(datos, conceptos, "TEST_USER")
        
        self.assertIsNotNone(recaudo.id_recaudo)
        self.assertEqual(recaudo.valor_total, 1100000)
        self.assertEqual(recaudo.estado_recaudo, 'Pendiente')
        
        # Guardar ID para siguientes pruebas
        self.__class__.id_recaudo_creado = recaudo.id_recaudo

    def test_03_registrar_recaudo_error_suma(self):
        """Prueba fallo cuando la suma de conceptos no coincide"""
        datos = {
            'id_contrato_a': self.id_contrato_a,
            'fecha_pago': '2024-03-05',
            'valor_total': 1000000, # Valor declarado
            'metodo_pago': 'Efectivo'
        }
        conceptos = [
            {'tipo_concepto': 'Canon', 'periodo': '2024-03', 'valor': 500000} # Suma real = 500k
        ]
        
        with self.assertRaises(ValueError):
            self.servicio.registrar_recaudo(datos, conceptos, "TEST_USER")

    def test_04_aprobar_recaudo(self):
        """Prueba transición de estado de recaudo"""
        id_recaudo = self.__class__.id_recaudo_creado
        
        self.servicio.aprobar_recaudo(id_recaudo, "ADMIN")
        
        info = self.servicio.obtener_detalle_recaudo_ui(id_recaudo)
        self.assertEqual(info['estado_recaudo'], 'Aplicado')

    def test_05_generar_liquidacion_mensual(self):
        """Prueba generación automática de liquidación"""
        periodo = "2024-02"
        datos = {
            'otros_ingresos': 0,
            'gastos_reparaciones': 50000,
            'observaciones': 'Descuento por reparación grifo'
        }
        
        liq = self.servicio.generar_liquidacion_mensual(
            self.id_contrato_m, periodo, datos, "CONTADOR"
        )
        
        self.assertIsNotNone(liq.id_liquidacion)
        self.assertEqual(liq.estado_liquidacion, 'En Proceso')
        
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
        self.assertEqual(liq.impuesto_4x1000, 4000)
        self.assertEqual(liq.gastos_reparaciones, 50000)
        self.assertEqual(liq.neto_a_pagar, 827000)
        
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
        info = self.servicio.obtener_detalle_liquidacion_ui(id_liq)
        self.assertEqual(info['estado'], 'Aprobada')
        
        # 2. Pagar
        self.servicio.marcar_liquidacion_pagada(
            id_liq, "2024-02-10", "Transferencia", "REF-PAGO-001", "TESORERO"
        )
        info = self.servicio.obtener_detalle_liquidacion_ui(id_liq)
        self.assertEqual(info['estado'], 'Pagada')
        self.assertEqual(info['referencia_pago'], 'REF-PAGO-001')

    def test_08_generacion_pdfs(self):
        """Prueba que los archivos PDF se generen físicamente"""
        # PDF Recaudo
        path_recaudo = self.servicio.generar_comprobante_pago(self.__class__.id_recaudo_creado)
        self.assertTrue(os.path.exists(path_recaudo), "PDF Recaudo no creado")
        self.assertTrue(path_recaudo.endswith('.pdf'))
        
        # PDF Liquidación
        path_liq = self.servicio.generar_estado_cuenta_pdf(self.__class__.id_liq_creada)
        self.assertTrue(os.path.exists(path_liq), "PDF Liquidación no creado")
        self.assertTrue(path_liq.endswith('.pdf'))

    @classmethod
    def tearDownClass(cls):
        """Limpiar archivos de prueba, conservar DB si falla para depurar"""
        # os.remove(DB_PATH) 
        # shutil.rmtree(DOCS_DIR)
        pass

if __name__ == '__main__':
    unittest.main()
