"""
Tests unitarios para las constantes y Enums del módulo de Recaudos.
Cobertura: MetodoPago, EstadoRecaudo, TipoConcepto
"""
import pytest

from src.dominio.constantes.recaudo import (
    EstadoRecaudo,
    MetodoPago,
    TipoConcepto,
)


class TestMetodoPago:
    """Suite de tests para el enum MetodoPago."""

    def test_valores_contiene_todos_los_metodos(self) -> None:
        """Verifica que valores() retorna todos los métodos."""
        esperados = ["Efectivo", "Transferencia", "PSE", "Consignación"]
        assert MetodoPago.valores() == esperados

    def test_requiere_referencia_efectivo(self) -> None:
        """Efectivo NO requiere referencia bancaria."""
        assert MetodoPago.requiere_referencia(MetodoPago.EFECTIVO) is False

    def test_requiere_referencia_transferencia(self) -> None:
        """Transferencia SÍ requiere referencia bancaria."""
        assert MetodoPago.requiere_referencia(MetodoPago.TRANSFERENCIA) is True

    def test_requiere_referencia_pse(self) -> None:
        """PSE SÍ requiere referencia bancaria."""
        assert MetodoPago.requiere_referencia(MetodoPago.PSE) is True

    def test_requiere_referencia_consignacion(self) -> None:
        """Consignación SÍ requiere referencia bancaria."""
        assert MetodoPago.requiere_referencia(MetodoPago.CONSIGNACION) is True

    def test_crear_desde_string(self) -> None:
        """Un string válido se puede convertir a MetodoPago."""
        metodo = MetodoPago("Transferencia")
        assert metodo == MetodoPago.TRANSFERENCIA

    def test_crear_desde_string_invalido(self) -> None:
        """Un string inválido lanza ValueError."""
        with pytest.raises(ValueError):
            MetodoPago("Bitcoin")

    def test_comparacion_con_string(self) -> None:
        """MetodoPago(str, Enum) se compara correctamente con strings."""
        assert MetodoPago.EFECTIVO == "Efectivo"
        assert MetodoPago.TRANSFERENCIA != "Efectivo"


class TestEstadoRecaudo:
    """Suite de tests para el enum EstadoRecaudo."""

    def test_valores_contiene_todos_los_estados(self) -> None:
        """Verifica que valores() retorna todos los estados."""
        esperados = ["Pendiente", "Aplicado", "Reversado"]
        assert EstadoRecaudo.valores() == esperados

    def test_pendiente_puede_editarse(self) -> None:
        """Pendiente SÍ puede editarse."""
        assert EstadoRecaudo.PENDIENTE.puede_editarse() is True

    def test_aplicado_no_puede_editarse(self) -> None:
        """Aplicado NO puede editarse."""
        assert EstadoRecaudo.APLICADO.puede_editarse() is False

    def test_reversado_no_puede_editarse(self) -> None:
        """Reversado NO puede editarse."""
        assert EstadoRecaudo.REVERSADO.puede_editarse() is False

    def test_pendiente_puede_aplicarse(self) -> None:
        """Pendiente SÍ puede aplicarse."""
        assert EstadoRecaudo.PENDIENTE.puede_aplicarse() is True

    def test_aplicado_no_puede_aplicarse(self) -> None:
        """Aplicado NO puede aplicarse (ya está aplicado)."""
        assert EstadoRecaudo.APLICADO.puede_aplicarse() is False

    def test_aplicado_puede_reversarse(self) -> None:
        """Aplicado SÍ puede reversarse."""
        assert EstadoRecaudo.APLICADO.puede_reversarse() is True

    def test_pendiente_no_puede_reversarse(self) -> None:
        """Pendiente NO puede reversarse."""
        assert EstadoRecaudo.PENDIENTE.puede_reversarse() is False

    def test_pendiente_puede_eliminarse(self) -> None:
        """Pendiente SÍ puede eliminarse."""
        assert EstadoRecaudo.PENDIENTE.puede_eliminarse() is True

    def test_aplicado_no_puede_eliminarse(self) -> None:
        """Aplicado NO puede eliminarse."""
        assert EstadoRecaudo.APLICADO.puede_eliminarse() is False


class TestTipoConcepto:
    """Suite de tests para el enum TipoConcepto."""

    def test_valores_contiene_todos_los_tipos(self) -> None:
        """Verifica que valores() retorna todos los tipos."""
        esperados = ["Canon", "Administración", "Mora", "Servicios", "Otro"]
        assert TipoConcepto.valores() == esperados

    def test_crear_desde_string(self) -> None:
        """Un string válido se puede convertir a TipoConcepto."""
        tipo = TipoConcepto("Administración")
        assert tipo == TipoConcepto.ADMINISTRACION
