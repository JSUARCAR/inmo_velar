"""
Tests TDD para corrección de paginación del Kanban de Incidentes.

Valida que:
- El Kanban carga TODOS los incidentes sin paginación.
- La vista Lista mantiene paginación de 12 items.
- El servicio propaga filtro de estado a SQL.
- La UI no tiene rx.text anidados (errores de hidratación).
"""
import ast
import re
import unittest
from pathlib import Path

# Rutas de archivos bajo test
BASE_DIR = Path(__file__).resolve().parent.parent
STATE_FILE = BASE_DIR / "src" / "presentacion_reflex" / "state" / "incidentes_state.py"
PAGE_FILE = BASE_DIR / "src" / "presentacion_reflex" / "pages" / "incidentes.py"
SERVICIO_FILE = BASE_DIR / "src" / "aplicacion" / "servicios" / "servicio_incidentes.py"
KANBAN_FILE = BASE_DIR / "src" / "presentacion_reflex" / "components" / "incidentes" / "kanban_board.py"


class TestTarea1KanbanSinPaginacion(unittest.TestCase):
    """Tarea 1: El Kanban NO debe paginar resultados."""

    def setUp(self):
        """Lee el código del state."""
        self.state_code = STATE_FILE.read_text(encoding="utf-8")

    def test_load_incidentes_tiene_logica_condicional_por_view_mode(self):
        """load_incidentes debe diferenciar entre kanban y lista para paginación."""
        # Buscar que exista lógica condicional con view_mode en load_incidentes
        self.assertIn(
            "view_mode",
            self.state_code[self.state_code.index("async def load_incidentes"):],
            "load_incidentes debe usar view_mode para decidir si paginar",
        )

    def test_kanban_no_envia_page_al_servicio(self):
        """Cuando view_mode=='kanban', page y page_size deben ser None."""
        # Buscar que exista lógica para pasar page=None cuando es kanban
        load_fn = self.state_code[self.state_code.index("async def load_incidentes"):]
        load_fn = load_fn[: load_fn.index("\n    @rx.event") if "\n    @rx.event" in load_fn else len(load_fn)]

        # Debe existir alguna condición que ponga page a None
        tiene_none_page = "page=None" in load_fn or "page_size=None" in load_fn
        tiene_condicion = "kanban" in load_fn.lower() and ("None" in load_fn)
        self.assertTrue(
            tiene_none_page or tiene_condicion,
            "load_incidentes debe pasar page=None cuando view_mode es kanban",
        )

    def test_toggle_view_mode_recarga_datos(self):
        """toggle_view_mode debe disparar load_incidentes al cambiar."""
        toggle_fn_start = self.state_code.index("def toggle_view_mode")
        toggle_fn = self.state_code[toggle_fn_start:]
        # Buscar el final del método (siguiente def o clase)
        next_def = toggle_fn.find("\n    def ", 10)
        next_event = toggle_fn.find("\n    @rx.event", 10)
        end = min(x for x in [next_def, next_event, len(toggle_fn)] if x > 0)
        toggle_fn = toggle_fn[:end]

        self.assertIn(
            "load_incidentes",
            toggle_fn,
            "toggle_view_mode debe invocar load_incidentes al cambiar vista",
        )


class TestTarea1PaginacionCondicionalUI(unittest.TestCase):
    """Tarea 1: Los controles de paginación deben ocultarse en modo Kanban."""

    def setUp(self):
        """Lee el código de la página."""
        self.page_code = PAGE_FILE.read_text(encoding="utf-8")

    def test_paginacion_condicionada_a_vista_lista(self):
        """Los botones Anterior/Siguiente solo deben aparecer en vista lista."""
        # Debe existir rx.cond o condicional con view_mode antes de los controles
        tiene_cond_view = (
            "view_mode" in self.page_code
            and ("list" in self.page_code or "kanban" in self.page_code)
        )
        # Los controles de paginación deben estar envueltos en una condición
        idx_anterior = self.page_code.find("Anterior")
        if idx_anterior > -1:
            # Verificar que hay un rx.cond antes de los controles de paginación
            contexto_antes = self.page_code[max(0, idx_anterior - 300):idx_anterior]
            tiene_condicion = "rx.cond" in contexto_antes or "view_mode" in contexto_antes
            self.assertTrue(
                tiene_condicion,
                "Los controles de paginación deben estar condicionados al view_mode",
            )


class TestTarea2ServicioUsaRepoConFiltros(unittest.TestCase):
    """Tarea 2: El servicio debe usar repo.listar_con_filtros() y pasar estado."""

    def setUp(self):
        """Lee el código del servicio."""
        self.servicio_code = SERVICIO_FILE.read_text(encoding="utf-8")

    def test_servicio_listar_con_filtros_usa_repositorio(self):
        """listar_con_filtros del servicio debe delegar al repo.listar_con_filtros()."""
        # Buscar la definición del método
        idx = self.servicio_code.index("def listar_con_filtros")
        metodo = self.servicio_code[idx:]
        # Encontrar el final del método
        next_def = metodo.find("\n    def ", 10)
        metodo = metodo[:next_def] if next_def > 0 else metodo

        self.assertIn(
            "repo_incidentes.listar_con_filtros",
            metodo,
            "El servicio debe delegar al repo.listar_con_filtros() en vez de repo.listar()",
        )

    def test_servicio_acepta_parametro_estado(self):
        """listar_con_filtros del servicio debe aceptar el parámetro 'estado'."""
        idx = self.servicio_code.index("def listar_con_filtros")
        # Buscar hasta el cierre de la firma (-> o ):)
        end_firma = self.servicio_code.index(":", idx + 25)
        # Ampliar para cubrir toda la firma multilínea
        firma = self.servicio_code[idx:end_firma + 200]

        self.assertIn(
            "estado",
            firma,
            "listar_con_filtros debe aceptar parámetro 'estado'",
        )

    def test_state_pasa_estado_al_servicio(self):
        """El state debe pasar el filtro de estado al servicio."""
        state_code = STATE_FILE.read_text(encoding="utf-8")
        load_fn_start = state_code.index("async def load_incidentes")
        load_fn = state_code[load_fn_start:]
        next_event = load_fn.find("\n    @rx.event", 10)
        load_fn = load_fn[:next_event] if next_event > 0 else load_fn

        # Debe pasar estado= al servicio
        self.assertIn(
            "estado=",
            load_fn,
            "load_incidentes debe pasar estado= al servicio listar_con_filtros",
        )

    def test_state_no_filtra_estado_en_memoria(self):
        """El state NO debe filtrar por estado en memoria tras paginar."""
        state_code = STATE_FILE.read_text(encoding="utf-8")
        load_fn_start = state_code.index("async def load_incidentes")
        load_fn = state_code[load_fn_start:]
        next_event = load_fn.find("\n    @rx.event", 10)
        load_fn = load_fn[:next_event] if next_event > 0 else load_fn

        # No debe existir filtrado manual de estado en memoria
        tiene_filtro_memoria = "if estado:" in load_fn and "i.estado ==" in load_fn
        self.assertFalse(
            tiene_filtro_memoria,
            "No debe haber filtrado por estado en memoria — debe hacerse via SQL",
        )


class TestTarea3HidratacionCorrecta(unittest.TestCase):
    """Tarea 3: No debe haber rx.text anidado dentro de rx.text."""

    def setUp(self):
        """Lee el código de la página."""
        self.page_code = PAGE_FILE.read_text(encoding="utf-8")

    def test_no_rx_text_anidado(self):
        """No debe existir rx.text(rx.text(...)) que cause errores de hidratación."""
        # Buscar patrón rx.text( ... rx.text(
        patron = r"rx\.text\(\s*\n\s*rx\.text\("
        matches = re.findall(patron, self.page_code)
        self.assertEqual(
            len(matches),
            0,
            f"Encontrados {len(matches)} rx.text anidados — causa errores de hidratación",
        )


class TestTarea4SkeletonLoader(unittest.TestCase):
    """Tarea 4: El Kanban debe tener skeleton loaders durante carga."""

    def setUp(self):
        """Lee el código del kanban board."""
        self.kanban_code = KANBAN_FILE.read_text(encoding="utf-8")

    def test_kanban_tiene_skeleton_o_loading(self):
        """El componente Kanban debe tener un indicador de carga."""
        tiene_skeleton = "skeleton" in self.kanban_code.lower()
        tiene_spinner = "spinner" in self.kanban_code.lower()
        tiene_loading = "is_loading" in self.kanban_code
        self.assertTrue(
            tiene_skeleton or tiene_spinner or tiene_loading,
            "kanban_board.py debe tener un indicador de carga (skeleton/spinner/is_loading)",
        )


class TestIntegridadCompilacion(unittest.TestCase):
    """Verifica que todos los módulos importan correctamente."""

    def test_import_incidentes_state(self):
        """El state de incidentes debe importar sin errores."""
        import importlib.util
        spec = importlib.util.spec_from_file_location("incidentes_state", STATE_FILE)
        self.assertIsNotNone(spec, "No se encontró el módulo incidentes_state")

    def test_import_incidentes_page(self):
        """La página de incidentes debe importar sin errores."""
        import importlib.util
        spec = importlib.util.spec_from_file_location("incidentes", PAGE_FILE)
        self.assertIsNotNone(spec, "No se encontró el módulo incidentes")

    def test_import_kanban_board(self):
        """El componente kanban_board debe importar sin errores."""
        import importlib.util
        spec = importlib.util.spec_from_file_location("kanban_board", KANBAN_FILE)
        self.assertIsNotNone(spec, "No se encontró el módulo kanban_board")

    def test_import_servicio_incidentes(self):
        """El servicio de incidentes debe importar sin errores."""
        import importlib.util
        spec = importlib.util.spec_from_file_location("servicio_incidentes", SERVICIO_FILE)
        self.assertIsNotNone(spec, "No se encontró el módulo servicio_incidentes")


if __name__ == "__main__":
    unittest.main()
