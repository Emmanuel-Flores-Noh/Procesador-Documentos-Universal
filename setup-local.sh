#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

PYTHON_BIN="${PYTHON:-python3}"
SHARED_VENV_DIR="${SHARED_VENV_DIR:-${HOME}/.venv}"
VENV_DIR="$SHARED_VENV_DIR"
VENV_PY="$VENV_DIR/bin/python"

# Directorio de datos del usuario para pdu.
if [ -n "${XDG_DATA_HOME:-}" ]; then
    DATA_BASE="$XDG_DATA_HOME"
else
    DATA_BASE="${HOME}/.local/share"
fi
DATA_DIR="$DATA_BASE/pdu"
BIN_DIR="$DATA_DIR/bin"

echo "========================================"
echo " Configurando entorno local de pdu"
echo "========================================"
echo "Entorno virtual: $VENV_DIR"
echo "Directorio de datos: $DATA_DIR"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
    echo "[Error] No se encontró '$PYTHON_BIN'. Instala Python 3 y vuelve a intentarlo."
    exit 1
fi

if [ ! -d "$VENV_DIR" ]; then
    echo ""
    echo "1. Creando entorno virtual en $VENV_DIR ..."
    mkdir -p "$(dirname "$VENV_DIR")"
    if ! "$PYTHON_BIN" -m venv "$VENV_DIR"; then
        echo "[Error] No se pudo crear el entorno virtual."
        echo "En Debian/Ubuntu puede que necesites instalar: sudo apt install python3-venv"
        exit 1
    fi
else
    echo ""
    echo "1. El entorno virtual ya existe en $VENV_DIR."
fi

echo ""
echo "2. Instalando pdu y sus dependencias de Python ..."
"$VENV_PY" -m pip install --upgrade pip
"$VENV_PY" -m pip install --upgrade "$ROOT"

"$VENV_PY" -c "import weasyprint" >/dev/null 2>&1 || {
    echo ""
    echo "[Advertencia] WeasyPrint se instaló, pero no pudo importarse."
    echo "Probablemente falten librerías del sistema. En Debian/Ubuntu:"
    echo "  sudo apt install libpango-1.0-0 libpangoft2-1.0-0 libcairo2 libffi-dev"
}

echo ""
echo "3. Preparando carpeta de datos y binarios de Mermaid ..."
mkdir -p "$BIN_DIR"

PNPM_MODE=""
if command -v pnpm >/dev/null 2>&1; then
    PNPM_MODE="pnpm"
elif command -v corepack >/dev/null 2>&1; then
    echo "   pnpm no está instalado; intentando activarlo con corepack ..."
    corepack enable pnpm >/dev/null 2>&1 || true
    if command -v pnpm >/dev/null 2>&1; then
        PNPM_MODE="pnpm"
    else
        PNPM_MODE="corepack"
    fi
fi

if [ -n "$PNPM_MODE" ]; then
    if [ "$PNPM_MODE" = "corepack" ]; then
        (cd "$BIN_DIR" && corepack pnpm add @mermaid-js/mermaid-cli --ignore-scripts)
        (cd "$BIN_DIR" && corepack pnpm approve-builds puppeteer || true)
        (cd "$BIN_DIR" && corepack pnpm rebuild puppeteer || true)
    else
        (cd "$BIN_DIR" && pnpm add @mermaid-js/mermaid-cli --ignore-scripts)
        (cd "$BIN_DIR" && pnpm approve-builds puppeteer || true)
        (cd "$BIN_DIR" && pnpm rebuild puppeteer || true)
    fi

    PUPPETEER_BIN="$BIN_DIR/node_modules/.bin/puppeteer"
    if [ -x "$PUPPETEER_BIN" ]; then
        echo ""
        echo "4. Verificando navegador para Puppeteer ..."
        if ! (cd "$BIN_DIR" && "$PUPPETEER_BIN" browsers install chrome); then
            echo "[Advertencia] No se pudo descargar Chrome automáticamente."
            echo "Si Mermaid falla, define PUPPETEER_EXECUTABLE_PATH con la ruta de un navegador."
        fi
    fi
else
    echo "[Advertencia] No se encontró pnpm."
    echo "Mermaid CLI no se instalará automáticamente. Instala pnpm con:"
    echo "  corepack enable pnpm"
    echo "o:"
    echo "  npm install -g pnpm"
    echo "Después vuelve a ejecutar este script."
fi

echo ""
echo "========================================"
echo " Entorno local listo"
echo "========================================"
echo "Mermaid se guarda en: $BIN_DIR"
echo "Estilos de usuario: $DATA_DIR/estilos"
echo ""
echo "Activa el entorno con:"
echo "  source $VENV_DIR/bin/activate"
echo ""
echo "O ejecuta directamente:"
echo "  $VENV_PY -m pdu --help"
