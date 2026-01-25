# InmoVelar - Script de inicio robusto para servidor web
# Este script asegura que el puerto esté libre antes de iniciar

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "  InmoVelar - Sistema de Gestión Inmobiliaria" -ForegroundColor Cyan
Write-Host "  Iniciador de Servidor Web" -ForegroundColor Cyan
Write-Host "============================================================`n" -ForegroundColor Cyan

# 1. Verificar si hay procesos Python usando el puerto 8080
Write-Host "🔍 Verificando puerto 8080..." -ForegroundColor Yellow

$portInUse = netstat -ano | findstr ":8080.*LISTENING"

if ($portInUse) {
    Write-Host "⚠️  Puerto 8080 está en uso. Limpiando procesos..." -ForegroundColor Red
    
    # Extraer PID de cada línea
    $portInUse -split "`n" | ForEach-Object {
        if ($_ -match '\s+(\d+)\s*$') {
            $pid = $matches[1]
            Write-Host "   Deteniendo proceso PID: $pid" -ForegroundColor Yellow
            Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
        }
    }
    
    Write-Host "⏳ Esperando liberación del puerto..." -ForegroundColor Yellow
    Start-Sleep -Seconds 3
}

# 2. Verificar nuevamente
$portCheck = netstat -ano | findstr ":8080.*LISTENING"
if ($portCheck) {
    Write-Host "❌ Error: No se logró liberar el puerto 8080" -ForegroundColor Red
    Write-Host "   Intente cerrar manualmente los procesos Python" -ForegroundColor Red
    pause
    exit 1
}

Write-Host "✅ Puerto 8080 disponible`n" -ForegroundColor Green

# 3. Activar entorno virtual
if (Test-Path ".\venv\Scripts\Activate.ps1") {
    Write-Host "🔧 Activando entorno virtual..." -ForegroundColor Yellow
    & .\venv\Scripts\Activate.ps1
    Write-Host "✅ Entorno virtual activado`n" -ForegroundColor Green
} else {
    Write-Host "⚠️  No se encontró entorno virtual en ./venv" -ForegroundColor Yellow
}

# 4. Iniciar servidor
Write-Host "🚀 Iniciando servidor web..." -ForegroundColor Green
Write-Host "📍 URL: http://localhost:8080" -ForegroundColor Cyan
Write-Host "🔄 El navegador se abrirá automáticamente...`n" -ForegroundColor Cyan
Write-Host "💡 Presiona Ctrl+C para detener el servidor`n" -ForegroundColor Yellow

python run_web.py
