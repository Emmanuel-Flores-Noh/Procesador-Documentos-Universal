"""Detección de dependencias externas (mmdc, navegador) y configuración de Puppeteer."""
from __future__ import annotations

import functools
import json
import os
import shutil
import sys

from ..nucleo.rutas import ROOT_DIR, directorio_datos, es_ejecutable, preparar_directorios  # noqa: F401

MENSAJE_MMDC_FALTANTE = (
    "Se necesita Mermaid CLI (mmdc) para compilar diagramas.\n"
    "  Opción local:  ./setup-local.sh (Linux/macOS) o setup-local.cmd (Windows)\n"
    "  Opción global: pnpm add -g @mermaid-js/mermaid-cli\n"
    "  O indica su ruta con la variable de entorno MMDC_PATH."
)

_SUBRUTAS_BIN = ("", "bin", os.path.join("bin", "node_modules", ".bin"), os.path.join("node_modules", ".bin"))


def _directorios_binarios() -> list[str]:
    """Carpetas donde se busca `mmdc`, en orden de prioridad y sin duplicados."""
    candidatos = [os.environ.get("PDU_BIN")]
    for base in (directorio_datos(crear=False), os.path.join(os.path.expanduser("~"), ".locq")):
        candidatos.extend(os.path.join(base, sub) for sub in _SUBRUTAS_BIN)
    candidatos.extend(os.path.join(ROOT_DIR, sub) for sub in _SUBRUTAS_BIN[1:3])

    directorios: list[str] = []
    for ruta in candidatos:
        if ruta:
            ruta = os.path.abspath(os.path.expanduser(ruta))
            if ruta not in directorios:
                directorios.append(ruta)
    return directorios


@functools.lru_cache(maxsize=1)
def buscar_mmdc() -> str | None:
    """Ruta de Mermaid CLI: $MMDC_PATH, PATH del sistema o carpetas de datos de pdu."""
    candidatos = [os.environ.get("MMDC_PATH"), shutil.which("mmdc")]
    nombres = ("mmdc.cmd", "mmdc.exe", "mmdc") if os.name == "nt" else ("mmdc",)
    for directorio in _directorios_binarios():
        candidatos.extend(os.path.join(directorio, nombre) for nombre in nombres)
    return next((c for c in candidatos if c and es_ejecutable(c)), None)


def faltan_dependencias() -> bool:
    return buscar_mmdc() is None


def _rutas_navegador_plataforma() -> list[str]:
    if sys.platform == "darwin":
        return [
            "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
            "/Applications/Chromium.app/Contents/MacOS/Chromium",
            "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
        ]
    if os.name == "nt":
        rutas = []
        for variable in ("PROGRAMFILES", "PROGRAMFILES(X86)", "LOCALAPPDATA"):
            base = os.environ.get(variable)
            if base:
                rutas += [
                    os.path.join(base, "Google", "Chrome", "Application", "chrome.exe"),
                    os.path.join(base, "Chromium", "Application", "chrome.exe"),
                    os.path.join(base, "Microsoft", "Edge", "Application", "msedge.exe"),
                ]
        return rutas
    return ["/usr/bin/chromium", "/usr/bin/chromium-browser", "/usr/bin/google-chrome", "/usr/bin/google-chrome-stable"]


@functools.lru_cache(maxsize=1)
def buscar_navegador() -> str | None:
    """Navegador para Puppeteer: variables de entorno, PATH o rutas habituales."""
    for variable in ("PUPPETEER_EXECUTABLE_PATH", "CHROME_PATH", "CHROMIUM_PATH"):
        ruta = os.environ.get(variable)
        if ruta and os.path.isfile(ruta):
            return ruta
    for nombre in (
        "chromium", "chromium-browser", "google-chrome", "google-chrome-stable",
        "microsoft-edge", "microsoft-edge-stable", "chrome",
    ):
        ruta = shutil.which(nombre)
        if ruta:
            return ruta
    return next((c for c in _rutas_navegador_plataforma() if os.path.isfile(c)), None)


def _escribir_si_cambia(ruta: str, contenido: str) -> str:
    """Escribe `contenido` en `ruta` solo si difiere de lo que ya hay; devuelve la ruta."""
    try:
        with open(ruta, encoding="utf-8") as f:
            if f.read() == contenido:
                return ruta
    except OSError:
        pass
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(contenido)
    return ruta


def preparar_puppeteer(directorio: str | None = None) -> str:
    """Escribe (solo si cambió) la configuración de Puppeteer y devuelve su ruta.

    Por defecto se guarda en el directorio de datos de pdu para no ensuciar la
    carpeta de documentos; `directorio` permite indicar otra ubicación.
    """
    directorio = directorio or directorio_datos(crear=True)
    os.makedirs(directorio, exist_ok=True)

    config = {"args": ["--no-sandbox", "--disable-setuid-sandbox"]}
    navegador = buscar_navegador()
    if navegador:
        config["executablePath"] = navegador
    return _escribir_si_cambia(os.path.join(directorio, "puppeteer-config.json"), json.dumps(config, indent=4))


# Mermaid dibuja por defecto las etiquetas con <foreignObject> (HTML dentro del
# SVG), que WeasyPrint no renderiza: el texto desaparecería del PDF. Con
# htmlLabels=false las etiquetas son <text> SVG nativo.
CONFIG_MERMAID_SVG = {
    "htmlLabels": False,
    "flowchart": {"htmlLabels": False},
    "class": {"htmlLabels": False},
    "state": {"htmlLabels": False},
}


def preparar_config_mermaid_svg(directorio: str | None = None) -> str:
    """Escribe (solo si cambió) la configuración de Mermaid para exportar SVG y devuelve su ruta."""
    directorio = directorio or directorio_datos(crear=True)
    os.makedirs(directorio, exist_ok=True)
    return _escribir_si_cambia(
        os.path.join(directorio, "mermaid-config-svg.json"), json.dumps(CONFIG_MERMAID_SVG, indent=4)
    )
