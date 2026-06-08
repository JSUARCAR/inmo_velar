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
        mock_repo.cambiar_estado.assert_called_once_with(1, "Aplicado", "admin")

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


class TestServicioRecaudoListarPaginado:
    """Tests de listado paginado con campos extendidos (arrendatario + habitante)."""

    @pytest.fixture
    def mock_repo(self) -> Mock:
        return Mock()

    @pytest.fixture
    def mock_db(self) -> Mock:
        return Mock()

    @pytest.fixture
    def servicio(self, mock_repo: Mock, mock_db: Mock) -> ServicioRecaudo:
        return ServicioRecaudo(mock_repo, mock_db)

    def test_listar_paginado_incluye_telefonos(
        self, servicio: ServicioRecaudo, mock_repo: Mock
    ) -> None:
        """El DTO de listado incluye telefono_arrendatario."""
        mock_repo.contar_con_filtros.return_value = 1
        mock_repo.listar_paginado.return_value = [
            {
                "id_recaudo": 1,
                "id_contrato": 10,
                "codigo_contrato": "ID:10",
                "direccion": "Cra 15 #10-20",
                "matricula": "12345",
                "arrendatario": "Juan Pérez",
                "telefono_arrendatario": "3151234567",
                "habitante": "María López",
                "telefono_habitante": "3007654321",
                "fecha_pago": "2026-04-01",
                "fecha_pago_contrato": "2026-04-01",
                "valor_total": 1500000,
                "metodo_pago": "Efectivo",
                "referencia": "",
                "estado": "Pendiente",
                "observaciones": "",
            }
        ]

        from src.dominio.interfaces.repositorio_recaudo import FiltrosRecaudo

        filtros = FiltrosRecaudo(page=1, page_size=25)
        resultado = servicio.listar_paginado(filtros)

        assert len(resultado.items) == 1
        assert resultado.items[0].telefono_arrendatario == "3151234567"

    def test_listar_paginado_incluye_habitante(
        self, servicio: ServicioRecaudo, mock_repo: Mock
    ) -> None:
        """El DTO de listado incluye habitante y telefono_habitante."""
        mock_repo.contar_con_filtros.return_value = 1
        mock_repo.listar_paginado.return_value = [
            {
                "id_recaudo": 1,
                "id_contrato": 10,
                "codigo_contrato": "ID:10",
                "direccion": "Cra 15 #10-20",
                "matricula": "12345",
                "arrendatario": "Juan Pérez",
                "telefono_arrendatario": "3151234567",
                "habitante": "María López",
                "telefono_habitante": "3007654321",
                "fecha_pago": "2026-04-01",
                "fecha_pago_contrato": "2026-04-01",
                "valor_total": 1500000,
                "metodo_pago": "Efectivo",
                "referencia": "",
                "estado": "Pendiente",
                "observaciones": "",
            }
        ]

        from src.dominio.interfaces.repositorio_recaudo import FiltrosRecaudo

        filtros = FiltrosRecaudo(page=1, page_size=25)
        resultado = servicio.listar_paginado(filtros)

        assert len(resultado.items) == 1
        assert resultado.items[0].habitante == "María López"
        assert resultado.items[0].telefono_habitante == "3007654321"

    def test_listar_paginado_campos_vacios_por_defecto(
        self, servicio: ServicioRecaudo, mock_repo: Mock
    ) -> None:
        """Campos de habitante vacíos cuando no hay datos."""
        mock_repo.contar_con_filtros.return_value = 1
        mock_repo.listar_paginado.return_value = [
            {
                "id_recaudo": 1,
                "id_contrato": 10,
                "codigo_contrato": "ID:10",
                "direccion": "Cra 15 #10-20",
                "matricula": "12345",
                "arrendatario": "Juan Pérez",
                "telefono_arrendatario": "",
                "habitante": "",
                "telefono_habitante": "",
                "fecha_pago": "2026-04-01",
                "fecha_pago_contrato": "2026-04-01",
                "valor_total": 1500000,
                "metodo_pago": "Efectivo",
                "referencia": "",
                "estado": "Pendiente",
                "observaciones": "",
            }
        ]

        from src.dominio.interfaces.repositorio_recaudo import FiltrosRecaudo

        filtros = FiltrosRecaudo(page=1, page_size=25)
        resultado = servicio.listar_paginado(filtros)

        assert len(resultado.items) == 1
        assert resultado.items[0].habitante == ""
        assert resultado.items[0].telefono_habitante == ""


class TestServicioRecaudoObtenerDetalle:
    """Tests de detalle con campos de habitante."""

    @pytest.fixture
    def mock_repo(self) -> Mock:
        return Mock()

    @pytest.fixture
    def mock_db(self) -> Mock:
        db = Mock()
        db.get_placeholder.return_value = "%s"
        return db

    @pytest.fixture
    def servicio(self, mock_repo: Mock, mock_db: Mock) -> ServicioRecaudo:
        return ServicioRecaudo(mock_repo, mock_db)

    def test_detalle_incluye_habitante(
        self, servicio: ServicioRecaudo, mock_repo: Mock, mock_db: Mock
    ) -> None:
        """El detalle del recaudo incluye datos del habitante."""
        mock_repo.obtener_por_id.return_value = Recaudo(
            id_recaudo=1,
            id_contrato_a=10,
            fecha_pago="2026-04-01",
            valor_total=1500000,
            metodo_pago=MetodoPago.EFECTIVO,
            estado_recaudo=EstadoRecaudo.PENDIENTE,
        )
        mock_repo.obtener_conceptos_por_recaudo.return_value = []

        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = {
            "DIRECCION_PROPIEDAD": "Cra 15 #10-20",
            "MATRICULA_INMOBILIARIA": "12345",
            "ARRENDATARIO": "Juan Pérez",
            "TELEFONO_ARRENDATARIO": "3151234567",
            "NOMBRE_HABITANTE": "María López",
            "TELEFONO_HABITANTE": "3007654321",
        }
        mock_db.get_dict_cursor.return_value = mock_cursor

        mock_conn = Mock()
        mock_db.obtener_conexion.return_value.__enter__ = Mock(return_value=mock_conn)
        mock_db.obtener_conexion.return_value.__exit__ = Mock(return_value=False)

        resultado = servicio.obtener_detalle(1)

        assert resultado is not None
        assert resultado.habitante == "María López"
        assert resultado.telefono_habitante == "3007654321"
        assert resultado.telefono_arrendatario == "3151234567"

    def test_detalle_sin_habitante(
        self, servicio: ServicioRecaudo, mock_repo: Mock, mock_db: Mock
    ) -> None:
        """El detalle maneja gracefully cuando no hay habitante."""
        mock_repo.obtener_por_id.return_value = Recaudo(
            id_recaudo=1,
            id_contrato_a=10,
            fecha_pago="2026-04-01",
            valor_total=1500000,
            metodo_pago=MetodoPago.EFECTIVO,
            estado_recaudo=EstadoRecaudo.PENDIENTE,
        )
        mock_repo.obtener_conceptos_por_recaudo.return_value = []

        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = {
            "DIRECCION_PROPIEDAD": "Cra 15 #10-20",
            "MATRICULA_INMOBILIARIA": "12345",
            "ARRENDATARIO": "Juan Pérez",
            "TELEFONO_ARRENDATARIO": "3151234567",
            "NOMBRE_HABITANTE": None,
            "TELEFONO_HABITANTE": None,
        }
        mock_db.get_dict_cursor.return_value = mock_cursor

        mock_conn = Mock()
        mock_db.obtener_conexion.return_value.__enter__ = Mock(return_value=mock_conn)
        mock_db.obtener_conexion.return_value.__exit__ = Mock(return_value=False)

        resultado = servicio.obtener_detalle(1)

        assert resultado is not None
        assert resultado.habitante == ""
        assert resultado.telefono_habitante == ""
