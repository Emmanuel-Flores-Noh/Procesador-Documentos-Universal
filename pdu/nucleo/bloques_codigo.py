"""Protección y restauración de bloques de código.

Antes de transformar el texto (diagramas, imágenes, LaTeX) los bloques de
código se sustituyen por marcadores ``<!--PREFIJO_N-->`` para que su contenido
no se modifique; al final se restauran en una sola pasada.
"""
from __future__ import annotations

import re
from dataclasses import dataclass

PATRON_FENCED = re.compile(r"(```([a-zA-Z0-9_-]*)\r?\n([\s\S]*?)\r?\n```)", re.MULTILINE)
PATRON_INLINE_CODE = re.compile(r"(`+)(.+?)\1", re.DOTALL)


@dataclass
class BloquesProtegidos:
    texto: str
    bloques: list[str]


def _marcador(prefijo: str, idx: int) -> str:
    return f"<!--{prefijo}_{idx}-->"


def proteger(contenido: str, *, prefijo: str, modo_math: str = "preservar") -> BloquesProtegidos:
    """Sustituye bloques de código por marcadores.

    ``modo_math`` controla los bloques ```` ```math ````:
    - ``"preservar"``: se dejan intactos (los procesará la etapa LaTeX).
    - ``"convertir"``: se transforman en ``$$...$$``.
    """
    bloques: list[str] = []

    def guardar(bloque: str) -> str:
        bloques.append(bloque)
        return _marcador(prefijo, len(bloques) - 1)

    def proteger_fenced(match: re.Match) -> str:
        lenguaje = (match.group(2) or "").strip().lower()
        if lenguaje == "math":
            if modo_math == "convertir":
                return f"\n\n$${match.group(3)}$$\n\n"
            return match.group(0)
        return guardar(match.group(0))

    texto = PATRON_FENCED.sub(proteger_fenced, contenido)
    texto = PATRON_INLINE_CODE.sub(lambda m: guardar(m.group(0)), texto)
    return BloquesProtegidos(texto, bloques)


def restaurar(texto: str, bloques: list[str], *, prefijo: str) -> str:
    """Reemplaza los marcadores por sus bloques originales (una sola pasada)."""
    if not bloques:
        return texto
    patron = re.compile(rf"<!--{re.escape(prefijo)}_(\d+)-->")

    def reponer(match: re.Match) -> str:
        idx = int(match.group(1))
        return bloques[idx] if idx < len(bloques) else match.group(0)

    return patron.sub(reponer, texto)
