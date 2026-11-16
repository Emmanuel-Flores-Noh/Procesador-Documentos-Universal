"""Orquestación del pipeline completo: diagramas -> LaTeX -> Markdown."""
from __future__ import annotations

import os

from .nucleo.rutas import resolver_salida


def _titulo(texto: str) -> None:
    print("=" * 40)
    print(f" {texto}")
    print("=" * 40)


def ejecutar_pipeline(entrada, out_dir=None, diagramas_out=None, estilo=None, *, forzar=False, trabajos=None) -> int:
    """Compila los diagramas de ``docs/diagramas`` y genera los PDF.

    Sigue las reglas de salida de la CLI: un archivo -> directorio actual, una
    carpeta -> ``./out``. Devuelve el código de salida (0 = éxito).
    """
    from .diagramas.tuberia import ejecutar_diagramas_autonomo
    from .markdown.descubrimiento import encontrar_docs_dir
    from .markdown.tuberia import procesar_markdown

    ruta = os.path.abspath(entrada)
    if not os.path.exists(ruta):
        raise FileNotFoundError(f"La ruta no existe: {ruta}")

    out_dir = resolver_salida(out_dir, os.path.isfile(ruta))
    diagramas_out = os.path.abspath(diagramas_out) if diagramas_out else os.path.join(out_dir, "diagramas")

    docs_dir = encontrar_docs_dir(ruta)
    if docs_dir is None:
        docs_dir = ruta if os.path.isdir(ruta) else os.path.dirname(ruta)
    docs_dir = str(docs_dir)

    dir_diagramas = os.path.join(docs_dir, "diagramas")
    if os.path.isdir(dir_diagramas):
        _titulo("Etapa 1/2: diagramas Mermaid")
        ok, _ = ejecutar_diagramas_autonomo(
            dir_diagramas, diagramas_out, docs_dir=docs_dir, forzar=forzar, trabajos=trabajos
        )
        if not ok:
            print("Pipeline detenido: corrige los errores de diagramas e inténtalo de nuevo.")
            return 1
        print()

    _titulo("Etapa 2/2: documentos (LaTeX + Markdown -> PDF)")
    fallos = procesar_markdown(ruta, out_dir=out_dir, diagramas_out=diagramas_out, estilo=estilo, trabajos=trabajos)
    print()
    if fallos:
        print(f"Proceso finalizado con {fallos} documento(s) fallido(s).")
        return 1
    print(f"¡Proceso finalizado! Resultados en: {out_dir}")
    return 0
