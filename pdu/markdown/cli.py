"""CLI de la etapa Markdown (`pdu markdown`)."""
from __future__ import annotations

import os

from ..nucleo.ayuda import agregar_opcion_trabajos, crear_parser
from ..nucleo.errores import ErrorProcesador
from ..nucleo.rutas import resolver_salida
from .estilos import directorio_estilos_usuario, estilos_disponibles

DESCRIPCION = """\
Convierte documentos Markdown a PDF (HTML + CSS con WeasyPrint). Por cada
documento se concatenan sus .md en orden alfabético con un salto de página
entre archivos, se compilan los diagramas .mmd referenciados que falten, se
renderizan las fórmulas LaTeX y se aplica el estilo CSS elegido."""

EPILOGO = """\
entrada aceptada:
  archivo.md            un PDF con el nombre del archivo
  docs/markdown/Proy/   un PDF «Proy.pdf» con todos sus .md
  docs/                 un PDF por cada subcarpeta de docs/markdown/

salida:
  un archivo            directorio actual
  una carpeta           ./out  (diagramas en ./out/diagramas)
  -o CARPETA            la carpeta indicada

estilos:
  Usa --listar-estilos para verlos. Para añadir uno propio copia un .css en
  {estilos}

ejemplos:
  pdu markdown docs
  pdu markdown docs/markdown/MiProyecto --estilo academico
  pdu markdown capitulo.md -o pdfs --estilo ./mi-estilo.css

alias: md, 3"""


def construir_parser():
    parser = crear_parser(
        prog="pdu markdown",
        description=DESCRIPCION,
        epilog=EPILOGO.format(estilos=directorio_estilos_usuario(crear=False)),
    )
    parser.add_argument("entrada", nargs="?", help="archivo .md, carpeta de un documento o carpeta docs/")
    agregar_opciones_documento(parser)
    parser.add_argument("--listar-estilos", action="store_true", help="muestra los estilos disponibles y termina")
    return parser


def agregar_opciones_documento(parser) -> None:
    """Opciones comunes a `pdu markdown` y `pdu all`."""
    parser.add_argument("-o", "--out", dest="out_dir", metavar="CARPETA", help="carpeta de salida de los PDF")
    parser.add_argument("--diagramas-out", metavar="CARPETA",
                        help="carpeta para los diagramas compilados (por defecto: <salida>/diagramas)")
    parser.add_argument("-s", "--estilo", metavar="NOMBRE|CSS",
                        help="estilo del PDF: nombre (default, compacto, academico, ...) o ruta a un .css")
    agregar_opcion_trabajos(parser)


def main(argv=None) -> int:
    parser = construir_parser()
    args = parser.parse_args(argv)

    if args.listar_estilos:
        print("\n".join(estilos_disponibles()))
        return 0
    if not args.entrada:
        parser.print_help()
        return 1

    entrada = os.path.abspath(args.entrada)
    if not os.path.exists(entrada):
        print(f"Error: la ruta no existe: {entrada}")
        return 1

    from .tuberia import procesar_markdown

    out_dir = resolver_salida(args.out_dir, os.path.isfile(entrada))
    try:
        fallos = procesar_markdown(
            entrada, out_dir=out_dir, diagramas_out=args.diagramas_out, estilo=args.estilo, trabajos=args.trabajos
        )
    except (FileNotFoundError, ValueError, ErrorProcesador) as e:
        print(f"Error: {e}")
        return 1
    return 1 if fallos else 0


if __name__ == "__main__":
    raise SystemExit(main())
