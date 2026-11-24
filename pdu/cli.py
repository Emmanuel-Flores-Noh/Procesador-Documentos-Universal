"""CLI universal del procesador de documentos (`pdu`).

Cada subcomando se registra una sola vez en `COMANDOS`; su módulo se importa
solo al ejecutarlo, de modo que `pdu --help` responde al instante.
"""
from __future__ import annotations

import difflib
import importlib
import os
import sys
from dataclasses import dataclass

from . import __version__


@dataclass(frozen=True)
class Comando:
    nombre: str
    alias: tuple[str, ...]
    resumen: str
    destino: str  # "modulo:funcion" que recibe argv y devuelve el código de salida

    def ejecutar(self, argv: list[str]) -> int:
        modulo, funcion = self.destino.split(":")
        return getattr(importlib.import_module(modulo, __package__), funcion)(argv)


COMANDOS: tuple[Comando, ...] = (
    Comando("all", ("todo", "pipeline", "0"),
            "Pipeline completo: diagramas, LaTeX y Markdown -> PDF.", ".cli:main_all"),
    Comando("mermaid", ("diagramas", "diagrama", "diagrams", "diagram", "1"),
            "Compila diagramas Mermaid (.mmd) a PNG, PDF y SVG.", ".diagramas.cli:main"),
    Comando("latex", ("2",),
            "Renderiza fórmulas LaTeX a SVG (expresión o Markdown).", ".latex.cli:main"),
    Comando("markdown", ("md", "3"),
            "Convierte documentos Markdown a PDF.", ".markdown.cli:main"),
    Comando("estructura", ("init",),
            "Crea la estructura de carpetas docs/ (diagramas, markdown, extras).", ".estructura:main"),
)

ALIASES: dict[str, str] = {
    nombre: c.nombre for c in COMANDOS for nombre in (c.nombre, *c.alias)
}
COMMANDS = set(ALIASES)
_POR_NOMBRE = {c.nombre: c for c in COMANDOS}


def _texto_ayuda() -> str:
    filas = "\n".join(
        f"  {c.nombre:<11} {c.resumen}" + (f"\n  {'':<11} alias: {', '.join(c.alias)}" if c.alias else "")
        for c in COMANDOS
    )
    return f"""\
uso: pdu [comando] [opciones] [entrada]

Procesador universal de documentos {__version__}: convierte documentación técnica
(diagramas Mermaid, fórmulas LaTeX y Markdown) en PDF.

comandos:
{filas}

  Si el primer argumento no es un comando se asume «all»: `pdu docs`
  equivale a `pdu all docs`.

opciones globales:
  -h, --help        muestra esta ayuda (o `pdu <comando> --help`)
  -V, --version     muestra la versión

estructura esperada de docs/:
  docs/diagramas/*.mmd          diagramas, referenciados como ![t](nombre.mmd)
  docs/markdown/<Doc>/*.md      cada subcarpeta genera <Doc>.pdf
  docs/extras/                  recursos adicionales (imágenes, etc.)

reglas de salida:
  un archivo de entrada -> directorio actual
  una carpeta           -> ./out
  -o/--out RUTA         -> la carpeta indicada

variables de entorno:
  PDU_DATA_DIR                  directorio de datos (estilos/, bin/)
  PDU_JOBS                      procesos mmdc simultáneos por defecto
  MMDC_PATH, PDU_BIN            ruta de Mermaid CLI o carpeta que lo contiene
  PUPPETEER_EXECUTABLE_PATH     navegador usado por Mermaid CLI

ejemplos:
  pdu estructura docs/MiProyecto     crea la estructura de carpetas
  pdu docs                           genera todos los PDF en ./out
  pdu markdown docs --estilo academico
  pdu mermaid docs/diagramas -j 2
  pdu latex --expr "E = mc^2"
"""


def main_all(argv=None) -> int:
    """`pdu all`: pipeline completo."""
    from .markdown.cli import agregar_opciones_documento
    from .nucleo.ayuda import crear_parser
    from .nucleo.errores import ErrorProcesador
    from .orquestador import ejecutar_pipeline

    parser = crear_parser(
        prog="pdu all",
        description=(
            "Ejecuta el pipeline completo: compila los diagramas de docs/diagramas\n"
            "(omitiendo los que están al día), renderiza las fórmulas LaTeX y genera\n"
            "un PDF por documento."
        ),
        epilog=(
            "salida:\n"
            "  un archivo            directorio actual\n"
            "  una carpeta           ./out  (diagramas en ./out/diagramas/{png,pdf,svg})\n"
            "\n"
            "ejemplos:\n"
            "  pdu all docs\n"
            "  pdu docs -o build --estilo compacto\n"
            "  pdu docs --forzar -j 2\n"
            "\n"
            "alias: todo, pipeline, 0"
        ),
    )
    parser.add_argument("entrada", nargs="?", default="docs",
                        help="carpeta docs/, carpeta de un documento o archivo .md (por defecto: docs)")
    agregar_opciones_documento(parser)
    parser.add_argument("-f", "--forzar", action="store_true", help="recompila todos los diagramas aunque estén al día")
    args = parser.parse_args(argv)
    try:
        return ejecutar_pipeline(
            args.entrada,
            out_dir=args.out_dir,
            diagramas_out=args.diagramas_out,
            estilo=args.estilo,
            forzar=args.forzar,
            trabajos=args.trabajos,
        )
    except (FileNotFoundError, ValueError, ErrorProcesador) as e:
        print(f"Error: {e}")
        return 1


def _parece_ruta(token: str) -> bool:
    return os.path.exists(token) or any(c in token for c in "/\\.~")


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)

    if not argv or argv[0] in ("-h", "--help"):
        print(_texto_ayuda())
        return 0
    if argv[0] in ("-V", "--version"):
        print(f"pdu {__version__}")
        return 0

    primero = argv[0]
    if primero in ("help", "ayuda"):
        if len(argv) > 1 and argv[1] in ALIASES:
            return _POR_NOMBRE[ALIASES[argv[1]]].ejecutar(["--help"])
        print(_texto_ayuda())
        return 0
    if primero in ALIASES:
        comando, resto = _POR_NOMBRE[ALIASES[primero]], argv[1:]
    elif primero.startswith("-") or _parece_ruta(primero):
        comando, resto = _POR_NOMBRE["all"], argv
    else:
        sugerencias = difflib.get_close_matches(primero, list(ALIASES), n=1)
        pista = f" ¿Quisiste decir «{ALIASES[sugerencias[0]]}»?" if sugerencias else ""
        print(f"pdu: comando o ruta desconocida: '{primero}'.{pista}", file=sys.stderr)
        print("Ejecuta `pdu --help` para ver los comandos disponibles.", file=sys.stderr)
        return 2

    try:
        return comando.ejecutar(resto)
    except KeyboardInterrupt:
        print("\nOperación cancelada por el usuario.", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
