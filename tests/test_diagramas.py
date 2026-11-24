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


def test_esta_actualizado_exige_svg(tmp_path):
    mmd = tmp_path / "a.mmd"
    mmd.write_text("x")
    for ext in ("png", "pdf"):
        (tmp_path / f"a.{ext}").write_text("x")
    salidas = [str(tmp_path / f"a.{e}") for e in ("png", "pdf")]
    assert esta_actualizado(str(mmd), *salidas) is True
    assert esta_actualizado(str(mmd), *salidas, str(tmp_path / "a.svg")) is False


def test_crear_diagrama_rutas_svg(tmp_path):
    from pdu.diagramas.descubrimiento import crear_diagrama
    d = crear_diagrama("flujo", "/x/flujo.mmd", "/o/png", "/o/pdf", "/o/svg")
    assert d.ruta_svg == os.path.join("/o/svg", "flujo.svg")


def test_compilar_diagrama_genera_svg_con_config(tmp_path):
    from pdu.diagramas import compilador
    llamadas = []
    with patch.object(compilador, "_ejecutar_mmdc", lambda *a: llamadas.append(a)):
        ok = compilador.compilar_diagrama(
            "a.mmd", str(tmp_path / "png" / "a.png"), str(tmp_path / "pdf" / "a.pdf"), "pp.json", "mmdc",
            ruta_svg=str(tmp_path / "svg" / "a.svg"), config_mermaid="cfg.json",
        )
    assert ok
    assert [Path(a[3]).suffix for a in llamadas] == [".png", ".pdf", ".svg"]
    assert llamadas[-1][4] == "cfg.json" and llamadas[0][4] is None
    assert (tmp_path / "svg").is_dir()


def test_sustituir_diagramas_usa_svg(tmp_path):
    from pdu.markdown.imagenes import PATRON_MMD, reemplazar_diagramas_por_svg
    (tmp_path / "flujo.svg").write_text("<svg/>")
    res = PATRON_MMD.sub(lambda m: reemplazar_diagramas_por_svg(m, str(tmp_path)), "![F](flujo.mmd)")
    assert res == f"![F]({(tmp_path / 'flujo.svg').as_uri()})"
