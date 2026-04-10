"""
Tests unitarios para los modelos de Propiedad Horizontal.
"""

import pytest
from pydantic import ValidationError


class TestAsistenciaModel:
    """Tests para el modelo AsistenciaModel."""

    def test_crear_asistencia_model_completo(self):
        """Test: Crear AsistenciaModel con todos los campos."""
        from src.presentacion_reflex.state.propiedad_horizontal_models import (
            AsistenciaModel,
        )

        asistencia = AsistenciaModel(
            id_asistencia=1,
            id_propiedad=10,
            direccion_propiedad="Calle 123",
            fecha_asistencia="2026-04-15",
            hora_asistencia="14:00",
            tipo_reunion="Ordinaria",
            tipo_asistente="Propietario",
            nombre_asistente="Juan Pérez",
            costo_asistente=0.0,
            direccion_asistencia="Edificio Centro",
            estado_asistencia="Programada",
            color_tipo="blue",
        )

        assert asistencia.id_asistencia == 1
        assert asistencia.id_propiedad == 10
        assert asistencia.tipo_reunion == "Ordinaria"
        assert asistencia.estado_asistencia == "Programada"

    def test_asistencia_model_campos_requeridos(self):
        """Test: Verificar campos requeridos."""
        from src.presentacion_reflex.state.propiedad_horizontal_models import (
            AsistenciaModel,
        )

        with pytest.raises(ValidationError):
            AsistenciaModel()


class TestPagoAdminModel:
    """Tests para el modelo PagoAdminModel."""

    def test_crear_pago_admin_model_completo(self):
        """Test: Crear PagoAdminModel con todos los campos."""
        from src.presentacion_reflex.state.propiedad_horizontal_models import (
            PagoAdminModel,
        )

        pago = PagoAdminModel(
            id_pago_admin=1,
            id_propiedad=10,
            nombre_propietario="Juan Pérez",
            direccion_propiedad="Calle 123",
            valor_administracion=500000.0,
            valor_formateado="$500,000",
            fecha_pago=15,
            link_pago="https://pago.com/123",
            periodo_pago="2026-04",
            estado_pago="Pendiente",
            color_estado="yellow",
        )

        assert pago.id_pago_admin == 1
        assert pago.valor_administracion == 500000.0
        assert pago.estado_pago == "Pendiente"

    def test_pago_admin_model_campos_requeridos(self):
        """Test: Verificar campos requeridos."""
        from src.presentacion_reflex.state.propiedad_horizontal_models import (
            PagoAdminModel,
        )

        with pytest.raises(ValidationError):
            PagoAdminModel()


class TestPropiedadHorizontalStateImports:
    """Tests para verificar importación correcta en State."""

    def test_state_importa_modelos_desde_ubicacion_centralizada(self):
        """Test: Verificar que el State usa los modelos centralizados."""
        from src.presentacion_reflex.state.propiedad_horizontal_models import (
            AsistenciaModel,
            PagoAdminModel,
        )

        # Verificar que las clases existen y son las correctas
        assert hasattr(AsistenciaModel, "model_fields")
        assert hasattr(PagoAdminModel, "model_fields")

        # Verificar campos esperados
        asistencia_fields = set(AsistenciaModel.model_fields.keys())
        assert "id_asistencia" in asistencia_fields
        assert "tipo_reunion" in asistencia_fields

        pago_fields = set(PagoAdminModel.model_fields.keys())
        assert "id_pago_admin" in pago_fields
        assert "valor_administracion" in pago_fields
