"""
Tests para el Servicio de Aplicación de Recaudos.
Utiliza mocks del repositorio para aislar la lógica de negocio.
"""
import pytest
from unittest.mock import Mock, MagicMock
from datetime import date

from src.dominio.constantes.recaudo import MetodoPago, EstadoRecaudo
from src.dominio.entidades.recaudo import Recaudo
from src.aplicacion.esquemas.recaudo import ComandoRegistrarPago
from src.aplicacion.servicios.servicio_recaudo import ServicioRecaudo


class TestServicioRecaudoRegistro:
    """Tests de registro de pagos."""

    @pytest.fixture
    def mock_repo(self) -> Mock:
        """Repositorio mock."""
        return Mock()

    @pytest.fixture
    def mock_db(self) -> Mock:
        """DatabaseManager mock."""
        return Mock()

    @pytest.fixture
    def servicio(self, mock_repo: Mock, mock_db: Mock) -> ServicioRecaudo:
        """Servicio con dependencias mock."""
        return ServicioRecaudo(mock_repo, mock_db)

    def test_registrar_pago_exitoso(
        self, servicio: ServicioRecaudo, mock_repo: Mock
    ) -> None:
        """Registrar pago con datos válidos crea recaudo."""
        mock_repo.crear.return_value = Recaudo(
            id_recaudo=1,
            id_contrato_a=1,
            fecha_pago="2026-04-01",
            valor_total=1500000,
            metodo_pago=MetodoPago.EFECTIVO,
        )

        comando = ComandoRegistrarPago(
            id_contrato_a=1,
            fecha_pago=date(2026, 4, 1),
            valor_total=1500000,
            metodo_pago=MetodoPago.EFECTIVO,
            tipo_concepto="Canon",
            periodo="2026-04",
        )

        resultado = servicio.registrar_pago(comando, "admin")

        assert resultado.id_recaudo == 1
        mock_repo.crear.assert_called_once()


class TestServicioRecaudoAplicar:
    """Tests de aplicación de pagos."""

    @pytest.fixture
    def mock_repo(self) -> Mock:
        return Mock()

    @pytest.fixture
    def mock_db(self) -> Mock:
        return Mock()

    @pytest.fixture
    def servicio(self, mock_repo: Mock, mock_db: Mock) -> ServicioRecaudo:
        return ServicioRecaudo(mock_repo, mock_db)

    def test_aplicar_pago_exitoso(
        self, servicio: ServicioRecaudo, mock_repo: Mock
    ) -> None:
        """Aplicar pago Pendiente cambia a Aplicado."""
        mock_repo.obtener_por_id.return_value = Recaudo(
            id_recaudo=1,
            id_contrato_a=1,
            fecha_pago="2026-04-01",
            valor_total=1000000,
            metodo_pago=MetodoPago.EFECTIVO,
            estado_recaudo=EstadoRecaudo.PENDIENTE,
        )

        resultado = servicio.aplicar_pago(1, "admin")

        assert resultado.exito is True
        assert "aplicado" in resultado.mensaje
        mock_repo.cambiar_estado.assert_called_once_with(
            1, "Aplicado", "admin"
        )

    def test_aplicar_pago_no_encontrado(
        self, servicio: ServicioRecaudo, mock_repo: Mock
    ) -> None:
        """Aplicar pago inexistente retorna error."""
        mock_repo.obtener_por_id.return_value = None

        resultado = servicio.aplicar_pago(999, "admin")

        assert resultado.exito is False
        assert "no encontrado" in resultado.mensaje

    def test_aplicar_pago_ya_aplicado(
        self, servicio: ServicioRecaudo, mock_repo: Mock
    ) -> None:
        """Aplicar pago ya Aplicado retorna error."""
        mock_repo.obtener_por_id.return_value = Recaudo(
            id_recaudo=1,
            id_contrato_a=1,
            fecha_pago="2026-04-01",
            valor_total=1000000,
            metodo_pago=MetodoPago.EFECTIVO,
            estado_recaudo=EstadoRecaudo.APLICADO,
        )

        resultado = servicio.aplicar_pago(1, "admin")

        assert resultado.exito is False
        assert "Pendiente" in resultado.mensaje


class TestServicioRecaudoReversar:
    """Tests de reversión de pagos."""

    @pytest.fixture
    def mock_repo(self) -> Mock:
        return Mock()

    @pytest.fixture
    def mock_db(self) -> Mock:
        return Mock()

    @pytest.fixture
    def servicio(self, mock_repo: Mock, mock_db: Mock) -> ServicioRecaudo:
        return ServicioRecaudo(mock_repo, mock_db)

    def test_reversar_pago_exitoso(
        self, servicio: ServicioRecaudo, mock_repo: Mock
    ) -> None:
        """Reversar pago Aplicado cambia a Reversado."""
        mock_repo.obtener_por_id.return_value = Recaudo(
            id_recaudo=1,
            id_contrato_a=1,
            fecha_pago="2026-04-01",
            valor_total=1000000,
            metodo_pago=MetodoPago.EFECTIVO,
            estado_recaudo=EstadoRecaudo.APLICADO,
        )

        resultado = servicio.reversar_pago(1, "admin")

        assert resultado.exito is True
        assert "reversado" in resultado.mensaje

    def test_reversar_pago_pendiente_falla(
        self, servicio: ServicioRecaudo, mock_repo: Mock
    ) -> None:
        """Reversar pago Pendiente retorna error."""
        mock_repo.obtener_por_id.return_value = Recaudo(
            id_recaudo=1,
            id_contrato_a=1,
            fecha_pago="2026-04-01",
            valor_total=1000000,
            metodo_pago=MetodoPago.EFECTIVO,
            estado_recaudo=EstadoRecaudo.PENDIENTE,
        )

        resultado = servicio.reversar_pago(1, "admin")

        assert resultado.exito is False
        assert "Aplicado" in resultado.mensaje


class TestServicioRecaudoEliminar:
    """Tests de eliminación de pagos."""

    @pytest.fixture
    def mock_repo(self) -> Mock:
        return Mock()

    @pytest.fixture
    def mock_db(self) -> Mock:
        return Mock()

    @pytest.fixture
    def servicio(self, mock_repo: Mock, mock_db: Mock) -> ServicioRecaudo:
        return ServicioRecaudo(mock_repo, mock_db)

    def test_eliminar_pago_pendiente(
        self, servicio: ServicioRecaudo, mock_repo: Mock
    ) -> None:
        """Eliminar pago Pendiente es exitoso."""
        mock_repo.obtener_por_id.return_value = Recaudo(
            id_recaudo=1,
            id_contrato_a=1,
            fecha_pago="2026-04-01",
            valor_total=1000000,
            metodo_pago=MetodoPago.EFECTIVO,
            estado_recaudo=EstadoRecaudo.PENDIENTE,
        )

        resultado = servicio.eliminar_pago(1, "admin")

        assert resultado.exito is True
        mock_repo.eliminar.assert_called_once_with(1, "admin")

    def test_eliminar_pago_aplicado_falla(
        self, servicio: ServicioRecaudo, mock_repo: Mock
    ) -> None:
        """Eliminar pago Aplicado retorna error."""
        mock_repo.obtener_por_id.return_value = Recaudo(
            id_recaudo=1,
            id_contrato_a=1,
            fecha_pago="2026-04-01",
            valor_total=1000000,
            metodo_pago=MetodoPago.EFECTIVO,
            estado_recaudo=EstadoRecaudo.APLICADO,
        )

        resultado = servicio.eliminar_pago(1, "admin")

        assert resultado.exito is False
        assert "Pendiente" in resultado.mensaje
        mock_repo.eliminar.assert_not_called()
