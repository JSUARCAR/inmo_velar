import asyncio
from playwright.async_api import async_playwright
import traceback

async def run_test():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            print("1. Navegando a la raz (login)...")
            await page.goto("https://extraordinary-joy-production-2fd2.up.railway.app/", timeout=60000)
            
            print("2. Esperando el formulario de login...")
            await page.wait_for_selector("input[type='text'], input[placeholder='Usuario'], input[name='username']", timeout=15000)
            
            print("3. Rellenando credenciales...")
            await page.screenshot(path="login.png")
            # Try to find username input
            username_input = await page.query_selector("input[type='text'], input[placeholder='Usuario'], input[name='username']")
            if username_input:
                await username_input.fill("jsuarcar")
            else:
                print("No se encontr input de usuario.")
                
            password_input = await page.query_selector("input[type='password'], input[placeholder*='ontraseña'], input[name='password']")
            if password_input:
                await password_input.fill("velarjoan2026")
            else:
                print("No se encontr input de password.")
                
            print("4. Enviando login...")
            await page.screenshot(path="login_filled.png")
            # Presionar enter para login
            await page.keyboard.press("Enter")
            
            print("4.5 Navegando a Contratos...")
            await asyncio.sleep(3)
            await page.goto("https://extraordinary-joy-production-2fd2.up.railway.app/contratos", timeout=60000)
            
            # Esperar a que estemos en la pgina de contratos (buscar la tabla)
            print("5. Esperando a que cargue el Dashboard de Contratos...")
            await asyncio.sleep(5)
            await page.screenshot(path="dashboard.png")
            
            # Buscar el primer contrato en la lista y hacer clic en Ver Detalle (evitar el ojo del sidebar)
            print("6. Buscando el botn 'Ver Detalle'...")
            # Usually inside a table or card
            botones_detalle = await page.query_selector_all("button:has(.lucide-eye)")
            if botones_detalle:
                print(f"Se encontraron {len(botones_detalle)} botones de detalle. Haciendo clic en el ltimo (tabla)...")
                await botones_detalle[-1].click()
            else:
                print("No se encontraron contratos en la vista actual.")
                return
                
            # Esperar a que se abra el modal de detalle
            print("7. Esperando que abra el modal de Detalle de Contrato...")
            await asyncio.sleep(2)
            await page.screenshot(path="modal.png")
            
            # Buscar si existe el Gestor Documental (cloud-upload icon o el texto "Gestin Documental")
            print("8. Validando implementacin de Gestin Documental en el Modal...")
            
            # Buscar el header que dice "Gestin Documental"
            gestion_doc = await page.query_selector("text='Gestión Documental'")
            cloud_icon = await page.query_selector(".lucide-cloud-upload")
            
            if gestion_doc or cloud_icon:
                print("\n[XITO] VALIDACIN POSITIVA: El Gestor Documental s se renderiza dentro del modal de detalle de contrato en produccin.")
            else:
                print("\n[FALLO] VALIDACIN NEGATIVA: El Gestor Documental NO es visible en el modal. Es posible que el cambio an no est desplegado en Railway.")
                
            # Extraer todo el texto del modal para anlisis de ingeniera inversa
            modal = await page.query_selector("[role='dialog']")
            if modal:
                texto_modal = await modal.inner_text()
                print("\n--- Contenido de Texto del Modal ---")
                print(texto_modal[:500] + "...\n(truncado)")
                print("------------------------------------")
                
            # Captura de pantalla como evidencia (opcional, se guarda local)
            await page.screenshot(path="evidencia_detalle_contrato.png")
            print("\nEvidencia guardada en 'evidencia_detalle_contrato.png'")
            
        except Exception as e:
            print("Error durante la ejecucin del test de Playwright:")
            traceback.print_exc()
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run_test())
