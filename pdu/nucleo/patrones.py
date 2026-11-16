"""Expresiones regulares y utilidades de referencias compartidas entre etapas."""
from __future__ import annotations

import re

# ![alt](ruta.mmd)  -> referencia a un diagrama Mermaid.
PATRON_MMD = re.compile(r"!\[([^\]]*)\]\(([^)]+)\.mmd\)")
# ![alt](destino "titulo opcional")  -> imagen Markdown genérica.
PATRON_IMG = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
# <img ... src="...">  -> imagen HTML embebida en el Markdown.
PATRON_HTML_IMG = re.compile(r'(<img\b[^>]*?\bsrc=["\'])([^"\']+)(["\'][^>]*?>)', re.IGNORECASE)

_PATRON_URL_EXTERNA = re.compile(r"^(https?://|data:|file://)", re.IGNORECASE)


def es_url_externa(ruta: str) -> bool:
    """Indica si `ruta` es una URL (http, data o file) que no debe reescribirse."""
    return bool(_PATRON_URL_EXTERNA.match(ruta))
