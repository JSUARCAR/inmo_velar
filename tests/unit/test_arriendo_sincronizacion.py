import unittest
from unittest.mock import MagicMock
from src.aplicacion.servicios.servicio_contrato_arrendamiento import ServicioContratoArrendamiento
from src.dominio.constantes.estados_contrato import EstadoContrato
from src.dominio.entidades.contrato_arrendamiento import ContratoArrendamiento

class TestArriendoSincronizacion(unittest.TestCase):
    def setUp(self):
        self.repo_arriendo = MagicMock()
        self.repo_propiedad = MagicMock()
        self.repo_renovacion = MagicMock()
        self.repo_ipc = MagicMock()
        self.repo_mandato = MagicMock()
        
        # Configure db mock to bypass transaccion()
        self.repo_arriendo.db = MagicMock()
        self.repo_arriendo.db.transaccion.return_value.__enter__ = MagicMock()
        self.repo_arriendo.db.transaccion.return_value.__exit__ = MagicMock()
        
        self.servicio = ServicioContratoArrendamiento(
            repo_arriendo=self.repo_arriendo,
            repo_propiedad=self.repo_propiedad,
            repo_renovacion=self.repo_renovacion,
            repo_ipc=self.repo_ipc,
            repo_mandato=self.repo_mandato,
        )

    def test_crear_arriendo_activa_disponibilidad_ocupada(self):
        # Arrange
        datos = {
            "id_propiedad": 1,
            "id_arrendatario": 2,
            "id_codeudor": None,
            "fecha_inicio": "2026-01-01",
            "fecha_fin": "2026-12-31",
            "duracion_meses": 12,
            "canon": 1000000,
            "deposito": 500000,
            "fecha_pago": "5"
        }
        usuario = "test_user"
        
        self.repo_arriendo.obtener_activo_por_propiedad.return_value = None
        
        contrato_creado = ContratoArrendamiento(id_contrato_a=10, id_propiedad=1)
        self.repo_arriendo.crear.return_value = contrato_creado
        
        propiedad_mock = MagicMock()
        propiedad_mock.disponibilidad_propiedad = 1 # 1 is Disponible
        self.repo_propiedad.obtener_por_id.return_value = propiedad_mock
        
        # Act
        # Avoid CalculadoraContratos logic by patching it or just let it pass if it returns True
        with unittest.mock.patch('src.dominio.servicios.calculadora_contratos.CalculadoraContratos.validar_coherencia') as mock_validar:
            mock_validar.return_value = (True, "OK")
            with unittest.mock.patch('src.dominio.servicios.calculadora_contratos.CalculadoraContratos.calcular_ciclo_pago_arrendamiento') as mock_ciclo:
                mock_ciclo.return_value = 1
                self.servicio.crear_arrendamiento(datos, usuario)
        
        # Assert
        self.assertEqual(propiedad_mock.disponibilidad_propiedad, 0) # 0 is Ocupada
        self.repo_propiedad.actualizar.assert_called_once_with(propiedad_mock, usuario)

    def test_terminar_arriendo_libera_disponibilidad(self):
        # Arrange
        id_contrato = 10
        usuario = "test_user"
        
        arriendo_mock = ContratoArrendamiento(
            id_contrato_a=id_contrato,
            id_propiedad=1,
            estado_contrato_a=EstadoContrato.ACTIVO
        )
        self.repo_arriendo.obtener_por_id.return_value = arriendo_mock
        
        propiedad_mock = MagicMock()
        propiedad_mock.disponibilidad_propiedad = 0 # Ocupada
        self.repo_propiedad.obtener_por_id.return_value = propiedad_mock
        
        # Act
        self.servicio.terminar_arrendamiento(id_contrato, "Fin", usuario, EstadoContrato.FINALIZADO)
        
        # Assert
        self.assertEqual(propiedad_mock.disponibilidad_propiedad, 1) # Libre
        self.repo_propiedad.actualizar.assert_called_once_with(propiedad_mock, usuario)

if __name__ == '__main__':
    unittest.main()
