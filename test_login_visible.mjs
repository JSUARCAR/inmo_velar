import { chromium } from 'playwright';

(async () => {
    console.log("Lanzando navegador en modo visible...");
    // headless: false forzará abrir la ventana del navegador en tu pantalla
    // slowMo: 500 agregará un retraso de 500ms entre cada acción para que puedas verlo
    const browser = await chromium.launch({ headless: false, slowMo: 500 });
    const context = await browser.newContext();
    const page = await context.newPage();
    
    const url = "https://inmovelar-production.up.railway.app/login";
    console.log(`Navegando a ${url} ...`);
    
    try {
        await page.goto(url, { waitUntil: "networkidle" });
        
        console.log("Esperando que el formulario cargue...");
        await page.waitForTimeout(2000); 
        
        console.log("Escribiendo usuario...");
        await page.getByPlaceholder("nombre.usuario").click();
        await page.getByPlaceholder("nombre.usuario").fill("admin");
        
        console.log("Escribiendo contraseña...");
        await page.getByPlaceholder("••••••••").click();
        await page.getByPlaceholder("••••••••").fill("admin0123");
        
        console.log("Haciendo clic en 'Acceder al Panel'...");
        await page.getByText("Acceder al Panel").click();
        
        console.log("Esperando 10 segundos para que puedas observar el resultado visualmente...");
        await page.waitForTimeout(10000);
        
        console.log(`URL final: ${page.url()}`);
        
    } catch (e) {
        console.log(`Error en el script: ${e}`);
    } finally {
        console.log("Cerrando navegador...");
        await browser.close();
    }
})();
