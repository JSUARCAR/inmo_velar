"""
Tests de Verificación: Optimización Tipográfica - Sistema 10%
Valida que las correcciones de legibilidad, estandarización y
breakpoints móviles están aplicadas correctamente.

Patrón: Arrange-Act-Assert (AAA)
Cobertura: CSS variables, Radix overrides, KPI card, pages
"""

import re
import pytest
from pathlib import Path


# === CONSTANTES DE TEST ===

# Ruta base del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent
CSS_FILE = BASE_DIR / "assets" / "custom_layout_v2.css"
STYLES_PY = BASE_DIR / "src" / "presentacion_reflex" / "styles.py"
KPI_CARD_PY = (
    BASE_DIR / "src" / "presentacion_reflex" / "components" / "dashboard" / "kpi_card.py"
)
LOGIN_PY = BASE_DIR / "src" / "presentacion_reflex" / "pages" / "login.py"
PROPIEDADES_PY = BASE_DIR / "src" / "presentacion_reflex" / "pages" / "propiedades.py"
DASHBOARD_PY = BASE_DIR / "src" / "presentacion_reflex" / "pages" / "dashboard.py"


@pytest.fixture
def css_content() -> str:
    """Lee el contenido del archivo CSS principal."""
    return CSS_FILE.read_text(encoding="utf-8")


@pytest.fixture
def kpi_card_content() -> str:
    """Lee el contenido del archivo KPI card."""
    return KPI_CARD_PY.read_text(encoding="utf-8")


@pytest.fixture
def login_content() -> str:
    """Lee el contenido de la página de login."""
    return LOGIN_PY.read_text(encoding="utf-8")


@pytest.fixture
def propiedades_content() -> str:
    """Lee el contenido de la página de propiedades."""
    return PROPIEDADES_PY.read_text(encoding="utf-8")


@pytest.fixture
def dashboard_content() -> str:
    """Lee el contenido de la página de dashboard."""
    return DASHBOARD_PY.read_text(encoding="utf-8")


# ============================================================================
# TAREA 1: Corregir size="1" para legibilidad (≥11px)
# ============================================================================


class TestTarea1CorregirSize1:
    """Verifica que --font-size-1 y --font-size-xs son ≥ 11px a 12px base."""

    def test_font_size_xs_minimo_11px_en_root(self, css_content: str) -> None:
        """--font-size-xs en :root debe ser ≥ 0.917rem (11px @ 12px base)."""
        match = re.search(r"--font-size-xs:\s*([\d.]+)rem", css_content)
        assert match is not None, "--font-size-xs no encontrado en :root"
        valor_rem = float(match.group(1))
        valor_px = valor_rem * 12  # base 12px
        assert valor_px >= 11, (
            f"--font-size-xs = {valor_rem}rem = {valor_px}px, debería ser ≥ 11px"
        )

    def test_font_size_1_radix_themes_minimo_11px(self, css_content: str) -> None:
        """--font-size-1 en .radix-themes debe ser ≥ 0.917rem (11px @ 12px base)."""
        # Buscar en el bloque .radix-themes
        radix_block = re.search(
            r"\.radix-themes\s*\{([^}]+)\}", css_content
        )
        assert radix_block is not None, "Bloque .radix-themes no encontrado"
        match = re.search(
            r"--font-size-1:\s*([\d.]+)rem", radix_block.group(1)
        )
        assert match is not None, "--font-size-1 no encontrado en .radix-themes"
        valor_rem = float(match.group(1))
        valor_px = valor_rem * 12
        assert valor_px >= 11, (
            f"--font-size-1 en .radix-themes = {valor_rem}rem = {valor_px}px, "
            "debería ser ≥ 11px"
        )

    def test_font_size_1_dark_theme_consistente(self, css_content: str) -> None:
        """--font-size-1 en dark theme debe ser coherente con light theme."""
        # Buscar ambos valores de --font-size-1
        matches = re.findall(r"--font-size-1:\s*([\d.]+)rem", css_content)
        assert len(matches) >= 2, (
            f"Se esperaban al menos 2 declaraciones de --font-size-1, "
            f"encontradas {len(matches)}"
        )
        # Verificar que light y dark usan el mismo valor
        assert matches[0] == matches[1], (
            f"--font-size-1 inconsistente: light={matches[0]}rem, dark={matches[1]}rem"
        )

    def test_no_queda_075rem_en_font_size_1(self, css_content: str) -> None:
        """No debe haber --font-size-1: 0.75rem (valor antiguo ilegible)."""
        assert "--font-size-1: 0.75rem" not in css_content, (
            "ERROR: --font-size-1 todavía usa 0.75rem (9px), debería ser ≥ 0.917rem"
        )


# ============================================================================
# TAREA 2: Estandarizar size="8" en todo el sistema
# ============================================================================


class TestTarea2EstandarizarSize8:
    """Verifica que todos los headings size='8' usan la variable CSS centralizada."""

    def test_login_sin_font_size_hardcoded(self, login_content: str) -> None:
        """Login no debe tener font_size=[...] junto a size='8'."""
        # Verificar que no hay font_size con lista de valores
        assert "font_size=[" not in login_content or "size=\"8\"" not in login_content.split("font_size=[")[0][-100:], (
            "Login todavía tiene font_size=[...] hardcoded junto a size='8'"
        )

    def test_propiedades_sin_font_size_hardcoded(self, propiedades_content: str) -> None:
        """Propiedades no debe tener font_size=[...] junto a size='8'."""
        # Buscar heading con size="8" y verificar que no tiene font_size=[...]
        lines = propiedades_content.split("\n")
        for i, line in enumerate(lines):
            if 'size="8"' in line:
                # Verificar las 3 líneas siguientes no tienen font_size=[
                context = "\n".join(lines[max(0, i-1):i+4])
                assert "font_size=[" not in context, (
                    f"Propiedades tiene font_size=[...] hardcoded cerca de size='8' "
                    f"en línea {i+1}"
                )

    def test_dashboard_usa_variable_css(self, dashboard_content: str) -> None:
        """Dashboard debe usar size='8' sin font_size override."""
        lines = dashboard_content.split("\n")
        for i, line in enumerate(lines):
            if 'size="8"' in line:
                context = "\n".join(lines[max(0, i-1):i+4])
                assert "font_size=" not in context, (
                    f"Dashboard tiene font_size hardcoded cerca de size='8' "
                    f"en línea {i+1}"
                )

    def test_font_size_8_variable_css_consistente(self, css_content: str) -> None:
        """--font-size-8 debe ser el mismo en light y dark themes."""
        matches = re.findall(r"--font-size-8:\s*([\d.]+)rem", css_content)
        assert len(matches) >= 2, (
            f"Expected ≥2 --font-size-8 declarations, found {len(matches)}"
        )
        assert matches[0] == matches[1], (
            f"--font-size-8 inconsistente: light={matches[0]}rem, dark={matches[1]}rem"
        )


# ============================================================================
# TAREA 3: Optimizar breakpoints móviles (≥12px mínimo)
# ============================================================================


class TestTarea3BreakpointsMoviles:
    """Verifica que el font-size base en móvil garantiza legibilidad."""

    def test_mobile_html_font_size_minimo_12px(self, css_content: str) -> None:
        """El font-size de html en @media (max-width: 768px) debe ser ≥ 12px."""
        # Buscar el bloque @media mobile
        mobile_block = re.search(
            r"@media\s*\(max-width:\s*768px\)\s*\{(.+?)\}\s*\}",
            css_content,
            re.DOTALL,
        )
        assert mobile_block is not None, (
            "No se encontró el bloque @media (max-width: 768px)"
        )
        # Buscar html { font-size: Xpx } dentro del bloque
        html_match = re.search(
            r"html\s*\{[^}]*font-size:\s*(\d+)px", mobile_block.group(1)
        )
        assert html_match is not None, (
            "No se encontró html { font-size } en el bloque mobile"
        )
        font_size_px = int(html_match.group(1))
        assert font_size_px >= 12, (
            f"Font-size base en móvil = {font_size_px}px, debería ser ≥ 12px"
        )

    def test_mobile_font_size_1_override_existe(self, css_content: str) -> None:
        """Debe existir un override de --font-size-1 en el bloque mobile."""
        mobile_block = re.search(
            r"@media\s*\(max-width:\s*768px\)\s*\{(.+?)\}\s*\}",
            css_content,
            re.DOTALL,
        )
        assert mobile_block is not None
        assert "--font-size-1:" in mobile_block.group(1), (
            "No hay override de --font-size-1 en el bloque mobile"
        )

    def test_no_queda_font_size_10px_en_mobile(self, css_content: str) -> None:
        """No debe haber font-size: 10px en el bloque mobile."""
        mobile_block = re.search(
            r"@media\s*\(max-width:\s*768px\)\s*\{(.+?)\}\s*\}",
            css_content,
            re.DOTALL,
        )
        assert mobile_block is not None
        assert "font-size: 10px" not in mobile_block.group(1), (
            "ERROR: Font-size base móvil todavía es 10px (debe ser ≥ 12px)"
        )


# ============================================================================
# TAREA 4: Ajustar KPI cards - consolidar en CSS variables
# ============================================================================


class TestTarea4AjustarKPICards:
    """Verifica que las KPI cards no tienen font_size hardcoded."""

    def test_kpi_elite_sin_breakpoints_hardcoded(self, kpi_card_content: str) -> None:
        """El variant 'elite' no debe tener font_size=rx.breakpoints(...)."""
        assert "rx.breakpoints(" not in kpi_card_content, (
            "KPI card todavía usa rx.breakpoints() para font_size. "
            "Debería usar la variable CSS --font-size-8 vía size='8'"
        )

    def test_kpi_standard_sin_font_size_list(self, kpi_card_content: str) -> None:
        """El variant 'standard' no debe tener font_size=[...] hardcoded."""
        assert "font_size=[" not in kpi_card_content, (
            "KPI card standard todavía usa font_size=[...] hardcoded."
        )

    def test_kpi_usa_size_prop_radix(self, kpi_card_content: str) -> None:
        """KPI card debe usar size= prop de Radix para tipografía."""
        assert 'size="8"' in kpi_card_content or 'size="6"' in kpi_card_content, (
            "KPI card no usa size prop de Radix para valores principales"
        )


# ============================================================================
# VERIFICACIÓN DE INTEGRIDAD: Imports y Compilación
# ============================================================================


class TestIntegridadCompilacion:
    """Verifica que todos los módulos importan correctamente."""

    def test_import_styles(self) -> None:
        """El módulo styles debe importar sin errores."""
        from src.presentacion_reflex import styles

        assert hasattr(styles, "FONT_SIZE_XS"), "FONT_SIZE_XS no existe en styles"
        assert hasattr(styles, "FONT_SIZE_SM"), "FONT_SIZE_SM no existe en styles"
        assert styles.FONT_SIZE_XS == "var(--font-size-xs)"

    def test_import_kpi_card(self) -> None:
        """El componente KPI card debe importar sin errores."""
        from src.presentacion_reflex.components.dashboard.kpi_card import kpi_card

        assert callable(kpi_card), "kpi_card no es callable"

    def test_import_pages(self) -> None:
        """Las páginas principales deben importar sin errores."""
        from src.presentacion_reflex.pages import dashboard, login, propiedades

        assert dashboard is not None
        assert login is not None
        assert propiedades is not None

    def test_archivos_css_existen(self) -> None:
        """Los archivos CSS del sistema deben existir."""
        assert CSS_FILE.exists(), f"CSS file no encontrado: {CSS_FILE}"

    def test_consistencia_font_scale_css(self) -> None:
        """La escala tipográfica CSS debe ser monótonamente creciente."""
        content = CSS_FILE.read_text(encoding="utf-8")
        # Extraer todos los font-size del :root
        root_match = re.search(r":root\s*\{([^}]+)\}", content, re.DOTALL)
        assert root_match is not None
        sizes = re.findall(
            r"--font-size-\w+:\s*([\d.]+)rem", root_match.group(1)
        )
        sizes_float = [float(s) for s in sizes]
        for i in range(1, len(sizes_float)):
            assert sizes_float[i] >= sizes_float[i - 1], (
                f"Escala tipográfica no es creciente: "
                f"{sizes_float[i-1]}rem > {sizes_float[i]}rem"
            )
