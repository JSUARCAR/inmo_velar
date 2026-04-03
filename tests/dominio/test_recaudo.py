"""
Tests unitarios para la entidad Recaudo.
Cobertura: Creación, validaciones, inmutabilidad, transiciones de estado.
"""
import pytest
from datetime import date

from src.dominio.entidades.recaudo import Recaudo
from src.dominio.constantes.recaudo import MetodoPago, EstadoRecaudo


class TestRecaudoCreacion:
    """Tests de creación de la entidad Recaudo."""

    def test_crear_recaudo_efectivo_valido(self) -> None:
        """Crear recaudo en efectivo con datos mínimos válidos."""
        recaudo = Recaudo(
            id_contrato_a=1,
            fecha_pago="2026-04-01",
            valor_total=1500000,
            metodo_pago=MetodoPago.EFECTIVO,
        )

        assert recaudo.valor_total == 1500000
        assert recaudo.metodo_pago == MetodoPago.EFECTIVO
        assert recaudo.estado_recaudo == EstadoRecaudo.PENDIENTE
        assert recaudo.referencia_bancaria is None

    def test_crear_recaudo_transferencia_con_referencia(self) -> None:
        """Crear recaudo con transferencia y referencia válida."""
        recaudo = Recaudo(
            id_contrato_a=1,
            fecha_pago="2026-04-01",
            valor_total=2000000,
            metodo_pago=MetodoPago.TRANSFERENCIA,
            referencia_bancaria="REF-2026-001",
        )

        assert recaudo.metodo_pago == MetodoPago.TRANSFERENCIA
        assert recaudo.referencia_bancaria == "REF-2026-001"

    def test_crear_con_string_normaliza_a_enum(self) -> None:
        """Strings de BD se normalizan a Enums correctamente."""
        recaudo = Recaudo(
            id_contrato_a=1,
            fecha_pago="2026-04-01",
            valor_total=1000000,
            metodo_pago="Efectivo",
            estado_recaudo="Pendiente",
        )

        assert isinstance(recaudo.metodo_pago, MetodoPago)
        assert isinstance(recaudo.estado_recaudo, EstadoRecaudo)


class TestRecaudoValidaciones:
    """Tests de validaciones de negocio de Recaudo."""

    def test_rechazar_valor_cero(self) -> None:
        """Recaudo con valor cero debe fallar."""
        with pytest.raises(ValueError, match="mayor a cero"):
            Recaudo(
                id_contrato_a=1,
                fecha_pago="2026-04-01",
                valor_total=0,
                metodo_pago=MetodoPago.EFECTIVO,
            )

    def test_rechazar_valor_negativo(self) -> None:
        """Recaudo con valor negativo debe fallar."""
        with pytest.raises(ValueError, match="mayor a cero"):
            Recaudo(
                id_contrato_a=1,
                fecha_pago="2026-04-01",
                valor_total=-100,
                metodo_pago=MetodoPago.EFECTIVO,
            )

    def test_referencia_obligatoria_para_transferencia(self) -> None:
        """Transferencia sin referencia debe fallar."""
        with pytest.raises(ValueError, match="referencia bancaria"):
            Recaudo(
                id_contrato_a=1,
                fecha_pago="2026-04-01",
                valor_total=1000000,
                metodo_pago=MetodoPago.TRANSFERENCIA,
            )

    def test_referencia_obligatoria_para_pse(self) -> None:
        """PSE sin referencia debe fallar."""
        with pytest.raises(ValueError, match="referencia bancaria"):
            Recaudo(
                id_contrato_a=1,
                fecha_pago="2026-04-01",
                valor_total=1000000,
                metodo_pago=MetodoPago.PSE,
            )

    def test_referencia_obligatoria_para_consignacion(self) -> None:
        """Consignación sin referencia debe fallar."""
        with pytest.raises(ValueError, match="referencia bancaria"):
            Recaudo(
                id_contrato_a=1,
                fecha_pago="2026-04-01",
                valor_total=1000000,
                metodo_pago=MetodoPago.CONSIGNACION,
            )

    def test_efectivo_sin_referencia_valido(self) -> None:
        """Efectivo sin referencia es válido."""
        recaudo = Recaudo(
            id_contrato_a=1,
            fecha_pago="2026-04-01",
            valor_total=1000000,
            metodo_pago=MetodoPago.EFECTIVO,
        )
        assert recaudo.referencia_bancaria is None

    def test_metodo_pago_string_invalido(self) -> None:
        """String de método de pago inválido lanza ValueError."""
        with pytest.raises(ValueError):
            Recaudo(
                id_contrato_a=1,
                fecha_pago="2026-04-01",
                valor_total=1000000,
                metodo_pago="Bitcoin",
            )


class TestRecaudoEstados:
    """Tests de transiciones de estado."""

    def _crear_recaudo_pendiente(self) -> Recaudo:
        """Helper: crea un recaudo en estado Pendiente."""
        return Recaudo(
            id_recaudo=1,
            id_contrato_a=10,
            fecha_pago="2026-04-01",
            valor_total=1500000,
            metodo_pago=MetodoPago.EFECTIVO,
            estado_recaudo=EstadoRecaudo.PENDIENTE,
        )

    def _crear_recaudo_aplicado(self) -> Recaudo:
        """Helper: crea un recaudo en estado Aplicado."""
        return Recaudo(
            id_recaudo=1,
            id_contrato_a=10,
            fecha_pago="2026-04-01",
            valor_total=1500000,
            metodo_pago=MetodoPago.EFECTIVO,
            estado_recaudo=EstadoRecaudo.APLICADO,
        )

    def test_cambiar_pendiente_a_aplicado(self) -> None:
        """Pendiente → Aplicado es válido."""
        recaudo = self._crear_recaudo_pendiente()
        aplicado = recaudo.cambiar_estado(EstadoRecaudo.APLICADO, "admin")

        assert aplicado.estado_recaudo == EstadoRecaudo.APLICADO
        assert aplicado.updated_by == "admin"
        assert aplicado.updated_at is not None

    def test_cambiar_aplicado_a_reversado(self) -> None:
        """Aplicado → Reversado es válido."""
        recaudo = self._crear_recaudo_aplicado()
        reversado = recaudo.cambiar_estado(EstadoRecaudo.REVERSADO, "admin")

        assert reversado.estado_recaudo == EstadoRecaudo.REVERSADO

    def test_no_aplicar_ya_aplicado(self) -> None:
        """Aplicar un recaudo ya Aplicado debe fallar."""
        recaudo = self._crear_recaudo_aplicado()

        with pytest.raises(ValueError, match="Pendiente"):
            recaudo.cambiar_estado(EstadoRecaudo.APLICADO, "admin")

    def test_no_reversar_pendiente(self) -> None:
        """Reversar un recaudo Pendiente debe fallar."""
        recaudo = self._crear_recaudo_pendiente()

        with pytest.raises(ValueError, match="Aplicado"):
            recaudo.cambiar_estado(EstadoRecaudo.REVERSADO, "admin")

    def test_inmutabilidad_al_cambiar_estado(self) -> None:
        """Cambiar estado retorna nueva instancia, no modifica la original."""
        original = self._crear_recaudo_pendiente()
        modificado = original.cambiar_estado(EstadoRecaudo.APLICADO, "admin")

        assert original.estado_recaudo == EstadoRecaudo.PENDIENTE
        assert modificado.estado_recaudo == EstadoRecaudo.APLICADO
        assert original is not modificado


class TestRecaudoProperties:
    """Tests de propiedades calculadas."""

    def test_esta_aplicado_true(self) -> None:
        """Propiedad esta_aplicado retorna True cuando estado es Aplicado."""
        recaudo = Recaudo(
            id_contrato_a=1,
            fecha_pago="2026-04-01",
            valor_total=1000000,
            metodo_pago=MetodoPago.EFECTIVO,
            estado_recaudo=EstadoRecaudo.APLICADO,
        )
        assert recaudo.esta_aplicado is True
        assert recaudo.esta_reversado is False

    def test_esta_reversado_true(self) -> None:
        """Propiedad esta_reversado retorna True cuando estado es Reversado."""
        recaudo = Recaudo(
            id_contrato_a=1,
            fecha_pago="2026-04-01",
            valor_total=1000000,
            metodo_pago=MetodoPago.EFECTIVO,
            estado_recaudo=EstadoRecaudo.REVERSADO,
        )
        assert recaudo.esta_reversado is True
        assert recaudo.esta_aplicado is False
