@echo off
chcp 65001 >nul
cls
echo ============================================================
echo   InmoVelar - Inicio Limpio del Servidor
echo ============================================================
echo.

REM [1/5] Buscar proceso usando puerto 8080
echo [1/5] Buscando procesos en puerto 8080...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8080.*LISTENING"') do (
    set PID=%%a
    goto :found_pid
)
echo   ^> No hay procesos usando el puerto 8080
goto :activate_venv

:found_pid
echo   ^> Encontrado proceso con PID: %PID%
echo [2/5] Deteniendo proceso %PID%...
taskkill /F /PID %PID% >nul 2>&1
if %errorlevel% equ 0 (
    echo   ^> Proceso detenido exitosamente
) else (
    echo   ! Error al detener el proceso
    echo   ! Intenta cerrarlo manualmente o reinicia tu PC
    pause
    exit /b 1
)

echo.
echo [3/5] Esperando liberación del puerto...
timeout /t 2 /nobreak >nul

REM Verificar que el puerto esté realmente libre
for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":8080.*LISTENING"') do (
    echo   ! ADVERTENCIA: El puerto 8080 sigue ocupado
    echo   ! Espera unos segundos más...
    timeout /t 3 /nobreak >nul
)
echo   ^> Puerto 8080 liberado

:activate_venv
echo.
echo [4/5] Activando entorno virtual...
if not exist ".\venv\Scripts\activate.bat" (
    echo   ! Error: No se encontró el entorno virtual
    echo   ! Asegúrate de estar en el directorio correcto
    pause
    exit /b 1
)
call .\venv\Scripts\activate.bat
echo   ^> Entorno virtual activado

echo.
echo [5/5] Iniciando servidor web...
echo ============================================================
echo.
echo   📍 URL: http://localhost:8080
echo   🌐 El navegador se abrirá automáticamente
echo.
echo   ⚠️  IMPORTANTE: 
echo      - Presiona Ctrl+C para detener el servidor
echo      - NO cierres esta ventana sin detener primero
echo      - Ejecuta este script cada vez para evitar conflictos
echo.
echo ============================================================
echo.

python run_web.py

echo.
echo ============================================================
echo   Servidor detenido correctamente
echo ============================================================
pause
