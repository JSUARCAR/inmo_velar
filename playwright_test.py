from playwright.sync_api import sync_playwright
import time

def run(playwright):
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()

    print("Navegando a la URL...")
    page.goto("https://extraordinary-joy-production-2fd2.up.railway.app/liquidaciones")
    
    print("Iniciando sesión...")
    # Asumiendo los selectores básicos para un form de login genérico de Reflex si redirige
    # O tal vez ya haya inputs. Vamos a esperar a que cargue.
    time.sleep(2)
    
    # Check if login is needed (si hay inputs de username/password)
    username_input = page.locator("input[name='username'], input[placeholder*='usuario' i], input[placeholder*='user' i]")
    if username_input.count() > 0:
        username_input.first.fill("jsuarcar")
        page.locator("input[name='password'], input[type='password']").first.fill("velarjoan2026")
        page.locator("button[type='submit'], button:has-text('Iniciar'), button:has-text('Ingresar'), button:has-text('Login')").first.click()
        time.sleep(3)
        print("Login completado.")
        
        # Redirigiendo explícitamente a liquidaciones de nuevo por si acaso el login redirige a dashboard
        page.goto("https://extraordinary-joy-production-2fd2.up.railway.app/liquidaciones")
        time.sleep(3)

    print("Buscando la liquidación 562 o CONJ CIUDADELA COMFENALCO...")
    # Intentar usar el campo de búsqueda de la tabla de liquidaciones
    search_input = page.locator("input[placeholder*='Buscar' i]")
    if search_input.count() > 0:
        search_input.first.fill("562")
        search_input.first.press("Enter")
        time.sleep(3)
        
    print("Buscando botón de Editar...")
    # Click on edit button (icon-button con icon 'pencil' o class que lo contenga)
    # The table has a pencil icon for editing
    edit_buttons = page.locator("button:has(svg.lucide-pencil)")
    if edit_buttons.count() > 0:
        edit_buttons.first.click()
        print("Botón Editar clickeado.")
    else:
        print("No se encontró el botón Editar. Buscando alternativas...")
        # fallback
        page.get_by_role("button", name="Editar").first.click()
        
    time.sleep(2)
    
    print("Buscando botón 'Seleccionar Incidentes'...")
    select_inc_btn = page.locator("button:has-text('Seleccionar Incidentes')")
    if select_inc_btn.count() > 0:
        print("Haciendo clic en 'Seleccionar Incidentes'...")
        select_inc_btn.first.click()
        time.sleep(2)
        
        # Comprobar si el modal se abrió
        modal_header = page.locator("text='Seleccionar Incidentes'")
        # En Reflex, el dialog suele renderizarse en un Div con role="dialog" o similar
        dialog = page.locator("[role='dialog']")
        if dialog.count() > 1:
            print("=> RESULTADO: Se abrió un nuevo modal.")
        else:
            print("=> RESULTADO: NO sucedió nada, el modal no apareció.")
    else:
        print("No se encontró el botón 'Seleccionar Incidentes'")

    print("Dejando el navegador abierto por 5 segundos para que puedas visualizarlo...")
    time.sleep(5)
    
    context.close()
    browser.close()

with sync_playwright() as playwright:
    run(playwright)
