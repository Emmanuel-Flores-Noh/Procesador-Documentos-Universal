"""CLI de la etapa LaTeX (`pdu latex`)."""
from __future__ import annotations

import glob
import os
import sys

from ..nucleo.ayuda import crear_parser
from ..nucleo.rutas import guardar_salida, resolver_salida
from .renderizador import latex_a_svg, verificar_dependencias
from .tuberia import procesar_latex_en_markdown

DESCRIPCION = """\
Renderiza fórmulas LaTeX a SVG con ziamath (sin necesidad de una instalación
de TeX). Puede convertir una expresión suelta o procesar documentos Markdown,
sustituyendo $...$, $$...$$, \\(...\\), \\[...\\] y bloques ```math por
imágenes SVG embebidas. El código entre comillas invertidas no se modifica."""

EPILOGO = """\
modos de uso:
  --expr "LATEX"        expresión -> formula.svg (o -o ARCHIVO)
  archivo.md            -> <nombre>-procesado.md en el directorio actual
  carpeta/              cada .md -> ./out/<nombre>-procesado.md
  "LATEX"               si la entrada no es una ruta existente, se trata
                        como expresión

ejemplos:
  pdu latex --expr "E = mc^2"
  pdu latex --expr "\\frac{a}{b}" --inline -o fraccion.svg
  pdu latex capitulo.md --stdout
  pdu latex docs/markdown/MiProyecto -o procesados"""


def construir_parser():
    parser = crear_parser(prog="pdu latex", description=DESCRIPCION, epilog=EPILOGO)
    parser.add_argument("entrada", nargs="?", help="archivo .md, carpeta con .md o expresión LaTeX")
    parser.add_argument("-e", "--expr", metavar="LATEX", help="renderiza esta expresión a SVG")
    parser.add_argument("--inline", action="store_true", help="renderiza la expresión como fórmula en línea")
    parser.add_argument("-o", "--out", metavar="RUTA", help="archivo (expresión o .md) o carpeta (directorio) de salida")
    parser.add_argument("--stdout", action="store_true", help="imprime el resultado en lugar de guardarlo")
    return parser


def _emitir(contenido: str, destino: str, stdout: bool, etiqueta: str) -> int:
    if stdout:
        print(contenido)
    else:
        print(f"{etiqueta} guardado en {guardar_salida(destino, contenido)}")
    return 0


def _expresion(latex: str, inline: bool, out: str | None, stdout: bool) -> int:
    if not verificar_dependencias():
        return 1
    try:
        svg = latex_a_svg(latex, inline=inline)
    except Exception as e:
        print(f"Error: no se pudo renderizar '{latex}': {e}", file=sys.stderr)
        return 1
    return _emitir(svg, out or os.path.join(os.getcwd(), "formula.svg"), stdout, "SVG")


def _procesar_md(ruta: str) -> str:
    with open(ruta, encoding="utf-8") as f:
        return procesar_latex_en_markdown(f.read())


def _nombre_procesado(ruta: str) -> str:
    return os.path.splitext(os.path.basename(ruta))[0] + "-procesado.md"


def main(argv=None) -> int:
    parser = construir_parser()
    args = parser.parse_args(argv)

    if args.expr is not None:
        return _expresion(args.expr, args.inline, args.out, args.stdout)
    if not args.entrada:
        parser.print_help()
        return 1

    entrada = os.path.abspath(args.entrada)

    if os.path.isfile(entrada):
        if not entrada.lower().endswith(".md"):
            print(f"Error: se esperaba un archivo Markdown (.md): {entrada}")
            return 1
        destino = args.out or os.path.join(resolver_salida(None, True), _nombre_procesado(entrada))
        return _emitir(_procesar_md(entrada), destino, args.stdout, "Markdown procesado")

    if os.path.isdir(entrada):
        archivos = sorted(glob.glob(os.path.join(entrada, "*.md")))
        if not archivos:
            print(f"Error: no hay archivos .md en: {entrada}")
            return 1
        out_dir = resolver_salida(args.out, False)
        for archivo in archivos:
            _emitir(_procesar_md(archivo), os.path.join(out_dir, _nombre_procesado(archivo)), args.stdout, "Markdown procesado")
        return 0

    # Parece una ruta pero no existe: es más probable un error tipográfico que una fórmula.
    if args.entrada.lower().endswith(".md") or os.sep in args.entrada or "/" in args.entrada:
        print(f"Error: la ruta no existe: {entrada}  (para una expresión usa --expr)")
        return 1
    # No es una ruta: se interpreta como expresión LaTeX.
    return _expresion(args.entrada, args.inline, args.out, args.stdout)


if __name__ == "__main__":
    raise SystemExit(main())
