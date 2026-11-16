"""Renderizado LaTeX -> SVG / Data URI con `ziamath` (cargado bajo demanda)."""
from __future__ import annotations

import base64
import functools
import sys

COLOR_POR_DEFECTO = "#1e293b"

_NO_CARGADO = object()
_zm = _NO_CARGADO


def _ziamath():
    """Importa `ziamath` la primera vez que se necesita (ahorra ~0,5 s de arranque)."""
    global _zm
    if _zm is _NO_CARGADO:
        try:
            import ziamath
        except ImportError:
            ziamath = None
        _zm = ziamath
    return _zm


def __getattr__(nombre):
    # Compatibilidad: `renderizador.zm` sigue disponible como atributo del módulo.
    if nombre == "zm":
        return _ziamath()
    raise AttributeError(nombre)


def verificar_dependencias() -> bool:
    """True si `ziamath` está disponible; si no, muestra cómo instalarlo."""
    if _ziamath() is None:
        print(
            "  [Advertencia] La librería 'ziamath' no está instalada; las fórmulas\n"
            "  LaTeX se dejarán sin renderizar. Instálala con: pip install ziamath",
            file=sys.stderr,
        )
        return False
    return True


@functools.lru_cache(maxsize=2048)
def latex_a_svg(latex_str: str, inline: bool = False, font_size: float | None = None,
                color: str = COLOR_POR_DEFECTO) -> str:
    zm = _ziamath()
    if zm is None:
        raise RuntimeError("ziamath no está instalado en el entorno (pip install ziamath).")
    latex_limpio = latex_str.strip()
    if not latex_limpio:
        return ""
    return zm.Latex(latex_limpio, inline=inline, size=font_size, color=color).svg()


@functools.lru_cache(maxsize=2048)
def latex_a_data_uri(latex_str: str, inline: bool = False, font_size: float | None = None,
                     color: str = COLOR_POR_DEFECTO) -> str:
    svg = latex_a_svg(latex_str, inline=inline, font_size=font_size, color=color)
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode("utf-8")).decode("ascii")
