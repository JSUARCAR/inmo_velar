import { test, expect } from '@playwright/test';

test('login ante fallo de red termina sin colgar', async ({ page }) => {
    // 1. Ir a login
    await page.goto('/login');
    
    // 2. Llenar form
    await page.getByPlaceholder("nombre.usuario").fill("admin");
    await page.getByPlaceholder("        ").fill("password123"); 
    
    // 3. Interceptar evento backend de reflex y abortar para simular caida de red
    // Reflex send events to /_event endpoint
    await page.route('**/_event', route => route.abort('failed'));
    
    // 4. Capturar startTime
    const startTime = Date.now();
    
    // 5. Click en Acceder
    const submitBtn = page.getByText("Acceder al Panel");
    await submitBtn.click();
    
    // 6. Al abortar la red, Reflex mismo puede tirar un toast de error general o el timeout entra
    // Reflex tiene un on_error handler general. Pero el punto es que el botón se libere.
    // En este caso extremo de red rota del lado del cliente, Reflex 0.4+ libera el loading 
    // y muestra "Cannot connect to server".
    // Verificamos que el loading desaparece.
    await expect(submitBtn).toBeEnabled({ timeout: 10000 });
    
    const duration = Date.now() - startTime;
    console.log(`Fallo red tard ${duration}ms`);
});
