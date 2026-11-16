"""Etapa 3: documentos Markdown."""
from .descubrimiento import documentos_en_markdown, encontrar_docs_dir, resolver_objetivo
from .estilos import cargar_estilo, estilos_disponibles
from .filtros import (
    AsegurarDiagramas,
    AplicarPlantilla,
    ConcatenarArchivos,
    ConvertirAHtml,
    EscribirPdf,
    ProtegerCodigo,
    RenderizarLatex,
    ResolverImagenes,
    RestaurarCodigo,
    SustituirDiagramas,
)
from .imagenes import (
    PATRON_HTML_IMG,
    PATRON_MMD,
    reemplazar_diagramas_por_png,
    reemplazar_imagenes_locales,
    reemplazar_src_html,
)
from .tuberia import procesar_documento, procesar_markdown

__all__ = [
    "AsegurarDiagramas",
    "AplicarPlantilla",
    "ConcatenarArchivos",
    "ConvertirAHtml",
    "EscribirPdf",
    "ProtegerCodigo",
    "RenderizarLatex",
    "ResolverImagenes",
    "RestaurarCodigo",
    "SustituirDiagramas",
    "cargar_estilo",
    "documentos_en_markdown",
    "encontrar_docs_dir",
    "estilos_disponibles",
    "procesar_documento",
    "procesar_markdown",
    "reemplazar_diagramas_por_png",
    "reemplazar_imagenes_locales",
    "reemplazar_src_html",
    "resolver_objetivo",
]