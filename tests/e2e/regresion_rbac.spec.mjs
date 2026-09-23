import { test, expect } from '@playwright/test';

// Credenciales canónicas (T036): TEST_USER/TEST_PASSWORD definidos en .env.
// Usuario restringido opcional (T039): RBAC_RESTRICTED_USER / RBAC_RESTRICTED_PASSWORD.
const ADMIN_USER = process.env.TEST_USER ?? "admin";
const ADMIN_PASS = process.env.TEST_PASSWORD ?? "admin0123";
const RESTRICTED_USER = process.env.RBAC_RESTRICTED_USER;
const RESTRICTED_PASS = process.env.RBAC_RESTRICTED_PASSWORD;

test('admin accede a modulo protegido tras login', async ({ page }) => {
    // 1. Login como Admin
    await page.goto('/login');
    await page.getByPlaceholder("nombre.usuario").fill(ADMIN_USER);
    await page.getByPlaceholder("        ").fill(ADMIN_PASS);
    await page.getByText("Acceder al Panel").click();
    await page.waitForURL('/dashboard', { timeout: 10000 });

    // 2. Navegar a un módulo protegido desde el sidebar
    await page.goto('/personas');
    await page.waitForLoadState("networkidle");
    const url = page.url();
    // Si no hay permisos, require_login redirige; Admin siempre debe entrar
    expect(url).toContain('/personas');
});

test('usuario con rol restringido no accede al modulo protegido', async ({ page }) => {
    test.skip(
        !RESTRICTED_USER || !RESTRICTED_PASS,
        "RBAC_RESTRICTED_USER / RBAC_RESTRICTED_PASSWORD no definidos en .env"
    );

    // 1. Login como usuario de rol restringido (sin permiso sobre /personas)
    await page.goto('/login');
    await page.getByPlaceholder("nombre.usuario").fill(RESTRICTED_USER);
    await page.getByPlaceholder("        ").fill(RESTRICTED_PASS);
    await page.getByText("Acceder al Panel").click();
    await page.waitForURL('**/dashboard**', { timeout: 10000 });

    // 2. Intentar ingresar al módulo protegido: no debe mostrar el contenido
    await page.goto('/personas');
    await page.waitForTimeout(1500);
    const url = page.url();
    const noPermiso = page.getByText(/No tiene permisos|Sin permisos|Acceso denegado/i);

    // Redirige a /login o muestra mensaje de permiso denegado
    const redirigido = !url.includes('/personas');
    if (!redirigido) {
        await expect(noPermiso).toBeVisible({ timeout: 5000 });
    }
});