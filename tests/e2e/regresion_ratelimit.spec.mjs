import { test, expect } from '@playwright/test';

test('rate limiting', async ({ page }) => {
    // Solo local para no bloquear la IP en el de produccion (como dice T031)
    await page.goto('/login');
    for (let i = 0; i < 6; i++) {
        await page.getByPlaceholder("nombre.usuario").fill("admin_test_" + i);
        await page.getByPlaceholder("        ").fill("password123"); 
        await page.getByText("Acceder al Panel").click();
        await page.waitForTimeout(100);
    }
    
    const errorMsg = page.getByText("Demasiados intentos. Intente de nuevo en 15 minutos.");
    await errorMsg.waitFor({ state: 'visible', timeout: 5000 });
});
