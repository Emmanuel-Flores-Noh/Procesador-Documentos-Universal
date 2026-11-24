"""Filtros de la etapa de documentos Markdown."""
from __future__ import annotations

import os
from pathlib import Path

from ..diagramas.tuberia import compilar_diagramas_requeridos
from ..latex.tuberia import procesar_latex_en_markdown
from ..nucleo.bloques_codigo import proteger, restaurar
from ..nucleo.contextos import ContextoDocumento
from .imagenes import (
    PATRON_HTML_IMG,
    PATRON_IMG,
    PATRON_MMD,
    reemplazar_diagramas_por_svg,
    reemplazar_imagenes_locales,
    reemplazar_src_html,
)
from .pdf import generar_pdf
from .plantilla import construir_html
from .resaltado import CLASE_CSS, css_resaltado_para_tema

PREFIJO_MARKDOWN = "CODE_BLOCK_IMG"
SALTO_DE_PAGINA = '\n\n<div style="page-break-before: always;"></div>\n\n'
EXTENSIONES_MARKDOWN = ("fenced_code", "codehilite", "tables")
CONFIG_EXTENSIONES = {
    # guess_lang=False: sin ```lenguaje el bloque queda en texto plano.
    "codehilite": {"css_class": CLASE_CSS, "guess_lang": False, "use_pygments": True},
}


class ConcatenarArchivos:
    """Une los .md del documento (orden alfabético) con un salto de página entre ellos."""
    nombre = "concatenar-archivos"

    def procesar(self, ctx: ContextoDocumento) -> ContextoDocumento:
        partes = [Path(a).read_text(encoding="utf-8") + "\n\n" for a in sorted(ctx.documento.archivos_md)]
        ctx.texto += SALTO_DE_PAGINA.join(partes)
        return ctx


class AsegurarDiagramas:
    """Compila los diagramas que el documento referencia y aún no están al día."""
    nombre = "asegurar-diagramas"

    def procesar(self, ctx: ContextoDocumento) -> ContextoDocumento:
        compilar_diagramas_requeridos(
            ctx.documento.archivos_md, ctx.docs_dir, ctx.documento.subcarpeta, ctx.diagramas_out, ctx.trabajos
        )
        return ctx


class ProtegerCodigo:
    nombre = "proteger-codigo"

    def procesar(self, ctx: ContextoDocumento) -> ContextoDocumento:
        protegido = proteger(ctx.texto, prefijo=PREFIJO_MARKDOWN, modo_math="preservar")
        ctx.texto = protegido.texto
        ctx.bloques_codigo = protegido.bloques
        return ctx


class SustituirDiagramas:
    """``![...](x.mmd)`` -> SVG compilado (vectorial)."""
    nombre = "sustituir-diagramas"

    def procesar(self, ctx: ContextoDocumento) -> ContextoDocumento:
        ctx.texto = PATRON_MMD.sub(lambda m: reemplazar_diagramas_por_svg(m, ctx.dir_svg), ctx.texto)
        return ctx


class ResolverImagenes:
    """Rutas de imágenes relativas -> URIs absolutas para WeasyPrint."""
    nombre = "resolver-imagenes"

    def procesar(self, ctx: ContextoDocumento) -> ContextoDocumento:
        base = ctx.documento.subcarpeta
        ctx.texto = PATRON_IMG.sub(lambda m: reemplazar_imagenes_locales(m, base), ctx.texto)
        ctx.texto = PATRON_HTML_IMG.sub(lambda m: reemplazar_src_html(m, base), ctx.texto)
        return ctx


class RestaurarCodigo:
    nombre = "restaurar-codigo"

    def procesar(self, ctx: ContextoDocumento) -> ContextoDocumento:
        ctx.texto = restaurar(ctx.texto, ctx.bloques_codigo, prefijo=PREFIJO_MARKDOWN)
        ctx.bloques_codigo = []
        return ctx


class RenderizarLatex:
    nombre = "renderizar-latex"

    def procesar(self, ctx: ContextoDocumento) -> ContextoDocumento:
        ctx.texto = procesar_latex_en_markdown(ctx.texto)
        return ctx


class ConvertirAHtml:
    nombre = "convertir-a-html"

    def procesar(self, ctx: ContextoDocumento) -> ContextoDocumento:
        import markdown

        ctx.html_body = markdown.markdown(
            ctx.texto, extensions=list(EXTENSIONES_MARKDOWN), extension_configs=CONFIG_EXTENSIONES
        )
        return ctx


class AplicarPlantilla:
    nombre = "aplicar-plantilla"

    def procesar(self, ctx: ContextoDocumento) -> ContextoDocumento:
        ctx.html_completo = construir_html(ctx.html_body, css_resaltado_para_tema(ctx.css) + ctx.css)
        return ctx


class EscribirPdf:
    """Escribe ``<out_docs>/<nombre>.pdf``. Un fallo se anota en `ctx.fallo` sin abortar."""
    nombre = "escribir-pdf"

    def procesar(self, ctx: ContextoDocumento) -> ContextoDocumento:
        ruta_pdf = os.path.join(ctx.out_docs, f"{ctx.documento.nombre}.pdf")
        base_url = Path(ctx.documento.subcarpeta).resolve().as_uri() + "/"
        try:
            generar_pdf(ctx.html_completo, ruta_pdf, base_url)
        except Exception as e:
            print(f"  [Error] No se pudo generar el PDF de '{ctx.documento.nombre}': {e}")
            ctx.fallo = str(e)
            return ctx
        ctx.ruta_pdf = ruta_pdf
        print(f"  [OK] PDF generado: {ruta_pdf}")
        return ctx
