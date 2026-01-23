# ============================================================================
# Script de Inicio - Reflex (Puerto 3000)
# Sistema de Gestión Inmobiliaria Velar - Versión Web
# ============================================================================

Write-Host "🚀 Iniciando Inmobiliaria Velar - Reflex..." -ForegroundColor Cyan
Write-Host ""

# Activar entorno virtual (si existe)
if (Test-Path ".\venv\Scripts\Activate.ps1") {
    Write-Host "✓ Activando entorno virtual..." -ForegroundColor Green
    .\venv\Scripts\Activate.ps1
}
else {
    Write-Host "⚠ No se encontró entorno virtual en .\venv\" -ForegroundColor Yellow
}

# Verificar que Reflex está instalado
if (-not (Get-Command reflex -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Reflex no está instalado." -ForegroundColor Red
    Write-Host "Ejecute: pip install reflex" -ForegroundColor Yellow
    Read-Host "Presione Enter para salir"
    exit 1
}

# Verificar versión de Reflex
$reflexVersion = reflex --version 2>&1
Write-Host "✓ $reflexVersion" -ForegroundColor Green

# Exportar variable de entorno (feature flag)
$env:USE_REFLEX = "true"

# Limpiar caché anterior si existe
if (Test-Path ".\.web\") {
    Write-Host "🧹 Limpiando caché anterior..." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  Servidor Reflex iniciando..." -ForegroundColor Cyan
Write-Host "  URL: http://localhost:3000" -ForegroundColor Green
Write-Host "  Presione Ctrl+C para detener" -ForegroundColor Yellow
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Ejecutar aplicación Reflex
try {
    reflex run --backend-port 8000 --loglevel info
}
catch {
    Write-Host "`n❌ Error al ejecutar Reflex: $_" -ForegroundColor Red
    Read-Host "Presione Enter para salir"
    exit 1
}

# Si se detiene normalmente
Write-Host "`n✓ Servidor Reflex detenido." -ForegroundColor Green
