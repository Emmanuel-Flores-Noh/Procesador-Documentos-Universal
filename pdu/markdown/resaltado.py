"""CSS de resaltado de sintaxis para los bloques de código (Pygments).

Cada tema puede personalizar los colores de dos formas, combinables:

1. Elegir la paleta base de Pygments con una variable CSS::

       :root { --pdu-resaltado: tango; }

   Si no se declara (o el nombre no existe) se usa ``default``.

2. Sobrescribir tokens concretos, p. ej. ``.codehilite .k { color: #7c3aed; }``.
   El CSS del tema va después del de Pygments, así que los tokens que el tema
   no declara conservan el color de la paleta base.

El fondo del bloque siempre lo pone el tema (regla ``.codehilite``).
"""
from __future__ import annotations

import re
from functools import lru_cache

CLASE_CSS = "codehilite"
PALETA_POR_DEFECTO = "default"
PATRON_PALETA = re.compile(r"--pdu-resaltado\s*:\s*[\"']?([A-Za-z0-9_-]+)")


def paleta_del_tema(css_tema: str) -> str:
    """Nombre de la paleta Pygments declarada en el tema, o la de por defecto."""
    from pygments.styles import get_all_styles

    m = PATRON_PALETA.search(css_tema or "")
    if not m:
        return PALETA_POR_DEFECTO
    nombre = m.group(1)
    if nombre not in set(get_all_styles()):
        print(f"  [Aviso] Paleta de resaltado desconocida '{nombre}'; se usa '{PALETA_POR_DEFECTO}'.")
        return PALETA_POR_DEFECTO
    return nombre


@lru_cache(maxsize=None)
def css_resaltado(paleta: str = PALETA_POR_DEFECTO) -> str:
    """Reglas CSS de Pygments para ``.codehilite`` sin el fondo (lo pone el tema)."""
    from pygments.formatters import HtmlFormatter

    css = HtmlFormatter(style=paleta).get_style_defs(f".{CLASE_CSS}")
    lineas = [l for l in css.splitlines() if not l.startswith(f".{CLASE_CSS} {{ background")]
    return "\n".join(lineas) + "\n"


def css_resaltado_para_tema(css_tema: str) -> str:
    return css_resaltado(paleta_del_tema(css_tema))
