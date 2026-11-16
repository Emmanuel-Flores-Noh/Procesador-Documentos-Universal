"""Generación de PDF con WeasyPrint (importado bajo demanda: tarda varios segundos)."""
from __future__ import annotations


def generar_pdf(html_completo: str, ruta_pdf: str, base_url: str) -> None:
    from weasyprint import HTML

    HTML(string=html_completo, base_url=base_url).write_pdf(ruta_pdf)
