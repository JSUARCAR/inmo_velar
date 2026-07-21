# ============================================================================
# Script de Inicio - Reflex (Puerto 3000)
# Sistema de Gestión Inmobiliaria Velar - Versión Web
# ============================================================================

Write-Host "Iniciando Inmobiliaria Velar - Reflex..." -ForegroundColor Cyan
Write-Host ""

# Activar entorno virtual (si existe)
if (Test-Path ".\venv\Scripts\Activate.ps1") {
    Write-Host "Activando entorno virtual..." -ForegroundColor Green
    .\venv\Scripts\Activate.ps1
}
else {
    Write-Host "No se encontro entorno virtual en .\venv\" -ForegroundColor Yellow
}

# Verificar que Reflex esta instalado
if (-not (python -m reflex --version 2> $null)) {
    Write-Host "Reflex no esta instalado." -ForegroundColor Red
    Write-Host "Ejecute: pip install reflex" -ForegroundColor Yellow
    Read-Host "Presione Enter para salir"
    exit 1
}

# Verificar version de Reflex
try {
    $reflexVersion = python -m reflex --version 2>&1
    Write-Host "Version: $reflexVersion" -ForegroundColor Green
} catch {
    Write-Host "No se pudo determinar la version de Reflex" -ForegroundColor Yellow
}

# Exportar variable de entorno (feature flag)
$env:USE_REFLEX = "true"

# Limpiar cache anterior si existe (DESACTIVADO para evitar que Reflex deba reconstruir todo el frontend, lo cual causa errores en la generación de package.json)
# if (Test-Path ".\.web\") {
#     Write-Host "Limpiando cache anterior..." -ForegroundColor Yellow
#     Remove-Item -Recurse -Force ".\.web\"
# }

Write-Host ""
Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  Servidor Reflex iniciando..." -ForegroundColor Cyan
Write-Host "  URL: http://localhost:3000" -ForegroundColor Green
Write-Host "  Presione Ctrl+C para detener" -ForegroundColor Yellow
Write-Host "======================================" -ForegroundColor Cyan
Write-Host ""

# Ejecutar aplicacion Reflex
try {
    python -m reflex run --backend-port 8001 --loglevel info
}
catch {
    Write-Host "Error al ejecutar Reflex: $_" -ForegroundColor Red
    Read-Host "Presione Enter para salir"
    exit 1
}

# Si se detiene normalmente
Write-Host "Servidor Reflex detenido." -ForegroundColor Green
