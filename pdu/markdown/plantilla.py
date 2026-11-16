"""Plantilla HTML del documento."""
from __future__ import annotations

PLANTILLA_HTML = """<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
{{CSS}}
    </style>
</head>
<body>
{{CONTENIDO}}
</body>
</html>
"""


def construir_html(html_body: str, css: str) -> str:
    return PLANTILLA_HTML.replace("{{CSS}}", css).replace("{{CONTENIDO}}", html_body)