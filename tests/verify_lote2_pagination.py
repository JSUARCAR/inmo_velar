import sys
import os
import unittest
from unittest.mock import MagicMock, patch

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.dominio.modelos.pagination import PaginatedResult, PaginationParams
# Mock DatabaseManager for testing without real DB connection if possible, 
# but for integration we might want real DB. 
# However, to avoid dependency on local DB state, I will mock the execute/fetchall behavior 
# to ensure the CODE logic is correct (SQL syntax check is harder without real DB, but we can check python logic).
# Actually, if I can use the real DB it's better, but I don't know if it's populated.
# Let's try to trust the user's DB exists or mock if it fails.
# Given the user just ran the app, the DB likely exists.

class TestFinancialPagination(unittest.TestCase):
    
    def setUp(self):
        # Mock dependencies
        self.mock_db_manager = MagicMock()
        self.mock_conn = MagicMock()
        self.mock_cursor = MagicMock()
        
        self.mock_db_manager.obtener_conexion.return_value.__enter__.return_value = self.mock_conn
        self.mock_conn.cursor.return_value = self.mock_cursor
        
        # Setup common mock returns for count and data
        self.mock_cursor.fetchone.return_value = {'total': 10} # Default total
        self.mock_cursor.fetchall.return_value = [] # Default empty list
        
        # Import services here to avoid import errors if dependencies are missing at top level
        from src.aplicacion.servicios.servicio_financiero import ServicioFinanciero
        from src.aplicacion.servicios.servicio_liquidacion_asesores import ServicioLiquidacionAsesores
        from src.infraestructura.repositorios.repositorio_liquidacion_asesor_sqlite import RepositorioLiquidacionAsesorSQLite
        
        self.servicio_financiero = ServicioFinanciero(self.mock_db_manager)
        
        # Setup ServicioLiquidacionAsesores with mocked repos
        self.repo_liq_sqlite = RepositorioLiquidacionAsesorSQLite(self.mock_db_manager)
        self.servicio_liq_asesores = ServicioLiquidacionAsesores(
            repo_liquidacion=self.repo_liq_sqlite,
            repo_descuento=MagicMock(),
            repo_pago=MagicMock()
        )

    def test_recaudos_paginado_structure(self):
        """Verify listar_recaudos_paginado returns PaginatedResult"""
        print("\nTesting listar_recaudos_paginado structure...")
        
        # Setup mock return for data query
        # Columns: ID_RECAUDO, FECHA_PAGO, ESTADO_RECAUDO, VALOR_TOTAL, METODO_PAGO, DIRECCION_PROPIEDAD
        mock_row = (1, '2023-01-01', 'Pendiente', 100000, 'Efectivo', 'Calle 123')
        self.mock_cursor.fetchall.return_value = [mock_row]
        
        result = self.servicio_financiero.listar_recaudos_paginado(page=1, page_size=10)
        
        self.assertIsInstance(result, PaginatedResult)
        self.assertEqual(result.total, 10)
        self.assertEqual(len(result.items), 1)
        self.assertEqual(result.items[0]['id'], 1)
        self.assertEqual(result.items[0]['contrato'], 'Calle 123')
        print("OK - listar_recaudos_paginado passed")

    def test_liquidaciones_paginado_structure(self):
        """Verify listar_liquidaciones_paginado returns PaginatedResult"""
        print("\nTesting listar_liquidaciones_paginado structure...")
        
        # Columns: ID, PERIODO, ESTADO, CANON, OTROS_ING, COMISION, IVA, 4x1000, G_ADMIN, G_SERV, G_REP, OTROS_EGR, DIRECCION
        mock_row = (
            5, '2023-01', 'Aprobada', 
            1000000, 0, # Ingresos
            100000, 19000, 4000, 50000, 0, 0, 0, # Egresos
            'Carrera 456'
        )
        self.mock_cursor.fetchall.return_value = [mock_row]
        
        result = self.servicio_financiero.listar_liquidaciones_paginado(page=1, page_size=10)
        
        self.assertIsInstance(result, PaginatedResult)
        self.assertEqual(result.total, 10)
        item = result.items[0]
        self.assertEqual(item['id'], 5)
        # Neto calculation check: 1000000 - (100000+19000+4000+50000) = 1000000 - 173000 = 827000
        self.assertEqual(item['neto'], 827000)
        print("OK - listar_liquidaciones_paginado passed")

    def test_liq_asesores_paginado_structure(self):
        """Verify listar_liq_asesores_paginado returns PaginatedResult"""
        print("\nTesting listar_liq_asesores_paginado structure...")
        
        # Mock dict-like row thanks to sqlite3.Row or similar
        # Since I mocked cursor.row_factory in code to be dict/row, but here I return tuple/list from fetchall?
        # The logic in service does `conn.row_factory = sqlite3.Row`.
        # When mocking, I need to ensure `row['COLUMN']` works if the code uses it.
        # My previous test used tuples because the service used index access `row[0]`.
        # BUT ServicioLiquidacionAsesores uses `row['COLUMN']`.
        # I must return objects that support valid getitem.
        
        class MockRow(dict):
            def __getitem__(self, key):
                return super().get(key, None)
                
        row_data = MockRow({
            'ID_LIQUIDACION_ASESOR': 10,
            'PERIODO_LIQUIDACION': '2023-02',
            'ESTADO_LIQUIDACION': 'Pendiente',
            'COMISION_BRUTA': 50000,
            'TOTAL_DESCUENTOS': 0,
            'VALOR_NETO_ASESOR': 50000,
            'PORCENTAJE_COMISION': 1000, # 10.00%
            'ID_CONTRATO_A': 99,
            'ID_ASESOR': 2,
            'PUEDE_EDITARSE': 1,
            'PUEDE_APROBARSE': 0,
            'PUEDE_ANULARSE': 1,
            'NOMBRE_COMPLETO': 'Asesor Test'
        })
        
        self.mock_cursor.fetchall.return_value = [row_data]
        
        result = self.servicio_liq_asesores.listar_liq_asesores_paginado(page=1, page_size=10)
        
        self.assertIsInstance(result, PaginatedResult)
        self.assertEqual(result.total, 10)
        item = result.items[0]
        self.assertEqual(item['id_liquidacion_asesor'], 10)
        self.assertEqual(item['porcentaje_real'], 10.0)
        self.assertEqual(item['nombre_asesor'], 'Asesor Test')
        print("OK - listar_liq_asesores_paginado passed")
        
    def test_liq_asesores_metrics(self):
        """Verify obtener_metricas_filtradas returns dictionary"""
        print("\nTesting obtener_metricas_filtradas...")
        
        # Return list of tuples (ESTADO, TOTAL)
        self.mock_cursor.fetchall.return_value = [
            ('Pendiente', 500000),
            ('Aprobada', 1000000)
        ]
        
        result = self.servicio_liq_asesores.obtener_metricas_filtradas()
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['Pendiente'], 500000)
        self.assertEqual(result['Aprobada'], 1000000)
        self.assertEqual(result['Pagada'], 0) # Default
        print("OK - obtener_metricas_filtradas passed")

if __name__ == '__main__':
    unittest.main()
