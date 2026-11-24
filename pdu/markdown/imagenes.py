"""Reescritura de referencias a imágenes y diagramas a URIs absolutas (file://)."""
from __future__ import annotations

import os
import re
from pathlib import Path

from ..nucleo.patrones import PATRON_HTML_IMG, PATRON_IMG, PATRON_MMD, es_url_externa

__all__ = [
    "PATRON_HTML_IMG",
    "PATRON_IMG",
    "PATRON_MMD",
    "reemplazar_diagramas_por_png",
    "reemplazar_diagramas_por_svg",
    "reemplazar_imagenes_locales",
    "reemplazar_src_html",
]

_PATRON_TITULO = re.compile(r'^(.*?)\s+(["\'].*?["\'])$')


def _uri_local(ruta_relativa: str, base: str) -> str:
    """URI file:// de una ruta relativa a `base`, avisando si el archivo no existe."""
    ruta_absoluta = os.path.abspath(os.path.join(base, ruta_relativa))
    if not os.path.exists(ruta_absoluta):
        print(f"  [Advertencia] No se encontró la imagen '{ruta_relativa}' ({ruta_absoluta}).")
    return Path(ruta_absoluta).as_uri()


def _separar_destino(destino: str) -> tuple[str, str]:
    """Divide el destino de ``![alt](destino)`` en (url, ' "titulo"')."""
    if destino.startswith("<"):
        cierre = destino.find(">")
        if cierre == -1:
            return destino, ""
        resto = destino[cierre + 1:].strip()
        return destino[1:cierre].strip(), f" {resto}" if resto else ""
    match = _PATRON_TITULO.match(destino)
    if match:
        return match.group(1).strip(), f" {match.group(2)}"
    return destino, ""


def _reemplazar_diagrama(match: re.Match, directorio: str, extension: str) -> str:
    nombre_base = os.path.basename(match.group(2))
    ruta = os.path.abspath(os.path.join(directorio, f"{nombre_base}.{extension}"))
    if not os.path.exists(ruta):
        print(f"  [Advertencia] Falta el {extension.upper()} compilado de '{nombre_base}.mmd' ({ruta}).")
    return f"![{match.group(1)}]({Path(ruta).as_uri()})"


def reemplazar_diagramas_por_svg(match: re.Match, dir_svg: str) -> str:
    """``![alt](x.mmd)`` -> ``![alt](file:///.../svg/x.svg)`` (vectorial, sin pérdida de calidad)."""
    return _reemplazar_diagrama(match, dir_svg, "svg")


def reemplazar_diagramas_por_png(match: re.Match, dir_png: str) -> str:
    """``![alt](x.mmd)`` -> ``![alt](file:///.../png/x.png)``."""
    return _reemplazar_diagrama(match, dir_png, "png")


def reemplazar_imagenes_locales(match: re.Match, subcarpeta: str) -> str:
    """Convierte imágenes Markdown relativas en URIs absolutas respecto a `subcarpeta`."""
    url, titulo = _separar_destino(match.group(2).strip())
    if es_url_externa(url) or url.lower().endswith(".mmd"):
        return match.group(0)
    return f"![{match.group(1)}]({_uri_local(url, subcarpeta)}{titulo})"


def reemplazar_src_html(match: re.Match, subcarpeta: str) -> str:
    """Igual que `reemplazar_imagenes_locales` pero para ``<img src="...">``."""
    src = match.group(2).strip()
    if es_url_externa(src):
        return match.group(0)
    return f"{match.group(1)}{_uri_local(src, subcarpeta)}{match.group(3)}"
