import { test, expect } from '@playwright/test';

const RUTAS_PROTEGIDAS = [
    '/dashboard',
    '/personas',
    '/propiedades',
    '/contratos',
    '/liquidaciones',
    '/liquidacion_asesores',
    '/recaudos',
    '/recibos',
    '/propiedad_horizontal',
    '/usuarios',
    '/seguros',
    '/saldos_favor',
    '/proveedores',
    '/incrementos',
    '/incidentes',
    '/desocupaciones',
    '/configuracion',
    '/auditoria'
];

test.describe('Navegación Rutas Protegidas', () => {
    // Aumentar el timeout porque visitamos 18 rutas y recargamos
    test.setTimeout(120000);
    
    test('navegar y recargar rutas no produce error genérico (SC-003, SC-005)', async ({ page }) => {
        // 1. Ir a login
        await page.goto('/login');
        
        // 2. Llenar form
        await page.getByPlaceholder("nombre.usuario").click();
        await page.getByPlaceholder("nombre.usuario").fill(process.env.TEST_USER ?? "admin");
        
        await page.locator('input[type="password"]').click();
        await page.locator('input[type="password"]').fill(process.env.TEST_PASSWORD ?? "admin0123");
        
        // 3. Click en Acceder
        const submitBtn = page.getByText("Acceder al Panel");
        await submitBtn.click();
        
        // 4. Esperar la redirección a /dashboard
        await page.waitForURL('/dashboard', { timeout: 15000 });
        
        // Iterar sobre todas las rutas protegidas
        for (const ruta of RUTAS_PROTEGIDAS) {
            // 5a. Navegar a la ruta
            await page.goto(ruta);
            
            // Validar que NO aparezca el error genérico de Reflex
            const errorText = await page.getByText("An error occurred. Contact the website administrator.").count();
            expect(errorText, `Error genérico encontrado al cargar ${ruta}`).toBe(0);
            
            // 5b. Recargar página (Edge Case 4)
            await page.reload();
            
            // Validar que NO aparezca el error genérico después de recargar
            const errorTextAfter = await page.getByText("An error occurred. Contact the website administrator.").count();
            expect(errorTextAfter, `Error genérico encontrado al recargar ${ruta}`).toBe(0);
        }
    });
});
