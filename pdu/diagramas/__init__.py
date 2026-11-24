"""Etapa 1: diagramas Mermaid (.mmd -> PNG, PDF y SVG)."""
from ..nucleo.rutas import preparar_directorios
from .compilador import compilar_diagrama, compilar_varios
from .entorno import (
    buscar_mmdc,
    buscar_navegador,
    faltan_dependencias,
    preparar_config_mermaid_svg,
    preparar_puppeteer,
)
from .tuberia import compilar_diagramas_requeridos, ejecutar_diagramas_autonomo, procesar_diagramas

__all__ = [
    "buscar_mmdc",
    "buscar_navegador",
    "compilar_diagrama",
    "compilar_diagramas_requeridos",
    "compilar_varios",
    "ejecutar_diagramas_autonomo",
    "faltan_dependencias",
    "preparar_config_mermaid_svg",
    "preparar_directorios",
    "preparar_puppeteer",
    "procesar_diagramas",
]
