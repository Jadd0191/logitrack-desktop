@echo off
REM LogiTrack Desktop - Script de instalación
REM Fase 8: Empaquetado y distribución

echo 🚚 LogiTrack Desktop - Instalador
echo ==================================
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python no encontrado. Instala Python 3.11+
    pause
    exit /b 1
)

REM Crear entorno virtual
echo 📦 Creando entorno virtual...
python -m venv venv
call venv\Scripts\activate.bat

REM Instalar dependencias
echo 📥 Instalando dependencias...
pip install --upgrade pip
pip install -r requirements.txt

REM Crear carpeta de datos
if not exist data mkdir data

echo.
echo ✅ Instalación completada!
echo.
echo Para ejecutar la aplicación:
echo   venv\Scripts\activate
echo   python -m logitrack
pause