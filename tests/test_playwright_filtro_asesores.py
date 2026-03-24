from playwright.sync_api import sync_playwright, expect
import time

def test_filtro_asesores():
    print("Iniciando prueba Playwright...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        try:
            # 1. Navegar a la URL
            print("Navegando a la URL...")
            page.goto("https://extraordinary-joy-production-2fd2.up.railway.app/")
            page.wait_for_load_state("networkidle")

            # 2. Login
            print("Iniciando sesión...")
            # Usando locators basados en el código fuente de login.py
            username_input = page.locator("input[name='username']")
            username_input.wait_for(state="visible", timeout=15000)
            username_input.fill("admin")
            
            password_input = page.locator("input[type='password']")
            password_input.fill("admin0123")
            
            # Hay botones para ver contraseña, así que es mejor buscar el botón de submit o que contiene Ingresar
            login_button = page.locator("button:has-text('Ingresar'), button[type='submit']").first
            login_button.click()

            # Esperar a que pase del login
            page.wait_for_url("**/dashboard*", timeout=15000)
            print("Login completado.")
            
            # 3. Navegar a Liquidaciones
            print("Navegando al módulo de Liquidaciones...")
            page.goto("https://extraordinary-joy-production-2fd2.up.railway.app/liquidaciones")
            page.wait_for_timeout(5000) # Esperar a que carguen los datos y el toolbar

            # 4. Validar Filtro de Asesores en Vista Individual
            print("\n--- Vista Individual ---")
            comboboxes = page.get_by_role("combobox").all()
            
            if len(comboboxes) >= 3:
                asesor_combobox = comboboxes[2]
                asesor_combobox.click()
                page.wait_for_timeout(2000)
                
                options = page.get_by_role("option").all()
                opciones_texto = [opt.inner_text() for opt in options]
                print(f"Opciones cargadas en el filtro Asesor: {opciones_texto}")
                
                if len(options) > 1:
                    print("✅ ÉXITO: El filtro de asesores cargó correctamente más de una opción en Vista Individual.")
                else:
                    print("❌ ERROR: El filtro de asesores solo cargó 'Todos' o está vacío en Vista Individual.")
                
                page.keyboard.press("Escape")
                page.wait_for_timeout(1000)
            else:
                print("❌ ERROR: No se encontraron suficientes comboboxes en la barra de herramientas.")

            # 5. Cambiar a Vista Agrupada (Por Propietario)
            print("\n--- Cambiando a Vista Agrupada ---")
            switch = page.get_by_role("switch")
            if switch.count() > 0:
                switch.first.click()
                page.wait_for_timeout(4000)
                
                # 6. Validar Filtro de Asesores de nuevo
                comboboxes_agrupados = page.get_by_role("combobox").all()
                if len(comboboxes_agrupados) >= 3:
                    asesor_combobox_agrupado = comboboxes_agrupados[2]
                    asesor_combobox_agrupado.click()
                    page.wait_for_timeout(2000)
                    
                    options_agrupadas = page.get_by_role("option").all()
                    opciones_texto_agrupadas = [opt.inner_text() for opt in options_agrupadas]
                    print(f"Opciones cargadas en el filtro Asesor (Vista Agrupada): {opciones_texto_agrupadas}")
                    
                    if len(options_agrupadas) > 1:
                        print("✅ ÉXITO: El filtro de asesores cargó correctamente en Vista Agrupada.")
                    else:
                        print("❌ ERROR: El filtro de asesores solo cargó 'Todos' o está vacío en Vista Agrupada.")
                else:
                    print("❌ ERROR: No se encontraron comboboxes tras cambiar de vista.")
            else:
                print("❌ ERROR: No se encontró el switch para cambiar a vista agrupada.")

        except Exception as e:
            print(f"Ocurrió un error durante la ejecución: {e}")
            page.screenshot(path="error_screenshot_v2.png")
            print("Se ha guardado un pantallazo del error en error_screenshot_v2.png")

        finally:
            browser.close()

if __name__ == "__main__":
    test_filtro_asesores()
