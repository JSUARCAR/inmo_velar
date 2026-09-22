"""
Tests unitarios para las funciones puras del script de remediación (T027).
Verifica:
1. Resolución de fecha efectiva por contrato (propia, herencia de arriendo, fallback inicio).
2. Evaluación y detección determinística de discrepancias.
"""

from scripts.remediacion.remediar_grupos_pago_v4 import (
    resolver_fecha_efectiva,
    evaluar_contrato,
)


class TestRemediacionFuncionesPuras:
    """Pruebas unitarias sin I/O de las funciones puras del script."""

    def test_resolver_fecha_efectiva_renovacion_propia(self) -> None:
        """Si el contrato tiene renovación propia, prevalece sobre cualquier otra fecha."""
        fecha = resolver_fecha_efectiva(
            tipo_contrato="Mandato",
            fecha_inicio_contrato="2024-01-01",
            fecha_inicio_renovacion_propia="2025-01-02",
            fecha_inicio_renovacion_arriendo="2025-06-01",
        )
        assert fecha == "2025-01-02"

    def test_resolver_fecha_efectiva_herencia_mandato(self) -> None:
        """Si es mandato sin renovación propia pero su arriendo fue renovado, hereda el período."""
        fecha = resolver_fecha_efectiva(
            tipo_contrato="Mandato",
            fecha_inicio_contrato="2024-01-01",
            fecha_inicio_renovacion_propia=None,
            fecha_inicio_renovacion_arriendo="2025-06-01",
        )
        assert fecha == "2025-06-01"

    def test_resolver_fecha_efectiva_arriendo_sin_renovacion_no_hereda(self) -> None:
        """Un arrendamiento sin renovación propia NO hereda; usa su fecha de inicio original."""
        fecha = resolver_fecha_efectiva(
            tipo_contrato="Arrendamiento",
            fecha_inicio_contrato="2024-01-01",
            fecha_inicio_renovacion_propia=None,
            fecha_inicio_renovacion_arriendo="2025-06-01",
        )
        assert fecha == "2024-01-01"

    def test_resolver_fecha_efectiva_fallback_inicio(self) -> None:
        """Si no hay renovaciones, retorna la fecha de inicio original del contrato."""
        fecha = resolver_fecha_efectiva(
            tipo_contrato="Mandato",
            fecha_inicio_contrato="2024-05-18",
            fecha_inicio_renovacion_propia=None,
            fecha_inicio_renovacion_arriendo=None,
        )
        assert fecha == "2024-05-18"

    def test_evaluar_contrato_mandato_detecta_discrepancia(self) -> None:
        """Detecta discrepancia si grupo o día no coinciden con la regla V2 de mandato."""
        # Fecha efectiva día 8 -> Tramo 2: Grupo 2, día 20
        # Valores actuales incorrectos: grupo 1, día 10
        item = evaluar_contrato(
            tipo_contrato="Mandato",
            id_contrato=10,
            id_propiedad=100,
            fecha_inicio_contrato="2025-05-08",
            grupo_actual=1,
            dia_pago_actual="10",
        )
        assert item["discrepancia"] is True
        assert item["grupo_esperado"] == 2
        assert item["dia_pago_esperado"] == "20"
        assert item["grupo_actual"] == 1
        assert item["dia_pago_actual"] == "10"

    def test_evaluar_contrato_arrendamiento_conforme_sin_discrepancia(self) -> None:
        """Retorna discrepancia=False si los valores coinciden con la regla V2 de arriendo."""
        # Fecha efectiva día 18 -> Tramo 3: Grupo 3, día exacto 18
        item = evaluar_contrato(
            tipo_contrato="Arrendamiento",
            id_contrato=20,
            id_propiedad=200,
            fecha_inicio_contrato="2025-05-18",
            grupo_actual=3,
            dia_pago_actual="18",
        )
        assert item["discrepancia"] is False
        assert item["grupo_esperado"] == 3
        assert item["dia_pago_esperado"] == "18"

    # --- Bordes de tramos V2 ---

    def test_evaluar_borde_dia_7_grupo_1(self) -> None:
        """Día 7 = límite superior del tramo 1."""
        item = evaluar_contrato("Mandato", 30, 300, "2025-01-07", 1, "10")
        assert item["discrepancia"] is False

    def test_evaluar_borde_dia_8_grupo_2(self) -> None:
        """Día 8 = límite inferior del tramo 2."""
        item = evaluar_contrato("Mandato", 31, 301, "2025-01-08", 2, "20")
        assert item["discrepancia"] is False

    def test_evaluar_borde_dia_17_grupo_2(self) -> None:
        """Día 17 = límite superior del tramo 2."""
        item = evaluar_contrato("Mandato", 32, 302, "2025-01-17", 2, "20")
        assert item["discrepancia"] is False

    def test_evaluar_borde_dia_18_grupo_3(self) -> None:
        """Día 18 = límite inferior del tramo 3."""
        item = evaluar_contrato("Mandato", 33, 303, "2025-01-18", 3, "30")
        assert item["discrepancia"] is False

    def test_evaluar_borde_dia_27_grupo_3(self) -> None:
        """Día 27 = límite superior del tramo 3."""
        item = evaluar_contrato("Mandato", 34, 304, "2025-01-27", 3, "30")
        assert item["discrepancia"] is False

    def test_evaluar_borde_dia_28_grupo_1(self) -> None:
        """Día 28 = límite inferior del tramo 1 (wrap-around)."""
        item = evaluar_contrato("Mandato", 35, 305, "2025-01-28", 1, "10")
        assert item["discrepancia"] is False

    def test_evaluar_borde_dia_31_grupo_1(self) -> None:
        """Día 31 = dentro del tramo 1."""
        item = evaluar_contrato("Mandato", 36, 306, "2025-01-31", 1, "10")
        assert item["discrepancia"] is False

    def test_evaluar_borde_dia_1_grupo_1(self) -> None:
        """Día 1 = dentro del tramo 1."""
        item = evaluar_contrato("Mandato", 37, 307, "2025-02-01", 1, "10")
        assert item["discrepancia"] is False

    # --- Valores nulos y edge cases ---

    def test_evaluar_grupo_actual_none_genera_discrepancia(self) -> None:
        """grupo_operativo=None (sanitizado a 0) siempre genera discrepancia."""
        item = evaluar_contrato(
            tipo_contrato="Mandato",
            id_contrato=40,
            id_propiedad=400,
            fecha_inicio_contrato="2025-01-01",
            grupo_actual=None,
            dia_pago_actual=None,
        )
        assert item["discrepancia"] is True
        assert item["grupo_actual"] == 0

    def test_evaluar_grupo_actual_cero_genera_discrepancia(self) -> None:
        """grupo_operativo=0 no es válido (solo 1/2/3), genera discrepancia."""
        item = evaluar_contrato(
            tipo_contrato="Arrendamiento",
            id_contrato=41,
            id_propiedad=401,
            fecha_inicio_contrato="2025-03-01",
            grupo_actual=0,
            dia_pago_actual="0",
        )
        assert item["discrepancia"] is True
        assert item["grupo_esperado"] == 1
        assert item["dia_pago_esperado"] == "1"

    # --- Herencia en evaluar_contrato ---

    def test_evaluar_mandato_hereda_arriendo(self) -> None:
        """Mandato sin renovación propia con arriendo renovado hereda la fecha del arriendo."""
        item = evaluar_contrato(
            tipo_contrato="Mandato",
            id_contrato=50,
            id_propiedad=500,
            fecha_inicio_contrato="2024-01-01",
            grupo_actual=1,
            dia_pago_actual="10",
            fecha_inicio_ren_propia=None,
            fecha_inicio_ren_arriendo="2025-05-20",  # Día 20 -> G3, día mandato 30
        )
        assert item["discrepancia"] is True
        assert item["grupo_esperado"] == 3
        assert item["dia_pago_esperado"] == "30"

    # --- Resolver fecha efectiva: edge cases ---

    def test_resolver_fecha_efectiva_renovacion_propia_vacia(self) -> None:
        """String vacío en renovación propia se trata como ausente."""
        fecha = resolver_fecha_efectiva(
            tipo_contrato="Mandato",
            fecha_inicio_contrato="2024-01-01",
            fecha_inicio_renovacion_propia="",
            fecha_inicio_renovacion_arriendo="2025-03-10",
        )
        assert fecha == "2025-03-10"

    def test_resolver_fecha_efectiva_trunca_timestamp(self) -> None:
        """Fechas con timestamp se truncan a los primeros 10 caracteres."""
        fecha = resolver_fecha_efectiva(
            tipo_contrato="Mandato",
            fecha_inicio_contrato="2024-01-01T00:00:00",
            fecha_inicio_renovacion_propia="2025-06-15T12:30:00",
        )
        assert fecha == "2025-06-15"
