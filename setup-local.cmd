@echo off
setlocal
set "ROOT=%~dp0"
cd /d "%ROOT%"

if "%SHARED_VENV_DIR%"=="" (
    set "VENV_DIR=%USERPROFILE%\.venv"
) else (
    set "VENV_DIR=%SHARED_VENV_DIR%"
)
set "VENV_PY=%VENV_DIR%\Scripts\python.exe"

if "%APPDATA%"=="" (
    set "DATA_BASE=%LOCALAPPDATA%"
) else (
    set "DATA_BASE=%APPDATA%"
)
set "DATA_DIR=%DATA_BASE%\pdu"
set "BIN_DIR=%DATA_DIR%\bin"

echo ========================================
echo  Configurando entorno local de pdu
echo ========================================
echo Entorno virtual: %VENV_DIR%
echo Directorio de datos: %DATA_DIR%

where py >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    set "PYTHON=py -3"
) else (
    set "PYTHON=python"
)

%PYTHON% --version >nul 2>nul
if errorlevel 1 (
    echo [Error] No se encontro Python 3. Instalalo y vuelve a intentarlo.
    exit /b 1
)

if not exist "%VENV_DIR%" (
    echo.
    echo 1. Creando entorno virtual en %VENV_DIR% ...
    %PYTHON% -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo [Error] No se pudo crear el entorno virtual.
        exit /b 1
    )
) else (
    echo.
    echo 1. El entorno virtual ya existe.
)

echo.
echo 2. Instalando pdu y sus dependencias de Python ...
"%VENV_PY%" -m pip install --upgrade pip
if errorlevel 1 exit /b 1
"%VENV_PY%" -m pip install --upgrade "%ROOT%"
if errorlevel 1 exit /b 1

"%VENV_PY%" -c "import weasyprint" >nul 2>nul
if errorlevel 1 (
    echo.
    echo [Advertencia] WeasyPrint se instalo, pero no pudo importarse.
    echo Probablemente falten librerias del sistema requeridas por WeasyPrint.
)

echo.
echo 3. Preparando carpeta de datos y binarios de Mermaid ...
if not exist "%BIN_DIR%" mkdir "%BIN_DIR%"

set "PNPM_CMD="

where pnpm >nul 2>nul
if not errorlevel 1 (
    set "PNPM_CMD=pnpm"
    goto pnpm_listo
)

where corepack >nul 2>nul
if errorlevel 1 goto pnpm_no_disponible

echo    pnpm no esta instalado; intentando activarlo con corepack ...
call corepack enable pnpm >nul 2>nul
where pnpm >nul 2>nul
if not errorlevel 1 (
    set "PNPM_CMD=pnpm"
    goto pnpm_listo
)
set "PNPM_CMD=corepack"
goto pnpm_listo

:pnpm_no_disponible
echo [Advertencia] No se encontro pnpm.
echo Mermaid CLI no se instalara automaticamente. Instala pnpm con:
echo   corepack enable pnpm
echo o:
echo   npm install -g pnpm
goto fin_mermaid

:pnpm_listo
pushd "%BIN_DIR%"
if "%PNPM_CMD%"=="corepack" (
    call corepack pnpm add @mermaid-js/mermaid-cli --ignore-scripts
    call corepack pnpm approve-builds puppeteer
    call corepack pnpm rebuild puppeteer
) else (
    call pnpm add @mermaid-js/mermaid-cli --ignore-scripts
    call pnpm approve-builds puppeteer
    call pnpm rebuild puppeteer
)
if errorlevel 1 (
    popd
    exit /b 1
)
popd

if exist "%BIN_DIR%\node_modules\.bin\puppeteer.cmd" (
    echo.
    echo 4. Verificando navegador para Puppeteer ...
    pushd "%BIN_DIR%"
    call "%BIN_DIR%\node_modules\.bin\puppeteer.cmd" browsers install chrome
    if errorlevel 1 (
        echo [Advertencia] No se pudo descargar Chrome automaticamente.
        echo Si Mermaid falla, define PUPPETEER_EXECUTABLE_PATH con la ruta de un navegador.
    )
    popd
)

:fin_mermaid

echo.
echo ========================================
echo  Entorno local listo
echo ========================================
echo Mermaid se guarda en: %BIN_DIR%
echo Estilos de usuario: %DATA_DIR%\estilos
echo.
echo Activa el entorno con:
echo   %VENV_DIR%\Scripts\activate
echo.
echo O ejecuta directamente:
echo   %VENV_PY% -m pdu --help
