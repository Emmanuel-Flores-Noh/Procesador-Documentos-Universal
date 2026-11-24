"""Descubrimiento y resolución de diagramas Mermaid."""
from __future__ import annotations

import glob
import os

from ..nucleo.bloques_codigo import proteger
from ..nucleo.contextos import Diagrama
from ..nucleo.patrones import PATRON_MMD, es_url_externa
from ..nucleo.rutas import salida_diagramas

__all__ = [
    "PATRON_MMD",
    "archivos_mmd_de_entrada",
    "buscar_archivos_mmd",
    "crear_diagrama",
    "detectar_diagramas_mermaid",
    "esta_actualizado",
    "obtener_salida_diagramas",
    "resolver_ruta_diagrama",
]


def buscar_archivos_mmd(dir_diagramas: str) -> list[str]:
    return sorted(glob.glob(os.path.join(dir_diagramas, "*.mmd")))


def archivos_mmd_de_entrada(entrada: str) -> list[str]:
    """Archivos .mmd de una entrada de la CLI.

    Acepta un archivo .mmd, una carpeta con .mmd o una carpeta de documentos
    que contenga `diagramas/`.
    """
    if os.path.isfile(entrada):
        return [os.path.abspath(entrada)]
    archivos = buscar_archivos_mmd(entrada)
    if not archivos and os.path.isdir(os.path.join(entrada, "diagramas")):
        archivos = buscar_archivos_mmd(os.path.join(entrada, "diagramas"))
    return archivos


def detectar_diagramas_mermaid(archivos_md: list[str]) -> list[str]:
    """Referencias ``![...](x.mmd)`` de los archivos, sin duplicados y fuera de bloques de código."""
    referencias: list[str] = []
    for archivo in archivos_md:
        with open(archivo, encoding="utf-8") as f:
            texto = proteger(f.read(), prefijo="CODE_BLOCK_IMG").texto
        for match in PATRON_MMD.finditer(texto):
            referencia = match.group(2).strip()
            if referencia and not es_url_externa(referencia) and referencia not in referencias:
                referencias.append(referencia)
    return referencias


def resolver_ruta_diagrama(referencia: str, docs_dir: str, subcarpeta: str) -> str | None:
    """Busca el .mmd de una referencia en `docs/diagramas`, la subcarpeta del documento y `docs/`."""
    referencia = referencia.strip()
    if es_url_externa(referencia):
        return None
    if referencia.startswith("<") and referencia.endswith(">"):
        referencia = referencia[1:-1].strip()
    if referencia.lower().endswith(".mmd"):
        referencia = referencia[:-4]
    referencia = referencia.replace("\\", os.sep)

    if os.path.isabs(referencia):
        candidatos = [referencia]
    else:
        candidatos = [
            os.path.join(docs_dir, "diagramas", referencia),
            os.path.join(subcarpeta, referencia),
            os.path.join(docs_dir, referencia),
            os.path.join(docs_dir, "diagramas", os.path.basename(referencia)),
        ]
    for candidato in candidatos:
        candidato = os.path.abspath(candidato + ".mmd")
        if os.path.isfile(candidato):
            return candidato
    return None


def esta_actualizado(ruta_mmd: str, *salidas: str) -> bool:
    """True si todas las `salidas` (PNG, PDF, SVG...) existen y son más recientes que el .mmd."""
    try:
        origen = os.path.getmtime(ruta_mmd)
        return all(os.path.getmtime(s) >= origen for s in salidas if s)
    except OSError:
        return False


def crear_diagrama(
    referencia: str, ruta_mmd: str, out_png: str, out_pdf: str, out_svg: str | None = None
) -> Diagrama:
    """`out_svg` vacío o None guarda el SVG junto al PNG."""
    nombre_base = os.path.splitext(os.path.basename(ruta_mmd))[0]
    return Diagrama(
        referencia=referencia,
        ruta_mmd=ruta_mmd,
        ruta_png=os.path.join(out_png, f"{nombre_base}.png"),
        ruta_pdf=os.path.join(out_pdf, f"{nombre_base}.pdf"),
        ruta_svg=os.path.join(out_svg or out_png, f"{nombre_base}.svg"),
    )


def obtener_salida_diagramas(docs_dir: str, diagramas_out: str | None = None) -> str:
    return salida_diagramas(docs_dir, diagramas_out)
