import { test, expect } from '@playwright/test';

test('ruta protegida sin sesion redirige a login', async ({ page }) => {
    // 1. Ir a dashboard sin login
    await page.goto('/dashboard');
    
    // 2. Debe redirigir a login
    await expect(page).toHaveURL(/.*\/login/);
    
    // Toast error podria mostrarse
    // "Sesión expirada. Por favor, inicie sesión nuevamente."
});
