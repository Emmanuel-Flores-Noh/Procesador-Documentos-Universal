"""Utilidades compartidas para los textos de ayuda de la CLI."""
from __future__ import annotations

import argparse


class FormateadorAyuda(argparse.RawDescriptionHelpFormatter):
    """Conserva el formato de descripción/epílogo y traduce los títulos de argparse."""

    def __init__(self, prog, indent_increment=2, max_help_position=30, width=None):
        super().__init__(prog, indent_increment, max_help_position, width)

    def add_usage(self, usage, actions, groups, prefix=None):
        return super().add_usage(usage, actions, groups, prefix or "uso: ")


def _traducir_titulos(parser: argparse.ArgumentParser) -> None:
    parser._positionals.title = "argumentos"
    parser._optionals.title = "opciones"
    for accion in parser._actions:
        if isinstance(accion, argparse._HelpAction):
            accion.help = "muestra esta ayuda y termina"


def crear_parser(**kwargs) -> argparse.ArgumentParser:
    """`ArgumentParser` con el formateador y los títulos en español."""
    kwargs.setdefault("formatter_class", FormateadorAyuda)
    parser = argparse.ArgumentParser(**kwargs)
    _traducir_titulos(parser)
    return parser


def agregar_opcion_trabajos(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "-j", "--jobs",
        dest="trabajos",
        type=_entero_positivo,
        metavar="N",
        help="procesos mmdc simultáneos (por defecto: $PDU_JOBS o min(4, núcleos))",
    )


def _entero_positivo(valor: str) -> int:
    try:
        numero = int(valor)
    except ValueError:
        raise argparse.ArgumentTypeError(f"se esperaba un entero positivo: {valor!r}") from None
    if numero < 1:
        raise argparse.ArgumentTypeError(f"se esperaba un entero positivo: {valor!r}")
    return numero
