"""
Tests unitarios para los formateadores de PropiedadHorizontalState.
"""

import pytest
from datetime import date, time


class TestFormateoFechas:
    """Tests para verificar manejo de excepciones específicas en formateo de fechas."""

    def test_formatear_fecha_date_valido(self):
        """Test: Formatear fecha con objeto date válido."""
        from src.presentacion_reflex.state.propiedad_horizontal_state import (
            PropiedadHorizontalState,
        )

        state = PropiedadHorizontalState()
        resultado = state._formatear_fecha(date(2026, 4, 15))
        assert resultado == "15/04/2026"

    def test_formatear_fecha_string_iso_valido(self):
        """Test: Formatear fecha con string ISO válido."""
        from src.presentacion_reflex.state.propiedad_horizontal_state import (
            PropiedadHorizontalState,
        )

        state = PropiedadHorizontalState()
        resultado = state._formatear_fecha("2026-04-15")
        assert resultado == "15/04/2026"

    def test_formatear_fecha_string_guiones_valido(self):
        """Test: Formatear fecha con string formato YYYY-MM-DD."""
        from src.presentacion_reflex.state.propiedad_horizontal_state import (
            PropiedadHorizontalState,
        )

        state = PropiedadHorizontalState()
        resultado = state._formatear_fecha("2026-04-15")
        assert resultado == "15/04/2026"

    def test_formatear_fecha_none_retorna_na(self):
        """Test: Formatear fecha None retorna N/A."""
        from src.presentacion_reflex.state.propiedad_horizontal_state import (
            PropiedadHorizontalState,
        )

        state = PropiedadHorizontalState()
        resultado = state._formatear_fecha(None)
        assert resultado == "N/A"

    def test_formatear_fecha_invalida_datos_corruptos(self):
        """Test: Formatear fecha con datos corruptos alerta específicamente."""
        from src.presentacion_reflex.state.propiedad_horizontal_state import (
            PropiedadHorizontalState,
        )

        state = PropiedadHorizontalState()
        # Fecha con formato inválido que indica dato corrupto en BD
        resultado = state._formatear_fecha("fecha-invalida-xyz")
        assert resultado == "Error Fecha"

    def test_formatear_fecha_lista_datos_corruptos(self):
        """Test: Formatear fecha con lista (dato corrupto) alerta específicamente."""
        from src.presentacion_reflex.state.propiedad_horizontal_state import (
            PropiedadHorizontalState,
        )

        state = PropiedadHorizontalState()
        resultado = state._formatear_fecha([2026, 4, 15])
        assert resultado == "Error Fecha"


class TestFormateoHoras:
    """Tests para verificar manejo de excepciones específicas en formateo de horas."""

    def test_formatear_hora_time_valido(self):
        """Test: Formatear hora con objeto time válido."""
        from src.presentacion_reflex.state.propiedad_horizontal_state import (
            PropiedadHorizontalState,
        )

        state = PropiedadHorizontalState()
        resultado = state._formatear_hora(time(14, 30))
        assert resultado == "02:30 PM"

    def test_formatear_hora_string_hms_valido(self):
        """Test: Formatear hora con string HH:MM:SS válido."""
        from src.presentacion_reflex.state.propiedad_horizontal_state import (
            PropiedadHorizontalState,
        )

        state = PropiedadHorizontalState()
        resultado = state._formatear_hora("14:30:00")
        assert resultado == "02:30 PM"

    def test_formatear_hora_string_hm_valido(self):
        """Test: Formatear hora con string HH:MM válido."""
        from src.presentacion_reflex.state.propiedad_horizontal_state import (
            PropiedadHorizontalState,
        )

        state = PropiedadHorizontalState()
        resultado = state._formatear_hora("14:30")
        assert resultado == "02:30 PM"

    def test_formatear_hora_none_retorna_na(self):
        """Test: Formatear hora None retorna N/A."""
        from src.presentacion_reflex.state.propiedad_horizontal_state import (
            PropiedadHorizontalState,
        )

        state = PropiedadHorizontalState()
        resultado = state._formatear_hora(None)
        assert resultado == "N/A"

    def test_formatear_hora_invalida_datos_corruptos(self):
        """Test: Formatear hora con datos corruptos alerta específicamente."""
        from src.presentacion_reflex.state.propiedad_horizontal_state import (
            PropiedadHorizontalState,
        )

        state = PropiedadHorizontalState()
        resultado = state._formatear_hora("hora-invalida")
        assert resultado == "Error Hora"


class TestFormateoMontos:
    """Tests para verificar formateo de montos."""

    def test_formatear_monto_numero_valido(self):
        """Test: Formatear monto con número válido."""
        from src.presentacion_reflex.state.propiedad_horizontal_state import (
            PropiedadHorizontalState,
        )

        state = PropiedadHorizontalState()
        resultado = state._formatear_monto(500000)
        assert resultado == "$500,000"

    def test_formatear_monto_none_retorna_cero(self):
        """Test: Formatear monto None retorna $0."""
        from src.presentacion_reflex.state.propiedad_horizontal_state import (
            PropiedadHorizontalState,
        )

        state = PropiedadHorizontalState()
        resultado = state._formatear_monto(None)
        assert resultado == "$0"

    def test_formatear_monto_invalido_retorna_cero(self):
        """Test: Formatear monto con valor inválido retorna $0."""
        from src.presentacion_reflex.state.propiedad_horizontal_state import (
            PropiedadHorizontalState,
        )

        state = PropiedadHorizontalState()
        resultado = state._formatear_monto("no-es-numero")
        assert resultado == "$0"
