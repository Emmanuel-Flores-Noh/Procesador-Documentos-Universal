"""Tubería de documentos Markdown y API pública."""
from __future__ import annotations

import os

from ..nucleo.contextos import ContextoDocumento, Documento
from ..nucleo.filtros import Tuberia
from ..nucleo.rutas import salida_diagramas, salida_docs
from .descubrimiento import resolver_objetivo
from .estilos import ESTILO_POR_DEFECTO, cargar_estilo
from .filtros import (
    AplicarPlantilla,
    AsegurarDiagramas,
    ConcatenarArchivos,
    ConvertirAHtml,
    EscribirPdf,
    ProtegerCodigo,
    RenderizarLatex,
    ResolverImagenes,
    RestaurarCodigo,
    SustituirDiagramas,
)


def construir_tuberia_documento(css: str | None = None) -> Tuberia:
    """Markdown -> PDF. El argumento `css` se conserva por compatibilidad."""
    return Tuberia(
        "documento",
        [
            ConcatenarArchivos(),
            AsegurarDiagramas(),
            ProtegerCodigo(),
            SustituirDiagramas(),
            ResolverImagenes(),
            RestaurarCodigo(),
            RenderizarLatex(),
            ConvertirAHtml(),
            AplicarPlantilla(),
            EscribirPdf(),
        ],
    )


def procesar_documento(
    archivos_md,
    nombre_proyecto,
    subcarpeta,
    docs_dir,
    out_dir=None,
    diagramas_out=None,
    estilo=None,
    css=None,
    trabajos=None,
) -> bool:
    """Genera el PDF de un documento. Devuelve True si se escribió correctamente."""
    out_docs = salida_docs(docs_dir, out_dir)
    os.makedirs(out_docs, exist_ok=True)
    print(f"Procesando documento: {nombre_proyecto} ...")

    if css is None:
        _, css = cargar_estilo(estilo)

    ctx = ContextoDocumento(
        documento=Documento(subcarpeta=subcarpeta, nombre=nombre_proyecto, archivos_md=list(archivos_md)),
        docs_dir=docs_dir,
        out_docs=out_docs,
        diagramas_out=diagramas_out or salida_diagramas(docs_dir, None),
        estilo=estilo or ESTILO_POR_DEFECTO,
        css=css,
        trabajos=trabajos,
    )
    construir_tuberia_documento().ejecutar(ctx)
    return ctx.fallo is None


def procesar_markdown(entrada, out_dir=None, diagramas_out=None, estilo=None, trabajos=None) -> int:
    """Procesa todos los documentos de `entrada`. Devuelve el número de fallos."""
    docs_dir, documentos = resolver_objetivo(entrada)
    if not documentos:
        print(f"No se encontraron documentos para procesar en: {docs_dir}")
        return 0

    if out_dir and not diagramas_out:
        diagramas_out = os.path.join(os.path.abspath(out_dir), "diagramas")

    nombre_estilo, css = cargar_estilo(estilo)
    print(f"Carpeta de documentos: {docs_dir}")
    print(f"Estilo: {nombre_estilo}")

    fallos = 0
    for doc in documentos:
        ok = procesar_documento(
            doc.archivos_md,
            doc.nombre,
            doc.subcarpeta,
            docs_dir,
            out_dir=out_dir,
            diagramas_out=diagramas_out,
            estilo=nombre_estilo,
            css=css,
            trabajos=trabajos,
        )
        fallos += not ok
    return fallos
