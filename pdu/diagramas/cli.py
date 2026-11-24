"""CLI de la etapa de diagramas Mermaid (`pdu mermaid`)."""
from __future__ import annotations

import argparse
import os

from ..nucleo.ayuda import agregar_opcion_trabajos, crear_parser
from ..nucleo.rutas import resolver_salida
from .descubrimiento import archivos_mmd_de_entrada
from .tuberia import ejecutar_diagramas_autonomo

DESCRIPCION = """\
Compila diagramas Mermaid (.mmd) a PNG (fondo transparente), PDF y SVG
usando Mermaid CLI (mmdc). Los diagramas cuyo PNG, PDF y SVG son más
recientes que el .mmd se omiten, salvo que se use --forzar."""

EPILOGO = """\
entrada aceptada:
  archivo.mmd           un único diagrama
  carpeta/              todos los .mmd de la carpeta
  docs/                 si no hay .mmd directos, se usa docs/diagramas/

salida (PNG, PDF y SVG juntos):
  un archivo            directorio actual
  una carpeta           ./out
  -o RUTA               la carpeta indicada

ejemplos:
  pdu mermaid diagrama.mmd
  pdu mermaid docs/diagramas -o salida
  pdu mermaid docs --forzar -j 2

alias: diagramas, diagrama, diagrams, diagram, 1"""


def construir_parser() -> argparse.ArgumentParser:
    parser = crear_parser(prog="pdu mermaid", description=DESCRIPCION, epilog=EPILOGO)
    parser.add_argument("entrada", help="archivo .mmd, carpeta con .mmd o carpeta de documentos con diagramas/")
    parser.add_argument("-o", "--out", dest="out_dir", metavar="CARPETA", help="carpeta de salida (ver «salida» abajo)")
    parser.add_argument("-f", "--forzar", action="store_true", help="recompila aunque los diagramas estén al día")
    agregar_opcion_trabajos(parser)
    return parser


def main(argv=None) -> int:
    args = construir_parser().parse_args(argv)

    entrada = os.path.abspath(args.entrada)
    if not os.path.exists(entrada):
        print(f"Error: la ruta no existe: {entrada}")
        return 1
    archivos = archivos_mmd_de_entrada(entrada)
    if not archivos:
        print(f"Error: no se encontraron archivos .mmd en: {entrada}")
        return 1

    es_archivo = os.path.isfile(entrada)
    out_dir = resolver_salida(args.out_dir, es_archivo)
    docs_dir = os.path.dirname(entrada) if es_archivo else entrada

    ok, _ = ejecutar_diagramas_autonomo(
        archivos, out_dir, docs_dir, forzar=args.forzar, trabajos=args.trabajos, planos=True
    )
    if not ok:
        return 1
    print(f"Diagramas en: {out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
