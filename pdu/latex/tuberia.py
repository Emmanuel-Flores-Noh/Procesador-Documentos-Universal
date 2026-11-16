"""Tubería LaTeX y API pública."""
from __future__ import annotations

from ..nucleo.contextos import TextoProtegido
from ..nucleo.filtros import Tuberia
from .filtros import (
    DesescaparDolares,
    ProtegerCodigo,
    RestaurarCodigo,
    SustituirBloques,
    SustituirEnLinea,
)
from .renderizador import COLOR_POR_DEFECTO, verificar_dependencias


def construir_tuberia(inline_size: float = 11, block_size: float = 13, color: str = COLOR_POR_DEFECTO) -> Tuberia:
    return Tuberia(
        "latex",
        [
            ProtegerCodigo(),
            SustituirBloques(block_size=block_size, color=color),
            SustituirEnLinea(inline_size=inline_size, color=color),
            RestaurarCodigo(),
            DesescaparDolares(),
        ],
    )


def procesar_latex_en_markdown(
    contenido_md: str, inline_size: float = 11, block_size: float = 13, color: str = COLOR_POR_DEFECTO
) -> str:
    """Sustituye las fórmulas LaTeX del Markdown por imágenes SVG embebidas.

    Si `ziamath` no está instalado devuelve el texto sin cambios.
    """
    if not verificar_dependencias():
        return contenido_md
    return construir_tuberia(inline_size, block_size, color).ejecutar(TextoProtegido(contenido_md)).texto
