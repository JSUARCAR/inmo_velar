import { test, expect } from '@playwright/test';

test('login invalido muestra error y restablece spinner', async ({ page }) => {
    // 1. Ir a login
    await page.goto('/login');
    
    // 2. Llenar form con incorrecto
    await page.getByPlaceholder("nombre.usuario").fill("admin_invalido_test");
    await page.getByPlaceholder("        ").fill("password123"); // 8 spaces placeholder!
    
    // 3. Capturar startTime
    const startTime = Date.now();
    
    // 4. Click en Acceder
    const submitBtn = page.getByText("Acceder al Panel");
    await submitBtn.click();
    
    // 5. Esperar al toast o mensaje de error visible
    const errorMsg = page.getByText("Credenciales inválidas. Verifique usuario y contraseña.");
    await errorMsg.waitFor({ state: 'visible', timeout: 5000 });
    
    const duration = Date.now() - startTime;
    console.log(`Respuesta invalida tard ${duration}ms`);
    expect(duration).toBeLessThan(5000);
    
    // 6. Verificar spinner restablecido (si el botn est habilitado y sin spinner, el texto original debe estar visible o no tener disabled)
    // Reflex sets pointer-events: none on loading buttons usually, or disabled.
    // Check if the button is enabled again or loading is false.
    // Wait a brief moment for reflex state update delta
    await page.waitForTimeout(500); 
    
    // In reflex, the loading state might disable the button
    const isBtnDisabled = await submitBtn.isDisabled();
    expect(isBtnDisabled).toBe(false);
});
