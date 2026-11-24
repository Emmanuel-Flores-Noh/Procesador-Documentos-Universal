"""Filtros de la etapa de diagramas."""
from __future__ import annotations

import os

from ..nucleo.contextos import ContextoDiagramas
from ..nucleo.errores import DependenciaFaltante
from ..nucleo.rutas import preparar_directorios
from .compilador import compilar_varios
from .descubrimiento import (
    archivos_mmd_de_entrada,
    crear_diagrama,
    detectar_diagramas_mermaid,
    esta_actualizado,
    resolver_ruta_diagrama,
)
from .entorno import MENSAJE_MMDC_FALTANTE, buscar_mmdc, preparar_config_mermaid_svg, preparar_puppeteer


def _imprimir_error_mmdc() -> None:
    print(MENSAJE_MMDC_FALTANTE)


class DescubrirArchivos:
    """Añade al contexto los .mmd de una carpeta o una lista de archivos."""
    nombre = "descubrir-archivos"

    def __init__(self, origen):
        self.origen = origen

    def procesar(self, ctx: ContextoDiagramas) -> ContextoDiagramas:
        if isinstance(self.origen, (list, tuple)):
            archivos = list(self.origen)
        else:
            archivos = archivos_mmd_de_entrada(self.origen)
        if not archivos:
            print(f"No se encontraron archivos .mmd en '{self.origen}'.")
        ctx.diagramas = [
            crear_diagrama(os.path.splitext(os.path.basename(r))[0], r, ctx.out_png, ctx.out_pdf, ctx.out_svg)
            for r in archivos
        ]
        return ctx


class DetectarReferencias:
    """Lee los .md del documento y anota los diagramas que referencian."""
    nombre = "detectar-referencias"

    def procesar(self, ctx: ContextoDiagramas) -> ContextoDiagramas:
        ctx.referencias = detectar_diagramas_mermaid(ctx.archivos_md)
        return ctx


class ResolverRutas:
    nombre = "resolver-rutas"

    def procesar(self, ctx: ContextoDiagramas) -> ContextoDiagramas:
        for referencia in ctx.referencias:
            ruta_mmd = resolver_ruta_diagrama(referencia, ctx.docs_dir, ctx.subcarpeta or "")
            if ruta_mmd is None:
                print(f"  [Advertencia] No se encontró el diagrama '{referencia}.mmd'.")
                continue
            ctx.diagramas.append(crear_diagrama(referencia, ruta_mmd, ctx.out_png, ctx.out_pdf, ctx.out_svg))
        return ctx


class OmitirActualizados:
    """Deja en `ctx.pendientes` solo los diagramas cuyo PNG/PDF/SVG está desactualizado."""
    nombre = "omitir-actualizados"

    def __init__(self, forzar: bool = False, informar: bool = True):
        self.forzar = forzar
        self.informar = informar

    def procesar(self, ctx: ContextoDiagramas) -> ContextoDiagramas:
        if self.forzar:
            ctx.pendientes = list(ctx.diagramas)
            return ctx
        ctx.pendientes = [
            d for d in ctx.diagramas if not esta_actualizado(d.ruta_mmd, d.ruta_png, d.ruta_pdf, d.ruta_svg)
        ]
        al_dia = len(ctx.diagramas) - len(ctx.pendientes)
        if al_dia and self.informar:
            print(f"  {al_dia} diagrama(s) ya al día (usa --forzar para recompilar).")
        return ctx


class VerificarDependencias:
    """Localiza `mmdc` si hay diagramas pendientes.

    Si falta y es obligatorio, aborta la tubería; si no, solo avisa.
    """
    nombre = "verificar-dependencias"

    def __init__(self, obligatorio: bool = True):
        self.obligatorio = obligatorio

    def procesar(self, ctx: ContextoDiagramas) -> ContextoDiagramas:
        if not ctx.pendientes:
            return ctx
        ctx.mmdc = ctx.mmdc or buscar_mmdc()
        ctx.dependencias_ok = ctx.mmdc is not None
        if ctx.dependencias_ok:
            return ctx
        if self.obligatorio:
            _imprimir_error_mmdc()
            raise DependenciaFaltante("No se encontró Mermaid CLI (mmdc).")
        print("  [Advertencia] " + MENSAJE_MMDC_FALTANTE)
        return ctx


class PrepararSalidas:
    nombre = "preparar-salidas"

    def procesar(self, ctx: ContextoDiagramas) -> ContextoDiagramas:
        if not ctx.pendientes or not ctx.dependencias_ok:
            return ctx
        preparar_directorios([ctx.out_png, ctx.out_pdf, ctx.out_svg or ctx.out_png])
        if ctx.config_puppeteer is None:
            ctx.config_puppeteer = preparar_puppeteer()
        if ctx.config_mermaid is None:
            ctx.config_mermaid = preparar_config_mermaid_svg()
        return ctx


class CompilarPendientes:
    nombre = "compilar-pendientes"

    def procesar(self, ctx: ContextoDiagramas) -> ContextoDiagramas:
        if not ctx.pendientes or not ctx.dependencias_ok:
            return ctx
        compilados, fallidos = compilar_varios(
            ctx.pendientes, ctx.config_puppeteer, ctx.mmdc, ctx.trabajos, config_mermaid=ctx.config_mermaid
        )
        ctx.compilados += compilados
        ctx.fallidos += fallidos
        return ctx
