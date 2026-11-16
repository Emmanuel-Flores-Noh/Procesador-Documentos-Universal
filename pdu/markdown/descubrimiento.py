"""Descubrimiento de documentos Markdown."""
from __future__ import annotations

import glob
import os
from pathlib import Path

from ..nucleo.contextos import Documento


def encontrar_docs_dir(ruta):
    actual = Path(ruta).expanduser().resolve()
    if actual.is_file():
        actual = actual.parent
    for candidato in [actual, *actual.parents]:
        if candidato.name == "markdown":
            return candidato.parent
        if (candidato / "markdown").is_dir():
            return candidato
    return None


def documentos_en_markdown(dir_markdown):
    documentos = []
    with os.scandir(dir_markdown) as entradas:
        subcarpetas = sorted(
            (entrada for entrada in entradas if entrada.is_dir()),
            key=lambda entrada: entrada.name,
        )
    for subcarpeta in subcarpetas:
        archivos_md = sorted(glob.glob(os.path.join(subcarpeta.path, "*.md")))
        if not archivos_md:
            print(f"Omitiendo subcarpeta '{subcarpeta.name}' (no contiene archivos .md)")
            continue
        documentos.append(Documento(subcarpeta.path, subcarpeta.name, archivos_md))
    return documentos


def resolver_objetivo(entrada):
    ruta = Path(entrada).expanduser().resolve()
    if not ruta.exists():
        raise FileNotFoundError(f"La ruta especificada no existe: {ruta}")
    if ruta.is_file():
        if ruta.suffix.lower() != ".md":
            raise ValueError(f"El archivo debe ser Markdown (.md): {ruta}")
        docs_dir = encontrar_docs_dir(ruta)
        if docs_dir is None:
            docs_dir = ruta.parent
        return str(docs_dir), [Documento(str(ruta.parent), ruta.stem, [str(ruta)])]
    if not ruta.is_dir():
        raise ValueError(f"La ruta no es un archivo ni una carpeta válida: {ruta}")
    docs_dir = encontrar_docs_dir(ruta)
    if docs_dir is not None:
        if ruta.name == "markdown":
            return str(docs_dir), documentos_en_markdown(ruta)
        if (ruta / "markdown").is_dir():
            return str(docs_dir), documentos_en_markdown(ruta / "markdown")
        archivos_md = sorted(glob.glob(os.path.join(str(ruta), "*.md")))
        if archivos_md:
            return str(docs_dir), [Documento(str(ruta), ruta.name, archivos_md)]
    archivos_md = sorted(glob.glob(os.path.join(str(ruta), "*.md")))
    if archivos_md:
        return str(ruta.parent), [Documento(str(ruta), ruta.name, archivos_md)]
    raise ValueError(
        f"No se encontraron documentos para procesar en: {ruta}\n"
        "Pasa la carpeta de documentos (con 'markdown/'), una carpeta de documento "
        "o un archivo .md específico."
    )