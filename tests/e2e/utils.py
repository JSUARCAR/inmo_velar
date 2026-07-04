from playwright.sync_api import Page, expect

def navigate_to_module(page: Page, module_name: str, url_path: str):
    """Navega a un módulo específico usando el sidebar o directamente la URL."""
    base_url = "https://extraordinary-joy-production-2fd2.up.railway.app/"
    target_url = f"{base_url}{url_path}"
    
    # Navegación directa es más rápida y menos propensa a fallos de UI
    page.goto(target_url)
    # Esperamos que cargue la tabla principal o título
    page.wait_for_load_state("networkidle")
    
def select_property_in_table(page: Page, property_name: str):
    """Busca una propiedad en la tabla actual de forma flexible."""
    # Buscar directamente el texto (sin asumir role="row")
    elemento = page.get_by_text(property_name, exact=False).first
    expect(elemento).to_be_visible(timeout=15000)
    
    # Intentamos devolver el <tr> padre si existe, sino el propio elemento
    row = page.locator("tr").filter(has_text=property_name).first
    return row
