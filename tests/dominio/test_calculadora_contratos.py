
import unittest
from datetime import date
from src.dominio.servicios.calculadora_contratos import CalculadoraContratos

class TestCalculadoraContratos(unittest.TestCase):
    def test_mes_completo_estandar(self):
        # 1 de Enero a 31 de Enero = 1 mes
        res = CalculadoraContratos.calcular_duracion_meses("2024-01-01", "2024-01-31")
        self.assertEqual(res, 1)

    def test_mes_completo_intercalado(self):
        # 15 de Enero a 14 de Febrero = 1 mes
        res = CalculadoraContratos.calcular_duracion_meses("2024-01-15", "2024-02-14")
        self.assertEqual(res, 1)

    def test_doce_meses_exactos(self):
        # 1 de Enero a 31 de Diciembre = 12 meses
        res = CalculadoraContratos.calcular_duracion_meses("2024-01-01", "2024-12-31")
        self.assertEqual(res, 12)

    def test_mes_incompleto(self):
        # 15 de Enero a 10 de Febrero = 0 meses comerciales
        res = CalculadoraContratos.calcular_duracion_meses("2024-01-15", "2024-02-10")
        self.assertEqual(res, 0)

    def test_fechas_invertidas(self):
        res = CalculadoraContratos.calcular_duracion_meses("2024-02-01", "2024-01-01")
        self.assertEqual(res, 0)

    def test_fin_de_mes_ajuste(self):
        # 31 de Enero a 28 de Febrero (año no bisiesto) = 1 mes
        res = CalculadoraContratos.calcular_duracion_meses("2023-01-31", "2023-02-28")
        self.assertEqual(res, 1)

    def test_bisiesto(self):
        # 31 de Enero a 29 de Febrero (año bisiesto) = 1 mes
        res = CalculadoraContratos.calcular_duracion_meses("2024-01-31", "2024-02-29")
        self.assertEqual(res, 1)

if __name__ == "__main__":
    unittest.main()
