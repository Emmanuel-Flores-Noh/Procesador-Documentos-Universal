"""Rutas y utilidades comunes de sistema de archivos."""
from __future__ import annotations

import os
from pathlib import Path

# Raíz del proyecto en desarrollo (padre del paquete `pdu`).
ROOT_DIR = str(Path(__file__).resolve().parents[2])


def directorio_datos(crear: bool = True) -> str:
    """Directorio de datos del usuario para pdu.

    - ``$PDU_DATA_DIR`` si está definida.
    - Linux/macOS: ``$XDG_DATA_HOME/pdu`` o ``~/.local/share/pdu``.
    - Windows: ``%APPDATA%\\pdu`` (o ``%LOCALAPPDATA%\\pdu``).
    """
    override = os.environ.get("PDU_DATA_DIR")
    if override:
        ruta = os.path.abspath(os.path.expanduser(override))
    elif os.name == "nt":
        base = (
            os.environ.get("APPDATA")
            or os.environ.get("LOCALAPPDATA")
            or os.path.join(os.path.expanduser("~"), "AppData", "Roaming")
        )
        ruta = os.path.join(base, "pdu")
    else:
        base = os.environ.get("XDG_DATA_HOME") or os.path.join(os.path.expanduser("~"), ".local", "share")
        ruta = os.path.join(base, "pdu")

    if crear:
        try:
            os.makedirs(ruta, exist_ok=True)
        except OSError:
            pass
    return ruta


# Alias por compatibilidad con versiones anteriores.
obtener_directorio_datos = directorio_datos
get_data_dir = directorio_datos
data_dir = directorio_datos


def es_ejecutable(ruta: str) -> bool:
    if not os.path.isfile(ruta):
        return False
    return os.name == "nt" or os.access(ruta, os.X_OK)


def preparar_directorios(directorios) -> None:
    for directorio in directorios or ():
        os.makedirs(directorio, exist_ok=True)


def guardar_salida(ruta: str, contenido: str) -> str:
    """Escribe `contenido` en `ruta` (creando carpetas) y devuelve la ruta absoluta."""
    ruta = os.path.abspath(ruta)
    directorio = os.path.dirname(ruta)
    if directorio:
        os.makedirs(directorio, exist_ok=True)
    with open(ruta, "w", encoding="utf-8") as f:
        f.write(contenido)
    return ruta


def resolver_salida(out: str | None, es_archivo: bool) -> str:
    """Carpeta de salida según las reglas de la CLI.

    - ``-o/--out`` explícito: se usa tal cual.
    - Entrada de un solo archivo: directorio actual.
    - Entrada de un directorio: ``./out`` en el directorio actual.
    """
    if out:
        return os.path.abspath(out)
    if es_archivo:
        return os.getcwd()
    return os.path.join(os.getcwd(), "out")


def salida_docs(docs_dir: str, out_dir: str | None = None) -> str:
    return os.path.abspath(out_dir) if out_dir else os.path.join(docs_dir, "out", "docs")


def salida_diagramas(docs_dir: str, diagramas_out: str | None = None) -> str:
    return os.path.abspath(diagramas_out) if diagramas_out else os.path.join(docs_dir, "out", "diagramas")
