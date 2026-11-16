"""Subcomando para generar la estructura de carpetas de documentación."""
from __future__ import annotations

import os
from pathlib import Path

ESTRUCTURA = (
    Path("diagramas"),
    Path("markdown"),
    Path("extras"),
)

RESPUESTAS_AFIRMATIVAS = {"s", "si", "sí", "y", "yes"}


def construir_plan(raiz, crear_raiz):
    """Carpetas que formarán la estructura (incluida la raíz si hay que crearla)."""
    carpetas = []
    if crear_raiz:
        carpetas.append(raiz)
    for relativa in ESTRUCTURA:
        carpetas.append(raiz / relativa)
    return carpetas


def validar_destino(ruta):
    """Devuelve (raiz, crear_raiz) o lanza ValueError con un mensaje claro."""
    if ruta.parent == ruta:
        raise ValueError("No se puede usar la raíz del sistema como destino.")
    if ruta.exists():
        if not ruta.is_dir():
            raise ValueError(f"La ruta final existe pero no es una carpeta: {ruta}")
        return ruta, False
    padre = ruta.parent
    if not padre.exists():
        raise ValueError(f"La carpeta padre no existe: {padre}")
    if not padre.is_dir():
        raise ValueError(f"La carpeta padre no es un directorio: {padre}")
    return ruta, True


def confirmar(faltantes):
    """Muestra las carpetas a crear y pide confirmación interactiva."""
    print("Se crearán las siguientes carpetas:")
    for carpeta in faltantes:
        print(f"  - {carpeta}")
    try:
        respuesta = input("\n¿Crear la estructura? [s/N]: ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        print("\nOperación cancelada. No se creó ninguna carpeta.")
        return False
    if respuesta not in RESPUESTAS_AFIRMATIVAS:
        print("Operación cancelada. No se creó ninguna carpeta.")
        return False
    return True


DESCRIPCION = """\
Crea la estructura de carpetas que espera pdu:

  <ruta>/
    diagramas/    archivos .mmd
    markdown/     una subcarpeta por documento con sus .md
    extras/       imágenes y otros recursos

Si <ruta> no existe se crea (su carpeta padre debe existir). Las carpetas
que ya existen se respetan; nunca se borra nada."""

EPILOGO = """\
ejemplos:
  pdu estructura                         usa ./docs
  pdu estructura docs/MiProyecto
  pdu estructura docs/MiProyecto -nc     sin pedir confirmación

alias: init"""


def construir_parser():
    from .nucleo.ayuda import crear_parser

    parser = crear_parser(prog="pdu estructura", description=DESCRIPCION, epilog=EPILOGO)
    parser.add_argument("ruta", nargs="?", default="docs", help="carpeta destino (por defecto: docs)")
    parser.add_argument(
        "-nc", "-y", "--no-confirmation",
        dest="sin_confirmacion",
        action="store_true",
        help="crea las carpetas sin pedir confirmación",
    )
    return parser


def main(argv=None, prog=None):
    parser = construir_parser()
    if prog:
        parser.prog = prog
    args = parser.parse_args(argv)

    if not args.ruta.strip():
        print("Error: la ruta no puede estar vacía.")
        return 1

    ruta = Path(os.path.abspath(os.path.expanduser(args.ruta)))

    try:
        raiz, crear_raiz = validar_destino(ruta)
    except ValueError as e:
        print(f"Error: {e}")
        return 1

    carpetas = construir_plan(raiz, crear_raiz)

    for carpeta in carpetas:
        if carpeta.exists() and not carpeta.is_dir():
            print(f"Error: existe un archivo donde debería ir una carpeta: {carpeta}")
            return 1

    faltantes = [carpeta for carpeta in carpetas if not carpeta.exists()]

    if not faltantes:
        print(f"La estructura ya existe en: {raiz}")
        return 0

    print(f"Ruta destino: {raiz}")

    if not args.sin_confirmacion and not confirmar(faltantes):
        return 1

    for carpeta in faltantes:
        try:
            carpeta.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            print(f"Error: no se pudo crear '{carpeta}': {e}")
            return 1
        print(f"  [Creada] {carpeta}")

    print(f"\nEstructura generada en: {raiz}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
