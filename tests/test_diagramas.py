import os
import tempfile
from pathlib import Path
from unittest.mock import patch

from pdu.diagramas.descubrimiento import detectar_diagramas_mermaid, resolver_ruta_diagrama, esta_actualizado
from pdu.diagramas.filtros import _imprimir_error_mmdc


def test_detectar_referencias_ignora_bloques_de_codigo():
    with tempfile.TemporaryDirectory() as d:
        md = os.path.join(d, "a.md")
        with open(md, "w", encoding="utf-8") as f:
            f.write("![d](diag.mmd)\n```\n![x](nope.mmd)\n```\n")
        refs = detectar_diagramas_mermaid([md])
        assert refs == ["diag"]


def test_resolver_ruta_candidatos(tmp_path):
    docs = tmp_path / "docs"
    (docs / "diagramas").mkdir(parents=True)
    (docs / "diagramas" / "flujo.mmd").write_text("graph TD;A-->B")
    res = resolver_ruta_diagrama("flujo", str(docs), str(docs / "markdown" / "P"))
    assert res is not None and res.endswith("flujo.mmd")


def test_esta_actualizado_false_si_falta(tmp_path):
    mmd = tmp_path / "a.mmd"
    mmd.write_text("x")
    assert esta_actualizado(str(mmd), str(tmp_path / "a.png"), str(tmp_path / "a.pdf")) is False