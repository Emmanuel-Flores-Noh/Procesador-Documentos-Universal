"""Contextos (dataclasses) que fluyen por las tuberías."""
from __future__ import annotations

import os
from dataclasses import dataclass, field


@dataclass
class Documento:
    """Un documento final: una carpeta con uno o varios .md que forman un PDF."""
    subcarpeta: str
    nombre: str
    archivos_md: list[str]


@dataclass
class Diagrama:
    referencia: str
    ruta_mmd: str
    ruta_png: str = ""
    ruta_pdf: str = ""

    @property
    def nombre(self) -> str:
        return os.path.basename(self.ruta_mmd)


@dataclass
class ContextoDiagramas:
    docs_dir: str
    out_png: str
    out_pdf: str
    archivos_md: list[str] = field(default_factory=list)
    subcarpeta: str | None = None
    referencias: list[str] = field(default_factory=list)
    diagramas: list[Diagrama] = field(default_factory=list)
    pendientes: list[Diagrama] = field(default_factory=list)
    mmdc: str | None = None
    config_puppeteer: str | None = None
    dependencias_ok: bool = True
    trabajos: int | None = None
    compilados: int = 0
    fallidos: int = 0


@dataclass
class TextoProtegido:
    texto: str
    bloques: list[str] = field(default_factory=list)


@dataclass
class ContextoDocumento:
    documento: Documento
    docs_dir: str
    out_docs: str
    diagramas_out: str
    estilo: str = "default"
    css: str = ""
    texto: str = ""
    bloques_codigo: list[str] = field(default_factory=list)
    html_body: str = ""
    html_completo: str = ""
    ruta_pdf: str = ""
    trabajos: int | None = None
    fallo: str | None = None

    @property
    def dir_png(self) -> str:
        return os.path.join(self.diagramas_out, "png")
