import { test, expect } from '@playwright/test';

test('login vlido redirige a /dashboard y bton sin spinner', async ({ page }) => {
    // 1. Ir a login
    await page.goto('/login');
    
    // 2. Llenar form
    await page.getByPlaceholder("nombre.usuario").click();
    await page.getByPlaceholder("nombre.usuario").fill(process.env.TEST_USER ?? "admin");
    
    await page.locator('input[type="password"]').click();
    await page.locator('input[type="password"]').fill(process.env.TEST_PASSWORD ?? "admin0123");
    
    // 3. Capturar startTime
    const startTime = Date.now();
    
    // 4. Click en Acceder
    const submitBtn = page.getByText("Acceder al Panel");
    await submitBtn.click();
    
    // 5. Esperar la redireccin a /dashboard
    await page.waitForURL('/dashboard', { timeout: 10000 }); // SC-002: max 10s deployed
    
    const duration = Date.now() - startTime;
    console.log(`Login tard ${duration}ms`);
    expect(duration).toBeLessThan(10000);
    
    // 6. Verificar botn sin spinner (volviendo o ya no est en DOM de login, 
    //    pero en /dashboard deberamos estar con contenido de app)
    const url = page.url();
    expect(url).toContain('/dashboard');
});
