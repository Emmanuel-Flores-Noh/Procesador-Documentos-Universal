"""Tuberías de la etapa de diagramas y API pública."""
from __future__ import annotations

import os

from ..nucleo.contextos import ContextoDiagramas
from ..nucleo.errores import ErrorProcesador
from ..nucleo.filtros import Tuberia
from .descubrimiento import obtener_salida_diagramas
from .filtros import (
    CompilarPendientes,
    DescubrirArchivos,
    DetectarReferencias,
    OmitirActualizados,
    PrepararSalidas,
    ResolverRutas,
    VerificarDependencias,
)


def construir_tuberia_autonoma(origen, forzar: bool = False) -> Tuberia:
    """Compila los .mmd de una carpeta (o lista de archivos). `mmdc` es obligatorio."""
    return Tuberia(
        "diagramas",
        [
            DescubrirArchivos(origen),
            OmitirActualizados(forzar=forzar),
            VerificarDependencias(obligatorio=True),
            PrepararSalidas(),
            CompilarPendientes(),
        ],
    )


def construir_tuberia_documento() -> Tuberia:
    """Compila solo los diagramas referenciados por un documento. `mmdc` es opcional."""
    return Tuberia(
        "diagramas-documento",
        [
            DetectarReferencias(),
            ResolverRutas(),
            OmitirActualizados(informar=False),
            VerificarDependencias(obligatorio=False),
            PrepararSalidas(),
            CompilarPendientes(),
        ],
    )


def ejecutar_diagramas_autonomo(
    origen,
    out_diagramas: str,
    docs_dir: str | None = None,
    *,
    forzar: bool = False,
    trabajos: int | None = None,
    planos: bool = False,
):
    """Compila diagramas y devuelve ``(ok, ctx)``.

    Con ``planos=True`` PNG, PDF y SVG se guardan juntos en `out_diagramas`; si
    no, en las subcarpetas ``png/``, ``pdf/`` y ``svg/``.
    """
    if docs_dir is None:
        base = origen[0] if isinstance(origen, (list, tuple)) and origen else origen
        docs_dir = os.path.dirname(os.path.abspath(base))
    out_png = out_diagramas if planos else os.path.join(out_diagramas, "png")
    out_pdf = out_diagramas if planos else os.path.join(out_diagramas, "pdf")
    out_svg = out_diagramas if planos else os.path.join(out_diagramas, "svg")
    ctx = ContextoDiagramas(
        docs_dir=docs_dir, out_png=out_png, out_pdf=out_pdf, out_svg=out_svg, trabajos=trabajos
    )
    try:
        construir_tuberia_autonoma(origen, forzar=forzar).ejecutar(ctx)
    except ErrorProcesador as e:
        if ctx.dependencias_ok:  # el mensaje de mmdc faltante ya se mostró
            print(f"Error: {e}")
        return False, ctx
    return ctx.fallidos == 0, ctx


def compilar_diagramas_requeridos(archivos_md, docs_dir, subcarpeta, diagramas_out=None, trabajos=None):
    out_diagramas = obtener_salida_diagramas(docs_dir, diagramas_out)
    ctx = ContextoDiagramas(
        docs_dir=docs_dir,
        out_png=os.path.join(out_diagramas, "png"),
        out_pdf=os.path.join(out_diagramas, "pdf"),
        out_svg=os.path.join(out_diagramas, "svg"),
        archivos_md=list(archivos_md),
        subcarpeta=subcarpeta,
        trabajos=trabajos,
    )
    construir_tuberia_documento().ejecutar(ctx)
    return ctx


def procesar_diagramas(dir_diagramas, out_png, out_pdf, config_puppeteer=None, mmdc=None, out_svg=None):
    """Compatibilidad con la API antigua: compila todos los .mmd de `dir_diagramas`.

    Sin `out_svg`, el SVG se guarda en ``svg/`` junto a la carpeta de los PNG.
    """
    ctx = ContextoDiagramas(
        docs_dir=os.path.dirname(os.path.abspath(dir_diagramas)),
        out_png=out_png,
        out_pdf=out_pdf,
        out_svg=out_svg or os.path.join(os.path.dirname(os.path.abspath(out_png)), "svg"),
        mmdc=mmdc,
        config_puppeteer=config_puppeteer,
    )
    construir_tuberia_autonoma(dir_diagramas, forzar=True).ejecutar(ctx)
    return ctx
