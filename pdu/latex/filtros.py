"""Filtros de texto de la etapa LaTeX."""
from __future__ import annotations

import html
import re
import sys

from ..nucleo.bloques_codigo import proteger, restaurar
from ..nucleo.contextos import TextoProtegido
from .renderizador import COLOR_POR_DEFECTO, latex_a_data_uri

PREFIJO = "CODE_BLOCK_PLACEHOLDER"

PATRON_BLOQUE_DOLARES = re.compile(r"\$\$(.+?)\$\$", re.DOTALL)
PATRON_BLOQUE_CORCHETES = re.compile(r"\\\[(.+?)\\\]", re.DOTALL)
PATRON_INLINE_DOLARES = re.compile(r"(?<!\\)\$(?!\s)([^\$\r\n]+?)(?<!\s)(?<!\\)\$")
PATRON_INLINE_PARENTESIS = re.compile(r"\\\((.+?)\\\)", re.DOTALL)


class ProtegerCodigo:
    nombre = "proteger-codigo"

    def procesar(self, datos: TextoProtegido) -> TextoProtegido:
        protegido = proteger(datos.texto, prefijo=PREFIJO, modo_math="convertir")
        return TextoProtegido(protegido.texto, protegido.bloques)


class _SustituirFormulas:
    """Base: reemplaza fórmulas por imágenes SVG embebidas (o código si fallan)."""
    nombre = ""
    inline = False
    patrones: tuple[re.Pattern, ...] = ()

    def __init__(self, size: float, color: str = COLOR_POR_DEFECTO):
        self.size = size
        self.color = color

    def _html_ok(self, uri: str, alt: str) -> str:
        raise NotImplementedError

    def _html_error(self, alt: str) -> str:
        raise NotImplementedError

    def _reemplazar(self, match: re.Match) -> str:
        formula = match.group(1).strip()
        if not formula:
            return ""
        alt = html.escape(formula, quote=True)
        try:
            uri = latex_a_data_uri(formula, inline=self.inline, font_size=self.size, color=self.color)
        except Exception as e:
            tipo = "en línea" if self.inline else "de bloque"
            print(f"  [Advertencia] No se pudo renderizar la fórmula {tipo} '{formula[:40]}': {e}", file=sys.stderr)
            return self._html_error(alt)
        return self._html_ok(uri, alt)

    def procesar(self, datos: TextoProtegido) -> TextoProtegido:
        texto = datos.texto
        for patron in self.patrones:
            texto = patron.sub(self._reemplazar, texto)
        return TextoProtegido(texto, datos.bloques)


class SustituirBloques(_SustituirFormulas):
    """Fórmulas de bloque: ``$$...$$`` y ``\\[...\\]``."""
    nombre = "sustituir-bloques"
    patrones = (PATRON_BLOQUE_DOLARES, PATRON_BLOQUE_CORCHETES)

    def __init__(self, block_size: float = 13, color: str = COLOR_POR_DEFECTO):
        super().__init__(block_size, color)

    def _html_ok(self, uri, alt):
        return f'\n\n<div class="math-block"><img src="{uri}" class="math-block-img" alt="{alt}" /></div>\n\n'

    def _html_error(self, alt):
        return f'\n\n<div class="math-block math-error"><pre><code>{alt}</code></pre></div>\n\n'


class SustituirEnLinea(_SustituirFormulas):
    """Fórmulas en línea: ``$...$`` y ``\\(...\\)``."""
    nombre = "sustituir-en-linea"
    inline = True
    patrones = (PATRON_INLINE_DOLARES, PATRON_INLINE_PARENTESIS)

    def __init__(self, inline_size: float = 11, color: str = COLOR_POR_DEFECTO):
        super().__init__(inline_size, color)

    def _html_ok(self, uri, alt):
        return f'<span class="math-inline"><img src="{uri}" class="math-inline-img" alt="{alt}" /></span>'

    def _html_error(self, alt):
        return f'<code class="math-error">{alt}</code>'


class RestaurarCodigo:
    nombre = "restaurar-codigo"

    def procesar(self, datos: TextoProtegido) -> TextoProtegido:
        return TextoProtegido(restaurar(datos.texto, datos.bloques, prefijo=PREFIJO), [])


class DesescaparDolares:
    nombre = "desescapar-dolares"

    def procesar(self, datos: TextoProtegido) -> TextoProtegido:
        return TextoProtegido(datos.texto.replace(r"\$", "$"), datos.bloques)
