"""
Script de validación usando Playwright para verificar la integración
Incidentes-Liquidaciones en la Liquidación No. 572
"""

import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context(viewport={"width": 1280, "height": 900})
        page = await context.new_page()
        
        try:
            # 1. Navegar a la aplicación
            print("1. Navegando a http://localhost:3000/liquidaciones...")
            await page.goto("http://localhost:3000", wait_until="domcontentloaded")
            await page.wait_for_timeout(3000)
            print(f"   URL actual: {page.url}")
            
            # 2. Login
            print("2. Iniciando sesion...")
            # Verificar si estamos en la página de login
            await page.wait_for_timeout(2000)
            
            # Buscar campos de login por placeholder o label
            usuario_input = page.locator("input[placeholder*='usuario'], input[placeholder*='nombre']").first
            password_input = page.locator("input[type='password']").first
            
            if await usuario_input.count() > 0:
                await usuario_input.fill("jsuarcar")
                await password_input.fill("velarjoan2026")
                await page.wait_for_timeout(500)
                
                # Hacer clic en el botón de acceso
                submit_btn = page.locator("button:has-text('Acceder'), button[type='submit']").first
                await submit_btn.click()
                await page.wait_for_timeout(4000)
                print("   [OK] Login completado")
            else:
                print("   [INFO] Ya estamos en la pagina principal")
            
            # 3. Navegar a Liquidaciones
            print("3. Navegando a Liquidaciones...")
            await page.click("text=Liquidaciones")
            await page.wait_for_timeout(3000)
            await page.screenshot(path="scripts/01_liquidaciones_lista.png")
            print(f"   URL actual: {page.url}")
            
            # 4. Buscar la propiedad "Calle Falsa 123 - Test Renov"
            print("4. Buscando propiedad 'Calle Falsa 123 - Test Renov'...")
            
            # Buscar por texto contiene "Calle Falsa 123"
            propiedad = page.locator("text=Calle Falsa 123").first
            if await propiedad.count() > 0:
                await propiedad.click()
                await page.wait_for_timeout(2000)
                await page.screenshot(path="scripts/02_propiedad_seleccionada.png")
                print("   [OK] Propiedad seleccionada")
            else:
                print("   [FAIL] No se encontro la propiedad")
                # Listar todas las propiedades visibles
                items = await page.locator("text=/Calle|Carrera|Avenida/").all()
                print(f"   Propiedades encontradas: {len(items)}")
                for item in items[:5]:
                    texto = await item.text_content()
                    print(f"     - {texto}")
                return
            
            # 5. Buscar la liquidación y abrir editor
            print("5. Buscando liquidacion...")
            await page.wait_for_timeout(1000)
            
            # Buscar botón de editar
            editar_btns = page.locator("text=Editar")
            count = await editar_btns.count()
            print(f"   Botones 'Editar' encontrados: {count}")
            
            if count > 0:
                await editar_btns.first.click()
                await page.wait_for_timeout(2000)
                await page.screenshot(path="scripts/03_editar_liquidacion.png")
                print("   [OK] Formulario de edicion abierto")
                
                # 6. Verificar campo Incidentes
                print("6. Verificando campo 'Incidentes'...")
                incidentes_input = page.locator("input[name='valor_incidentes']")
                if await incidentes_input.count() > 0:
                    valor_incidentes = await incidentes_input.input_value()
                    print(f"   Valor Incidentes: ${valor_incidentes}")
                    if valor_incidentes and valor_incidentes != "0":
                        print("   [OK] Campo Incidentes tiene valor")
                    else:
                        print("   [FAIL] Campo Incidentes esta vacio o en 0")
                else:
                    print("   [WARN] No se encontro input de incidentes")
                
                # 7. Verificar campo Observaciones
                print("7. Verificando campo 'Observaciones'...")
                observaciones = page.locator("textarea[name='observaciones']")
                if await observaciones.count() > 0:
                    valor_obs = await observaciones.input_value()
                    print(f"   Observaciones: '{valor_obs}'")
                    if valor_obs and "Inc #" in valor_obs:
                        print("   [OK] Campo Observaciones contiene ID del incidente")
                    else:
                        print("   [FAIL] Campo Observaciones no contiene ID del incidente")
                else:
                    print("   [WARN] No se encontro textarea de observaciones")
                
                await page.screenshot(path="scripts/04_verificacion_campos.png")
            else:
                print("   No se encontro boton de editar")
            
            # 8. Cerrar modal
            print("8. Cerrando modal...")
            cancelar = page.locator("button:has-text('Cancelar'), button:has-text('Cerrar')").first
            if await cancelar.count() > 0:
                await cancelar.click()
                await page.wait_for_timeout(1000)
            
            print("\n=== VALIDACION COMPLETADA ===")
            print("Screenshots guardados en scripts/")
            
        except Exception as e:
            print(f"Error: {e}")
            await page.screenshot(path="scripts/error_screenshot.png")
        finally:
            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
